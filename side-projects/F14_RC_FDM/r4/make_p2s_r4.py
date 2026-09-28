from pathlib import Path
import json,csv,math
import trimesh
ROOT=Path(__file__).resolve().parent
STL=ROOT/'stl'; OUT=ROOT/'p2s'
IND=OUT/'individual_3mf'; PL=OUT/'plates_3mf'; PS=OUT/'plate_stl'
for d in (IND,PL,PS):
    d.mkdir(parents=True,exist_ok=True)
    for f in d.glob('*'):
        if f.is_file(): f.unlink()

BED=256.0; M=6.0; GAP=7.0
PROFILES={
 'SHELL':{'layer':0.20,'walls':4,'infill':8},
 'WING':{'layer':0.20,'walls':4,'infill':12},
 'STRUCT':{'layer':0.16,'walls':8,'infill':55},
 'STRUCT_LIGHT':{'layer':0.20,'walls':5,'infill':25},
 'DUCT':{'layer':0.20,'walls':4,'infill':10},
 'COSMETIC':{'layer':0.16,'walls':3,'infill':8},
}
def profile(n):
    if n in {'wing_box'} or n.startswith(('sweep_servo_mount_','taileron_servo_mount_')): return 'STRUCT'
    if n.startswith(('battery_tray','esc_tray_','receiver_tray','bec_tray')): return 'STRUCT_LIGHT'
    if n.startswith(('wing_','taileron_','vstab_','wing_glove_')): return 'WING'
    if n.startswith(('intake_','nacelle_','edf_ring_')): return 'DUCT'
    if n=='canopy': return 'COSMETIC'
    return 'SHELL'
def scene_export(meshes,path):
    s=trimesh.Scene()
    for n,m in meshes:s.add_geometry(m,geom_name=n,node_name=n)
    path.write_bytes(s.export(file_type='3mf'))
parts={}
for f in sorted(STL.glob('*.stl')):
    if f.name.startswith('F14_R4_assembled_'): continue
    n=f.stem;m=trimesh.load_mesh(f,force='mesh',process=True)
    b=m.bounds;m.apply_translation([0,0,-b[0][2]])
    parts[n]=m;scene_export([(n,m)],IND/f'{n}.3mf')
for f in ['F14_R4_assembled_20deg.stl','F14_R4_assembled_68deg.stl']:
    p=STL/f
    if p.exists(): scene_export([(p.stem,trimesh.load_mesh(p,force='mesh'))],IND/f'{p.stem}.3mf')

plate_plan=[
 ('Fuselage_01',['fuse_01']),('Fuselage_02',['fuse_02','canopy']),('Fuselage_03',['fuse_03']),
 ('Fuselage_04',['fuse_04']),('Fuselage_05',['fuse_05']),('Fuselage_06',['fuse_06','beavertail']),
 ('Wingbox',['wing_box']),('Sweep_Servos',['sweep_servo_mount_L','sweep_servo_mount_R']),
 ('Wing_L_Root',['wing_L_root']),('Wing_R_Root',['wing_R_root']),('Wing_L_Mid',['wing_L_mid']),
 ('Wing_R_Mid',['wing_R_mid']),('Wing_L_Tip',['wing_L_tip']),('Wing_R_Tip',['wing_R_tip']),
 ('Glove_L',['wing_glove_L_front','wing_glove_L_rear']),('Glove_R',['wing_glove_R_front','wing_glove_R_rear']),('Tailerons',['taileron_L','taileron_R']),
 ('VTails',['vstab_L','vstab_R']),('Taileron_Servos',['taileron_servo_mount_L','taileron_servo_mount_R']),
 ('Intakes',['intake_L','intake_R','edf_ring_L','edf_ring_R']),
 ('Nacelle_Mid',['nacelle_mid_L','nacelle_mid_R']),('Nacelle_Rear',['nacelle_rear_L','nacelle_rear_R']),
 ('Battery',['battery_tray']),('ESCs',['esc_tray_L','esc_tray_R']),('RX_BEC',['receiver_tray','bec_tray'])
]
def pack(names):
    local=2.5 if names==['wing_box'] else M
    items=[]
    for n in names:
        base=parts[n]
        opts=[]
        for deg in (0,90):
            q=base.copy()
            if deg:q.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[0,0,1]))
            e=q.extents
            if e[0]<=BED-2*local and e[1]<=BED-2*local:opts.append((e[0],e[1],q))
        if not opts: raise RuntimeError(f'{n} does not fit P2S')
        items.append((n,*min(opts,key=lambda z:z[0]*z[1])))
    items.sort(key=lambda z:max(z[1],z[2]),reverse=True)
    x=y=local;rh=0;placed=[]
    for n,w,h,q in items:
        if x+w>BED-local:x=local;y+=rh+GAP;rh=0
        if y+h>BED-local:raise RuntimeError(f'plate overflow {names}')
        b=q.bounds;q.apply_translation([x-b[0][0],y-b[0][1],-b[0][2]])
        placed.append((n,q));x+=w+GAP;rh=max(rh,h)
    return placed
manifest=[]
for i,(label,names) in enumerate(plate_plan,1):
    p=pack(names)
    scene_export(p,PL/f'P2S_R4_{i:02d}_{label}.3mf')
    trimesh.util.concatenate([m for _,m in p]).export(PS/f'P2S_R4_{i:02d}_{label}.stl')
    manifest.append({'plate':i,'name':label,'parts':names,'profiles':sorted(set(profile(n) for n in names))})
(OUT/'profiles.json').write_text(json.dumps(PROFILES,indent=2))
(OUT/'plate_manifest.json').write_text(json.dumps(manifest,indent=2))
with open(OUT/'plate_manifest.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(['Plate','Name','Parts','Profiles'])
    for p in manifest:w.writerow([p['plate'],p['name'],';'.join(p['parts']),';'.join(p['profiles'])])
print(json.dumps({'parts_3mf':len(list(IND.glob('*.3mf'))),'plates':len(list(PL.glob('*.3mf')))},indent=2))
