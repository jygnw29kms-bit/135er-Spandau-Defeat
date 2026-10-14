"""v80: robust thin-slab BRep sampling of v79 key minimum cross-section."""
import adsk.core, adsk.fusion, json, os, hashlib

def run_review(app, build_source_wings, mm, outdir):
    prior=app.activeDocument; base=os.path.dirname(__file__)
    src=json.load(open(os.path.join(base,'F14_v80_section_inputs.json'),encoding='utf-8'))
    if hashlib.sha256(open(src['path'],'rb').read()).hexdigest()!=src['sha256']: raise RuntimeError('Source hash mismatch')
    if not app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(src['path'])): raise RuntimeError('Archive import failed')
    design=adsk.fusion.Design.cast(app.activeProduct); root=design.rootComponent
    temp=adsk.fusion.TemporaryBRepManager.get()
    keys=[b for b in root.bRepBodies if b.name=='CANDIDATE_CARBON_SWEEP_CLEARED_KEYS_v79']
    if len(keys)!=1: raise RuntimeError('Expected one v79 key body; got '+repr([b.name for b in root.bRepBodies]))
    key=keys[0]; bb=key.boundingBox
    xmin,xmax=bb.minPoint.x,bb.maxPoint.x; zmin,zmax=bb.minPoint.z,bb.maxPoint.z
    xmid=(xmin+xmax)/2.0; zmid=(zmin+zmax)/2.0
    xlen=(xmax-xmin)+0.2; zlen=(zmax-zmin)+0.2
    thickness_mm=0.10; thickness_cm=thickness_mm/10.0
    y0=float(src['y_start_mm']); y1=float(src['y_end_mm']); step=float(src['y_step_mm'])
    ys=[]; y=y0
    while y<=y1+1e-9:
        ys.append(round(y,6)); y+=step
    records=[]
    for y in ys:
        center=adsk.core.Point3D.create(xmid,mm(y),zmid)
        xd=adsk.core.Vector3D.create(1,0,0); yd=adsk.core.Vector3D.create(0,1,0)
        obb=adsk.core.OrientedBoundingBox3D.create(center,xd,yd,xlen,thickness_cm,zlen)
        slab=temp.createBox(obb)
        sample=temp.copy(key)
        ok=temp.booleanOperation(sample,slab,adsk.fusion.BooleanTypes.IntersectionBooleanType)
        if not ok:
            records.append({'y_mm':y,'intersection_ok':False,'area_mm2':0.0})
            continue
        body=root.bRepBodies.add(sample)
        props=body.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy)
        vol=props.volume
        sbb=body.boundingBox
        cx=props.centerOfMass.x*10.0 if props.centerOfMass else None
        cz=props.centerOfMass.z*10.0 if props.centerOfMass else None
        area=vol*1000.0/thickness_mm
        records.append({'y_mm':y,'intersection_ok':True,'slice_volume_cm3':vol,'area_mm2':area,'centroid_x_mm':cx,'centroid_z_mm':cz,'bbox_x_mm':[sbb.minPoint.x*10.0,sbb.maxPoint.x*10.0],'bbox_z_mm':[sbb.minPoint.z*10.0,sbb.maxPoint.z*10.0]})
        body.deleteMe()
    valid=[r for r in records if r.get('intersection_ok') and r.get('area_mm2',0)>0]
    if not valid: raise RuntimeError('No valid v80 slab intersections')
    minrec=min(valid,key=lambda r:r['area_mm2']); maxrec=max(valid,key=lambda r:r['area_mm2'])
    avg=sum(r['area_mm2'] for r in valid)/len(valid)
    audit={'status':'V80_KEY_MINIMUM_SECTION_SLAB_SCREEN','source':src,'slice_thickness_mm':thickness_mm,'sections':records,'minimum_section':minrec,'maximum_section':maxrec,'average_area_mm2':avg,'valid_section_count':len(valid),'requested_section_count':len(records),'all_sections_present':len(valid)==len(records),'minimum_key_section_verified_geometrically':len(valid)==len(records),'material_allowable_verified':False,'torsion_load_verified':False,'fit_coupon_verified':False,'structural_capacity_verified':False,'print_release':False,'flight_release':False,'study_source_sha256':hashlib.sha256(open(__file__,'rb').read()).hexdigest()}
    os.makedirs(outdir,exist_ok=True)
    json.dump(audit,open(os.path.join(outdir,'F14_v80_key_section_audit.json'),'w',encoding='utf-8'),indent=2)
    app.activeViewport.fit(); app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v80_key_section_review.png'),1600,1000)
    if prior: prior.activate()
    return audit