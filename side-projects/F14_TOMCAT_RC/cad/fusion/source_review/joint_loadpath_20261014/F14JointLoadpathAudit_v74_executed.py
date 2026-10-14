"""v74: verify the continuous carbon load path through the v73 printed segment joint."""
import adsk.core, adsk.fusion, json, os, hashlib

def run_review(app, build_source_wings, mm, outdir):
    prior=app.activeDocument
    base=os.path.dirname(__file__)
    src=json.load(open(os.path.join(base,'F14_v74_section_inputs.json'),encoding='utf-8-sig'))
    if hashlib.sha256(open(src['path'],'rb').read()).hexdigest()!=src['sha256']:
        raise RuntimeError('Source hash mismatch')
    imported=app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(src['path']))
    if not imported: raise RuntimeError('Archive import failed')
    design=adsk.fusion.Design.cast(app.activeProduct)
    root=design.rootComponent
    bodies=[root.bRepBodies.item(i) for i in range(root.bRepBodies.count)]
    spars=[b for b in bodies if '_R_' in b.name and 'CARBON' in b.name]
    ribs=[b for b in bodies if b.name in ('CANDIDATE_RIB_ZERO_CLEARANCE_-3','CANDIDATE_RIB_ZERO_CLEARANCE_3')]
    skins=[b for b in bodies if 'HOLLOW_WING_R_' in b.name]
    if len(spars)!=3 or len(ribs)!=2 or len(skins)!=2:
        raise RuntimeError('Unexpected v73 body inventory: '+repr([(b.name,b.isSolid) for b in bodies]))
    jy=float(src['joint_y_mm']); req=float(src['required_continuity_each_side_mm'])
    carbon=[]
    for b in spars:
        bb=b.boundingBox
        ymin=bb.minPoint.y*10.0; ymax=bb.maxPoint.y*10.0
        carbon.append({'body':b.name,'y_min_mm':ymin,'y_max_mm':ymax,'span_mm':ymax-ymin,
            'crosses_joint':ymin<jy<ymax,
            'covers_required_joint_zone':ymin <= jy-req and ymax >= jy+req})
    rib_end=[]
    for b in ribs:
        ys=[]
        for f in b.faces:
            pl=adsk.core.Plane.cast(f.geometry)
            if pl and abs(pl.normal.y)>0.999999:
                ys.append({'y_mm':f.pointOnFace.y*10.0,'area_mm2':f.area*100.0})
        rib_end.append({'rib':b.name,'end_faces':ys,'total_end_face_area_mm2':sum(x['area_mm2'] for x in ys)})
    audit={
      'status':'V74_CONTINUOUS_CARBON_JOINT_GATE',
      'source':src,
      'carbon_bodies':carbon,
      'rib_end_faces':rib_end,
      'carbon_continuity_pass':all(x['crosses_joint'] and x['covers_required_joint_zone'] for x in carbon),
      'required_continuity_each_side_mm':req,
      'printed_joint_primary_bending_member':False,
      'joint_geometry_designed':False,
      'torsion_transfer_verified':False,
      'structural_capacity_verified':False,
      'print_release':False,
      'flight_release':False,
      'study_source_sha256':hashlib.sha256(open(__file__,'rb').read()).hexdigest()
    }
    os.makedirs(outdir,exist_ok=True)
    json.dump(audit,open(os.path.join(outdir,'F14_v74_continuous_carbon_joint_audit.json'),'w',encoding='utf-8'),indent=2)
    app.activeViewport.fit(); app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v74_continuous_carbon_joint_review.png'),1600,1000)
    if prior: prior.activate()
    return audit
