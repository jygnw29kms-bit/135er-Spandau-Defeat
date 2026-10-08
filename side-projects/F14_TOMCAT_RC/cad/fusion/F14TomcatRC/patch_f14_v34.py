from pathlib import Path
files=[Path(r'C:\Users\dezen\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\F14TomcatRC\F14TomcatRC.py'),Path(r'C:\Users\dezen\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\F14TomcatRC_v18\F14TomcatRC_v18.py')]
fn=r'''

def build_crosstie_riser_socket_review_v34():
    """Connect v31 lower fork straps to the v33 routed lower carbon ties with compact riser/socket envelopes."""
    build_wingbox_fork_hardpoint_review_v31()
    design=adsk.fusion.Design.cast(_app.activeProduct); root=design.rootComponent
    _app.activeDocument.name='F14_v34_CROSSTIE_RISER_SOCKET_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in']); px=pivot['derived_full_scale_pivot_fs_in']*factor; py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]; dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in']); pz=(s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz)*factor
    fus=next(b for b in root.bRepBodies if b.name=='UPC_FUSELAGE_ROBUST_CLEARANCE_CUT_v29'); temporary=adsk.fusion.TemporaryBRepManager.get()
    lower_plate_z0=pz-12.5; lower_plate_top=lower_plate_z0+2.0
    routes={'FRONT':dict(xc=px-16.0,zc=pz-4.5),'REAR':dict(xc=px+16.0,zc=pz-5.5)}
    # Routed tie centers from v33: front +7 mm, rear +6 mm relative to v32 lower center pz-11.5.
    ties=[]; risers=[]; containment=[]; interfaces=[]
    for foreaft,r in routes.items():
        xc,zc=r['xc'],r['zc']
        tie=extrude_poly(root,'REF_CF6x4_'+foreaft+'_LOWER_v34',[(xc-3,-72),(xc+3,-72),(xc+3,72),(xc-3,72)],zc-3,6)
        tie.opacity=0.28; ties.append(tie)
        for sign,label in [(1,'R'),(-1,'L')]:
            # 12 mm fore/aft width aligns with v31 strap. 10 mm lateral socket length from |Y|=68..78.
            y0,y1=(68,78) if sign>0 else (-78,-68)
            x0,x1=xc-6,xc+6
            # Riser rises from lower fork plane to 1 mm above tube top; tube clearance is cut through it.
            z0=lower_plate_z0; z1=zc+4.0
            riser=extrude_poly(root,'ENG_RISER_SOCKET_'+foreaft+'_'+label+'_v34',[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1-z0)
            # Cut conservative rectangular 6.4 x 6.4 tube channel at routed tie height.
            channel=extrude_poly(root,'CUT_TUBE_CHANNEL_'+foreaft+'_'+label+'_v34',[(xc-3.2,y0-0.1),(xc+3.2,y0-0.1),(xc+3.2,y1+0.1),(xc-3.2,y1+0.1)],zc-3.2,6.4)
            tools=adsk.core.ObjectCollection.create(); tools.add(channel); ci=root.features.combineFeatures.createInput(riser,tools); ci.operation=adsk.fusion.FeatureOperations.CutFeatureOperation; ci.isKeepToolBodies=False; root.features.combineFeatures.add(ci)
            riser.opacity=0.50; risers.append(riser)
            rc=temporary.copy(riser); fc=temporary.copy(fus); rv=riser.volume; ok=temporary.booleanOperation(rc,fc,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=rc.volume if ok and rc.isValid else 0.0
            containment.append(dict(riser=riser.name,volume_cm3=rv,inside_fuselage_volume_cm3=iv,inside_fraction=(iv/rv if rv else 0.0)))
            # Check overlap to lower fork and geometric capture around tie envelope.
            fork=next(b for b in root.bRepBodies if b.name=='ENG_WINGBOX_FORK_LOWER_'+label+'_v31')
            a=temporary.copy(riser); b=temporary.copy(fork); ok2=temporary.booleanOperation(a,b,adsk.fusion.BooleanTypes.IntersectionBooleanType); ov=a.volume if ok2 and a.isValid else 0.0
            interfaces.append(dict(riser=riser.name,interface='riser_to_lower_fork',intersection_volume_cm3=ov,positive_overlap=ov>1e-4))
            # Channel should overlap the tie envelope, proving the socket surrounds the routed member.
            a=temporary.copy(tie); b=temporary.copy(riser); ok3=temporary.booleanOperation(a,b,adsk.fusion.BooleanTypes.IntersectionBooleanType); tv=a.volume if ok3 and a.isValid else 0.0
            interfaces.append(dict(riser=riser.name,interface='tie_to_riser_solid',intersection_volume_cm3=tv,positive_overlap=tv>1e-4,expected_zero_after_channel=True))
    # Dense moving-wing/lug collision test against fixed risers and routed ties.
    fixed=risers+ties; sweep_checks=[]
    for sweep in range(20,69,2):
        for sign,label in [(1,'R'),(-1,'L')]:
            angle=-sign*math.radians(sweep-20.0); rot=adsk.core.Matrix3D.create(); rot.setToRotation(angle,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(sign*py),mm(pz)))
            wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_')); lug=next(b for b in root.bRepBodies if b.name=='ENG_ROOT_LUG_'+label+'_v19')
            for moving_body,kind in [(wing,'outer_wing'),(lug,'root_lug')]:
                moving=temporary.copy(moving_body); temporary.transform(moving,rot)
                for part in fixed:
                    t=temporary.copy(moving); tool=temporary.copy(part); ok=temporary.booleanOperation(t,tool,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=t.volume if ok and t.isValid else 0.0
                    sweep_checks.append(dict(sweep_deg=sweep,side=label,moving_kind=kind,fixed_part=part.name,intersection_volume_cm3=iv,positive_overlap=iv>1e-4))
    residual=[r for r in sweep_checks if r['positive_overlap']]
    riser_vol=sum(r.volume for r in risers); riser_mass_petg=riser_vol*1.27; riser_mass_asa=riser_vol*1.07
    audit=dict(status='CROSSTIE_RISER_SOCKET_PACKAGING_REVIEW',source_revision='v31',
      geometry=dict(lower_fork_top_z_mm=lower_plate_top,front_tie_center_z_mm=routes['FRONT']['zc'],rear_tie_center_z_mm=routes['REAR']['zc'],tube_envelope_mm=[6,6],socket_channel_mm=[6.4,6.4],riser_planform_mm=[12,10]),
      riser_containment=containment,min_riser_inside_fraction=min(c['inside_fraction'] for c in containment),interfaces=interfaces,
      all_risers_engage_lower_forks=all(i['positive_overlap'] for i in interfaces if i['interface']=='riser_to_lower_fork'),
      fixed_riser_tie_sweep_collision_records=sweep_checks,residual_positive_overlaps=residual,dense_riser_tie_clearance_pass=(len(residual)==0),
      riser_total_volume_cm3=riser_vol,riser_mass_estimate_petg_g=riser_mass_petg,riser_mass_estimate_asa_g=riser_mass_asa,
      tube_retention_fastener_not_yet_defined=True,mechanical_detail_release=False,print_release=False,flight_release=False)
    outdir=os.path.join(config['export_dir'],'riser_socket_v34'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v34_CROSSTIE_RISER_SOCKET_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v34 export failed')
    with open(os.path.join(outdir,'F14_v34_riser_socket_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v34_riser_socket_review.png'),1600,1000)
    return audit

'''
for path in files:
    s=path.read_text(encoding='utf-8'); insert=s.index('def build_project_revision():')
    if 'def build_crosstie_riser_socket_review_v34()' not in s: s=s[:insert]+fn+s[insert:]
    s=s.replace('return build_lower_crosstie_routing_review_v33()','return build_crosstie_riser_socket_review_v34()',1)
    path.write_text(s,encoding='utf-8'); print('patched',path)
