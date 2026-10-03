from pathlib import Path
from collections import defaultdict
import math
bld=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\RathausSpandau_v1\rathaus_buildings_no_landmark.obj")
ter=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\RathausSpandau_v1\rathaus_terrain.obj")
verts=[];faces=[]
for line in bld.open(errors="ignore"):
    if line.startswith("v "):
        _,x,y,z=line.split()[:4];verts.append((float(x),float(y),float(z)))
    elif line.startswith("f "):faces.append([int(t.split("/")[0])-1 for t in line.split()[1:]])
parent=list(range(len(verts)))
def find(x):
    while parent[x]!=x:
        parent[x]=parent[parent[x]];x=parent[x]
    return x
def union(a,b):
    a,b=find(a),find(b)
    if a!=b:parent[b]=a
for f in faces:
    for v in f[1:]:union(f[0],v)
comp=defaultdict(list)
for i in range(len(verts)):comp[find(i)].append(i)
boxes=[]
for ids in comp.values():
    xs=[verts[i][0] for i in ids];ys=[verts[i][1] for i in ids]
    boxes.append((min(xs),max(xs),min(ys),max(ys)))
tv=[]
for line in ter.open(errors="ignore"):
    if line.startswith("v "):
        _,x,y,z=line.split()[:4];tv.append((float(x),float(y),float(z)))
def blocked(x,y,margin=500):
    return any(a-margin<=x<=b+margin and c-margin<=y<=d+margin for a,b,c,d in boxes)
def ground(x,y):return min(tv,key=lambda v:(v[0]-x)**2+(v[1]-y)**2)[2]
cx,cy=10033,-232
cands=[]
for r in range(10000,22001,1500):
    for deg in range(0,360,10):
        x=cx+r*math.cos(math.radians(deg));y=cy+r*math.sin(math.radians(deg))
        if -48000<x<48000 and -48000<y<48000 and not blocked(x,y,650):
            cands.append((r,deg,x,y,ground(x,y)+190))
# prefer southern/front half first
cands.sort(key=lambda q:(0 if q[3]<cy else 1,q[0],abs(q[1]-270)))
for q in cands[:40]:print("CAND",q)
