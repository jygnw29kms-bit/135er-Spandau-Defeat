from pathlib import Path
files=[Path(r'C:\Users\dezen\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\F14TomcatRC\F14TomcatRC.py'),Path(r'C:\Users\dezen\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\F14TomcatRC_v18\F14TomcatRC_v18.py')]
fn=r'''

def build_sweep_servo_packaging_review_v35():
    """Scan a central 42x21x40 mm sweep-servo envelope for fuselage containment and moving-wing clearance."""
    build_crosstie_riser_socket_review_v34()
    design=adsk.fusion.Design.cast(_app.activeProduct); root=design.rootComponent
    _app.activeDocument.name='F14_v35_SWEEP_SERVO_PACKAGING_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in']); px=pivot['derived_full_scale_pivot_fs_in']*factor; py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]; dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in']); pz=(s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz)*factor
    fus=next(b for b in root.bRepBodies if b.name=='UPC_FUSELAGE_ROBUST_CLEARANCE_CUT_v29'); temporary=adsk.fusion.TemporaryBRepManager.get()
    # Add upper carbon tie packaging envelopes so servo selection sees the complete current wingbox concept.
    upper=[]
    for foreaft,xc in [('FRONT',px-16.0),('REAR',px+16.0)]:
        tie=extrude_poly(root,'REF_CF6x4_'+foreaft+'_UPPER_v35',[(xc-3,-72),(xc+3,-72),(xc+3,72),(xc-3,72)],pz+8.5,6.0); tie.opacity=0.20; upper.append(tie)
    lower=[b for b in root.bRepBodies if b.name in ['REF_CF6x4_FRONT_LOWER_v34','REF_CF6x4_REAR_LOWER_v34']]
    risers=[b for b in root.bRepBodies if b.name.startswith('ENG_RISER_SOCKET_') and b.name.endswith('_v34')]
    forks=[b for b in root.bRepBodies if b.name.startswith('ENG_WINGBOX_FORK_') and b.name.endswith('_v31')]
    fixed_structure=upper+lower+risers+forks
    candidates=[]; candidate_bodies=[]
    # Place servo forward of front tie; scan X/Z while centered on aircraft centerline.
    for xc in [px-92,px-82,px-72,px-62,px-52]:
        for zc in [pz-8,pz+2,pz+12,pz+22]:
            x0,x1=xc-21,xc+21; y0,y1=-10.5,10.5; z0,z1=zc-20,zc+20
            body=extrude_poly(root,'REF_SWEEP_SERVO_X%03d_Z%03d_v35'%(round(xc),round(zc)),[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,40.0); body.opacity=0.06; candidate_bodies.append(body)
            bc=temporary.copy(body); fc=temporary.copy(fus); bv=body.volume; ok=temporary.booleanOperation(bc,fc,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=bc.volume if ok and bc.isValid else 0.0
            structural=[]; structural_iv=0.0
            for part in fixed_structure:
                a=temporary.copy(body); b=temporary.copy(part); ok2=temporary.booleanOperation(a,b,adsk.fusion.BooleanTypes.IntersectionBooleanType); ov=a.volume if ok2 and a.isValid else 0.0; structural_iv+=ov
                if ov>1e-4: structural.append(dict(part=part.name,intersection_volume_cm3=ov))
            moving_max=0.0; moving_hits=[]
            for sweep in range(20,69,4):
                for sign,label in [(1,'R'),(-1,'L')]:
                    angle=-sign*math.radians(sweep-20.0); rot=adsk.core.Matrix3D.create(); rot.setToRotation(angle,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(sign*py),mm(pz)))
                    wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_')); lug=next(b for b in root.bRepBodies if b.name=='ENG_ROOT_LUG_'+label+'_v19')
                    for mov,kind in [(wing,'outer_wing'),(lug,'root_lug')]:
                        a=temporary.copy(mov); temporary.transform(a,rot); b=temporary.copy(body); ok3=temporary.booleanOperation(a,b,adsk.fusion.BooleanTypes.IntersectionBooleanType); ov=a.volume if ok3 and a.isValid else 0.0; moving_max=max(moving_max,ov)
                        if ov>1e-4: moving_hits.append(dict(sweep_deg=sweep,side=label,kind=kind,intersection_volume_cm3=ov))
            rec=dict(x_center_mm=xc,z_center_mm=zc,bounds_mm=dict(x=[x0,x1],y=[y0,y1],z=[z0,z1]),volume_cm3=bv,
                inside_fuselage_volume_cm3=iv,inside_fraction=(iv/bv if bv else 0.0),structural_intersection_volume_cm3=structural_iv,structural_hits=structural,
                moving_max_intersection_cm3=moving_max,moving_hits=moving_hits,fully_packaged=(iv/bv>0.995 and structural_iv<1e-4 and moving_max<1e-4),body_name=body.name)
            candidates.append(rec)
    good=[r for r in candidates if r['fully_packaged']]
    if good: chosen=max(good,key=lambda r:(r['inside_fraction'],-abs((px-72)-r['x_center_mm']),-abs((pz+2)-r['z_center_mm'])))
    else: chosen=max(candidates,key=lambda r:(r['inside_fraction'],-r['structural_intersection_volume_cm3'],-r['moving_max_intersection_cm3']))
    for body in candidate_bodies:
        body.isLightBulbOn=(body.name==chosen['body_name'])
        if body.name==chosen['body_name']: body.name='RC_SWEEP_SERVO_ENVELOPE_v35'; body.opacity=0.35
    # Add conservative service/mounting envelope around selected servo: +3 mm XY, +2 mm Z.
    c=chosen; x0,x1=c['bounds_mm']['x'][0]-3,c['bounds_mm']['x'][1]+3; y0,y1=c['bounds_mm']['y'][0]-3,c['bounds_mm']['y'][1]+3; z0,z1=c['bounds_mm']['z'][0]-2,c['bounds_mm']['z'][1]+2
    service=extrude_poly(root,'RC_SWEEP_SERVO_SERVICE_ENVELOPE_v35',[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1-z0); service.opacity=0.10
    sc=temporary.copy(service); fc=temporary.copy(fus); sv=service.volume; ok=temporary.booleanOperation(sc,fc,adsk.fusion.BooleanTypes.IntersectionBooleanType); siv=sc.volume if ok and sc.isValid else 0.0
    audit=dict(status='SWEEP_SERVO_PACKAGING_SCAN',source_revision='v34',servo_envelope_mm=[42,21,40],candidate_count=len(candidates),candidate_results=candidates,
      chosen_candidate=chosen,chosen_fully_packaged=chosen['fully_packaged'],service_envelope_bounds_mm=dict(x=[x0,x1],y=[y0,y1],z=[z0,z1]),service_inside_fraction=(siv/sv if sv else 0.0),
      linkage_kinematics_verified=False,servo_torque_verified=False,servo_model_selected=False,mechanical_detail_release=False,print_release=False,flight_release=False)
    outdir=os.path.join(config['export_dir'],'sweep_servo_v35'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v35_SWEEP_SERVO_PACKAGING_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v35 export failed')
    with open(os.path.join(outdir,'F14_v35_sweep_servo_packaging_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v35_sweep_servo_packaging_review.png'),1600,1000)
    return audit

'''
for path in files:
    s=path.read_text(encoding='utf-8'); insert=s.index('def build_project_revision():')
    if 'def build_sweep_servo_packaging_review_v35()' not in s: s=s[:insert]+fn+s[insert:]
    s=s.replace('return build_crosstie_riser_socket_review_v34()','return build_sweep_servo_packaging_review_v35()',1)
    path.write_text(s,encoding='utf-8'); print('patched',path)
