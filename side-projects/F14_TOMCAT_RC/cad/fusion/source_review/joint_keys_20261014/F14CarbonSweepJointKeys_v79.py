"""v79: carve the carbon insertion swept-volume from the validated tapered v78 bridge."""
import adsk.core, adsk.fusion, json, os, hashlib

def _end_faces(body):
    out=[]
    for f in body.faces:
        pl=adsk.core.Plane.cast(f.geometry)
        if pl and abs(pl.normal.y)>0.999999: out.append((f.pointOnFace.y*10.0,f,f.area*100.0))
    return sorted(out,key=lambda x:x[0])

def _vol(body): return body.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume

def _profile_from_face(root,face,target_area,name):
    sk=root.sketches.add(face); sk.name=name
    for e in face.edges: sk.project(e)
    cand=[]
    for p in sk.profiles:
        props=p.areaProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy)
        cand.append((abs(props.area*100.0-target_area),props.area*100.0,p,p.profileLoops.count))
    if not cand: raise RuntimeError('No profile '+name)
    cand.sort(key=lambda x:x[0]); err,area,p,loops=cand[0]
    if err>1.0: raise RuntimeError('Profile mismatch '+name)
    return p,area,loops

def run_review(app, build_source_wings, mm, outdir):
    prior=app.activeDocument; base=os.path.dirname(__file__)
    src=json.load(open(os.path.join(base,'F14_v79_section_inputs.json'),encoding='utf-8'))
    if hashlib.sha256(open(src['path'],'rb').read()).hexdigest()!=src['sha256']: raise RuntimeError('Source hash mismatch')
    if not app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(src['path'])): raise RuntimeError('Archive import failed')
    original=adsk.fusion.Design.cast(app.activeProduct); temp=adsk.fusion.TemporaryBRepManager.get(); wanted=[]
    for i in range(original.rootComponent.bRepBodies.count):
        b=original.rootComponent.bRepBodies.item(i)
        if ('_R_' in b.name and ('CARBON' in b.name or 'HOLLOW_WING' in b.name)) or b.name in ('CANDIDATE_RIB_ZERO_CLEARANCE_-3','CANDIDATE_RIB_ZERO_CLEARANCE_3'):
            wanted.append((b.name,temp.copy(b)))
    if len(wanted)!=7: raise RuntimeError('Expected seven right-side bodies')
    doc=app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType); doc.name='F14_WING_JOINT_CARBON_SWEEP_KEYS_v79'
    design=adsk.fusion.Design.cast(app.activeProduct); design.designType=adsk.fusion.DesignTypes.DirectDesignType
    root=design.rootComponent; bodies=[]
    for name,copy in wanted:
        b=root.bRepBodies.add(copy); b.name=name; bodies.append(b)
    spars=[b for b in bodies if 'CARBON' in b.name]
    skin_inner=next(b for b in bodies if b.name=='CANDIDATE_HOLLOW_WING_R_INNER_NO_JOINTS')
    skin_outer=next(b for b in bodies if b.name=='CANDIDATE_HOLLOW_WING_R_OUTER_NO_JOINTS')
    inner=next(b for b in bodies if b.name=='CANDIDATE_RIB_ZERO_CLEARANCE_-3')
    outer=next(b for b in bodies if b.name=='CANDIDATE_RIB_ZERO_CLEARANCE_3')
    inner_y,inner_face,inner_area=max(_end_faces(inner),key=lambda x:x[0]); outer_y,outer_face,outer_area=min(_end_faces(outer),key=lambda x:x[0])
    shifted_copy=temp.copy(inner); tr=adsk.core.Matrix3D.create(); tr.translation=adsk.core.Vector3D.create(0,mm(float(src['target_axial_gap_mm'])),0); temp.transform(shifted_copy,tr)
    shifted=root.bRepBodies.add(shifted_copy); sy,sface,sarea=max(_end_faces(shifted),key=lambda x:x[0])
    p1,a1,l1=_profile_from_face(root,outer_face,outer_area,'V79_OUTER_PROFILE'); p2,a2,l2=_profile_from_face(root,sface,sarea,'V79_INNER_PROFILE')
    li=root.features.loftFeatures.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation); li.isSolid=True; li.loftSections.add(p1); li.loftSections.add(p2)
    lf=root.features.loftFeatures.add(li)
    candidates=[]
    for i in range(lf.bodies.count):
        b=lf.bodies.item(i); bb=b.boundingBox; span=(bb.maxPoint.y-bb.minPoint.y)*10.0
        if 4.95<=span<=5.05: candidates.append(b)
    if len(candidates)!=1: raise RuntimeError('Expected one 5 mm loft bridge')
    raw=candidates[0]; raw.name='REFERENCE_RAW_TAPERED_BRIDGE_v79'; raw_volume=_vol(raw)
    shifted.deleteMe()
    # Carve the union of all relative carbon positions encountered while the outer segment slides 5 mm inboard.
    carved=temp.copy(raw)
    sweep=float(src['carbon_sweep_mm']); step=float(src['carbon_sweep_step_mm']); n=int(round(sweep/step))
    carve_ops=[]
    for k in range(n+1):
        dy=k*step
        for spar in spars:
            cutter=temp.copy(spar)
            m=adsk.core.Matrix3D.create(); m.translation=adsk.core.Vector3D.create(0,mm(-dy),0); temp.transform(cutter,m)
            before_tmp=carved.volume if hasattr(carved,'volume') else None
            if not temp.booleanOperation(carved,cutter,adsk.fusion.BooleanTypes.DifferenceBooleanType): raise RuntimeError('Carbon sweep carve failed')
        carve_ops.append({'relative_carbon_shift_mm':-dy})
    keys=root.bRepBodies.add(carved); keys.name='CANDIDATE_CARBON_SWEEP_CLEARED_KEYS_v79'
    if not keys.isValid or not keys.isSolid: raise RuntimeError('Carved keys invalid')
    key_volume=_vol(keys); bb=keys.boundingBox; span=(bb.maxPoint.y-bb.minPoint.y)*10.0
    final=[]
    for blocker in [skin_inner,skin_outer]+spars:
        q=temp.copy(keys)
        if not temp.booleanOperation(q,temp.copy(blocker),adsk.fusion.BooleanTypes.DifferenceBooleanType): raise RuntimeError('Final boolean failed')
        scratch=root.bRepBodies.add(q); vv=_vol(scratch); scratch.deleteMe(); removed=max(0.0,key_volume-vv)
        final.append({'blocker':blocker.name,'removed_cm3':removed,'pass':removed<1e-7})
    axial_gap=app.measureManager.measureMinimumDistance(keys,inner).value*10.0
    stationary=[skin_inner,inner]+spars; insertion=[]
    for k in range(n,-1,-1):
        dy=k*step; moving=temp.copy(keys); m=adsk.core.Matrix3D.create(); m.translation=adsk.core.Vector3D.create(0,mm(dy),0); temp.transform(moving,m)
        hits=[]
        for blocker in stationary:
            q=temp.copy(moving)
            if not temp.booleanOperation(q,temp.copy(blocker),adsk.fusion.BooleanTypes.DifferenceBooleanType): raise RuntimeError('Insertion boolean failed')
            scratch=root.bRepBodies.add(q); vv=_vol(scratch); scratch.deleteMe(); removed=max(0.0,key_volume-vv)
            if removed>=1e-7: hits.append({'blocker':blocker.name,'removed_cm3':removed})
        insertion.append({'outboard_translation_mm':dy,'collision_free':not hits,'hits':hits})
    final_clear=all(x['pass'] for x in final); insertion_clear=all(x['collision_free'] for x in insertion); gap_pass=abs(axial_gap-float(src['target_axial_gap_mm']))<=0.03
    audit={'status':'V79_CARBON_SWEEP_CLEARED_TAPERED_KEYS','source':src,'profiles':{'outer_y_mm':outer_y,'inner_original_y_mm':inner_y,'inner_shifted_y_mm':sy,'outer_area_mm2':a1,'inner_area_mm2':a2},'raw_bridge_volume_cm3':raw_volume,'keys':{'volume_cm3':key_volume,'volume_retained_fraction':key_volume/raw_volume,'bbox_y_min_mm':bb.minPoint.y*10.0,'bbox_y_max_mm':bb.maxPoint.y*10.0,'span_mm':span,'face_count':keys.faces.count,'axial_gap_to_inner_rib_mm':axial_gap},'carbon_sweep_carve_samples':carve_ops,'final_collision_checks':final,'insertion_path_screen':insertion,'final_collision_free':final_clear,'insertion_collision_free':insertion_clear,'axial_gap_screen_pass':gap_pass,'geometry_candidate_pass':final_clear and insertion_clear and gap_pass,'primary_bending_path':'continuous carbon upper/lower caps and web','fit_coupon_verified':False,'torsion_transfer_verified':False,'minimum_key_section_verified':False,'adhesive_system_selected':False,'structural_capacity_verified':False,'print_release':False,'flight_release':False,'study_source_sha256':hashlib.sha256(open(__file__,'rb').read()).hexdigest()}
    os.makedirs(outdir,exist_ok=True)
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(os.path.join(outdir,'F14_WING_JOINT_CARBON_SWEEP_KEYS_v79.f3d'))): raise RuntimeError('Export failed')
    json.dump(audit,open(os.path.join(outdir,'F14_v79_carbon_sweep_keys_audit.json'),'w',encoding='utf-8'),indent=2)
    app.activeViewport.fit(); app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v79_carbon_sweep_keys_review.png'),1600,1000)
    if prior: prior.activate()
    return audit