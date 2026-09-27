from pathlib import Path
import math, json, csv
import trimesh

ROOT=Path(__file__).resolve().parent
STL=ROOT/'stl'
OUT=ROOT/'p2s'
IND=OUT/'individual_3mf'
PLATES=OUT/'plates_3mf'
PREV=OUT/'plate_stl'
for d in (IND,PLATES,PREV): d.mkdir(parents=True,exist_ok=True)

BED=256.0
MARGIN=6.0
GAP=7.0

PROFILES={
 'SHELL': dict(layer=0.20,walls=4,top=4,bottom=4,infill=8,flow=7.0,fraction=0.24,desc='strength-first fuselage shell'),
 'WING': dict(layer=0.20,walls=4,top=5,bottom=5,infill=12,flow=6.7,fraction=0.28,desc='reinforced wing/control surface'),
 'STRUCT': dict(layer=0.16,walls=8,top=8,bottom=8,infill=55,flow=6.0,fraction=0.68,desc='maximum-strength wing box/pivot/servo structure'),
 'STRUCT_LIGHT': dict(layer=0.20,walls=5,top=6,bottom=6,infill=25,flow=6.5,fraction=0.40,desc='reinforced electronics mounts and joiners'),
 'DUCT': dict(layer=0.20,walls=4,top=4,bottom=4,infill=10,flow=6.8,fraction=0.28,desc='reinforced EDF intake/nacelle'),
 'COSMETIC': dict(layer=0.16,walls=3,top=4,bottom=4,infill=8,flow=6.5,fraction=0.22,desc='canopy/cosmetic'),
}

def profile_for(n):
    if n.startswith('fuse_'): return 'SHELL'
    if n.startswith(('wing_','taileron_','vstab_','glove_')): return 'WING'
    if n in {'wing_box','sweep_crank','pivot_doubler_L','pivot_doubler_R','pivot_spacer_L','pivot_spacer_R','sweep_servo_mount_L','sweep_servo_mount_R','sweep_servo_adapter_STD_L','sweep_servo_adapter_STD_R','taileron_servo_mount_L','taileron_servo_mount_R'}: return 'STRUCT'
    if n.startswith(('intake_','nacelle_','edf_ring_')): return 'DUCT'
    if n == 'canopy': return 'COSMETIC'
    return 'STRUCT_LIGHT'

def orient(name,m):
    m=m.copy()
    if name.startswith(('fuse_','intake_','nacelle_','joiner_')):
        m.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[0,1,0]))
    b=m.bounds
    m.apply_translation([0,0,-b[0][2]])
    return m

def export_3mf(meshes,path):
    s=trimesh.Scene()
    for n,m in meshes:
        s.add_geometry(m,geom_name=n,node_name=n)
    path.write_bytes(s.export(file_type='3mf'))

parts={}; meta={}
for f in sorted(STL.glob('*.stl')):
    if f.name.startswith('F14_R3_assembled_reference'): continue
    n=f.stem
    m=orient(n,trimesh.load_mesh(f,force='mesh',process=True))
    parts[n]=m
    p=profile_for(n); cfg=PROFILES[p]
    vol=abs(float(m.volume))
    mat=vol*cfg['fraction']
    t=max(0.25,mat/cfg['flow']/3600 + float(m.area)/1_000_000*0.55 + float(m.extents[2])/1000*0.35 + 0.18)
    meta[n]={'profile':p,'volume_cm3':round(vol/1000,1),'estimated_hours':round(t,2),'extents_mm':[round(float(x),1) for x in m.extents]}
    export_3mf([(n,m)],IND/f'{n}.3mf')

plate_plan=[
 ('01_Fuselage_Nose_Service',['fuse_01','joiner_160','joiner_800']),
 ('02_Fuselage_Cockpit',['fuse_02','canopy']),
 ('03_Fuselage_Center_A',['fuse_03','joiner_320']),
 ('04_Fuselage_Center_B',['fuse_04','battery_tray']),
 ('05_Fuselage_Rear',['fuse_05','joiner_640']),
 ('06_Fuselage_Tail',['fuse_06','joiner_480','electronics_hatch']),
 ('07_Wingbox_Structural',['wing_box']),
 ('08_Sweep_Hardware',['sweep_crank','pivot_doubler_L','pivot_doubler_R','pivot_spacer_L','pivot_spacer_R']),
 ('09_Sweep_Servo_Mounts',['sweep_servo_mount_L','sweep_servo_mount_R','sweep_servo_adapter_STD_L','sweep_servo_adapter_STD_R']),
 ('10_Left_Wing_Root',['wing_L_root']),
 ('11_Right_Wing_Root',['wing_R_root']),
 ('12_Left_Wing_Mid',['wing_L_mid']),
 ('13_Left_Wing_Tip',['wing_L_tip']),
 ('14_Right_Wing_Mid',['wing_R_mid']),
 ('15_Right_Wing_Tip',['wing_R_tip']),
 ('16_Left_Glove',['glove_L']),
 ('17_Right_Glove',['glove_R']),
 ('18_Tailerons',['taileron_L','taileron_R']),
 ('19_Taileron_Servo_Mounts',['taileron_servo_mount_L','taileron_servo_mount_R']),
 ('20_Left_VTail',['vstab_L']),
 ('21_Right_VTail',['vstab_R']),
 ('22_EDF_Intakes',['intake_L','intake_R','edf_ring_L','edf_ring_R']),
 ('23_EDF_Nacelles_Mid',['nacelle_L_mid','nacelle_R_mid']),
 ('24_EDF_Nacelles_Rear',['nacelle_L_rear','nacelle_R_rear']),
 ('25_Electronics_Trays',['esc_tray_L','esc_tray_R','receiver_tray','bec_tray']),
]

def pack(names):
    local_margin=2.5 if names == ['wing_box'] else MARGIN
    items=[]
    for n in names:
        base=parts[n].copy()
        choices=[]
        for deg in (0,90):
            q=base.copy()
            if deg: q.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[0,0,1]))
            e=q.extents
            if e[0] <= BED-2*local_margin and e[1] <= BED-2*local_margin:
                choices.append((e[0],e[1],q,deg))
        if not choices: raise RuntimeError(f'{n} does not fit')
        w,h,q,deg=min(choices,key=lambda x:(x[0],x[0]*x[1]))
        items.append((n,q,w,h,deg))
    items.sort(key=lambda x:max(x[2],x[3]),reverse=True)
    x=local_margin; y=local_margin; rowh=0; placed=[]
    for n,m,w,h,deg in items:
        if x+w > BED-local_margin:
            x=local_margin; y+=rowh+GAP; rowh=0
        if y+h > BED-local_margin:
            raise RuntimeError(f'plate overflow: {names}')
        b=m.bounds
        m.apply_translation([x-b[0][0],y-b[0][1],-b[0][2]])
        placed.append((n,m))
        x+=w+GAP; rowh=max(rowh,h)
    return placed

manifest=[]
for idx,(label,names) in enumerate(plate_plan,1):
    placed=pack(names)
    export_3mf(placed,PLATES/f'P2S_R3_{idx:02d}_{label}.3mf')
    trimesh.util.concatenate([m for _,m in placed]).export(PREV/f'P2S_R3_{idx:02d}_{label}.stl')
    est=sum(meta[n]['estimated_hours'] for n in names)
    if len(names)>1: est=max(0.3,est-0.08*(len(names)-1))
    manifest.append({'plate':idx,'name':label,'parts':names,'profiles':sorted(set(meta[n]['profile'] for n in names)),'estimated_print_hours':round(est,2)})

assembled=STL/'F14_R3_assembled_reference.stl'
if assembled.exists():
    am=trimesh.load_mesh(assembled,force='mesh',process=True)
    export_3mf([('F14_R3_assembled_reference',am)],IND/'F14_R3_assembled_reference.3mf')

(OUT/'profiles.json').write_text(json.dumps(PROFILES,indent=2))
(OUT/'individual_metadata.json').write_text(json.dumps(meta,indent=2))
(OUT/'plate_manifest.json').write_text(json.dumps(manifest,indent=2))
with open(OUT/'plate_manifest.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['Plate','Name','Parts','Profiles','Estimated hours'])
    for p in manifest: w.writerow([p['plate'],p['name'],'; '.join(p['parts']),'; '.join(p['profiles']),p['estimated_print_hours']])

(OUT/'README.md').write_text('''# F-14 R3 P2S package\n\n- 41 printable individual 3MF files plus assembled-reference 3MF\n- 22 component-aware P2S plate 3MF files\n- 22 combined plate STL previews/fallbacks\n- profile and plate manifests\n\nPrint-time values are planning estimates; use Bambu Studio/OrcaSlicer for exact time with the real P2S and PETG spool.\n''')
print(json.dumps({'individual_3mf':len(list(IND.glob('*.3mf'))),'plate_3mf':len(list(PLATES.glob('*.3mf'))),'estimated_hours':round(sum(p['estimated_print_hours'] for p in manifest),1)},indent=2))
