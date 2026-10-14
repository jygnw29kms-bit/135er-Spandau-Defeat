"""Manufacturing-clearance screen derived directly from the verified v70 conformal-rib checkpoint."""
import adsk.core, adsk.fusion, json, os, hashlib

OFFSET_MM = 0.10


def run_review(app, build_source_wings, mm, outdir):
    prior = app.activeDocument
    src = json.load(open(os.path.join(os.path.dirname(__file__), 'F14_v71_section_inputs.json'), encoding='utf-8'))
    if hashlib.sha256(open(src['path'], 'rb').read()).hexdigest() != src['sha256']:
        raise RuntimeError('Source hash mismatch')

    imported = app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(src['path']))
    if not imported:
        raise RuntimeError('Archive import failed')
    original = adsk.fusion.Design.cast(app.activeProduct)
    temp = adsk.fusion.TemporaryBRepManager.get()
    copies = [(b.name, temp.copy(b)) for b in original.rootComponent.bRepBodies]
    if len(copies) != 12:
        raise RuntimeError('Expected twelve v70 source bodies')

    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    doc.name = 'F14_RIB_OFFSET_CLEARANCE_REVIEW_v71'
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.DirectDesignType
    root = design.rootComponent
    bodies = []
    for name, copy in copies:
        body = root.bRepBodies.add(copy)
        body.name = name
        bodies.append(body)

    ribs = [b for b in bodies if b.name.startswith('CANDIDATE_RIB_')]
    skins = [b for b in bodies if 'HOLLOW_WING_R_' in b.name]
    spars = [b for b in bodies if '_R_' in b.name and 'CARBON' in b.name]
    if len(ribs) != 2 or len(skins) != 2 or len(spars) != 3:
        raise RuntimeError('Unexpected v70 body inventory')

    offset_records = []
    for rib in ribs:
        before = rib.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume
        side_faces = []
        end_faces = 0
        for face in rib.faces:
            plane = adsk.core.Plane.cast(face.geometry)
            if plane and abs(plane.normal.y) > 0.999999:
                end_faces += 1
            else:
                side_faces.append(face)
        if end_faces != 2 or not side_faces:
            raise RuntimeError('Unexpected rib end-face selection: ' + rib.name)
        inp = root.features.offsetFacesFeatures.createInput(side_faces, adsk.core.ValueInput.createByReal(mm(-OFFSET_MM)))
        root.features.offsetFacesFeatures.add(inp)
        after = rib.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume
        if not rib.isValid or not rib.isSolid or not 0 < after < before:
            raise RuntimeError('Offset did not create a valid smaller rib: ' + rib.name)
        skin_gaps = [{
            'skin': skin.name,
            'gap_mm': app.measureManager.measureMinimumDistance(rib, skin).value * 10.0
        } for skin in skins]
        spar_gaps = [{
            'spar': spar.name,
            'gap_mm': app.measureManager.measureMinimumDistance(rib, spar).value * 10.0
        } for spar in spars]
        offset_records.append({
            'rib': rib.name,
            'side_faces': len(side_faces),
            'end_faces_preserved': end_faces,
            'offset_mm': -OFFSET_MM,
            'before_cm3': before,
            'after_cm3': after,
            'skin_gaps': skin_gaps,
            'spar_gaps': spar_gaps,
        })

    skin_checks = []
    for rib in ribs:
        before = rib.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume
        for skin in skins:
            cut = temp.copy(rib)
            if not temp.booleanOperation(cut, temp.copy(skin), adsk.fusion.BooleanTypes.DifferenceBooleanType):
                raise RuntimeError('Skin difference query failed')
            if not cut.isValid or not cut.isSolid:
                raise RuntimeError('Invalid skin difference result')
            measured = root.bRepBodies.add(cut)
            after = measured.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume
            if not measured.deleteMe():
                raise RuntimeError('Scratch measurement removal failed')
            gap = app.measureManager.measureMinimumDistance(rib, skin).value * 10.0
            removed = before - after
            skin_checks.append({
                'rib': rib.name,
                'skin': skin.name,
                'before_cm3': before,
                'after_difference_cm3': after,
                'removed_cm3': removed,
                'minimum_distance_mm': gap,
                'zero_interference_screen_pass': abs(removed) < 1e-7,
                'candidate_clearance_pass': gap >= OFFSET_MM * 0.95 and abs(removed) < 1e-7,
            })

    all_no_interference = all(x['zero_interference_screen_pass'] for x in skin_checks)
    own_skin_checks = []
    for rec in offset_records:
        token = '_INNER' if rec['rib'].endswith('-3') else '_OUTER'
        own = next(g for g in rec['skin_gaps'] if token in g['skin'])
        own_skin_checks.append(own['gap_mm'])
    manufacturing_candidate_pass = all_no_interference and all(g >= OFFSET_MM * 0.95 for g in own_skin_checks)

    audit = {
        'status': 'V71_MANUFACTURING_CLEARANCE_CANDIDATE',
        'source': src,
        'source_revision': 'v70_conformal_ribs',
        'offset_records': offset_records,
        'manufacturing_offset_candidate_mm': OFFSET_MM,
        'own_skin_minimum_gaps_mm': own_skin_checks,
        'all_skin_interference_screens_pass': all_no_interference,
        'manufacturing_clearance_candidate_pass': manufacturing_candidate_pass,
        'manufacturing_clearance_verified': False,
        'assembly_clearance_verified': False,
        'engagement_selected_for_production': False,
        'joint_designed': False,
        'structural_capacity_verified': False,
        'print_release': False,
        'flight_release': False,
        'study_source_sha256': hashlib.sha256(open(__file__, 'rb').read()).hexdigest(),
    }

    os.makedirs(outdir, exist_ok=True)
    export = os.path.join(outdir, 'F14_RIB_OFFSET_CLEARANCE_REVIEW_v71.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(export)):
        raise RuntimeError('Export failed')
    json.dump(audit, open(os.path.join(outdir, 'F14_v71_section_audit.json'), 'w', encoding='utf-8'), indent=2)
    app.activeViewport.fit()
    app.activeViewport.saveAsImageFile(os.path.join(outdir, 'F14_v71_section_review.png'), 1600, 1000)
    if prior:
        prior.activate()
    return audit
