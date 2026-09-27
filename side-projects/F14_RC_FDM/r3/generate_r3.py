from pathlib import Path
import math, json, csv, subprocess
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point
from shapely.ops import triangulate

ROOT=Path(__file__).resolve().parent
(ROOT/'stl').mkdir(exist_ok=True)
(ROOT/'plates').mkdir(exist_ok=True)
(ROOT/'docs').mkdir(exist_ok=True)

L=955.0
SPAN=977.5
PIVOT_X=426.0
PIVOT_Y=87.0
WALL=2.0

def mesh_from_vertices_faces(v,f,name=None):
    m=trimesh.Trimesh(np.array(v,float),np.array(f,int),process=True)
    if name:
        m.metadata['name']=name
    return m

def extrude_shapely(poly:Polygon,height:float,z0=-0.5):
    tris=[t for t in triangulate(poly) if poly.covers(t.representative_point())]
    verts=[]; faces=[]; idx={}
    def vid(x,y,z):
        k=(round(x,6),round(y,6),round(z,6))
        if k not in idx:
            idx[k]=len(verts); verts.append([x,y,z])
        return idx[k]
    zb=z0*height; zt=zb+height
    for t in tris:
        coords=list(t.exterior.coords)[:3]
        ib=[vid(x,y,zb) for x,y in coords]
        it=[vid(x,y,zt) for x,y in coords]
        faces.append([ib[0],ib[2],ib[1]])
        faces.append([it[0],it[1],it[2]])
    rings=[poly.exterior]+list(poly.interiors)
    for ri,ring in enumerate(rings):
        cs=list(ring.coords)
        for a,b in zip(cs[:-1],cs[1:]):
            a0=vid(a[0],a[1],zb); b0=vid(b[0],b[1],zb)
            a1=vid(a[0],a[1],zt); b1=vid(b[0],b[1],zt)
            if ri==0:
                faces += [[a0,b0,b1],[a0,b1,a1]]
            else:
                faces += [[a0,b1,b0],[a0,a1,b1]]
    return mesh_from_vertices_faces(verts,faces)

def box(size,center=(0,0,0)):
    m=trimesh.creation.box(extents=size)
    m.apply_translation(center)
    return m

def concat(*ms):
    return trimesh.util.concatenate([m for m in ms if m is not None])

def save(m,name):
    try:
        m.fix_normals()
    except Exception:
        pass
    m.merge_vertices()
    scaddir=ROOT/'scad'/'generated_parts'
    scaddir.mkdir(parents=True,exist_ok=True)
    sp=scaddir/f'{name}.scad'
    p=ROOT/'stl'/f'{name}.stl'
    pts=[[round(float(c),6) for c in v] for v in m.vertices]
    faces=[[int(i) for i in f] for f in m.faces]
    sp.write_text('polyhedron(points='+repr(pts)+', faces='+repr(faces)+', convexity=20);\n')
    subprocess.run(['openscad','-q','-o',str(p),str(sp)],check=True)
    # Normalize the OpenSCAD export so validation is deterministic across
    # trimesh versions. This does not change dimensions or topology intent.
    repaired=trimesh.load_mesh(p,force='mesh',process=True)
    repaired.merge_vertices()
    try:
        trimesh.repair.fix_winding(repaired)
        trimesh.repair.fix_normals(repaired,multibody=True)
    except TypeError:
        trimesh.repair.fix_normals(repaired)
    repaired.export(p)
    return p

stations=[
 (0,3,3,0),(42,17,18,0),(90,28,27,1),(145,34,34,4),(205,40,40,8),
 (270,48,43,10),(335,57,42,8),(405,63,39,6),(485,62,33,4),(570,57,28,3),
 (660,50,25,4),(745,42,24,8),(830,31,21,10),(910,18,15,7),(955,5,5,4)
]

def interp_station(x):
    if x<=stations[0][0]:
        return stations[0]
    if x>=stations[-1][0]:
        return stations[-1]
    for a,b in zip(stations[:-1],stations[1:]):
        if a[0]<=x<=b[0]:
            t=(x-a[0])/(b[0]-a[0])
            return (x,a[1]*(1-t)+b[1]*t,a[2]*(1-t)+b[2]*t,a[3]*(1-t)+b[3]*t)

def shell_segment(x0,x1,nang=28):
    xs=[x0]+[s[0] for s in stations if x0<s[0]<x1]+[x1]
    rings=[]
    for x in xs:
        _,ry,rz,zc=interp_station(x)
        outer=[]; inner=[]
        for i in range(nang):
            a=2*math.pi*i/nang
            outer.append([x,ry*math.cos(a),zc+rz*math.sin(a)])
            inner.append([x,max(0.8,ry-WALL)*math.cos(a),zc+max(0.8,rz-WALL)*math.sin(a)])
        rings.append((outer,inner))
    verts=[]; faces=[]; O=[]; I=[]
    for out,inn in rings:
        O.append(list(range(len(verts),len(verts)+nang))); verts.extend(out)
        I.append(list(range(len(verts),len(verts)+nang))); verts.extend(inn)
    for k in range(len(xs)-1):
        for i in range(nang):
            j=(i+1)%nang
            faces += [[O[k][i],O[k+1][i],O[k+1][j]],[O[k][i],O[k+1][j],O[k][j]]]
            faces += [[I[k][i],I[k+1][j],I[k+1][i]],[I[k][i],I[k][j],I[k+1][j]]]
    for end in [0,len(xs)-1]:
        for i in range(nang):
            j=(i+1)%nang
            if end==0:
                faces += [[O[end][i],I[end][j],I[end][i]],[O[end][i],O[end][j],I[end][j]]]
            else:
                faces += [[O[end][i],I[end][i],I[end][j]],[O[end][i],I[end][j],O[end][j]]]
    return mesh_from_vertices_faces(verts,faces)

parts={}
for i,(a,b) in enumerate([(0,160),(160,320),(320,480),(480,640),(640,800),(800,955)],1):
    parts[f'fuse_{i:02d}']=shell_segment(a,b)

canopy=trimesh.creation.icosphere(subdivisions=2,radius=1.0)
canopy.apply_scale([100,42,25])
canopy.apply_translation([285,0,38])
parts['canopy']=canopy

for x,ry,rz in [(160,35,35),(320,55,42),(480,62,34),(640,52,26),(800,35,22)]:
    n=48; verts=[]; faces=[]
    for xx in [-4,4]:
        for rad_y,rad_z in [(ry,rz),(ry-4,rz-4)]:
            for k in range(n):
                a=2*math.pi*k/n
                verts.append([xx,rad_y*math.cos(a),rad_z*math.sin(a)])
    for k in range(n):
        j=(k+1)%n
        faces += [[k,2*n+k,2*n+j],[k,2*n+j,j]]
        faces += [[n+k,n+j,3*n+j],[n+k,3*n+j,3*n+k]]
        faces += [[k,j,n+j],[k,n+j,n+k]]
        faces += [[2*n+k,3*n+k,3*n+j],[2*n+k,3*n+j,2*n+j]]
    parts[f'joiner_{x}']=mesh_from_vertices_faces(verts,faces)

def wing_outer_poly(y0,y1):
    def le(y): return 0.55*y
    def te(y): return 220+0.15*y
    return Polygon([(le(y0),y0),(te(y0),y0),(te(y1),y1),(le(y1),y1)])

for side in ['L','R']:
    for seg,(y0,y1) in {'root':(0,145),'mid':(140,275),'tip':(270,395)}.items():
        m=extrude_shapely(wing_outer_poly(y0,y1),10,z0=-0.5)
        if side=='R':
            m.apply_scale([1,-1,1])
        parts[f'wing_{side}_{seg}']=m

def annulus(rout,rin,h):
    outer=[(rout*math.cos(a),rout*math.sin(a)) for a in np.linspace(0,2*math.pi,65)[:-1]]
    inner=[(rin*math.cos(a),rin*math.sin(a)) for a in np.linspace(0,2*math.pi,49)[:-1]]
    return extrude_shapely(Polygon(outer,[inner]),h,z0=-0.5)

parts['pivot_doubler_L']=annulus(31,2.6,10)
parts['pivot_doubler_R']=annulus(31,2.6,10)
parts['pivot_spacer_L']=annulus(18,2.725,4)
parts['pivot_spacer_R']=annulus(18,2.725,4)

base=box([160,220,18])
towers=[]
for y in [-87,87]:
    t=annulus(33,2.6,26)
    t.apply_translation([0,y,0])
    towers.append(t)
parts['wing_box']=concat(base,*towers)

outer=Point(0,0).buffer(18,resolution=24).union(Polygon([(-65,-6),(65,-6),(65,6),(-65,6)]))
parts['sweep_crank']=extrude_shapely(outer,8,z0=-0.5)

for side in ['L','R']:
    poly=Polygon([(0,-18),(160,-35),(228,36),(135,103),(22,72)])
    m=extrude_shapely(poly,15,z0=-0.5)
    if side=='R':
        m.apply_scale([1,-1,1])
    parts[f'glove_{side}']=m

def tube_shell(length,ry0,rz0,ry1,rz1,n=32):
    xs=[-length/2,length/2]; verts=[]; faces=[]
    radii=[(ry0,rz0),(ry1,rz1)]; O=[]; I=[]
    for x,(ry,rz) in zip(xs,radii):
        out=[]; inn=[]
        for k in range(n):
            a=2*math.pi*k/n
            out.append([x,ry*math.cos(a),rz*math.sin(a)])
            inn.append([x,(ry-2)*math.cos(a),(rz-2)*math.sin(a)])
        O.append(list(range(len(verts),len(verts)+n))); verts+=out
        I.append(list(range(len(verts),len(verts)+n))); verts+=inn
    for k in range(n):
        j=(k+1)%n
        faces += [[O[0][k],O[1][k],O[1][j]],[O[0][k],O[1][j],O[0][j]]]
        faces += [[I[0][k],I[1][j],I[1][k]],[I[0][k],I[0][j],I[1][j]]]
        faces += [[O[0][k],O[0][j],I[0][j]],[O[0][k],I[0][j],I[0][k]]]
        faces += [[O[1][k],I[1][k],I[1][j]],[O[1][k],I[1][j],O[1][j]]]
    return mesh_from_vertices_faces(verts,faces)

for side in ['L','R']:
    parts[f'intake_{side}']=tube_shell(145,38,27,36,31)
    parts[f'nacelle_{side}_mid']=tube_shell(175,38,32,36,31)
    parts[f'nacelle_{side}_rear']=tube_shell(175,36,31,31,27)
parts['edf_ring_L']=annulus(32,25.4,8)
parts['edf_ring_R']=annulus(32,25.4,8)

for side in ['L','R']:
    m=extrude_shapely(Polygon([(0,0),(170,20),(151,104),(32,83)]),7,z0=-0.5)
    if side=='R':
        m.apply_scale([1,-1,1])
    parts[f'taileron_{side}']=m
    v=extrude_shapely(Polygon([(0,0),(148,15),(119,164),(73,184),(34,58)]),7,z0=-0.5)
    if side=='R':
        v.apply_scale([1,-1,1])
    parts[f'vstab_{side}']=v

parts['battery_tray']=box([220,64,6])
parts['electronics_hatch']=box([170,82,3.2])
parts['sweep_servo_mount']=box([58,34,18])

for name,m in parts.items():
    save(m,name)

assembled=[parts[f'fuse_{i:02d}'].copy() for i in range(1,7)]
assembled.append(parts['canopy'].copy())
m=parts['wing_box'].copy()
m.apply_translation([PIVOT_X,0,0])
assembled.append(m)

for side,sy in [('L',1),('R',-1)]:
    ang=-math.radians(20)*sy
    T=trimesh.transformations.rotation_matrix(ang,[0,0,1])
    for seg in ['root','mid','tip']:
        w=parts[f'wing_{side}_{seg}'].copy()
        w.apply_transform(T)
        w.apply_translation([PIVOT_X,sy*PIVOT_Y,0])
        assembled.append(w)
    g=parts[f'glove_{side}'].copy()
    g.apply_translation([382,sy*75,4])
    assembled.append(g)

for side,sy in [('L',1),('R',-1)]:
    for key,x in [(f'intake_{side}',535),(f'nacelle_{side}_mid',690),(f'nacelle_{side}_rear',855)]:
        q=parts[key].copy()
        q.apply_translation([x,sy*73,-22])
        assembled.append(q)

for side,sy in [('L',1),('R',-1)]:
    t=parts[f'taileron_{side}'].copy()
    t.apply_translation([755,sy*72,2])
    assembled.append(t)
    v=parts[f'vstab_{side}'].copy()
    v.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0]))
    v.apply_translation([772,sy*54,12])
    assembled.append(v)

assembly=concat(*assembled)
save(assembly,'F14_R3_assembled_reference')

rows=[]
for f in sorted((ROOT/'stl').glob('*.stl')):
    m=trimesh.load_mesh(f,force='mesh')
    m.merge_vertices()
    ext=m.extents
    rows.append({
      'file':f.name,
      'watertight':bool(m.is_watertight),
      'winding':bool(m.is_winding_consistent),
      'x_mm':round(float(ext[0]),2),
      'y_mm':round(float(ext[1]),2),
      'z_mm':round(float(ext[2]),2),
      'fits_256_any_orientation':bool(sorted(ext)[-2] <= 256 and sorted(ext)[-1] <= 256) if f.name!='F14_R3_assembled_reference.stl' else False,
      'faces':len(m.faces)
    })

with open(ROOT/'docs'/'mesh_validation.csv','w',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

summary={
 'count':len(rows),
 'individual_count':len(rows)-1,
 'watertight_individual':sum(r['watertight'] for r in rows if not r['file'].startswith('F14_R3_assembled')),
 'winding_individual':sum(r['winding'] for r in rows if not r['file'].startswith('F14_R3_assembled')),
 'fits256_individual':sum(r['fits_256_any_orientation'] for r in rows if not r['file'].startswith('F14_R3_assembled')),
 'failures':[r for r in rows if not r['file'].startswith('F14_R3_assembled') and not (r['watertight'] and r['winding'] and r['fits_256_any_orientation'])]
}
(ROOT/'docs'/'mesh_validation.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))

plate_groups=[
 ['fuse_01','joiner_160','joiner_320'],
 ['fuse_02','canopy'],
 ['fuse_03','electronics_hatch'],
 ['fuse_04','battery_tray'],
 ['fuse_05'],
 ['fuse_06'],
 ['wing_box','sweep_crank','pivot_spacer_L','pivot_spacer_R','pivot_doubler_L','pivot_doubler_R','sweep_servo_mount'],
 ['wing_L_root','wing_R_root'],
 ['wing_L_mid','wing_R_mid'],
 ['wing_L_tip','wing_R_tip'],
 ['glove_L','glove_R'],
 ['intake_L','intake_R'],
 ['nacelle_L_mid','nacelle_R_mid'],
 ['nacelle_L_rear','nacelle_R_rear','edf_ring_L','edf_ring_R'],
 ['taileron_L','taileron_R'],
 ['vstab_L','vstab_R'],
 ['joiner_480','joiner_640','joiner_800']
]

manifest=[]
for pi,names in enumerate(plate_groups,1):
    placed=[]; x=10; y=10; rowh=0
    for n in names:
        m=parts[n].copy()
        b=m.bounds
        ext=b[1]-b[0]
        if ext[1]>ext[0]:
            m.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[0,0,1]))
            b=m.bounds
            ext=b[1]-b[0]
        if x+ext[0]>246:
            x=10
            y+=rowh+8
            rowh=0
        m.apply_translation([x-b[0][0],y-b[0][1],-b[0][2]])
        placed.append(m)
        x+=ext[0]+8
        rowh=max(rowh,ext[1])
    plate=concat(*placed)
    plate.export(ROOT/'plates'/f'plate_{pi:02d}.stl')
    manifest.append({'plate':pi,'parts':names})

(ROOT/'plates'/'manifest.json').write_text(json.dumps(manifest,indent=2))
