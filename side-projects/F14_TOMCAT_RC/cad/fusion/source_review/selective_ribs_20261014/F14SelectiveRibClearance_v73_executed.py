"""Selective rib clearance: 0.15 mm skin assembly gap while retaining 0.10 mm spar bondline candidate."""
import adsk.core, adsk.fusion, json, os, hashlib

CURRENT_GAP_MM = 0.10
SKIN_TARGET_MM = 0.15
EXTRA_SKIN_OFFSET_MM = SKIN_TARGET_MM - CURRENT_GAP_MM
CONTACT_LIMIT_MM = 0.105


def run_review(app, build_source_wings, mm, outdir):
    prior = app.activeDocument
    src = json.load(open(os.path.join(os.path.dirname(__file__), 'F14_v73_section_inputs.json'), encoding='utf-8'))
    if hashlib.sha256(open(src['path'], 'rb').read()).hexdigest() != src['sha256']:
        raise RuntimeError('Source hash mismatch')
    imported = app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(src['path']))
    if not imported:
        raise RuntimeError('Archive import failed')
    original = adsk.fusion.Design.cast(app.activeProduct)
    temp = adsk.fusion.TemporaryBRepManager.get()
    copies = [(b.name, temp.copy(b)) for b in original.rootComponent.bRepBodies]
    if len(copies) != 12:
        raise RuntimeError('Expected twelve v71 source bodies')

    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    doc.name = 'F14_SELECTIVE_RIB_CLEARANCE_REVIEW_v73'
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
        raise RuntimeError('Unexpected v71 body inventory')

    selection_records = []
    for rib in ribs:
        selected = []
        counts = {'skin_only': 0, 'spar_only': 0, 'skin_and_spar': 0, 'free': 0, 'end': 0}
        for face in rib.faces:
            plane = adsk.core.Plane.cast(face.geometry)
            if plane and abs(plane.normal.y) > 0.999999:
                counts['end'] += 1
                continue
            skin_gap = min(app.measureManager.measureMinimumDistance(face, s).value * 10.0 for s in skins)
            spar_gap = min(app.measureManager.measureMinimumDistance(face, s).value * 10.0 for s in spars)
            skin_hit = skin_gap <= CONTACT_LIMIT_MM
            spar_hit = spar_gap <= CONTACT_LIMIT_MM
            if skin_hit and spar_hit:
                cls = 'skin_and_spar'
            elif skin_hit:
                cls = 'skin_only'
            elif spar_hit:
                cls = 'spar_only'
            else:
                cls = 'free'
            counts[cls] += 1
            if skin_hit:
                selected.append(face)
        if not selected:
            raise RuntimeError('No skin-contact faces selected: ' + rib.name)
        before = rib.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume
        inp = root.features.offsetFacesFeatures.createInput(selected, adsk.core.ValueInput.createByReal(mm(-EXTRA_SKIN_OFFSET_MM)))
        root.features.offsetFacesFeatures.add(inp)
        after = rib.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume
        if not rib.isValid or not rib.isSolid or not 0 < after < before:
            raise RuntimeError('Selective offset invalid: ' + rib.name)
        selection_records.append({
            'rib': rib.name,
            'classification_counts_before_offset': counts,
            'faces_given_extra_skin_offset': len(selected),
            'additional_skin_offset_mm': -EXTRA_SKIN_OFFSET_MM,
            'before_cm3': before,
            'after_cm3': after,
        })

    verification = []
    for rib in ribs:
        skin_gaps = [{'skin': s.name, 'gap_mm': app.measureManager.measureMinimumDistance(rib, s).value * 10.0} for s in skins]
        spar_gaps = [{'spar': s.name, 'gap_mm': app.measureManager.measureMinimumDistance(rib, s).value * 10.0} for s in spars]
        collision_checks = []
        before = rib.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume
        for blocker in skins + spars:
            cut = temp.copy(rib)
            if not temp.booleanOperation(cut, temp.copy(blocker), adsk.fusion.BooleanTypes.DifferenceBooleanType):
                raise RuntimeError('Difference query failed')
            measured = root.bRepBodies.add(cut)
            after = measured.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume
            measured.deleteMe()
            collision_checks.append({'blocker': blocker.name, 'removed_cm3': before - after, 'pass': abs(before - after) < 1e-7})
        verification.append({'rib': rib.name, 'skin_gaps': skin_gaps, 'spar_gaps': spar_gaps, 'collision_checks': collision_checks})

    own_skin_gaps = []
    for rec in verification:
        token = '_INNER' if rec['rib'].endswith('-3') else '_OUTER'
        own_skin_gaps.append(next(g['gap_mm'] for g in rec['skin_gaps'] if token in g['skin']))
    all_collisions_clear = all(c['pass'] for r in verification for c in r['collision_checks'])
    min_spar_gap = min(g['gap_mm'] for r in verification for g in r['spar_gaps'])
    skin_target_screen_pass = all(g >= SKIN_TARGET_MM * 0.95 for g in own_skin_gaps)
    spar_bondline_screen_pass = 0.095 <= min_spar_gap <= 0.105

    audit = {
        'status': 'V73_SELECTIVE_RIB_CLEARANCE_CANDIDATE',
        'source': src,
        'source_revision': 'v71_offset_clearance',
        'skin_target_mm': SKIN_TARGET_MM,
        'spar_bondline_target_mm': CURRENT_GAP_MM,
        'selection_records': selection_records,
        'verification': verification,
        'own_skin_gaps_mm': own_skin_gaps,
        'minimum_spar_gap_mm': min_spar_gap,
        'all_collision_screens_pass': all_collisions_clear,
        'skin_target_screen_pass': skin_target_screen_pass,
        'spar_bondline_screen_pass': spar_bondline_screen_pass,
        'geometry_candidate_pass': all_collisions_clear and skin_target_screen_pass and spar_bondline_screen_pass,
        'fit_coupon_verified': False,
        'adhesive_system_selected': False,
        'bondline_verified': False,
        'joint_designed': False,
        'structural_capacity_verified': False,
        'print_release': False,
        'flight_release': False,
        'study_source_sha256': hashlib.sha256(open(__file__, 'rb').read()).hexdigest(),
    }
    os.makedirs(outdir, exist_ok=True)
    export = os.path.join(outdir, 'F14_SELECTIVE_RIB_CLEARANCE_REVIEW_v73.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(export)):
        raise RuntimeError('Export failed')
    json.dump(audit, open(os.path.join(outdir, 'F14_v73_selective_clearance_audit.json'), 'w', encoding='utf-8'), indent=2)
    app.activeViewport.fit()
    app.activeViewport.saveAsImageFile(os.path.join(outdir, 'F14_v73_selective_clearance_review.png'), 1600, 1000)
    if prior:
        prior.activate()
    return audit
