from pathlib import Path
files=[Path(r'C:\Users\dezen\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\F14TomcatRC\F14TomcatRC.py'),Path(r'C:\Users\dezen\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\F14TomcatRC_v18\F14TomcatRC_v18.py')]
fn=r'''

def build_carbon_crosstie_wingbox_review_v32():
    """Tie v31 fork hardpoints together with four lightweight 6/4-mm carbon tube packaging envelopes."""
    build_wingbox_fork_hardpoint_review_v31()
    design=adsk.fusion.Design.cast(_app.activeProduct); root=design.rootComponent
    _app.activeDocument.name='F14_v32_CARBON_CROSSTIE_WINGBOX_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in']); px=pivot['derived_full_scale_pivot_fs_in']*factor; py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]; dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in']); pz=(s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz)*factor
    fus=next(b for b in root.bRepBodies if b.name=='UPC_FUSELAGE_ROBUST_CLEARANCE_CUT_v29')
    temporary=adsk.fusion.TemporaryBRepManager.get(); ties=[]; containment=[]; overlaps=[]; sweep_checks=[]
    y0,y1=-72.0,72.0; tube_od=6.0; tube_id=4.0; half=tube_od/2.0
    for foreaft,xc in [('FRONT',px-16.0),('REAR',px+16.0)]:
        for level,zc in [('LOWER',pz-11.5),('UPPER',pz+11.5)]:
            body=extrude_poly(root,'REF_CF6x4_'+foreaft+'_'+level+'_v32',[(xc-half,y0),(xc+half,y0),(xc+half,y1),(xc-half,y1)],zc-half,tube_od)
            body.opacity=0.30; ties.append(body)
            bc=temporary.copy(body); fc=temporary.copy(fus); bv=body.volume; ok=temporary.booleanOperation(bc,fc,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=bc.volume if ok and bc.isValid else 0.0
            containment.append(dict(tie=body.name,envelope_volume_cm3=bv,inside_fuselage_volume_cm3=iv,inside_fraction=(iv/bv if bv else 0.0)))
            # Verify each cross-tie actually overlaps both left/right fork structures, creating a real packaging path.
            for side in ['R','L']:
                fork=next(b for b in root.bRepBodies if b.name=='ENG_WINGBOX_FORK_'+level+'_'+side+'_v31')
                tc=temporary.copy(body); pc=temporary.copy(fork); ok2=temporary.booleanOperation(tc,pc,adsk.fusion.BooleanTypes.IntersectionBooleanType); ov=tc.volume if ok2 and tc.isValid else 0.0
                overlaps.append(dict(tie=body.name,side=side,fork=fork.name,intersection_volume_cm3=ov,positive_overlap=ov>1e-4))
    # Dense moving-wing collision check against all fixed cross-tie envelopes.
    for sweep in range(20,69,2):
        for sign,label in [(1,'R'),(-1,'L')]:
            angle=-sign*math.radians(sweep-20.0); rot=adsk.core.Matrix3D.create(); rot.setToRotation(angle,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(sign*py),mm(pz)))
            wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_')); lug=next(b for b in root.bRepBodies if b.name=='ENG_ROOT_LUG_'+label+'_v19')
            for moving_body,kind in [(wing,'outer_wing'),(lug,'root_lug')]:
                moving=temporary.copy(moving_body); temporary.transform(moving,rot)
                for tie in ties:
                    t=temporary.copy(moving); tool=temporary.copy(tie); ok=temporary.booleanOperation(t,tool,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=t.volume if ok and t.isValid else 0.0
                    sweep_checks.append(dict(sweep_deg=sweep,side=label,moving_kind=kind,tie=tie.name,intersection_volume_cm3=iv,positive_overlap=iv>1e-4))
    residual=[r for r in sweep_checks if r['positive_overlap']]; tie_len_mm=y1-y0
    tube_area_mm2=math.pi*(tube_od**2-tube_id**2)/4.0; tube_volume_cm3=tube_area_mm2*tie_len_mm/1000.0; tube_mass_each_g=tube_volume_cm3*1.60; total_mass=tube_mass_each_g*len(ties)
    audit=dict(status='CARBON_CROSSTIE_WINGBOX_PACKAGING_REVIEW',source_revision='v31',
      geometry=dict(tie_length_mm=tie_len_mm,tube_od_mm=tube_od,tube_id_mm=tube_id,front_x_mm=px-16,rear_x_mm=px+16,lower_z_mm=pz-11.5,upper_z_mm=pz+11.5,count=len(ties)),
      tie_containment=containment,min_tie_inside_fraction=min(c['inside_fraction'] for c in containment),fork_overlap=overlaps,
      all_ties_overlap_both_forks=all(o['positive_overlap'] for o in overlaps),fixed_tie_sweep_collision_records=sweep_checks,residual_positive_overlaps=residual,
      dense_tie_clearance_pass=(len(residual)==0),carbon_tube_mass_estimate_g_each=tube_mass_each_g,carbon_crosstie_total_mass_estimate_g=total_mass,
      v31_hardpoint_mass_estimate_g=28.45224678790477,combined_fork_plus_crosstie_mass_estimate_g=28.45224678790477+total_mass,
      carbon_tube_datasheet_verified=False,mechanical_detail_release=False,print_release=False,flight_release=False)
    outdir=os.path.join(config['export_dir'],'carbon_crosstie_v32'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v32_CARBON_CROSSTIE_WINGBOX_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v32 export failed')
    with open(os.path.join(outdir,'F14_v32_carbon_crosstie_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v32_carbon_crosstie_review.png'),1600,1000)
    return audit

'''
for path in files:
    s=path.read_text(encoding='utf-8'); insert=s.index('def build_project_revision():')
    if 'def build_carbon_crosstie_wingbox_review_v32()' not in s: s=s[:insert]+fn+s[insert:]
    s=s.replace('return build_wingbox_fork_hardpoint_review_v31()','return build_carbon_crosstie_wingbox_review_v32()',1)
    path.write_text(s,encoding='utf-8'); print('patched',path)
