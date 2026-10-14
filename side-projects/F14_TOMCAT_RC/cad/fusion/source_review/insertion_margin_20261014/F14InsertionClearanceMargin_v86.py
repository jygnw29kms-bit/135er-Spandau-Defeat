"""v86: continuous insertion-clearance margin scan at 0.1 mm steps."""
import adsk.core, adsk.fusion, json, os, hashlib

def run_review(app, build_source_wings, mm, outdir):
    prior=app.activeDocument; base=os.path.dirname(__file__)
    src=json.load(open(os.path.join(base,'F14_v86_section_inputs.json'),encoding='utf-8'))
    if hashlib.sha256(open(src['path'],'rb').read()).hexdigest()!=src['sha256']: raise RuntimeError('Source hash mismatch')
    if not app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(src['path'])): raise RuntimeError('Archive import failed')
    design=adsk.fusion.Design.cast(app.activeProduct); root=design.rootComponent; temp=adsk.fusion.TemporaryBRepManager.get()
    names=['CANDIDATE_OUTER_INSERT_SWEEP_CLEARED_v83','CANDIDATE_RIB_ZERO_CLEARANCE_-3','CANDIDATE_HOLLOW_WING_R_INNER_NO_JOINTS','CANDIDATE_CARBON_R_UPPER_CAP_NOT_STRENGTH_VERIFIED','CANDIDATE_CARBON_R_LOWER_CAP_NOT_STRENGTH_VERIFIED','CANDIDATE_CARBON_R_WEB_NOT_STRENGTH_VERIFIED']
    bodies={}
    for i in range(root.bRepBodies.count):
        b=root.bRepBodies.item(i)
        if b.name in names: bodies[b.name]=b
    miss=[n for n in names if n not in bodies]
    if miss: raise RuntimeError('Missing bodies '+repr(miss))
    insert=bodies[names[0]]; inner=bodies[names[1]]; skin=bodies[names[2]]; spars=[bodies[n] for n in names[3:]]
    step=float(src['step_mm']); dist=float(src['insertion_mm']); n=int(round(dist/step)); rows=[]
    for k in range(n,-1,-1):
        dy=k*step; moved=temp.copy(insert); m=adsk.core.Matrix3D.create(); m.translation=adsk.core.Vector3D.create(0,mm(dy),0); temp.transform(moved,m)
        scratch=root.bRepBodies.add(moved); scratch.name='V86_SCRATCH'
        skin_gap=app.measureManager.measureMinimumDistance(scratch,skin).value*10.0
        rib_gap=app.measureManager.measureMinimumDistance(scratch,inner).value*10.0
        cg=[]
        for s in spars: cg.append({'body':s.name,'gap_mm':app.measureManager.measureMinimumDistance(scratch,s).value*10.0})
        rows.append({'outboard_translation_mm':dy,'skin_gap_mm':skin_gap,'inner_rib_gap_mm':rib_gap,'carbon_gaps':cg,'minimum_carbon_gap_mm':min(x['gap_mm'] for x in cg)})
        scratch.deleteMe()
    minc=min(r['minimum_carbon_gap_mm'] for r in rows); mins=min(r['skin_gap_mm'] for r in rows); minr=min(r['inner_rib_gap_mm'] for r in rows)
    audit={'status':'V86_INSERTION_CLEARANCE_MARGIN_SCAN','source':src,'samples':rows,'minimum_carbon_gap_mm':minc,'minimum_skin_gap_mm':mins,'minimum_inner_rib_gap_mm':minr,'carbon_clearance_target_pass':minc>=float(src['carbon_target_clearance_mm'])*0.95,'skin_clearance_target_pass':mins>=float(src['skin_target_clearance_mm'])*0.95,'manufacturing_clearance_candidate_pass':minc>=float(src['carbon_target_clearance_mm'])*0.95 and mins>=float(src['skin_target_clearance_mm'])*0.95,'fit_coupon_verified':False,'structural_capacity_verified':False,'print_release':False,'flight_release':False,'study_source_sha256':hashlib.sha256(open(__file__,'rb').read()).hexdigest()}
    os.makedirs(outdir,exist_ok=True); json.dump(audit,open(os.path.join(outdir,'F14_v86_insertion_clearance_margin_audit.json'),'w',encoding='utf-8'),indent=2)
    app.activeViewport.fit(); app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v86_insertion_clearance_margin_review.png'),1600,1000)
    if prior: prior.activate()
    return audit