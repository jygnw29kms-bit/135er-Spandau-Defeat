"""Native minimum-distance study using immutable archived wing review geometry."""
import adsk.core,adsk.fusion,json,os,math,hashlib

def run_review(app,build_source_wings,mm,outdir):
    base=os.path.dirname(__file__)
    inputs=json.load(open(os.path.join(base,'F14_v60_clearance_inputs.json'),encoding='utf-8'))
    prior=app.activeDocument; temp=adsk.fusion.TemporaryBRepManager.get(); copies=[]
    for kind,source in inputs.items():
        raw=open(source['path'],'rb').read()
        if hashlib.sha256(raw).hexdigest()!=source['sha256']: raise RuntimeError('Archived source changed: '+kind)
        options=app.importManager.createFusionArchiveImportOptions(source['path'])
        doc=app.importManager.importToNewDocument(options)
        if not doc: raise RuntimeError('Could not import archived '+kind)
        design=adsk.fusion.Design.cast(app.activeProduct)
        bodies=[b for b in design.rootComponent.bRepBodies if (b.name.startswith('CANDIDATE_CARBON_') if kind=='spars' else b.name.startswith('CANDIDATE_HOLLOW_WING_'))]
        if len(bodies)!=(6 if kind=='spars' else 4): raise RuntimeError('Unexpected source body count: '+kind)
        copies.extend((kind,b.name,temp.copy(b)) for b in bodies)
    doc=app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    doc.name='F14_NATIVE_SPAR_SKIN_CLEARANCE_v60'; design=adsk.fusion.Design.cast(app.activeProduct); design.designType=adsk.fusion.DesignTypes.DirectDesignType
    root=design.rootComponent; groups={'spars':[],'shells':[]}
    for kind,name,copy in copies:
        if kind=='spars' and ('UPPER_CAP' in name or 'LOWER_CAP' in name):
            shift=-.03 if 'UPPER_CAP' in name else .03
            transform=adsk.core.Matrix3D.create(); transform.translation=adsk.core.Vector3D.create(0,0,mm(shift))
            if not temp.transform(copy,transform): raise RuntimeError('Candidate cap translation failed')
        body=root.bRepBodies.add(copy); body.name=name; body.opacity=.8 if kind=='spars' else .15; groups[kind].append(body)
    web_cuts=[]
    for index,web in enumerate(list(groups['spars'])):
        if '_WEB_' not in web.name: continue
        name=web.name; side='R' if '_R_' in name else 'L'
        before=web.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume
        tools=adsk.core.ObjectCollection.create()
        for cap in groups['spars']:
            if '_'+side+'_' in cap.name and '_CAP_' in cap.name: tools.add(cap)
        if tools.count!=2: raise RuntimeError('Expected two cap trimming tools')
        interface_gaps=[app.measureManager.measureMinimumDistance(web,tools.item(i)).value*10 for i in range(tools.count)]
        inp=root.features.combineFeatures.createInput(web,tools); inp.operation=adsk.fusion.FeatureOperations.CutFeatureOperation; inp.isKeepToolBodies=True
        feature=root.features.combineFeatures.add(inp)
        if not feature or feature.healthState==adsk.fusion.FeatureHealthStates.ErrorFeatureHealthState: raise RuntimeError('Native web trim failed: '+json.dumps(dict(feature_returned=feature is not None,feature_message=feature.errorOrWarningMessage if feature else None,interface_gaps_mm=interface_gaps,web_volume_cm3=before)))
        updated=feature.bodies.item(0); updated.name=name
        after=updated.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume
        if not updated.isValid or not updated.isSolid or not 0<after<before: raise RuntimeError('Invalid trimmed web')
        groups['spars'][index]=updated
        web_cuts.append(dict(side=side,before_cm3=before,after_cm3=after,removed_cm3=before-after,cap_tools_preserved=True))
    if len(web_cuts)!=2 or root.bRepBodies.count!=10: raise RuntimeError('Unexpected trimmed study body count')
    measurements=[]
    for spar in groups['spars']:
        side='R' if '_R_' in spar.name else 'L'
        for shell in groups['shells']:
            if '_'+side+'_' not in shell.name: continue
            result=app.measureManager.measureMinimumDistance(spar,shell)
            if not result or not math.isfinite(result.value): raise RuntimeError('Native minimum-distance query failed')
            measurements.append(dict(spar=spar.name,shell=shell.name,minimum_distance_mm=result.value*10,nominal_0p2mm_gap_pass=result.value*10>=.2-1e-4))
    if len(measurements)!=12: raise RuntimeError('Expected twelve same-side gap checks')
    audit=dict(status='NATIVE_SPAR_TO_SHELL_MINIMUM_DISTANCE',inputs=inputs,cap_inward_vertical_shift_mm=.03,cap_centroid_separation_reduction_mm=.06,web_interfaces_updated=True,web_interface_cuts=web_cuts,measurements=measurements,minimum_gap_mm=min(r['minimum_distance_mm'] for r in measurements),all_nominal_0p2mm_gaps_pass=all(r['nominal_0p2mm_gap_pass'] for r in measurements),source_outer_containment_previously_checked=True,bond_design_verified=False,structural_capacity_verified=False,print_release=False,study_source_sha256=hashlib.sha256(open(__file__,'rb').read()).hexdigest())
    os.makedirs(outdir,exist_ok=True)
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(os.path.join(outdir,'F14_NATIVE_SPAR_SKIN_CLEARANCE_v60.f3d'))): raise RuntimeError('Clearance study export failed')
    json.dump(audit,open(os.path.join(outdir,'F14_v60_clearance_audit.json'),'w',encoding='utf-8'),indent=2)
    app.activeViewport.fit(); app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v60_clearance_review.png'),1600,1000)
    if prior: prior.activate()
    return audit
