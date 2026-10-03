import math
from pathlib import Path
terrain=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\RathausSpandau_v1\rathaus_terrain.obj")
verts=[]
for line in terrain.open(errors="ignore"):
    if line.startswith("v "):
        _,x,y,z=line.split()[:4];verts.append((float(x),float(y),float(z)))
cx,cy=10085.0,289.6
a=math.radians(-37.4256)
def world(lx_m,ly_m):
    x=lx_m*100;y=ly_m*100
    ca,sa=math.cos(a),math.sin(a)
    return cx+x*ca-y*sa,cy+x*sa+y*ca
def nz(x,y):
    return min(verts,key=lambda v:(v[0]-x)**2+(v[1]-y)**2)[2]
locals=[(-24,-72),(-8,-76),(8,-76),(24,-72),(-24,72),(-8,76),(8,76),(24,72),(0,-95),(0,95)]
for q in locals:
    x,y=world(*q);z=nz(x,y)
    print(q,"=>",round(x,1),round(y,1),round(z+180,1),"ground",round(z,1))
