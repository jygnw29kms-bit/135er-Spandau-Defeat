from pathlib import Path
files=[Path(r'C:\Users\dezen\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\F14TomcatRC\F14TomcatRC.py'),Path(r'C:\Users\dezen\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\F14TomcatRC_v18\F14TomcatRC_v18.py')]
fn=r'''

def _cyl_body_v30(root,name,cx,cy,z0,radius,height):
    sk=root.sketches.add(axis_plane(root,'z',z0)); sk.name=name+'_SK'
    ctr=model_point(sk,cx,cy,z0); sk.sketchCurves.sketchCircles.addByCenterRadius(ctr,mm(radius))
    if sk.profiles.count!=1: raise RuntimeError('Cylinder profile failed '+name)
    ex=root.features.extrudeFeatures; ei=ex.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ei.setDistanceExtent(False,adsk.core.ValueInput.createByReal(mm(height)))
    body=ex.add(ei).bodies.item(0); body.name=name; return body

def _cut_cyl_v30(root,target,name,cx,cy,z0,radius,height):
    tool=_cyl_body_v30(root,name,cx,cy,z0,radius,height)
    tools=adsk.core.ObjectCollection.create(); tools.add(tool)
    ci=root.features.combineFeatures.createInput(target,tools); ci.operation=adsk.fusion.FeatureOperations.CutFeatureOperation; ci.isKeepToolBodies=False
    root.features.combineFeatures.add(ci)

def build_pivot_cassette_review_v30():
    """Add actual RC pivot shaft/bearing/hardpoint cassette envelopes to the v29 robust-clearance airframe."""
    build_robust_datum_clearance_review_v29()
    design=adsk.fusion.Design.cast(_app.activeProduct); root=design.rootComponent
    _app.activeDocument.name='F14_v30_PIVOT_CASSETTE_MECHANICAL_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    with open(os.path.join(base,'F14_pivot_cassette_screen_v30.json'),encoding='utf-8') as stream: screen=json.load(stream)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in']); px=pivot['derived_full_scale_pivot_fs_in']*factor; py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]; dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in'])
    pz=(s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz)*factor
    fus=next(b for b in root.bRepBodies if b.name=='UPC_FUSELAGE_ROBUST_CLEARANCE_CUT_v29')
    temporary=adsk.fusion.TemporaryBRepManager.get(); plates=[]; hardware=[]; plate_checks=[]; sweep_checks=[]
    plate_x0,plate_x1=px-22.0,px+22.0; plate_half_y=12.0; plate_t=2.0
    lower_z0=pz-12.5; upper_z0=pz+10.5
    for sign,label in [(1,'R'),(-1,'L')]:
        y=sign*py
        boss=next(b for b in root.bRepBodies if b.name=='ENG_PIVOT_BOSS_'+label+'_24OD_v19')
        # Machine the moving boss envelope for a 6.2-mm through bore and 13.1-mm x 5.1-mm bearing counterbores.
        _cut_cyl_v30(root,boss,'CUT_SHAFT_BORE_'+label+'_v30',px,y,pz-10.2,3.1,20.4)
        _cut_cyl_v30(root,boss,'CUT_BRG_LOWER_'+label+'_v30',px,y,pz-10.1,6.55,5.2)
        _cut_cyl_v30(root,boss,'CUT_BRG_UPPER_'+label+'_v30',px,y,pz+4.9,6.55,5.2)
        boss.name='ENG_PIVOT_BOSS_'+label+'_24OD_BEARING_SEATS_v30'
        # Fixed hardpoint plates touch the boss only through thrust hardware; 20-mm clear moving gap remains between plates.
        for pos,z0 in [('LOWER',lower_z0),('UPPER',upper_z0)]:
            plate=extrude_poly(root,'ENG_HARDPOINT_'+pos+'_'+label+'_v30',[(plate_x0,y-plate_half_y),(plate_x1,y-plate_half_y),(plate_x1,y+plate_half_y),(plate_x0,y+plate_half_y)],z0,plate_t)
            _cut_cyl_v30(root,plate,'CUT_PLATE_SHAFT_'+pos+'_'+label+'_v30',px,y,z0-0.1,3.1,plate_t+0.2)
            plate.opacity=0.55; plates.append(plate)
            # containment fraction inside provisional registered fuselage solid
            pcopy=temporary.copy(plate); fcopy=temporary.copy(fus); pv=plate.volume
            ok=temporary.booleanOperation(pcopy,fcopy,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=pcopy.volume if ok and pcopy.isValid else 0.0
            plate_checks.append(dict(side=label,plate=pos,plate_volume_cm3=pv,inside_fuselage_volume_cm3=iv,inside_fraction=(iv/pv if pv>0 else 0.0)))
        # Hardware reference envelopes: two 6x13x5 bearings, 6-mm shaft, two 16-mm thrust washers.
        for pos,z0 in [('LOWER',pz-10.0),('UPPER',pz+5.0)]:
            brg=_cyl_body_v30(root,'REF_BEARING_6x13x5_'+pos+'_'+label+'_v30',px,y,z0,6.5,5.0); brg.opacity=0.25; hardware.append(brg)
        shaft=_cyl_body_v30(root,'REF_SHAFT_6mm_'+label+'_v30',px,y,pz-13.0,3.0,26.0); shaft.opacity=0.35; hardware.append(shaft)
        for pos,z0 in [('LOWER',pz-10.5),('UPPER',pz+10.0)]:
            wash=_cyl_body_v30(root,'REF_THRUST_16OD_'+pos+'_'+label+'_v30',px,y,z0,8.0,0.5); wash.opacity=0.2; hardware.append(wash)
    # Check fixed hardpoint plates against moving wing + root-lug BReps across the full dense sweep.
    for sweep in range(20,69,2):
        for sign,label in [(1,'R'),(-1,'L')]:
            angle=-sign*math.radians(sweep-20.0); rot=adsk.core.Matrix3D.create(); rot.setToRotation(angle,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(sign*py),mm(pz)))
            wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_')); lug=next(b for b in root.bRepBodies if b.name=='ENG_ROOT_LUG_'+label+'_v19')
            sideplates=[p for p in plates if p.name.endswith('_'+label+'_v30')]
            for moving_body,kind in [(wing,'outer_wing'),(lug,'root_lug')]:
                moving=temporary.copy(moving_body); temporary.transform(moving,rot)
                for plate in sideplates:
                    target=temporary.copy(moving); tool=temporary.copy(plate); ok=temporary.booleanOperation(target,tool,adsk.fusion.BooleanTypes.IntersectionBooleanType)
                    iv=target.volume if ok and target.isValid else 0.0
                    sweep_checks.append(dict(sweep_deg=sweep,side=label,moving_kind=kind,plate=plate.name,intersection_volume_cm3=iv,positive_overlap=iv>1e-4))
    residual=[r for r in sweep_checks if r['positive_overlap']]
    plate_vol=sum(p.volume for p in plates); shaft_vol=2.0*math.pi*(0.3**2)*2.6 # cm^3; radius/height in cm
    audit=dict(status='PIVOT_CASSETTE_MECHANICAL_PACKAGING_REVIEW',source_revision='v29',engineering_screen=screen,
      geometry=dict(pivot_model_mm=dict(x=px,y=py,z=pz),shaft_d_mm=6.0,bearing_envelope_mm=[6,13,5],bearings_per_pivot=2,
        plate_planform_mm=[44,24],plate_thickness_mm=2.0,moving_gap_between_plates_mm=20.0,thrust_washer_mm=[6,16,0.5]),
      hardpoint_plate_containment=plate_checks,fixed_plate_sweep_collision_records=sweep_checks,residual_positive_overlaps=residual,
      dense_plate_clearance_pass=(len(residual)==0),hardpoint_plate_total_volume_cm3=plate_vol,steel_shaft_reference_volume_cm3=shaft_vol,
      bearing_ratings_verified=False,shaft_alloy_verified=False,hardpoint_material_verified=False,mechanical_detail_release=False,print_release=False,flight_release=False)
    outdir=os.path.join(config['export_dir'],'pivot_cassette_v30'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v30_PIVOT_CASSETTE_MECHANICAL_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v30 export failed')
    with open(os.path.join(outdir,'F14_v30_pivot_cassette_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v30_pivot_cassette_review.png'),1600,1000)
    return audit

'''
for path in files:
    s=path.read_text(encoding='utf-8')
    insert=s.index('def build_project_revision():')
    if 'def build_pivot_cassette_review_v30()' not in s: s=s[:insert]+fn+s[insert:]
    s=s.replace('return build_robust_datum_clearance_review_v29()','return build_pivot_cassette_review_v30()',1)
    path.write_text(s,encoding='utf-8'); print('patched',path)
