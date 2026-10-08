from pathlib import Path
files=[Path(r'C:\Users\dezen\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\F14TomcatRC\F14TomcatRC.py'),Path(r'C:\Users\dezen\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\F14TomcatRC_v18\F14TomcatRC_v18.py')]
fn=r'''

def build_lower_crosstie_routing_review_v33():
    """Scan lower carbon cross-tie Z positions for OML containment, then collision-check the best routes."""
    build_wingbox_fork_hardpoint_review_v31()
    design=adsk.fusion.Design.cast(_app.activeProduct); root=design.rootComponent
    _app.activeDocument.name='F14_v33_LOWER_CROSSTIE_ROUTING_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in']); px=pivot['derived_full_scale_pivot_fs_in']*factor; py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]; dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in']); pz=(s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz)*factor
    fus=next(b for b in root.bRepBodies if b.name=='UPC_FUSELAGE_ROBUST_CLEARANCE_CUT_v29'); temporary=adsk.fusion.TemporaryBRepManager.get()
    y0,y1=-72.0,72.0; od=6.0; half=3.0; current_z=pz-11.5
    candidates=[]; bodies={}
    for foreaft,xc in [('FRONT',px-16.0),('REAR',px+16.0)]:
        for step in range(0,8):
            zc=current_z+step*1.0
            body=extrude_poly(root,'REF_ROUTE_'+foreaft+'_Z%+05.1f_v33'%zc,[(xc-half,y0),(xc+half,y0),(xc+half,y1),(xc-half,y1)],zc-half,od); body.opacity=0.08
            bc=temporary.copy(body); fc=temporary.copy(fus); bv=body.volume; ok=temporary.booleanOperation(bc,fc,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=bc.volume if ok and bc.isValid else 0.0
            rec=dict(foreaft=foreaft,x_center_mm=xc,z_center_mm=zc,z_shift_from_v32_mm=zc-current_z,envelope_volume_cm3=bv,inside_fuselage_volume_cm3=iv,inside_fraction=(iv/bv if bv else 0.0),body_name=body.name)
            candidates.append(rec); bodies[(foreaft,zc)]=body
    chosen={}
    for foreaft in ['FRONT','REAR']:
        opts=[r for r in candidates if r['foreaft']==foreaft]
        chosen[foreaft]=max(opts,key=lambda r:(r['inside_fraction'],-abs(r['z_shift_from_v32_mm'])))
    chosen_bodies=[]
    for foreaft,rec in chosen.items():
        body=bodies[(foreaft,rec['z_center_mm'])]; body.name='REF_CF6x4_'+foreaft+'_LOWER_ROUTED_v33'; body.opacity=0.35; chosen_bodies.append(body)
    sweep_checks=[]
    for sweep in range(20,69,2):
        for sign,label in [(1,'R'),(-1,'L')]:
            angle=-sign*math.radians(sweep-20.0); rot=adsk.core.Matrix3D.create(); rot.setToRotation(angle,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(sign*py),mm(pz)))
            wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_')); lug=next(b for b in root.bRepBodies if b.name=='ENG_ROOT_LUG_'+label+'_v19')
            for moving_body,kind in [(wing,'outer_wing'),(lug,'root_lug')]:
                moving=temporary.copy(moving_body); temporary.transform(moving,rot)
                for tie in chosen_bodies:
                    t=temporary.copy(moving); tool=temporary.copy(tie); ok=temporary.booleanOperation(t,tool,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=t.volume if ok and t.isValid else 0.0
                    sweep_checks.append(dict(sweep_deg=sweep,side=label,moving_kind=kind,tie=tie.name,intersection_volume_cm3=iv,positive_overlap=iv>1e-4))
    residual=[r for r in sweep_checks if r['positive_overlap']]
    audit=dict(status='LOWER_CROSSTIE_VERTICAL_ROUTING_REVIEW',source_revision='v31',v32_lower_z_center_mm=current_z,
      candidate_routes=candidates,chosen_routes=chosen,min_chosen_inside_fraction=min(r['inside_fraction'] for r in chosen.values()),
      chosen_route_sweep_collision_records=sweep_checks,residual_positive_overlaps=residual,dense_chosen_route_clearance_pass=(len(residual)==0),
      riser_required=True,mechanical_detail_release=False,print_release=False,flight_release=False)
    outdir=os.path.join(config['export_dir'],'lower_crosstie_routing_v33'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v33_LOWER_CROSSTIE_ROUTING_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v33 export failed')
    with open(os.path.join(outdir,'F14_v33_lower_crosstie_routing_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v33_lower_crosstie_routing_review.png'),1600,1000)
    return audit

'''
for path in files:
    s=path.read_text(encoding='utf-8'); insert=s.index('def build_project_revision():')
    if 'def build_lower_crosstie_routing_review_v33()' not in s: s=s[:insert]+fn+s[insert:]
    s=s.replace('return build_carbon_crosstie_wingbox_review_v32()','return build_lower_crosstie_routing_review_v33()',1)
    path.write_text(s,encoding='utf-8'); print('patched',path)
