import adsk.core,adsk.fusion,json,os,hashlib

def run_review(app,build_source_wings,mm,outdir):
    prior=app.activeDocument
    matches=[d for d in app.documents if d.name=='F14_SOURCE_WING_SHELL_0p8_FEASIBILITY_v56']
    if len(matches)!=1: raise RuntimeError('Existing v56 document not unique: '+str([d.name for d in app.documents]))
    matches[0].activate()
    design=adsk.fusion.Design.cast(app.activeProduct); root=design.rootComponent
    if root.bRepBodies.count!=4 or not all(b.name.startswith('CANDIDATE_HOLLOW_WING_') for b in root.bRepBodies): raise RuntimeError('Expected four existing hollow segments')
    base=os.path.dirname(__file__)
    reference=json.load(open(os.path.join(base,'F14_v57_volume_reference.json'),encoding='utf-8'))
    plan=json.load(open(os.path.join(base,'F14_wing_segmentation_v15.json'),encoding='utf-8'))
    segments=[]; totals={'R':0.0,'L':0.0}
    for body in root.bRepBodies:
        if not body.isValid or not body.isSolid: raise RuntimeError('Invalid existing segment')
        side='R' if '_R_' in body.name else 'L'; bb=body.boundingBox
        bounds={a:[getattr(bb.minPoint,a)*10,getattr(bb.maxPoint,a)*10] for a in ['x','y','z']}
        size={a:v[1]-v[0] for a,v in bounds.items()}; footprint=[size['x']+16,size['z']+16]
        volume=body.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume
        totals[side]+=volume
        segments.append(dict(name=body.name,bounds_mm=bounds,volume_cm3=volume,print_height_mm=size['y'],footprint_with_brim_mm=footprint,assumed_envelope_fit=footprint[0]<=240 and footprint[1]<=240 and size['y']<=250))
    checks={}
    for side in ['R','L']:
        original=reference['original_volume_cm3'][side]; delta=totals[side]-original; relative=abs(delta)/original
        checks[side]=dict(original_cm3=original,split_sum_cm3=totals[side],relative_error=relative,strict_10ppm_pass=relative<=1e-5,documented_combined_200ppm_measurement_consistency=relative<=2e-4)
    audit=dict(status='NATIVE_EXISTING_HOLLOW_SEGMENT_CHECKPOINT',segments=segments,volume_checks=checks,reference_provenance=reference,physical_property_accuracy='VeryHigh: documented +/-0.01 percent per measurement',four_segments_fit=all(s['assumed_envelope_fit'] for s in segments),exact_volume_conservation_proved=False,joints_created=False,spar_skin_clearance_verified=False,slicer_checked=False,structural_capacity_verified=False,print_release=False,study_source_sha256=hashlib.sha256(open(__file__,'rb').read()).hexdigest())
    os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_HOLLOW_WING_SEGMENTS_CHECKPOINT_v57.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('Checkpoint export failed')
    json.dump(audit,open(os.path.join(outdir,'F14_v57_hollow_segment_audit.json'),'w',encoding='utf-8'),indent=2)
    app.activeViewport.fit(); app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v57_hollow_segments.png'),1600,1000)
    if prior and prior!=matches[0]: prior.activate()
    return audit
