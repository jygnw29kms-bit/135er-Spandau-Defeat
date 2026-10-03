import json, math, collections
from pathlib import Path
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
from shapely.ops import triangulate

ROOT=Path(r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final")
PLAN=json.load(open(ROOT/"Rathaus_roofplan_real.json"))
RAW=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\RathausSpandau_v1\Berlin3D_2025_3779_58218_-002\Mesh_3779_58218_-002.obj")
SHELL=ROOT/"Rathaus_Shell_REAL.obj"
ROOF=ROOT/"Rathaus_Roof_REAL.obj"
ox,oy=PLAN["origin_utm"]; ground=31.0

outer=PLAN["contours"][0]["poly"]
holes=[x["poly"] for x in PLAN["contours"] if x["parent"]==0]
poly=orient(Polygon(outer,holes),sign=1.0)
if not poly.is_valid:
    poly=poly.buffer(0)

# clean shell: walls from actual contour, open courtyards, top plate at measured eave
z0=0.0; z1=16.2
verts=[]; faces=[]
def addv(x,y,z):
    verts.append((float(x),float(y),float(z))); return len(verts)
def ringwalls(coords,flip=False):
    pts=list(coords)
    if pts[0]==pts[-1]:pts=pts[:-1]
    n=len(pts); bot=[];top=[]
    for x,y in pts:bot.append(addv(x,y,z0));top.append(addv(x,y,z1))
    for i in range(n):
        j=(i+1)%n
        if flip:faces.append((bot[i],top[i],top[j],bot[j]))
        else:faces.append((bot[i],bot[j],top[j],top[i]))
ringwalls(poly.exterior.coords,False)
for r in poly.interiors:ringwalls(r.coords,True)

# triangulated top plate respecting courtyards
for t in triangulate(poly):
    rp=t.representative_point()
    if not poly.covers(rp):continue
    coords=list(t.exterior.coords)[:3]
    ids=[addv(x,y,z1) for x,y in coords]
    faces.append(tuple(ids))
with open(SHELL,"w",encoding="utf-8") as f:
    f.write("o Rathaus_Shell_REAL\n")
    for x,y,z in verts:f.write(f"v {x:.4f} {y:.4f} {z:.4f}\n")
    for fc in faces:f.write("f "+" ".join(map(str,fc))+"\n")

# parse actual OBJ and extract largest upward roof component near tower
V=[];F=[]
for line in open(RAW,encoding="utf-8",errors="ignore"):
    if line.startswith("v "):V.append(tuple(map(float,line.split()[1:4])))
    elif line.startswith("f "):
        ids=[]
        for token in line.split()[1:]:
            s=token.split("/")[0]
            if s:ids.append(int(s)-1)
        if len(ids)>=3:
            for i in range(1,len(ids)-1):F.append((ids[0],ids[i],ids[i+1]))
sel=[]
for a,b,c in F:
    p0,p1,p2=V[a],V[b],V[c]
    cx=(p0[0]+p1[0]+p2[0])/3; cy=(p0[1]+p1[1]+p2[1])/3; cz=(p0[2]+p1[2]+p2[2])/3
    if not (ox-45<cx<ox+80 and oy-80<cy<oy+70 and cz>44):continue
    ux,uy,uz=p1[0]-p0[0],p1[1]-p0[1],p1[2]-p0[2]
    vx,vy,vz=p2[0]-p0[0],p2[1]-p0[1],p2[2]-p0[2]
    nx=uy*vz-uz*vy;ny=uz*vx-ux*vz;nz=ux*vy-uy*vx
    nn=(nx*nx+ny*ny+nz*nz)**.5
    if nn and abs(nz)/nn>.42:sel.append((a,b,c))
par=list(range(len(sel)));rank=[0]*len(sel)
def find(x):
    while par[x]!=x:
        par[x]=par[par[x]];x=par[x]
    return x
def union(a,b):
    a,b=find(a),find(b)
    if a==b:return
    if rank[a]<rank[b]:a,b=b,a
    par[b]=a
    if rank[a]==rank[b]:rank[a]+=1
vm={}
for i,tri in enumerate(sel):
    for vi in tri:
        if vi in vm:union(i,vm[vi])
        else:vm[vi]=i
comps=collections.defaultdict(list)
for i in range(len(sel)):comps[find(i)].append(i)
cand=[]
for ids in comps.values():
    if len(ids)<20:continue
    vs=set()
    for i in ids:vs.update(sel[i])
    xs=[V[v][0]-ox for v in vs];ys=[V[v][1]-oy for v in vs]
    mx=(min(xs)+max(xs))/2;my=(min(ys)+max(ys))/2
    if math.hypot(mx,my)<45:cand.append((len(ids),ids))
cand.sort(reverse=True,key=lambda q:q[0])
ids=cand[0][1]
used=sorted(set(v for i in ids for v in sel[i]))
remap={v:i+1 for i,v in enumerate(used)}
with open(ROOF,"w",encoding="utf-8") as f:
    f.write("o Rathaus_Roof_REAL\n")
    for vi in used:
        x,y,z=V[vi];f.write(f"v {x-ox:.4f} {y-oy:.4f} {z-ground:.4f}\n")
    for i in ids:
        a,b,c=sel[i];f.write(f"f {remap[a]} {remap[b]} {remap[c]}\n")
print("SHELL",SHELL,"verts",len(verts),"faces",len(faces))
print("ROOF",ROOF,"verts",len(used),"faces",len(ids))
