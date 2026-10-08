from pathlib import Path
files=[Path(r'C:\Users\dezen\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\F14TomcatRC\F14TomcatRC.py'),Path(r'C:\Users\dezen\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\F14TomcatRC_v18\F14TomcatRC_v18.py')]
fn=r'''

def build_wingbox_fork_hardpoint_review_v31():
    """Replace local v30 plates with fork hardpoints that carry pivot loads inboard into the central structure."""
    build_robust_datum_clearance_review_v29()
    design=adsk.fusion.Design.cast(_app.activeProduct); root=design.rootComponent
    _app.activeDocument.name='F14_v31_WINGBOX_FORK_HARDPOINT_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    with open(os.path.join(base,'F14_pivot_cassette_screen_v30.json'),encoding='utf-8') as stream: screen=json.load(stream)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in']); px=pivot['derived_full_scale_pivot_fs_in']*factor; py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]; dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in'])
    pz=(s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz)*factor
    fus=next(b for b in root.bRepBodies if b.name=='UPC_FUSELAGE_ROBUST_CLEARANCE_CUT_v29')
    temporary=adsk.fusion.TemporaryBRepManager.get(); plates=[]; segment_checks=[]; sweep_checks=[]; hardware=[]
    plate_t=2.0; lower_z0=pz-12.5; upper_z0=pz+10.5; inboard_abs_y=70.0
    for sign,label in [(1,'R'),(-1,'L')]:
        y=sign*py; boss=next(b for b in root.bRepBodies if b.name=='ENG_PIVOT_BOSS_'+label+'_24OD_v19')
        _cut_cyl_v30(root,boss,'CUT_SHAFT_BORE_'+label+'_v31',px,y,pz-10.2,3.1,20.4)
        _cut_cyl_v30(root,boss,'CUT_BRG_LOWER_'+label+'_v31',px,y,pz-10.1,6.55,5.2)
        _cut_cyl_v30(root,boss,'CUT_BRG_UPPER_'+label+'_v31',px,y,pz+4.9,6.55,5.2)
        boss.name='ENG_PIVOT_BOSS_'+label+'_24OD_BEARING_SEATS_v31'
        pad_in=y-sign*20.0; pad_out=y+sign*12.0; strap_in=sign*inboard_abs_y
        pad_y0,pad_y1=min(pad_in,pad_out),max(pad_in,pad_out); strap_y0,strap_y1=min(strap_in,pad_in),max(strap_in,pad_in)
        for pos,z0 in [('LOWER',lower_z0),('UPPER',upper_z0)]:
            parts=[]
            defs=[('PAD',px-22,px+22,pad_y0,pad_y1),('FRONT_STRAP',px-22,px-10,strap_y0,strap_y1),('REAR_STRAP',px+10,px+22,strap_y0,strap_y1)]
            for part,x0,x1,y0,y1 in defs:
                b=extrude_poly(root,'TMP_'+part+'_'+pos+'_'+label+'_v31',[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,plate_t)
                pv=b.volume; bc=temporary.copy(b); fc=temporary.copy(fus); ok=temporary.booleanOperation(bc,fc,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=bc.volume if ok and bc.isValid else 0.0
                segment_checks.append(dict(side=label,plate=pos,segment=part,volume_cm3=pv,inside_fuselage_volume_cm3=iv,inside_fraction=(iv/pv if pv else 0.0)))
                parts.append(b)
            target=parts[0]; tools=adsk.core.ObjectCollection.create(); tools.add(parts[1]); tools.add(parts[2])
            ci=root.features.combineFeatures.createInput(target,tools); ci.operation=adsk.fusion.FeatureOperations.JoinFeatureOperation; ci.isKeepToolBodies=False; root.features.combineFeatures.add(ci)
            target.name='ENG_WINGBOX_FORK_'+pos+'_'+label+'_v31'; _cut_cyl_v30(root,target,'CUT_FORK_SHAFT_'+pos+'_'+label+'_v31',px,y,z0-0.1,3.1,plate_t+0.2); target.opacity=0.55; plates.append(target)
        for pos,z0 in [('LOWER',pz-10.0),('UPPER',pz+5.0)]:
            brg=_cyl_body_v30(root,'REF_BEARING_6x13x5_'+pos+'_'+label+'_v31',px,y,z0,6.5,5.0); brg.opacity=0.25; hardware.append(brg)
        shaft=_cyl_body_v30(root,'REF_SHAFT_6mm_'+label+'_v31',px,y,pz-13.0,3.0,26.0); shaft.opacity=0.35; hardware.append(shaft)
        for pos,z0 in [('LOWER',pz-10.5),('UPPER',pz+10.0)]:
            wash=_cyl_body_v30(root,'REF_THRUST_16OD_'+pos+'_'+label+'_v31',px,y,z0,8.0,0.5); wash.opacity=0.2; hardware.append(wash)
    for sweep in range(20,69,2):
        for sign,label in [(1,'R'),(-1,'L')]:
            angle=-sign*math.radians(sweep-20.0); rot=adsk.core.Matrix3D.create(); rot.setToRotation(angle,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(sign*py),mm(pz)))
            wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_')); lug=next(b for b in root.bRepBodies if b.name=='ENG_ROOT_LUG_'+label+'_v19'); sideplates=[p for p in plates if p.name.endswith('_'+label+'_v31')]
            for moving_body,kind in [(wing,'outer_wing'),(lug,'root_lug')]:
                moving=temporary.copy(moving_body); temporary.transform(moving,rot)
                for plate in sideplates:
                    t=temporary.copy(moving); tool=temporary.copy(plate); ok=temporary.booleanOperation(t,tool,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=t.volume if ok and t.isValid else 0.0
                    sweep_checks.append(dict(sweep_deg=sweep,side=label,moving_kind=kind,plate=plate.name,intersection_volume_cm3=iv,positive_overlap=iv>1e-4))
    residual=[r for r in sweep_checks if r['positive_overlap']]
    strap_fracs=[c['inside_fraction'] for c in segment_checks if 'STRAP' in c['segment']]
    plate_vol=sum(p.volume for p in plates); density=1.60
    audit=dict(status='WINGBOX_FORK_HARDPOINT_PACKAGING_REVIEW',source_revision='v29',engineering_screen=screen,
      geometry=dict(pivot_model_mm=dict(x=px,y=py,z=pz),fork_inboard_abs_y_mm=inboard_abs_y,plate_thickness_mm=plate_t,pad_planform_mm=[44,32],strap_width_mm=12),
      segment_containment=segment_checks,min_inboard_strap_inside_fraction=min(strap_fracs) if strap_fracs else None,
      fixed_fork_sweep_collision_records=sweep_checks,residual_positive_overlaps=residual,dense_fork_clearance_pass=(len(residual)==0),
      hardpoint_plate_total_volume_cm3=plate_vol,hardpoint_mass_estimate_g_at_1p60=plate_vol*density,
      bearing_ratings_verified=False,shaft_alloy_verified=False,hardpoint_material_verified=False,mechanical_detail_release=False,print_release=False,flight_release=False)
    outdir=os.path.join(config['export_dir'],'wingbox_fork_v31'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v31_WINGBOX_FORK_HARDPOINT_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v31 export failed')
    with open(os.path.join(outdir,'F14_v31_wingbox_fork_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v31_wingbox_fork_review.png'),1600,1000)
    return audit

'''
for path in files:
    s=path.read_text(encoding='utf-8'); insert=s.index('def build_project_revision():')
    if 'def build_wingbox_fork_hardpoint_review_v31()' not in s: s=s[:insert]+fn+s[insert:]
    s=s.replace('return build_pivot_cassette_review_v30()','return build_wingbox_fork_hardpoint_review_v31()',1)
    path.write_text(s,encoding='utf-8'); print('patched',path)
