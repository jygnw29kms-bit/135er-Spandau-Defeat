from pathlib import Path
import math, json, csv, subprocess
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parent
for d in ['stl','scad/generated_parts','docs']:
    (ROOT/d).mkdir(parents=True,exist_ok=True)
for f in (ROOT/'stl').glob('*.stl'): f.unlink()
for f in (ROOT/'scad/generated_parts').glob('*.scad'): f.unlink()

# F-14 scale master: 19.55 m real extended span -> 900 mm model span.
REAL_SPAN=19550.0
REAL_LENGTH=19100.0
SCALE=900.0/REAL_SPAN
L=REAL_LENGTH*SCALE
TARGET_SPAN=900.0
PIVOT_X=385.0
PIVOT_Y=68.5
SHELL=2.4
SPAR_D=6.4
BEARING_D=10.2

def mesh(v,f):
    return trimesh.Trimesh(np.asarray(v,float),np.asarray(f,int),process=True)

def save(m,name):
    try: m.fix_normals()
    except Exception: pass
    m.merge_vertices()
    sp=ROOT/'scad'/'generated_parts'/f'{name}.scad'
    out=ROOT/'stl'/f'{name}.stl'
    pts=[[round(float(c),6) for c in p] for p in m.vertices]
    faces=[[int(i) for i in x] for x in m.faces]
    sp.write_text('polyhedron(points='+repr(pts)+', faces='+repr(faces)+', convexity=30);\n')
    subprocess.run(['openscad','-q','-o',str(out),str(sp)],check=True)
    q=trimesh.load_mesh(out,force='mesh',process=True)
    q.merge_vertices()
    try:
        trimesh.repair.fix_winding(q); trimesh.repair.fix_normals(q,multibody=True)
    except TypeError:
        trimesh.repair.fix_normals(q)
    q.export(out)
    return q

def superellipse_ring(x,ay,az,zc,n=2.4,count=40):
    out=[]
    p=2.0/n
    for i in range(count):
        a=2*math.pi*i/count
        ca,sa=math.cos(a),math.sin(a)
        y=ay*math.copysign(abs(ca)**p,ca)
        z=zc+az*math.copysign(abs(sa)**p,sa)
        out.append([x,y,z])
    return out

def shell_loft(stations,x0,x1,wall=SHELL,count=40):
    xs=[x0]+[s[0] for s in stations if x0<s[0]<x1]+[x1]
    def interp(x):
        for a,b in zip(stations[:-1],stations[1:]):
            if a[0] <= x <= b[0]:
                t=(x-a[0])/(b[0]-a[0])
                return [x]+[a[k]*(1-t)+b[k]*t for k in range(1,5)]
        return stations[0] if x<=stations[0][0] else stations[-1]
    V=[]; F=[]; OR=[]; IR=[]
    for x in xs:
        _,ay,az,zc,n=interp(x)
        o=superellipse_ring(x,ay,az,zc,n,count)
        i=superellipse_ring(x,max(0.8,ay-wall),max(0.8,az-wall),zc,n,count)
        OR.append(list(range(len(V),len(V)+count))); V+=o
        IR.append(list(range(len(V),len(V)+count))); V+=i
    for k in range(len(xs)-1):
        for i in range(count):
            j=(i+1)%count
            F += [[OR[k][i],OR[k+1][i],OR[k+1][j]],[OR[k][i],OR[k+1][j],OR[k][j]]]
            F += [[IR[k][i],IR[k+1][j],IR[k+1][i]],[IR[k][i],IR[k][j],IR[k+1][j]]]
    for e in [0,len(xs)-1]:
        for i in range(count):
            j=(i+1)%count
            if e==0:
                F += [[OR[e][i],IR[e][j],IR[e][i]],[OR[e][i],OR[e][j],IR[e][j]]]
            else:
                F += [[OR[e][i],IR[e][i],IR[e][j]],[OR[e][i],IR[e][j],OR[e][j]]]
    return mesh(V,F)

def tube_shell(length,ay0,az0,ay1,az1,wall=2.4,n=40):
    stations=[(0,ay0,az0,0,3.2),(length,ay1,az1,0,3.2)]
    return shell_loft(stations,0,length,wall,n)

def extrude_poly(points,h):
    poly=Polygon(points)
    return trimesh.creation.extrude_polygon(poly,h,engine='earcut').apply_translation([0,0,-h/2])

def box(ext,center=(0,0,0)):
    m=trimesh.creation.box(extents=ext); m.apply_translation(center); return m

# F-14-derived master station envelope from supplied plan/3-view reconstruction.
body_st=[
 (0,2.5,2.5,0,2.0),(45,14,13,0,2.0),(90,23,21,1,2.2),(140,30,27,4,2.5),
 (200,37,31,7,2.8),(260,43,30,8,3.0),(320,55,27,7,3.8),(370,76,25,5,5.0),
 (420,88,23,3,6.0),(470,72,21,1,5.5),(520,52,20,0,4.5),(580,39,19,1,4.0),
 (650,32,18,3,3.5),(720,27,17,5,3.0),(790,20,14,6,2.7),(850,10,8,6,2.3),(L,2.5,2.5,6,2.0)
]
parts={}
cuts=[0,145,290,430,570,720,L]
for i,(a,b) in enumerate(zip(cuts[:-1],cuts[1:]),1):
    parts[f'fuse_{i:02d}']=shell_loft(body_st,a,b)

# Cockpit/canopy.
can=trimesh.creation.icosphere(subdivisions=3,radius=1)
can.apply_scale([96,29,18]); can.apply_translation([250,0,37])
parts['canopy']=can

# Fixed wing gloves / lifting-body shoulders.
glove_pts=[(-75,-28),(130,-42),(190,22),(105,105),(-30,76)]
for side,sgn in [('L',1),('R',-1)]:
    pts=[(x,sgn*y) for x,y in glove_pts]
    parts[f'wing_glove_{side}']=trimesh.creation.extrude_polygon(Polygon(pts),12,engine='earcut')

# Intakes + nacelles: F-14 twin-engine spacing retained as separate RC ducts.
for side,sgn in [('L',1),('R',-1)]:
    intake=tube_shell(150,36,24,32,29,2.4); intake.apply_translation([405,sgn*57,-18]); parts[f'intake_{side}']=intake
    mid=tube_shell(165,33,30,31,28,2.6); mid.apply_translation([555,sgn*57,-17]); parts[f'nacelle_mid_{side}']=mid
    rear=tube_shell(150,31,28,27,24,2.6); rear.apply_translation([720,sgn*57,-15]); parts[f'nacelle_rear_{side}']=rear

# Central beavertail / engine tunnel closure.
bt=trimesh.creation.extrude_polygon(Polygon([(690,-36),(L,-18),(L,18),(690,36)]),14,engine='earcut')
bt.apply_translation([0,0,-12]); parts['beavertail']=bt

# Tail surfaces.
taileron_pts=[(0,0),(145,14),(133,82),(35,72)]
for side,sgn in [('L',1),('R',-1)]:
    p=[(x,sgn*y) for x,y in taileron_pts]
    m=trimesh.creation.extrude_polygon(Polygon(p),7,engine='earcut')
    m.apply_translation([690,sgn*44,3]); parts[f'taileron_{side}']=m

v_pts=[(0,0),(118,10),(96,118),(55,145),(20,45)]
for side,sgn in [('L',1),('R',-1)]:
    v=trimesh.creation.extrude_polygon(Polygon(v_pts),7,engine='earcut')
    v.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0]))
    v.apply_translation([690,sgn*56,10]); parts[f'vstab_{side}']=v

# Wing planform at forward 20-degree condition. Pivot is local origin.
def xle(y): return -35 + (145/371)*(y+25)
def xte(y): return 175 - (10/371)*(y+25)
wing_ranges={'root':(-25,110),'mid':(105,230),'tip':(225,346)}

def save_wing(name,side,seg,y0,y1):
    pts=[(xle(y0),y0),(xte(y0),y0),(xte(y1),y1),(xle(y1),y1)]
    sp=ROOT/'scad'/'generated_parts'/f'{name}.scad'
    out=ROOT/'stl'/f'{name}.stl'
    ptxt='['+','.join(f'[{x:.5f},{y:.5f}]' for x,y in pts)+']'
    yA,yB=y0+8,y1-8
    xA=(xle(yA)+xte(yA))*0.54
    xB=(xle(yB)+xte(yB))*0.54
    rootcuts='' if seg!='root' else 'translate([0,0,-8]) cylinder(h=16,d=10.2,$fn=64); translate([34,28,-8]) cylinder(h=16,d=3.2,$fn=40);'
    code=f'''$fn=64;
module raw(){{linear_extrude(height=10,center=true) polygon(points={ptxt});}}
module spar(){{hull(){{translate([{xA:.4f},{yA:.4f},0]) sphere(d=6.4,$fn=36); translate([{xB:.4f},{yB:.4f},0]) sphere(d=6.4,$fn=36);}}}}
module wing(){{difference(){{raw(); spar(); {rootcuts}}}}}
'''
    code += 'mirror([0,1,0]) wing();\n' if side=='R' else 'wing();\n'
    sp.write_text(code); subprocess.run(['openscad','-q','-o',str(out),str(sp)],check=True)
    q=trimesh.load_mesh(out,force='mesh',process=True); q.merge_vertices(); q.export(out); return q

for side in ['L','R']:
    for seg,(a,b) in wing_ranges.items():
        parts[f'wing_{side}_{seg}']=None

# Stability-first wing box: one continuous structural body with large relief windows.
# Simple CSG avoids non-manifold intersections while retaining substantial PETG around pivots.
wb_scad=ROOT/'scad'/'generated_parts'/'wing_box.scad'
wb_out=ROOT/'stl'/'wing_box.stl'
wb_scad.write_text(r'''$fn=72;
H=26;
difference(){
  translate([-82,-98,-H/2]) cube([164,196,H]);

  // Four relief windows; edge rails and central cross remain continuous.
  translate([-64,-48,-20]) cube([48,30,40]);
  translate([16,-48,-20]) cube([48,30,40]);
  translate([-64,18,-20]) cube([48,30,40]);
  translate([16,18,-20]) cube([48,30,40]);

  // 5x10x4 bearing pockets around 5 mm steel pivot shafts.
  translate([0,-68.5,-20]) cylinder(h=40,d=10.2);
  translate([0,68.5,-20]) cylinder(h=40,d=10.2);
}
''')
subprocess.run(['openscad','-q','-o',str(wb_out),str(wb_scad)],check=True)
wb=trimesh.load_mesh(wb_out,force='mesh',process=True)
wb.merge_vertices()
try:
    trimesh.repair.fix_winding(wb)
    trimesh.repair.fix_normals(wb,multibody=True)
except TypeError:
    trimesh.repair.fix_normals(wb)
wb.export(wb_out)
parts['wing_box']=wb

# RC equipment carriers.
def frame(ox,oy,ix,iy,h):
    outer=[(-ox/2,-oy/2),(ox/2,-oy/2),(ox/2,oy/2),(-ox/2,oy/2)]
    inner=[(-ix/2,-iy/2),(ix/2,-iy/2),(ix/2,iy/2),(-ix/2,iy/2)]
    return trimesh.creation.extrude_polygon(Polygon(outer,[inner]),h,engine='earcut')
for s in ['L','R']:
    parts[f'sweep_servo_mount_{s}']=frame(56,38,31,16.5,10)
    parts[f'taileron_servo_mount_{s}']=frame(48,30,31,16.5,8)
    parts[f'esc_tray_{s}']=box([82,40,5])
parts['battery_tray']=box([205,58,5])
parts['receiver_tray']=box([62,44,5])
parts['bec_tray']=box([58,38,5])

# EDF rings: 56 mm housing fit target.
def annulus(ro,ri,h):
    return trimesh.creation.annulus(r_min=ri,r_max=ro,height=h,sections=72)
parts['edf_ring_L']=annulus(36,28,10); parts['edf_ring_R']=annulus(36,28,10)

# Save all non-wing non-wingbox parts.
for n,m in list(parts.items()):
    if n=='wing_box' or n.startswith('wing_'): continue
    parts[n]=save(m,n)
for side in ['L','R']:
    for seg,(a,b) in wing_ranges.items():
        n=f'wing_{side}_{seg}'; parts[n]=save_wing(n,side,seg,a,b)

# Build assembly references for forward and swept wing positions.
def assemble(sweep_deg,name):
    ms=[parts[f'fuse_{i:02d}'].copy() for i in range(1,7)]
    for n in ['canopy','beavertail','wing_box','battery_tray','receiver_tray','bec_tray',
              'intake_L','intake_R','nacelle_mid_L','nacelle_mid_R','nacelle_rear_L','nacelle_rear_R',
              'taileron_L','taileron_R','vstab_L','vstab_R','wing_glove_L','wing_glove_R']:
        q=parts[n].copy()
        if n=='wing_box': q.apply_translation([PIVOT_X,0,0])
        ms.append(q)
    for side,sgn in [('L',1),('R',-1)]:
        ang=math.radians(sweep_deg)*sgn
        T=trimesh.transformations.rotation_matrix(ang,[0,0,1])
        for seg in wing_ranges:
            q=parts[f'wing_{side}_{seg}'].copy(); q.apply_transform(T); q.apply_translation([PIVOT_X,sgn*PIVOT_Y,0]); ms.append(q)
    whole=trimesh.util.concatenate(ms)
    whole.export(ROOT/'stl'/f'{name}.stl')
    return whole

a20=assemble(20,'F14_R4_assembled_20deg')
a68=assemble(68,'F14_R4_assembled_68deg')

# Validation.
rows=[]
for f in sorted((ROOT/'stl').glob('*.stl')):
    if f.name.startswith('F14_R4_assembled_'): continue
    m=trimesh.load_mesh(f,force='mesh',process=True); m.merge_vertices(); e=m.extents
    rows.append({'file':f.name,'watertight':bool(m.is_watertight),'winding':bool(m.is_winding_consistent),
                 'x_mm':round(float(e[0]),2),'y_mm':round(float(e[1]),2),'z_mm':round(float(e[2]),2),
                 'fits_p2s':bool(sorted(e)[-2] <= 256.0 and sorted(e)[-1] <= 256.0),'faces':len(m.faces)})
with open(ROOT/'docs'/'mesh_validation.csv','w',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
summary={'scale':SCALE,'scale_denominator':1/SCALE,'target_span_mm':TARGET_SPAN,'target_length_mm':L,
         'printable_parts':len(rows),'watertight':sum(r['watertight'] for r in rows),
         'winding':sum(r['winding'] for r in rows),'fits_p2s':sum(r['fits_p2s'] for r in rows),
         'failures':[r for r in rows if not(r['watertight'] and r['winding'] and r['fits_p2s'])]}
(ROOT/'docs'/'mesh_validation.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
