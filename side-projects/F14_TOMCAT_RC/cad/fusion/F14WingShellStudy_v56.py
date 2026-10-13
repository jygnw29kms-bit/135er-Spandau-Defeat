"""Native inside-shell feasibility only; no print or strength release."""
import adsk.core, adsk.fusion, json, os, traceback, math, hashlib

def run_review(app, build_source_wings, mm, outdir):
    build_source_wings()
    design=adsk.fusion.Design.cast(app.activeProduct)
    app.activeDocument.name='F14_SOURCE_WING_SHELL_0p8_FEASIBILITY_v56'
    root=design.rootComponent
    bodies=list(root.bRepBodies)
    assert len(bodies)==2
    attempts=[]
    left=next(b for b in bodies if b.boundingBox.maxPoint.y<0)
    temporary=adsk.fusion.TemporaryBRepManager.get()
    original_left=temporary.copy(left)
    for body in [b for b in bodies if b.boundingBox.minPoint.y>0]:
        name=body.name; before=body.volume; bounds=body.boundingBox
        side='R' if bounds.minPoint.y+bounds.maxPoint.y>0 else 'L'
        root_y=(bounds.minPoint.y if side=='R' else bounds.maxPoint.y)*10
        rec=dict(side=side,original_name=name,original_volume_cm3=before,inside_thickness_mm=.8,root_opening_y_mm=root_y,success=False)
        try:
            faces=[f for f in body.faces if abs(f.boundingBox.minPoint.y*10-root_y)<1e-4 and abs(f.boundingBox.maxPoint.y*10-root_y)<1e-4]
            if len(faces)!=1: raise RuntimeError('Expected one planar source-root cap, got '+str(len(faces)))
            collection=adsk.core.ObjectCollection.create(); collection.add(faces[0])
            inp=root.features.shellFeatures.createInput(collection,False)
            inp.insideThickness=adsk.core.ValueInput.createByReal(mm(.8))
            inp.outsideThickness=adsk.core.ValueInput.createByReal(0)
            feature=root.features.shellFeatures.add(inp)
            if not feature or feature.healthState==adsk.fusion.FeatureHealthStates.ErrorFeatureHealthState:
                raise RuntimeError('Native shell feature error: '+(feature.errorOrWarningMessage if feature else 'no feature'))
            result=feature.bodies.item(0)
            after=result.volume
            if not result.isValid or not result.isSolid or not math.isfinite(after) or not 0<after<before:
                raise RuntimeError('Shell did not produce a valid reduced-volume solid')
            current=result.boundingBox
            deviation=max(abs(getattr(getattr(current,corner),axis)-getattr(getattr(bounds,corner),axis))*10 for corner in ['minPoint','maxPoint'] for axis in ['x','y','z'])
            rec.update(success=True,shell_volume_cm3=after,material_volume_fraction=after/before,outer_bounds_max_change_mm=deviation,outer_bounds_preserved=deviation<1e-3,native_feature_message=feature.errorOrWarningMessage)
            result.name='CANDIDATE_SOURCE_WING_SHELL_'+side+'_NOT_PRINT_RELEASED'
        except Exception:
            rec['error']=traceback.format_exc()
        attempts.append(rec)
    mirrored=dict(side='L',success=False,method='mirror successful right shell')
    try:
        if not attempts[0]['success']: raise RuntimeError('Right shell failed; no mirror source')
        right=next(b for b in root.bRepBodies if b.name.startswith('CANDIDATE_SOURCE_WING_SHELL_R'))
        root.features.removeFeatures.add(left)
        collection=adsk.core.ObjectCollection.create(); collection.add(right)
        inp=root.features.mirrorFeatures.createInput(collection,root.xZConstructionPlane)
        inp.isCombine=False
        feature=root.features.mirrorFeatures.add(inp)
        result=feature.bodies.item(0)
        if not result.isValid or not result.isSolid: raise RuntimeError('Invalid mirrored shell')
        result.name='CANDIDATE_SOURCE_WING_SHELL_L_MIRRORED_NOT_PRINT_RELEASED'
        rb=right.boundingBox; lb=result.boundingBox
        error=max(abs(lb.minPoint.x-rb.minPoint.x),abs(lb.maxPoint.x-rb.maxPoint.x),abs(lb.minPoint.z-rb.minPoint.z),abs(lb.maxPoint.z-rb.maxPoint.z),abs(lb.minPoint.y+rb.maxPoint.y),abs(lb.maxPoint.y+rb.minPoint.y))*10
        volume_error=abs(result.volume-right.volume)/right.volume
        copy=temporary.copy(result); ok=temporary.booleanOperation(copy,original_left,adsk.fusion.BooleanTypes.IntersectionBooleanType)
        inside=copy.volume if ok and copy.isValid else None
        outside=result.volume-inside if inside is not None else None
        contained=outside is not None and abs(outside)<=max(1e-6,result.volume*1e-6)
        passed=(error<1e-3 and volume_error<1e-6 and contained and root.bRepBodies.count==2)
        mirrored.update(success=passed,outer_bounds_preserved=error<1e-3,symmetry_bounds_max_error_mm=error,shell_volume_cm3=result.volume,volume_relative_error=volume_error,inside_original_left_solid=contained,outside_volume_cm3=outside)
    except Exception:
        mirrored['error']=traceback.format_exc()
    attempts.append(mirrored)
    if not all(r['success'] for r in attempts): raise RuntimeError('Both shells required before splitting')
    with open(os.path.join(os.path.dirname(__file__),'F14_wing_segmentation_v15.json'),encoding='utf-8') as f: plan=json.load(f)
    source_path=os.path.join(os.path.dirname(__file__),'NASA_F14_basic_wing_v08.json')
    raw=open(source_path,'rb').read()
    if hashlib.sha256(raw).hexdigest()!=plan['source_dataset_sha256']: raise RuntimeError('Source wing dataset mismatch')
    split=plan['split_model_y_mm']
    original_volumes={}
    for body in list(root.bRepBodies):
        bb=body.boundingBox; side='R' if bb.minPoint.y+bb.maxPoint.y>0 else 'L'; sign=1 if side=='R' else -1
        original_volumes[side]=body.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume
        planes=root.constructionPlanes; pi=planes.createInput(); normal=root.xZConstructionPlane.geometry.normal.y
        pi.setByOffset(root.xZConstructionPlane,adsk.core.ValueInput.createByReal(mm(sign*split/normal)))
        plane=planes.add(pi)
        root.features.splitBodyFeatures.add(root.features.splitBodyFeatures.createInput(body,plane,True))
    if root.bRepBodies.count!=4: raise RuntimeError('Expected four hollow wing segments')
    segments=[]; totals={'R':0.0,'L':0.0}; labels=set()
    for body in root.bRepBodies:
        bb=body.boundingBox; bounds={a:[getattr(bb.minPoint,a)*10,getattr(bb.maxPoint,a)*10] for a in ['x','y','z']}
        middle=sum(bounds['y'])/2; side='R' if middle>0 else 'L'; part='INNER' if abs(middle)<split else 'OUTER'
        if (side,part) in labels or not body.isSolid or not body.isValid or body.volume<=0: raise RuntimeError('Invalid segment classification or body')
        labels.add((side,part)); body.name='CANDIDATE_HOLLOW_WING_'+side+'_'+part+'_NO_JOINTS'
        sizes={a:b[1]-b[0] for a,b in bounds.items()}; footprint=[sizes['x']+2*plan['assumed_brim_per_side_mm'],sizes['z']+2*plan['assumed_brim_per_side_mm']]
        usable=plan['design_assumed_usable_envelope_mm']; fits=footprint[0]<=usable[0] and footprint[1]<=usable[1] and sizes['y']<=usable[2]
        totals[side]+=body.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume
        segments.append(dict(name=body.name,bounds_mm=bounds,volume_cm3=body.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume,print_height_mm=sizes['y'],footprint_with_brim_mm=footprint,assumed_envelope_fit=fits))
    volume_checks={side:dict(original_cm3=original_volumes[side],split_sum_cm3=totals[side],relative_error=abs(totals[side]-original_volumes[side])/original_volumes[side],conserved=abs(totals[side]-original_volumes[side])<=max(1e-6,original_volumes[side]*1e-5)) for side in ['R','L']}
    if not all(c['conserved'] for c in volume_checks.values()): raise RuntimeError('Hollow segment volume mismatch: '+json.dumps(volume_checks,sort_keys=True))
    audit=dict(status='NATIVE_INSIDE_SHELL_FEASIBILITY',attempts=attempts,native_segments=segments,split_volume_checks=volume_checks,split_volume_calculation_accuracy='VeryHighCalculationAccuracy; documented +/-0.01 percent',four_segments_fit=all(r['assumed_envelope_fit'] for r in segments),study_source_sha256=hashlib.sha256(open(__file__,'rb').read()).hexdigest(),all_shells_valid=all(r['success'] and r.get('outer_bounds_preserved',False) for r in attempts),spar_skin_clearance_verified=False,joints_created=False,slicer_checked=False,structural_capacity_verified=False,print_release=False)
    os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_SOURCE_WING_SHELL_FEASIBILITY_v56.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('Shell review archive failed')
    with open(os.path.join(outdir,'F14_v56_shell_audit.json'),'w',encoding='utf-8') as f: json.dump(audit,f,indent=2)
    app.activeViewport.fit(); app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v56_shell_review.png'),1600,1000)
    return audit
