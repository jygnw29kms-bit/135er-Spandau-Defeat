"""Classify v70 conformal-rib side faces by actual contact with wing skin and carbon spar bodies."""
import adsk.core, adsk.fusion, json, os, hashlib

CONTACT_EPS_MM = 0.105


def run_review(app, build_source_wings, mm, outdir):
    prior = app.activeDocument
    src = json.load(open(os.path.join(os.path.dirname(__file__), 'F14_v72_section_inputs.json'), encoding='utf-8'))
    if hashlib.sha256(open(src['path'], 'rb').read()).hexdigest() != src['sha256']:
        raise RuntimeError('Source hash mismatch')
    imported = app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(src['path']))
    if not imported:
        raise RuntimeError('Archive import failed')
    design = adsk.fusion.Design.cast(app.activeProduct)
    bodies = list(design.rootComponent.bRepBodies)
    ribs = [b for b in bodies if b.name.startswith('CANDIDATE_RIB_')]
    skins = [b for b in bodies if 'HOLLOW_WING_R_' in b.name]
    spars = [b for b in bodies if '_R_' in b.name and 'CARBON' in b.name]
    if len(ribs) != 2 or len(skins) != 2 or len(spars) != 3:
        raise RuntimeError('Unexpected v70 body inventory')

    records = []
    totals = {'skin_only': 0, 'spar_only': 0, 'skin_and_spar': 0, 'free': 0, 'end': 0}
    for rib in ribs:
        faces = []
        for idx, face in enumerate(rib.faces):
            plane = adsk.core.Plane.cast(face.geometry)
            if plane and abs(plane.normal.y) > 0.999999:
                totals['end'] += 1
                faces.append({'index': idx, 'class': 'end', 'area_mm2': face.area * 100.0})
                continue
            sd = [(s.name, app.measureManager.measureMinimumDistance(face, s).value * 10.0) for s in skins]
            pd = [(s.name, app.measureManager.measureMinimumDistance(face, s).value * 10.0) for s in spars]
            skin_name, skin_gap = min(sd, key=lambda x: x[1])
            spar_name, spar_gap = min(pd, key=lambda x: x[1])
            skin_hit = skin_gap <= CONTACT_EPS_MM
            spar_hit = spar_gap <= CONTACT_EPS_MM
            if skin_hit and spar_hit:
                cls = 'skin_and_spar'
            elif skin_hit:
                cls = 'skin_only'
            elif spar_hit:
                cls = 'spar_only'
            else:
                cls = 'free'
            totals[cls] += 1
            faces.append({
                'index': idx,
                'class': cls,
                'area_mm2': face.area * 100.0,
                'nearest_skin': skin_name,
                'skin_gap_mm': skin_gap,
                'nearest_spar': spar_name,
                'spar_gap_mm': spar_gap,
            })
        records.append({'rib': rib.name, 'face_count': len(rib.faces), 'faces': faces})

    audit = {
        'status': 'V72_RIB_FACE_CONTACT_CLASSIFICATION',
        'source': src,
        'source_revision': 'v71_offset_clearance',
        'contact_epsilon_mm': CONTACT_EPS_MM,
        'totals': totals,
        'ribs': records,
        'selective_clearance_geometry_created': False,
        'assembly_clearance_verified': False,
        'bondline_verified': False,
        'structural_capacity_verified': False,
        'print_release': False,
        'flight_release': False,
        'study_source_sha256': hashlib.sha256(open(__file__, 'rb').read()).hexdigest(),
    }
    os.makedirs(outdir, exist_ok=True)
    json.dump(audit, open(os.path.join(outdir, 'F14_v72_face_classification_audit.json'), 'w', encoding='utf-8'), indent=2)
    app.activeViewport.fit()
    app.activeViewport.saveAsImageFile(os.path.join(outdir, 'F14_v72_face_classification_review.png'), 1600, 1000)
    if prior:
        prior.activate()
    return audit
