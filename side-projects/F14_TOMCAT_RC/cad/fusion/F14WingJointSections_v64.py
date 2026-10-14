"""Native joint-reference cuts; no production joint or strength release."""
import adsk.core, adsk.fusion, json, os, hashlib

def run_review(app,build_source_wings,mm,outdir):
    prior=app.activeDocument
    src=json.load(open(os.path.join(os.path.dirname(__file__),'F14_v64_section_inputs.json'),encoding='utf-8'))
    if hashlib.sha256(open(src['path'],'rb').read()).hexdigest()!=src['sha256']: raise RuntimeError('Source hash mismatch')
    imported=app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(src['path']))
    if not imported: raise RuntimeError('Archive import failed')
    original=adsk.fusion.Design.cast(app.activeProduct)
    temp=adsk.fusion.TemporaryBRepManager.get()
    copies=[(b.name,temp.copy(b)) for b in original.rootComponent.bRepBodies]
    if len(copies)!=10: raise RuntimeError('Expected ten source bodies')
    doc=app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    doc.name='F14_WING_JOINT_SECTION_REFERENCES_v64'
    design=adsk.fusion.Design.cast(app.activeProduct); design.designType=adsk.fusion.DesignTypes.DirectDesignType
    root=design.rootComponent; bodies=[]
    for name,copy in copies:
        body=root.bRepBodies.add(copy); body.name=name; bodies.append(body)
    records=[]
    for offset in (-3,3):
        y=363.9687853+offset
        ci=root.constructionPlanes.createInput()
        normal=root.xZConstructionPlane.geometry.normal.y
        ci.setByOffset(root.xZConstructionPlane,adsk.core.ValueInput.createByReal(mm(y)/normal))
        plane=root.constructionPlanes.add(ci); plane.name='JOINT_REFERENCE_Y_'+str(y)
        shell_token='_INNER' if offset<0 else '_OUTER'
        selected=[b for b in bodies if '_R_' in b.name and (('HOLLOW_WING' in b.name and shell_token in b.name) or 'CARBON' in b.name)]
        if len(selected)!=4: raise RuntimeError('Expected skin and three spar bodies')
        for body in selected:
            sketch=root.sketches.add(plane); sketch.name='REFERENCE_'+str(offset)+'_'+body.name
            curves=sketch.projectCutEdges(body)
            if not curves or curves.count==0: raise RuntimeError('Empty native cut: '+body.name)
            areas=[]
            for profile in sketch.profiles:
                props=profile.areaProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy)
                p=sketch.sketchToModelSpace(props.centroid)
                areas.append(dict(area_mm2=props.area*100,centroid_mm=[p.x*10,p.y*10,p.z*10],loop_count=profile.profileLoops.count))
            if not areas: raise RuntimeError('No closed cut profile: '+body.name)
            records.append(dict(y_mm=y,body=body.name,curve_count=curves.count,profiles=areas))
    if len(records)!=8: raise RuntimeError('Expected eight cut sketches')
    audit=dict(status='NATIVE_CUT_SECTION_REFERENCES',source=src,sections=records,study_engagement_span_mm=6,engagement_selected_for_production=False,joint_designed=False,structural_capacity_verified=False,print_release=False,study_source_sha256=hashlib.sha256(open(__file__,'rb').read()).hexdigest())
    os.makedirs(outdir,exist_ok=True)
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(os.path.join(outdir,'F14_WING_JOINT_SECTION_REFERENCES_v64.f3d'))): raise RuntimeError('Export failed')
    json.dump(audit,open(os.path.join(outdir,'F14_v64_section_audit.json'),'w',encoding='utf-8'),indent=2)
    app.activeViewport.fit(); app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v64_section_review.png'),1600,1000)
    if prior: prior.activate()
    return audit
