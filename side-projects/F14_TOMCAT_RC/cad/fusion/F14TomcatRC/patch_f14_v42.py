from pathlib import Path

TARGETS=[
 Path(r'C:\Users\dezen\Desktop\135er-Spandau-Defeat\side-projects\F14_TOMCAT_RC\cad\fusion\F14TomcatRC\F14TomcatRC.py'),
 Path(r'C:\Users\dezen\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\F14TomcatRC\F14TomcatRC.py')]

FUNC=r'''
def build_root_union_crank_packaging_v42():
    """Re-evaluate v41 using the mechanically valid packaging volume: fuselage OML plus the matching moving wing root."""
    design=adsk.fusion.Design.cast(_app.activeProduct); root=design.rootComponent if design else None
    if not root or not any(b.name=='REF_UPC_FUSELAGE_OUTER_OML_v37' for b in root.bRepBodies):
        build_inboard_sweep_crank_scan_v38(); design=adsk.fusion.Design.cast(_app.activeProduct); root=design.rootComponent
    _app.activeDocument.name='F14_v42_ROOT_UNION_CRANK_PACKAGING'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as f:pivot=json.load(f)
    with open(os.path.join(base,'F14_sweep_linkage_kinematics_v40.json'),encoding='utf-8') as f:kin=json.load(f)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as f:config=json.load(f)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as f:data=json.load(f)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in']); px=pivot['derived_full_scale_pivot_fs_in']*factor; py=pivot['derived_full_scale_pivot_bl_in']*factor
    outer=next(b for b in root.bRepBodies if b.name=='REF_UPC_FUSELAGE_OUTER_OML_v37'); temporary=adsk.fusion.TemporaryBRepManager.get()
    wings={label:next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_')) for label in ['R','L']}
    fixed=[b for b in root.bRepBodies if (b.name.startswith('ENG_RISER_SOCKET_') and b.name.endswith('_v34')) or b.name in ['REF_CF6x4_FRONT_LOWER_v34','REF_CF6x4_REAR_LOWER_v34','REF_CF6x4_FRONT_UPPER_v35','REF_CF6x4_REAR_UPPER_v35']]
    service=next((b for b in root.bRepBodies if b.name=='RC_SWEEP_SERVO_SERVICE_ENVELOPE_v35'),None)
    if service: fixed.append(service)
    # v41 R2 winner: candidate 1, z=196 mm.
    c=kin['top_candidates'][1]; zc=196.0; sy=c['slider_attach_y_mm']; dx0,dy0=c['crank_vector_at_20deg_mm']
    samples={r['sweep_deg']:r for r in c['samples'] if r['sweep_deg']%4==0}
    crank_records=[]; rod_records=[]; slider_records=[]
    def intersection_volume(a_body,b_body):
        a=temporary.copy(a_body); b=temporary.copy(b_body); ok=temporary.booleanOperation(a,b,adsk.fusion.BooleanTypes.IntersectionBooleanType); return a.volume if ok and a.isValid else 0.0
    def inside_outer(body):
        v=body.volume; return intersection_volume(body,outer)/v if v else 0.0
    def fixed_hit(body):
        return sum(intersection_volume(body,p) for p in fixed)
    # Rods stay entirely in fuselage and were collision-free in v41; verify again at the selected z-plane.
    for sweep in range(20,69,4):
        rec=samples[sweep]; sx=rec['slider_x_mm']; ax,ay=rec['crank_pin_mm']
        for label,sgn in [('R',1),('L',-1)]:
            rod=_link_rod_body_v37(root,'TMP42_ROD_%s_%02d'%(label,sweep),(sx,sgn*sy),(ax,sgn*ay),zc,5.0,4.0); rod.isLightBulbOn=False
            rod_records.append(dict(side=label,sweep_deg=sweep,inside_fraction=inside_outer(rod),fixed_collision_cm3=fixed_hit(rod))); rod.deleteMe()
    xmin,xmax=c['slider_x_min_mm'],c['slider_x_max_mm']; slider=extrude_poly(root,'TMP42_SLIDER',[(xmin-4,-sy-6),(xmax+4,-sy-6),(xmax+4,sy+6),(xmin-4,sy+6)],zc-2.5,5.0); slider.isLightBulbOn=False
    slider_records.append(dict(inside_fraction=inside_outer(slider),fixed_collision_cm3=fixed_hit(slider))); slider.deleteMe()
    # Crank is allowed inside fuselage OML OR the corresponding moving wing-root solid.
    for label,sgn in [('R',1),('L',-1)]:
        yp=sgn*py; arm=_link_rod_body_v37(root,'TMP42_CRANK_'+label,(px,yp),(px+dx0,sgn*(py+dy0)),zc,8.0,4.0); arm.isLightBulbOn=False
        for sweep in range(20,69,4):
            ang=-sgn*math.radians(sweep-20.0); rot=adsk.core.Matrix3D.create(); rot.setToRotation(ang,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(yp),mm(zc)))
            crank=temporary.copy(arm); temporary.transform(crank,rot); cv=crank.volume
            wing=temporary.copy(wings[label]); temporary.transform(wing,rot)
            allowed=temporary.copy(outer); temporary.booleanOperation(allowed,wing,adsk.fusion.BooleanTypes.UnionBooleanType)
            test=temporary.copy(crank); ok=temporary.booleanOperation(test,allowed,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=test.volume if ok and test.isValid else 0.0
            # Fixed-structure collision on transformed crank.
            hit=0.0
            for part in fixed:
                a=temporary.copy(crank); b=temporary.copy(part); okh=temporary.booleanOperation(a,b,adsk.fusion.BooleanTypes.IntersectionBooleanType); hit+=a.volume if okh and a.isValid else 0.0
            crank_records.append(dict(side=label,sweep_deg=sweep,allowed_union_inside_fraction=(iv/cv if cv else 0.0),fixed_collision_cm3=hit))
        arm.deleteMe()
    min_crank=min(r['allowed_union_inside_fraction'] for r in crank_records); max_crank_hit=max(r['fixed_collision_cm3'] for r in crank_records)
    min_rod=min(r['inside_fraction'] for r in rod_records); max_rod_hit=max(r['fixed_collision_cm3'] for r in rod_records)
    slider_inside=slider_records[0]['inside_fraction']; slider_hit=slider_records[0]['fixed_collision_cm3']
    fully=(min_crank>0.985 and min_rod>0.985 and slider_inside>0.985 and max_crank_hit<1e-4 and max_rod_hit<1e-4 and slider_hit<1e-4)
    for b in root.bRepBodies:
        if b.name.startswith('REF_V41_') or b.name.startswith('REF_V42_'): b.isLightBulbOn=False
    for sweep in range(20,69,4):
        rec=samples[sweep]; sx=rec['slider_x_mm']; ax,ay=rec['crank_pin_mm']
        for label,sgn in [('R',1),('L',-1)]: _link_rod_body_v37(root,'REF_V42_LINK_%s_%02d'%(label,sweep),(sx,sgn*sy),(ax,sgn*ay),zc,5.0,4.0).opacity=0.18
    s=extrude_poly(root,'REF_V42_SYNCHRONIZED_SLIDER_ENVELOPE',[(xmin-4,-sy-6),(xmax+4,-sy-6),(xmax+4,sy+6),(xmin-4,sy+6)],zc-2.5,5.0); s.opacity=0.22
    for label,sgn in [('R',1),('L',-1)]: _link_rod_body_v37(root,'REF_V42_CRANK_'+label,(px,sgn*py),(px+dx0,sgn*(py+dy0)),zc,8.0,4.0).opacity=0.50
    audit=dict(status='V42_ROOT_UNION_CRANK_PACKAGING',source_revision='v41',candidate_index=1,z_mm=zc,crank_vector_at_20deg_mm=c['crank_vector_at_20deg_mm'],slider_attach_y_mm=sy,slider_travel_mm=c['slider_travel_mm'],min_linkage_moment_arm_mm=c['min_linkage_moment_arm_mm'],max_linkage_moment_arm_mm=c['max_linkage_moment_arm_mm'],min_crank_allowed_union_inside_fraction=min_crank,max_crank_fixed_collision_cm3=max_crank_hit,min_rod_outer_inside_fraction=min_rod,max_rod_fixed_collision_cm3=max_rod_hit,slider_inside_fraction=slider_inside,slider_fixed_collision_cm3=slider_hit,crank_checks=crank_records,rod_checks=rod_records,fully_packaged=fully,mechanical_detail_release=False,print_release=False,flight_release=False)
    outdir=os.path.join(config['export_dir'],'root_union_crank_v42'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v42_ROOT_UNION_CRANK_PACKAGING.f3d'); design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target))
    with open(os.path.join(outdir,'F14_v42_root_union_crank_audit.json'),'w',encoding='utf-8') as f: json.dump(audit,f,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v42_root_union_crank_review.png'),1600,1000)
    return audit
'''

for p in TARGETS:
    txt=p.read_text(encoding='utf-8')
    if 'def build_root_union_crank_packaging_v42():' not in txt:
        marker='def build_project_revision():'
        txt=txt.replace(marker,FUNC+'\n'+marker,1)
    txt=txt.replace('return build_clearance_optimized_packaging_v41()','return build_root_union_crank_packaging_v42()',1)
    p.write_text(txt,encoding='utf-8')
    print('patched',p)
