"""Native joint-reference cuts; no production joint or strength release."""
import adsk.core, adsk.fusion, json, os, hashlib

def run_review(app,build_source_wings,mm,outdir):
    prior=app.activeDocument
    src=json.load(open(os.path.join(os.path.dirname(__file__),'F14_v70_section_inputs.json'),encoding='utf-8'))
    if hashlib.sha256(open(src['path'],'rb').read()).hexdigest()!=src['sha256']: raise RuntimeError('Source hash mismatch')
    imported=app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(src['path']))
    if not imported: raise RuntimeError('Archive import failed')
    original=adsk.fusion.Design.cast(app.activeProduct)
    temp=adsk.fusion.TemporaryBRepManager.get()
    copies=[(b.name,temp.copy(b)) for b in original.rootComponent.bRepBodies]
    if len(copies)!=10: raise RuntimeError('Expected ten source bodies')
    doc=app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    doc.name='F14_CONFORMAL_RIB_REVIEW_v70'
    design=adsk.fusion.Design.cast(app.activeProduct); design.designType=adsk.fusion.DesignTypes.DirectDesignType
    root=design.rootComponent; bodies=[]
    for name,copy in copies:
        body=root.bRepBodies.add(copy); body.name=name; bodies.append(body)
    records=[]; rib_records=[]
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
            if 'HOLLOW_WING' in body.name:
                cavity=[p for p in sketch.profiles if p.profileLoops.count==1]
                if len(cavity)!=1: raise RuntimeError('Ambiguous cavity profile')
                ei=root.features.extrudeFeatures.createInput(cavity[0],adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                ei.setDistanceExtent(False,adsk.core.ValueInput.createByReal(mm(.8)))
                feature=root.features.extrudeFeatures.add(ei)
                if not feature or feature.bodies.count!=1: raise RuntimeError('Rib blank extrusion failed')
                blank=feature.bodies.item(0); cut=temp.copy(blank)
                before=blank.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume
                for spar in bodies:
                    if '_R_' in spar.name and 'CARBON' in spar.name:
                        if not temp.booleanOperation(cut,temp.copy(spar),adsk.fusion.BooleanTypes.DifferenceBooleanType): raise RuntimeError('Rib spar cut failed')
                rib=root.bRepBodies.add(cut); rib.name='CANDIDATE_RIB_ZERO_CLEARANCE_'+str(offset)
                if not blank.deleteMe(): raise RuntimeError('Scratch blank removal failed')
                after=rib.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume
                if not rib.isValid or not rib.isSolid or not 0<after<before: raise RuntimeError('Invalid rib reference')
                rib_records.append(dict(y_reference_mm=y,before_cm3=before,after_cm3=after,thickness_mm=.8,fit_clearance_mm=0))
    conformal_cuts=[]
    for rib in [b for b in root.bRepBodies if b.name.startswith('CANDIDATE_RIB_')]:
        name=rib.name; before=rib.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume
        cut=temp.copy(rib)
        for skin in bodies:
            if 'HOLLOW_WING_R_' in skin.name:
                if not temp.booleanOperation(cut,temp.copy(skin),adsk.fusion.BooleanTypes.DifferenceBooleanType): raise RuntimeError('Conformal skin trim failed')
        revised=root.bRepBodies.add(cut)
        if not rib.deleteMe(): raise RuntimeError('Scratch rib replacement failed')
        revised.name=name
        after=revised.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume
        if not revised.isValid or not revised.isSolid or not 0<after<before: raise RuntimeError('Invalid conformal rib')
        conformal_cuts.append(dict(rib=name,before_cm3=before,after_cm3=after,removed_cm3=before-after))
    skin_checks=[]
    for rib in [b for b in root.bRepBodies if b.name.startswith('CANDIDATE_RIB_')]:
        before=rib.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume
        for skin in bodies:
            if 'HOLLOW_WING_R_' not in skin.name: continue
            cut=temp.copy(rib)
            if not temp.booleanOperation(cut,temp.copy(skin),adsk.fusion.BooleanTypes.DifferenceBooleanType): raise RuntimeError('Skin difference query failed')
            if not cut.isValid or not cut.isSolid: raise RuntimeError('Invalid skin difference result')
            measured=root.bRepBodies.add(cut)
            after=measured.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume
            if not measured.deleteMe(): raise RuntimeError('Scratch measurement removal failed')
            gap=app.measureManager.measureMinimumDistance(rib,skin).value*10
            skin_checks.append(dict(rib=rib.name,skin=skin.name,before_cm3=before,after_difference_cm3=after,removed_cm3=before-after,minimum_distance_mm=gap,zero_interference_screen_pass=abs(before-after)<1e-7))
    if len(skin_checks)!=4: raise RuntimeError('Expected four skin checks')
    if len(rib_records)!=2 or root.bRepBodies.count!=12: raise RuntimeError('Expected two rib references')
    if len(records)!=8: raise RuntimeError('Expected eight cut sketches')
    audit=dict(status='NATIVE_ZERO_CLEARANCE_RIB_REFERENCES',source=src,sections=records,rib_blanks=rib_records,conformal_cuts=conformal_cuts,manufacturing_clearance_added=False,skin_checks=skin_checks,all_skin_interference_screens_pass=all(x['zero_interference_screen_pass'] for x in skin_checks),assembly_clearance_verified=False,study_engagement_span_mm=6,engagement_selected_for_production=False,joint_designed=False,structural_capacity_verified=False,print_release=False,study_source_sha256=hashlib.sha256(open(__file__,'rb').read()).hexdigest())
    os.makedirs(outdir,exist_ok=True)
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(os.path.join(outdir,'F14_CONFORMAL_RIB_REVIEW_v70.f3d'))): raise RuntimeError('Export failed')
    json.dump(audit,open(os.path.join(outdir,'F14_v70_section_audit.json'),'w',encoding='utf-8'),indent=2)
    app.activeViewport.fit(); app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v70_section_review.png'),1600,1000)
    if prior: prior.activate()
    return audit
