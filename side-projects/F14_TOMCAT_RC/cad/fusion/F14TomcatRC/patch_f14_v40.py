from pathlib import Path
import json

FILES=[
 Path(r'C:\Users\dezen\Desktop\135er-Spandau-Defeat\side-projects\F14_TOMCAT_RC\cad\fusion\F14TomcatRC\F14TomcatRC.py'),
 Path(r'C:\Users\dezen\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\F14TomcatRC\F14TomcatRC.py'),
]

FN=r'''

def build_moment_arm_optimized_packaging_v40():
    """Package the v40 non-toggle sweep linkage. Reuse a loaded v38+ document when available."""
    design=adsk.fusion.Design.cast(_app.activeProduct); root=design.rootComponent if design else None
    if not root or not any(b.name=='REF_UPC_FUSELAGE_OUTER_OML_v37' for b in root.bRepBodies):
        build_inboard_sweep_crank_scan_v38()
        design=adsk.fusion.Design.cast(_app.activeProduct); root=design.rootComponent
    _app.activeDocument.name='F14_v40_MOMENT_ARM_OPTIMIZED_PACKAGING'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    with open(os.path.join(base,'F14_sweep_linkage_kinematics_v40.json'),encoding='utf-8') as stream: kin=json.load(stream)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    c=kin['selected_candidate']; dx0,dy0=c['crank_vector_at_20deg_mm']; sy=c['slider_attach_y_mm']; zc=184.0
    factor=900.0/(2.0*data['sections'][-1]['wbl_in']); px=pivot['derived_full_scale_pivot_fs_in']*factor; py=pivot['derived_full_scale_pivot_bl_in']*factor
    outer=next(b for b in root.bRepBodies if b.name=='REF_UPC_FUSELAGE_OUTER_OML_v37')
    service=next(b for b in root.bRepBodies if b.name=='RC_SWEEP_SERVO_SERVICE_ENVELOPE_v35')
    fixed=[b for b in root.bRepBodies if (b.name.startswith('ENG_WINGBOX_FORK_') and b.name.endswith('_v31')) or (b.name.startswith('ENG_RISER_SOCKET_') and b.name.endswith('_v34')) or b.name in ['REF_CF6x4_FRONT_LOWER_v34','REF_CF6x4_REAR_LOWER_v34','REF_CF6x4_FRONT_UPPER_v35','REF_CF6x4_REAR_UPPER_v35']]
    for b in root.bRepBodies:
        if b.name.startswith('REF_V38_') or b.name.startswith('ENG_SWEEP_INBOARD_CRANK_'): b.isLightBulbOn=False
    temporary=adsk.fusion.TemporaryBRepManager.get(); rods=[]; rod_inside=[]; rod_hits=[]
    samples={r['sweep_deg']:r for r in c['samples']}
    for sweep in range(20,69,4):
        rec=samples[sweep]; sx=rec['slider_x_mm']; ax,ay=rec['crank_pin_mm']
        for side,sgn in [('R',1),('L',-1)]:
            rod=_link_rod_body_v37(root,'REF_V40_LINK_%s_%02d'%(side,sweep),(sx,sgn*sy),(ax,sgn*ay),zc,5.0,4.0); rod.opacity=0.18; rods.append(rod)
            rv=rod.volume; rc=temporary.copy(rod); oc=temporary.copy(outer); ok=temporary.booleanOperation(rc,oc,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=rc.volume if ok and rc.isValid else 0.0; rod_inside.append(iv/rv if rv else 0.0)
            for part in fixed+[service]:
                a=temporary.copy(rod); b=temporary.copy(part); ok2=temporary.booleanOperation(a,b,adsk.fusion.BooleanTypes.IntersectionBooleanType); ov=a.volume if ok2 and a.isValid else 0.0
                if ov>1e-4: rod_hits.append(dict(side=side,sweep_deg=sweep,part=part.name,intersection_volume_cm3=ov))
    xmin,xmax=c['slider_x_min_mm'],c['slider_x_max_mm']
    slider=extrude_poly(root,'REF_V40_SYNCHRONIZED_SLIDER_ENVELOPE',[(xmin-4,-sy-6),(xmax+4,-sy-6),(xmax+4,sy+6),(xmin-4,sy+6)],zc-2.5,5.0); slider.opacity=0.22
    sv=slider.volume; sc=temporary.copy(slider); oc=temporary.copy(outer); ok=temporary.booleanOperation(sc,oc,adsk.fusion.BooleanTypes.IntersectionBooleanType); siv=sc.volume if ok and sc.isValid else 0.0
    slider_hits=[]
    for part in fixed+[service]:
        a=temporary.copy(slider); b=temporary.copy(part); ok2=temporary.booleanOperation(a,b,adsk.fusion.BooleanTypes.IntersectionBooleanType); ov=a.volume if ok2 and a.isValid else 0.0
        if ov>1e-4: slider_hits.append(dict(part=part.name,intersection_volume_cm3=ov))
    crank_bodies=[]; crank_inside=[]; crank_hits=[]
    for side,sgn in [('R',1),('L',-1)]:
        ypiv=sgn*py; ypin=sgn*(py+dy0); xpin=px+dx0
        arm=_link_rod_body_v37(root,'REF_V40_CRANK_'+side,(px,ypiv),(xpin,ypin),zc,10.0,5.0); arm.opacity=0.50; crank_bodies.append(arm)
        for sweep in range(20,69,4):
            angle=-sgn*math.radians(sweep-20.0); rot=adsk.core.Matrix3D.create(); rot.setToRotation(angle,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(ypiv),mm(zc)))
            mc=temporary.copy(arm); temporary.transform(mc,rot); mv=mc.volume
            oc=temporary.copy(outer); cc=temporary.copy(mc); ok3=temporary.booleanOperation(cc,oc,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=cc.volume if ok3 and cc.isValid else 0.0; crank_inside.append(iv/mv if mv else 0.0)
            for part in fixed+[service]:
                a=temporary.copy(mc); b=temporary.copy(part); ok4=temporary.booleanOperation(a,b,adsk.fusion.BooleanTypes.IntersectionBooleanType); ov=a.volume if ok4 and a.isValid else 0.0
                if ov>1e-4: crank_hits.append(dict(side=side,sweep_deg=sweep,part=part.name,intersection_volume_cm3=ov))
    min_rod=min(rod_inside) if rod_inside else 0.0; min_crank=min(crank_inside) if crank_inside else 0.0; slider_frac=(siv/sv if sv else 0.0)
    fully=(min_rod>0.985 and min_crank>0.985 and slider_frac>0.995 and not rod_hits and not slider_hits and not crank_hits)
    audit=dict(status='MOMENT_ARM_OPTIMIZED_SWEEP_PACKAGING',source_revision='v38',kinematics_source='v40',selected_candidate=c,
      min_rod_outer_oml_inside_fraction=min_rod,min_crank_outer_oml_inside_fraction=min_crank,slider_inside_fraction=slider_frac,
      rod_structural_hits=rod_hits,slider_structural_hits=slider_hits,crank_structural_hits=crank_hits,fully_packaged=fully,
      theoretical_min_wing_torque_Nm=c.get('theoretical_min_wing_torque_at_2Nm_servo_Nm'),estimated_servo_travel_deg=c.get('estimated_servo_travel_deg'),
      toggle_avoidance_verified=(c['min_linkage_moment_arm_mm']>=15.0),mechanical_detail_release=False,print_release=False,flight_release=False)
    outdir=os.path.join(config['export_dir'],'moment_arm_linkage_v40'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v40_MOMENT_ARM_OPTIMIZED_PACKAGING.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v40 export failed')
    with open(os.path.join(outdir,'F14_v40_moment_arm_packaging_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v40_moment_arm_packaging_review.png'),1600,1000)
    return audit

'''

for path in FILES:
    s=path.read_text(encoding='utf-8-sig')
    if 'def build_moment_arm_optimized_packaging_v40()' not in s:
        insert=s.index('def build_project_revision():')
        s=s[:insert]+FN+s[insert:]
    start=s.index('def build_project_revision():'); end=s.index('\nclass BuildRequestHandler',start)
    block=s[start:end].splitlines()
    for i,line in enumerate(block):
        if line.strip().startswith('return build_'):
            block[i]='    return build_moment_arm_optimized_packaging_v40()'; break
    s=s[:start]+'\n'.join(block)+s[end:]
    # Bridge-only startup mode avoids hour-long rebuilds when opening an exported checkpoint.
    needle="            if config.get('startup_mode')=='basic_wings_v08':\n"
    if "startup_mode')=='bridge_only'" not in s:
        replacement="            if config.get('startup_mode')=='bridge_only':\n                _created=True\n                with open(os.path.join(os.path.dirname(__file__),'F14_build_response.json'),'w',encoding='utf-8') as stream:\n                    json.dump(execution_ack('startup-bridge-only','completed'),stream,indent=2)\n                start_build_requests()\n                return\n            if config.get('startup_mode')=='basic_wings_v08':\n"
        s=s.replace(needle,replacement,1)
    path.write_text(s,encoding='utf-8')
    cfg=path.parent/'F14TomcatRC_config.json'
    data=json.loads(cfg.read_text(encoding='utf-8-sig')); data['startup_mode']='bridge_only'; cfg.write_text(json.dumps(data,indent=2),encoding='utf-8')
    print('patched',path)
