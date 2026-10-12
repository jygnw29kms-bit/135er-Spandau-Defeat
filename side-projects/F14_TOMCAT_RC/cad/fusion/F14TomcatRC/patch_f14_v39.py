from pathlib import Path

FILES=[
    Path(r'C:\Users\dezen\Desktop\135er-Spandau-Defeat\side-projects\F14_TOMCAT_RC\cad\fusion\F14TomcatRC\F14TomcatRC.py'),
    Path(r'C:\Users\dezen\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\F14TomcatRC\F14TomcatRC.py'),
]

FN=r'''

def _join_bodies_v39(root,target,tools):
    coll=adsk.core.ObjectCollection.create()
    for body in tools: coll.add(body)
    ci=root.features.combineFeatures.createInput(target,coll)
    ci.operation=adsk.fusion.FeatureOperations.JoinFeatureOperation
    ci.isKeepToolBodies=False
    root.features.combineFeatures.add(ci)
    return target

def build_sweep_mechanism_detail_v39():
    """Turn the v38 packaging result into a first real crank/slider mechanism and run preliminary load screens."""
    build_inboard_sweep_crank_scan_v38()
    design=adsk.fusion.Design.cast(_app.activeProduct); root=design.rootComponent
    _app.activeDocument.name='F14_v39_SWEEP_MECHANISM_DETAIL_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    audit38_path=os.path.join(config['export_dir'],'inboard_crank_v38','F14_v38_inboard_crank_audit.json')
    with open(audit38_path,encoding='utf-8') as stream: audit38=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in'])
    px=pivot['derived_full_scale_pivot_fs_in']*factor; py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]
    dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in'])
    pz=(s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz)*factor
    zc=184.0; temporary=adsk.fusion.TemporaryBRepManager.get()
    good=[r for r in audit38['candidate_results'] if r['fully_packaged']]
    if not good: raise RuntimeError('v39 requires a packaged v38 candidate')
    # v38 originally minimized travel. For real mechanics prefer a useful 15-20 mm stroke for resolution and force balance.
    chosen=min(good,key=lambda r:(abs(r['slider_travel_mm']-18.0),r['rod_length_mm']))
    dx0,dy0=chosen['crank_vector_at_20deg_mm']; sy=chosen['slider_attach_y_mm']
    xmin,xmax=chosen['slider_x_min_mm'],chosen['slider_x_max_mm']; stroke=xmax-xmin
    outer=next(b for b in root.bRepBodies if b.name=='REF_UPC_FUSELAGE_OUTER_OML_v37')
    service=next(b for b in root.bRepBodies if b.name=='RC_SWEEP_SERVO_SERVICE_ENVELOPE_v35')
    fixed=[b for b in root.bRepBodies if (b.name.startswith('ENG_WINGBOX_FORK_') and b.name.endswith('_v31')) or (b.name.startswith('ENG_RISER_SOCKET_') and b.name.endswith('_v34')) or b.name in ['REF_CF6x4_FRONT_LOWER_v34','REF_CF6x4_REAR_LOWER_v34','REF_CF6x4_FRONT_UPPER_v35','REF_CF6x4_REAR_UPPER_v35']]
    crank_bodies=[]; pin_refs=[]; rods=[]
    # 5-mm crank plate, 14-mm neck, 20-mm pivot hub, 12-mm rod-end boss. 6-mm pivot shaft + M3 rod pin.
    for side,sgn in [('R',1),('L',-1)]:
        ypiv=sgn*py; ypin=sgn*(py+dy0); xpin=px+dx0
        arm=_link_rod_body_v37(root,'ENG_SWEEP_CRANK_ARM_'+side+'_v39',(px,ypiv),(xpin,ypin),zc,14.0,5.0)
        hub=_cyl_body_v30(root,'TMP_CRANK_HUB_'+side+'_v39',px,ypiv,zc-2.5,10.0,5.0)
        boss=_cyl_body_v30(root,'TMP_CRANK_PIN_BOSS_'+side+'_v39',xpin,ypin,zc-2.5,6.0,5.0)
        _join_bodies_v39(root,arm,[hub,boss])
        _cut_cyl_v30(root,arm,'CUT_CRANK_PIVOT_'+side+'_v39',px,ypiv,zc-2.6,3.1,5.2)
        _cut_cyl_v30(root,arm,'CUT_CRANK_M3_'+side+'_v39',xpin,ypin,zc-2.6,1.65,5.2)
        arm.name='ENG_SWEEP_CRANK_'+side+'_v39'; arm.opacity=0.72; crank_bodies.append(arm)
        pin=_cyl_body_v30(root,'REF_M3_CRANK_PIN_'+side+'_v39',xpin,ypin,zc-3.5,1.5,7.0); pin.opacity=0.35; pin_refs.append(pin)
        sample20=next(r for r in chosen['samples'] if r['sweep_deg']==20)
        sx=sample20['slider_x_mm']
        rod=_link_rod_body_v37(root,'REF_LINK_ROD_'+side+'_v39',(sx,sgn*sy),(xpin,ypin),zc,5.0,4.0); rod.opacity=0.40; rods.append(rod)
    # One synchronized moving crossbar; two M3 rod pins at +/-sy.
    xmid=(xmin+xmax)/2.0
    slider=extrude_poly(root,'ENG_SWEEP_SLIDER_CROSSBAR_v39',[(xmid-4,-sy-7),(xmid+4,-sy-7),(xmid+4,sy+7),(xmid-4,sy+7)],zc-2.5,5.0)
    slider.opacity=0.62
    for sgn,label in [(1,'R'),(-1,'L')]:
        _cut_cyl_v30(root,slider,'CUT_SLIDER_M3_'+label+'_v39',xmid,sgn*sy,zc-2.6,1.65,5.2)
        pin=_cyl_body_v30(root,'REF_M3_SLIDER_PIN_'+label+'_v39',xmid,sgn*sy,zc-3.5,1.5,7.0); pin.opacity=0.35; pin_refs.append(pin)
    # Four fixed guide rails around the two slider ends. 0.6-mm lateral running clearance per side.
    rail_x0=xmin-8.0; rail_x1=xmax+8.0; rails=[]
    for sgn,label in [(1,'R'),(-1,'L')]:
        yc=sgn*sy
        for pos,off in [('IN',-sgn*8.1),('OUT',sgn*8.1)]:
            y=yc+off
            rail=extrude_poly(root,'ENG_SLIDER_GUIDE_'+label+'_'+pos+'_v39',[(rail_x0,y-1.5),(rail_x1,y-1.5),(rail_x1,y+1.5),(rail_x0,y+1.5)],zc-3.5,7.0)
            rail.opacity=0.70; rails.append(rail)
    # Full moving slider envelope for containment/collision checks.
    slider_env=extrude_poly(root,'REF_SLIDER_TRAVEL_ENVELOPE_v39',[(xmin-4,-sy-7),(xmax+4,-sy-7),(xmax+4,sy+7),(xmin-4,sy+7)],zc-2.5,5.0); slider_env.opacity=0.10
    checks=[]
    def containment(body,label):
        bc=temporary.copy(body); oc=temporary.copy(outer); v=body.volume
        ok=temporary.booleanOperation(bc,oc,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=bc.volume if ok and bc.isValid else 0.0
        frac=iv/v if v else 0.0; checks.append(dict(item=label,inside_fraction=frac)); return frac
    crank_inside=[containment(b,b.name) for b in crank_bodies]
    rail_inside=[containment(b,b.name) for b in rails]
    slider_inside=containment(slider_env,slider_env.name)
    fixed_hits=[]
    for moving in crank_bodies:
        side='R' if '_R_' in moving.name else 'L'; sgn=1 if side=='R' else -1; ypiv=sgn*py
        for sweep in range(20,69,4):
            angle=-sgn*math.radians(sweep-20.0); rot=adsk.core.Matrix3D.create(); rot.setToRotation(angle,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(ypiv),mm(zc)))
            mc=temporary.copy(moving); temporary.transform(mc,rot)
            for part in fixed+[service]+rails:
                a=temporary.copy(mc); b=temporary.copy(part); ok=temporary.booleanOperation(a,b,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=a.volume if ok and a.isValid else 0.0
                if iv>1e-4: fixed_hits.append(dict(side=side,sweep_deg=sweep,part=part.name,intersection_volume_cm3=iv))
    slider_hits=[]
    for part in fixed+[service]:
        a=temporary.copy(slider_env); b=temporary.copy(part); ok=temporary.booleanOperation(a,b,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=a.volume if ok and a.isValid else 0.0
        if iv>1e-4: slider_hits.append(dict(part=part.name,intersection_volume_cm3=iv))
    # Preliminary load screen. Final release waits for selected servo, material coupons and physical proof test.
    servo_stall_Nm=2.0; servo_horn_mm=17.0; servo_force_N=servo_stall_Nm/(servo_horn_mm/1000.0)
    dynamic_factor=2.5; design_rod_force_N=servo_force_N*dynamic_factor
    pin_area_mm2=math.pi*(3.0**2)/4.0; m3_single_shear_MPa=design_rod_force_N/pin_area_mm2
    crank_net_area_mm2=(14.0-3.3)*5.0; crank_net_stress_MPa=design_rod_force_N/crank_net_area_mm2
    moment_arms=[]
    for rec in chosen['samples']:
        ax,ay=rec['crank_pin_mm']; sx=rec['slider_x_mm']; rx=ax-px; ry=ay-py; vx=sx-ax; vy=sy-ay; L=math.hypot(vx,vy)
        if L>1e-9: moment_arms.append(abs(rx*(vy/L)-ry*(vx/L)))
    min_ma=min(moment_arms); theoretical_wing_torque_Nm=servo_force_N*(min_ma/1000.0)
    halfstroke=stroke/2.0
    servo_angle_each_deg=math.degrees(math.asin(min(0.999,halfstroke/servo_horn_mm)))
    mechanical_ok=(min(crank_inside)>0.995 and min(rail_inside)>0.995 and slider_inside>0.995 and not fixed_hits and not slider_hits)
    load_screen_ok=(m3_single_shear_MPa<80.0 and crank_net_stress_MPa<8.0 and theoretical_wing_torque_Nm>2.0)
    audit=dict(status='SWEEP_MECHANISM_DETAIL_REVIEW',source_revision='v38',selected_candidate=chosen,
      selection_reason='practical approximately 18 mm slider stroke instead of minimum-stroke v38 candidate',
      hardware=dict(pivot_bore_mm=6.2,rod_pin_bore_mm=3.3,crank_thickness_mm=5.0,crank_neck_width_mm=14.0,slider_crossbar_thickness_mm=5.0,guide_running_clearance_each_side_mm=0.6),
      kinematics=dict(slider_travel_mm=stroke,servo_horn_radius_mm=servo_horn_mm,estimated_servo_travel_deg=2.0*servo_angle_each_deg,min_linkage_moment_arm_mm=min_ma),
      preliminary_load_screen=dict(servo_stall_Nm=servo_stall_Nm,servo_force_N=servo_force_N,dynamic_factor=dynamic_factor,design_rod_force_N=design_rod_force_N,m3_single_shear_MPa=m3_single_shear_MPa,crank_net_section_stress_MPa=crank_net_stress_MPa,theoretical_min_wing_torque_Nm=theoretical_wing_torque_Nm,screen_pass=load_screen_ok),
      containment_checks=checks,crank_fixed_hits=fixed_hits,slider_fixed_hits=slider_hits,mechanical_geometry_verified=mechanical_ok,preliminary_load_screen_verified=load_screen_ok,
      servo_model_selected=False,material_coupon_verified=False,physical_proof_test_verified=False,mechanical_detail_release=(mechanical_ok and load_screen_ok),print_release=False,flight_release=False)
    outdir=os.path.join(config['export_dir'],'sweep_mechanism_v39'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v39_SWEEP_MECHANISM_DETAIL_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v39 export failed')
    with open(os.path.join(outdir,'F14_v39_sweep_mechanism_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v39_sweep_mechanism_review.png'),1600,1000)
    return audit

'''

for path in FILES:
    s=path.read_text(encoding='utf-8-sig')
    if 'def build_sweep_mechanism_detail_v39()' not in s:
        insert=s.index('def build_project_revision():')
        s=s[:insert]+FN+s[insert:]
    start=s.index('def build_project_revision():')
    end=s.index('\nclass BuildRequestHandler',start)
    block=s[start:end]
    lines=block.splitlines()
    for i,line in enumerate(lines):
        if line.strip().startswith('return build_'):
            lines[i]='    return build_sweep_mechanism_detail_v39()'
            break
    s=s[:start]+'\n'.join(lines)+s[end:]
    path.write_text(s,encoding='utf-8')
    print('patched',path)
