from pathlib import Path

repo = Path(r'C:\Users\dezen\Desktop\135er-Spandau-Defeat\side-projects\F14_TOMCAT_RC\cad\fusion\F14TomcatRC\F14TomcatRC.py')
live = Path(r'C:\Users\dezen\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\F14TomcatRC\F14TomcatRC.py')
files = [repo, live]

fn = r'''

def build_inboard_sweep_crank_scan_v38():
    """Replace the v37 direct-root rod with an inboard rotating crank and scan packaging over 20..68 deg."""
    build_linkage_plane_scan_v37()
    design=adsk.fusion.Design.cast(_app.activeProduct); root=design.rootComponent
    _app.activeDocument.name='F14_v38_INBOARD_SWEEP_CRANK_SCAN'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in']); px=pivot['derived_full_scale_pivot_fs_in']*factor; py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]; dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in']); pz=(s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz)*factor
    zc=184.0; temporary=adsk.fusion.TemporaryBRepManager.get()
    outer=next((b for b in root.bRepBodies if b.name=='REF_UPC_FUSELAGE_OUTER_OML_v37'),None)
    if outer is None: raise RuntimeError('v37 outer OML missing')
    service=next(b for b in root.bRepBodies if b.name=='RC_SWEEP_SERVO_SERVICE_ENVELOPE_v35')
    fixed=[b for b in root.bRepBodies if (b.name.startswith('ENG_WINGBOX_FORK_') and b.name.endswith('_v31')) or (b.name.startswith('ENG_RISER_SOCKET_') and b.name.endswith('_v34')) or b.name in ['REF_CF6x4_FRONT_LOWER_v34','REF_CF6x4_REAR_LOWER_v34','REF_CF6x4_FRONT_UPPER_v35','REF_CF6x4_REAR_UPPER_v35']]
    candidates=[]; bodies=[]
    vectors=[(-10,-20),(-10,-25),(-15,-25),(-15,-30),(-20,-30),(-20,-35)]
    slider_ys=[40.0,45.0,50.0,55.0]
    x0=525.0
    for dx0,dy0 in vectors:
        for sy in slider_ys:
            ax0=px+dx0; ay0=py+dy0; L=math.hypot(ax0-x0,ay0-sy)
            samples=[]; rod_inside=[]; rod_hits=[]; slider_x=[]; valid=True
            for sweep in range(20,69,4):
                a=-math.radians(sweep-20.0); ca=math.cos(a); sa=math.sin(a)
                dx=dx0*ca-dy0*sa; dy=dx0*sa+dy0*ca; ax=px+dx; ay=py+dy
                q=L*L-(ay-sy)*(ay-sy)
                if q<=0: valid=False; break
                sx=ax-math.sqrt(q); slider_x.append(sx)
                rod=_link_rod_body_v37(root,'REF_V38_LINK_%+03d_%+03d_Y%02d_S%02d'%(dx0,dy0,round(sy),sweep),(sx,sy),(ax,ay),zc,4.0,4.0); rod.opacity=0.02; bodies.append(rod)
                rv=rod.volume; rc=temporary.copy(rod); oc=temporary.copy(outer); ok=temporary.booleanOperation(rc,oc,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=rc.volume if ok and rc.isValid else 0.0; rod_inside.append(iv/rv if rv else 0.0)
                for part in fixed+[service]:
                    aa=temporary.copy(rod); bb=temporary.copy(part); ok2=temporary.booleanOperation(aa,bb,adsk.fusion.BooleanTypes.IntersectionBooleanType); ov=aa.volume if ok2 and aa.isValid else 0.0
                    if ov>1e-4: rod_hits.append(dict(sweep_deg=sweep,part=part.name,intersection_volume_cm3=ov))
                samples.append(dict(sweep_deg=sweep,slider_x_mm=sx,crank_pin_mm=[ax,ay]))
            if not valid: continue
            xmin=min(slider_x); xmax=max(slider_x)
            slider=extrude_poly(root,'REF_V38_SLIDER_%+03d_%+03d_Y%02d'%(dx0,dy0,round(sy)),[(xmin-3,sy-4),(xmax+3,sy-4),(xmax+3,sy+4),(xmin-3,sy+4)],zc-2.5,5.0); slider.opacity=0.03; bodies.append(slider)
            sv=slider.volume; sc=temporary.copy(slider); oc=temporary.copy(outer); ok=temporary.booleanOperation(sc,oc,adsk.fusion.BooleanTypes.IntersectionBooleanType); siv=sc.volume if ok and sc.isValid else 0.0
            sh=[]
            for part in fixed+[service]:
                aa=temporary.copy(slider); bb=temporary.copy(part); ok2=temporary.booleanOperation(aa,bb,adsk.fusion.BooleanTypes.IntersectionBooleanType); ov=aa.volume if ok2 and aa.isValid else 0.0
                if ov>1e-4: sh.append(dict(part=part.name,intersection_volume_cm3=ov))
            min_inside=min(rod_inside) if rod_inside else 0.0
            full=(min_inside>0.985 and siv/sv>0.995 and not rod_hits and not sh)
            candidates.append(dict(crank_vector_at_20deg_mm=[dx0,dy0],slider_attach_y_mm=sy,rod_length_mm=L,slider_x_min_mm=xmin,slider_x_max_mm=xmax,slider_travel_mm=xmax-xmin,min_rod_outer_oml_inside_fraction=min_inside,slider_inside_fraction=(siv/sv if sv else 0.0),rod_structural_hits=rod_hits,slider_structural_hits=sh,fully_packaged=full,samples=samples))
    good=[r for r in candidates if r['fully_packaged']]
    chosen=min(good,key=lambda r:(r['slider_travel_mm'],r['rod_length_mm'])) if good else max(candidates,key=lambda r:(r['min_rod_outer_oml_inside_fraction'],r['slider_inside_fraction'],-len(r['rod_structural_hits'])-len(r['slider_structural_hits'])))
    tag='V38_LINK_%+03d_%+03d_Y%02d'%(chosen['crank_vector_at_20deg_mm'][0],chosen['crank_vector_at_20deg_mm'][1],round(chosen['slider_attach_y_mm']))
    stag='V38_SLIDER_%+03d_%+03d_Y%02d'%(chosen['crank_vector_at_20deg_mm'][0],chosen['crank_vector_at_20deg_mm'][1],round(chosen['slider_attach_y_mm']))
    for b in bodies:
        keep=(tag in b.name or stag in b.name); b.isLightBulbOn=keep
        if keep: b.opacity=0.28
    dx0,dy0=chosen['crank_vector_at_20deg_mm']
    for side,sgn in [('R',1),('L',-1)]:
        ypin=sgn*(py+dy0); ypiv=sgn*py
        arm=_link_rod_body_v37(root,'ENG_SWEEP_INBOARD_CRANK_%s_v38',(px,ypiv),(px+dx0,ypin),zc,8.0,5.0); arm.opacity=0.55
    audit=dict(status='INBOARD_SWEEP_CRANK_PACKAGING_SCAN',source_revision='v37',candidate_count=len(candidates),candidate_results=candidates,chosen_candidate=chosen,chosen_fully_packaged=chosen['fully_packaged'],linkage_plane_z_mm=zc,crank_concept='pivot-concentric inboard rotating crank with short vertical transfer to wing root',crank_geometry_verified=chosen['fully_packaged'],slider_guide_geometry_verified=False,servo_torque_verified=False,mechanical_detail_release=False,print_release=False,flight_release=False)
    outdir=os.path.join(config['export_dir'],'inboard_crank_v38'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v38_INBOARD_SWEEP_CRANK_SCAN.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v38 export failed')
    with open(os.path.join(outdir,'F14_v38_inboard_crank_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v38_inboard_crank_review.png'),1600,1000)
    return audit

'''

for path in files:
    text=path.read_text(encoding='utf-8-sig')
    if 'def build_inboard_sweep_crank_scan_v38()' not in text:
        at=text.index('def build_project_revision():')
        text=text[:at]+fn+text[at:]
    text=text.replace('return build_linkage_plane_scan_v37()','return build_inboard_sweep_crank_scan_v38()',1)
    path.write_text(text,encoding='utf-8')
    print('patched',path)
