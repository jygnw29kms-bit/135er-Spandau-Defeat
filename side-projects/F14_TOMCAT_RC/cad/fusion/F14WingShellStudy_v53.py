"""Native inside-shell feasibility only; no print or strength release."""
import adsk.core, adsk.fusion, json, os, traceback, math

def run_review(app, build_source_wings, mm, outdir):
    build_source_wings()
    design=adsk.fusion.Design.cast(app.activeProduct)
    app.activeDocument.name='F14_SOURCE_WING_SHELL_0p8_FEASIBILITY_v53'
    root=design.rootComponent
    bodies=list(root.bRepBodies)
    assert len(bodies)==2
    attempts=[]
    for body in bodies:
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
    audit=dict(status='NATIVE_INSIDE_SHELL_FEASIBILITY',attempts=attempts,all_shells_valid=all(r['success'] and r.get('outer_bounds_preserved',False) for r in attempts),spar_skin_clearance_verified=False,joints_created=False,slicer_checked=False,structural_capacity_verified=False,print_release=False)
    os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_SOURCE_WING_SHELL_FEASIBILITY_v53.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('Shell review archive failed')
    with open(os.path.join(outdir,'F14_v53_shell_audit.json'),'w',encoding='utf-8') as f: json.dump(audit,f,indent=2)
    app.activeViewport.fit(); app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v53_shell_review.png'),1600,1000)
    return audit
