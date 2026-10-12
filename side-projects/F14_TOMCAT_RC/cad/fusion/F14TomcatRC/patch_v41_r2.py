from pathlib import Path
paths=[Path(r'C:\Users\dezen\Desktop\135er-Spandau-Defeat\side-projects\F14_TOMCAT_RC\cad\fusion\F14TomcatRC\F14TomcatRC.py'),Path(r'C:\Users\dezen\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\F14TomcatRC\F14TomcatRC.py')]
fn=r'''def build_clearance_optimized_packaging_v41():
    """Two-stage v41 clearance optimization; avoids brute-force Fusion history growth."""
    design=adsk.fusion.Design.cast(_app.activeProduct); root=design.rootComponent if design else None
    if not root or not any(b.name=='REF_UPC_FUSELAGE_OUTER_OML_v37' for b in root.bRepBodies):
        build_inboard_sweep_crank_scan_v38(); design=adsk.fusion.Design.cast(_app.activeProduct); root=design.rootComponent
    _app.activeDocument.name='F14_v41_CLEARANCE_OPTIMIZED_PACKAGING_R2'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as f:data=json.load(f)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as f:pivot=json.load(f)
    with open(os.path.join(base,'F14_sweep_linkage_kinematics_v40.json'),encoding='utf-8') as f:kin=json.load(f)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as f:config=json.load(f)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in']); px=pivot['derived_full_scale_pivot_fs_in']*factor; py=pivot['derived_full_scale_pivot_bl_in']*factor
    outer=next(b for b in root.bRepBodies if b.name=='REF_UPC_FUSELAGE_OUTER_OML_v37'); temporary=adsk.fusion.TemporaryBRepManager.get()
    problem=[b for b in root.bRepBodies if b.name in ['REF_CF6x4_FRONT_LOWER_v34','ENG_RISER_SOCKET_FRONT_R_v34','ENG_RISER_SOCKET_FRONT_L_v34']]
    def hitvol(body):
        total=0.0
        for part in problem:
            a=temporary.copy(body); b=temporary.copy(part); ok=temporary.booleanOperation(a,b,adsk.fusion.BooleanTypes.IntersectionBooleanType); total+=a.volume if ok and a.isValid else 0.0
        return total
    def inside(body):
        v=body.volume; a=temporary.copy(body); o=temporary.copy(outer); ok=temporary.booleanOperation(a,o,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=a.volume if ok and a.isValid else 0.0; return iv/v if v else 0.0
    def rod_collision(c,zc,ci):
        sy=c['slider_attach_y_mm']; samples={r['sweep_deg']:r for r in c['samples'] if r['sweep_deg']%4==0}; total=0.0
        for sweep in range(20,69,4):
            rec=samples[sweep]; sx=rec['slider_x_mm']; ax,ay=rec['crank_pin_mm']
            for side,sgn in [('R',1),('L',-1)]:
                rod=_link_rod_body_v37(root,'TMP41C_%02d_%03d_%s'%(ci,sweep,side),(sx,sgn*sy),(ax,sgn*ay),zc,5.0,4.0); rod.isLightBulbOn=False; total+=hitvol(rod); rod.deleteMe()
        return total
    selected=kin['selected_candidate']; coarse=[]
    for zi,zc in enumerate([168.0,172.0,176.0,180.0,188.0,192.0,196.0,200.0]): coarse.append({'z_mm':zc,'collision_volume_cm3':rod_collision(selected,zc,zi)})
    coarse.sort(key=lambda r:(r['collision_volume_cm3'],abs(r['z_mm']-184.0))); bz=coarse[0]['z_mm']
    zplanes=sorted(set(max(164.0,min(204.0,z)) for z in [bz-4.0,bz,bz+4.0])); results=[]
    for ci,c in enumerate(kin['top_candidates'][:4]):
        dx0,dy0=c['crank_vector_at_20deg_mm']; sy=c['slider_attach_y_mm']; samples={r['sweep_deg']:r for r in c['samples'] if r['sweep_deg']%4==0}
        for zc in zplanes:
            rh=0.0; ri=1.0
            for sweep in range(20,69,4):
                rec=samples[sweep]; sx=rec['slider_x_mm']; ax,ay=rec['crank_pin_mm']
                for side,sgn in [('R',1),('L',-1)]:
                    rod=_link_rod_body_v37(root,'TMP41R_%02d_%03d_%s'%(ci,sweep,side),(sx,sgn*sy),(ax,sgn*ay),zc,5.0,4.0); rod.isLightBulbOn=False; rh+=hitvol(rod); ri=min(ri,inside(rod)); rod.deleteMe()
            xmin,xmax=c['slider_x_min_mm'],c['slider_x_max_mm']; slider=extrude_poly(root,'TMP41S_%02d'%ci,[(xmin-4,-sy-6),(xmax+4,-sy-6),(xmax+4,sy+6),(xmin-4,sy+6)],zc-2.5,5.0); slider.isLightBulbOn=False; si=inside(slider); sh=hitvol(slider); slider.deleteMe()
            cri=1.0
            for side,sgn in [('R',1),('L',-1)]:
                yp=sgn*py; arm=_link_rod_body_v37(root,'TMP41A_%02d_%s'%(ci,side),(px,yp),(px+dx0,sgn*(py+dy0)),zc,8.0,4.0); arm.isLightBulbOn=False
                for sweep in range(20,69,4):
                    ang=-sgn*math.radians(sweep-20.0); rot=adsk.core.Matrix3D.create(); rot.setToRotation(ang,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(yp),mm(zc))); mc=temporary.copy(arm); temporary.transform(mc,rot); mv=mc.volume; oc=temporary.copy(outer); cc=temporary.copy(mc); ok=temporary.booleanOperation(cc,oc,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=cc.volume if ok and cc.isValid else 0.0; cri=min(cri,iv/mv if mv else 0.0)
                arm.deleteMe()
            collision=rh+sh; score=1000*min(ri,si,cri)-5000*collision+2*c['min_linkage_moment_arm_mm']-.5*c['slider_travel_mm']; results.append(dict(candidate_index=ci,z_mm=zc,score=score,collision_volume_cm3=collision,min_rod_inside=ri,slider_inside=si,min_crank_inside=cri,candidate=c))
    results.sort(key=lambda r:r['score'],reverse=True); best=results[0]; c=best['candidate']; zc=best['z_mm']; sy=c['slider_attach_y_mm']; dx0,dy0=c['crank_vector_at_20deg_mm']; samples={r['sweep_deg']:r for r in c['samples'] if r['sweep_deg']%4==0}
    for b in root.bRepBodies:
        if b.name.startswith('REF_V40_') or b.name.startswith('REF_V41_'): b.isLightBulbOn=False
    for sweep in range(20,69,4):
        rec=samples[sweep]; sx=rec['slider_x_mm']; ax,ay=rec['crank_pin_mm']
        for side,sgn in [('R',1),('L',-1)]: _link_rod_body_v37(root,'REF_V41_LINK_%s_%02d'%(side,sweep),(sx,sgn*sy),(ax,sgn*ay),zc,5.0,4.0).opacity=0.18
    xmin,xmax=c['slider_x_min_mm'],c['slider_x_max_mm']; s=extrude_poly(root,'REF_V41_SYNCHRONIZED_SLIDER_ENVELOPE',[(xmin-4,-sy-6),(xmax+4,-sy-6),(xmax+4,sy+6),(xmin-4,sy+6)],zc-2.5,5.0); s.opacity=0.22
    for side,sgn in [('R',1),('L',-1)]: _link_rod_body_v37(root,'REF_V41_CRANK_'+side,(px,sgn*py),(px+dx0,sgn*(py+dy0)),zc,8.0,4.0).opacity=0.50
    fully=(best['collision_volume_cm3']<1e-4 and best['min_rod_inside']>0.985 and best['slider_inside']>0.985 and best['min_crank_inside']>0.90)
    audit=dict(status='V41_CLEARANCE_OPTIMIZED_PACKAGING_R2',source_revision='v40',coarse_z_scan=coarse,refined_z_planes=zplanes,best=best,top_results=results[:12],fully_packaged=fully,toggle_avoidance_verified=(c['min_linkage_moment_arm_mm']>=15.0),mechanical_detail_release=False,print_release=False,flight_release=False)
    outdir=os.path.join(config['export_dir'],'clearance_linkage_v41'); os.makedirs(outdir,exist_ok=True); target=os.path.join(outdir,'F14_v41_CLEARANCE_OPTIMIZED_PACKAGING.f3d'); design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)); open(os.path.join(outdir,'F14_v41_clearance_packaging_audit.json'),'w',encoding='utf-8').write(json.dumps(audit,indent=2)); _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v41_clearance_packaging_review.png'),1600,1000); return audit

'''
for path in paths:
    s=path.read_text(encoding='utf-8-sig'); a=s.index('def build_clearance_optimized_packaging_v41():'); b=s.index('def build_project_revision():',a); s=s[:a]+fn+s[b:]; path.write_text(s,encoding='utf-8'); print('patched',path)
