from pathlib import Path
import math,json
OBJ=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\DerivedData\DGM1_FalkenhagenerFeld\falkenhagener_buildings_obb.obj")
GRID=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\FalkenhagenerFeld_DGM10m_grid.json")
v=[]
for l in OBJ.open("r",encoding="ascii",errors="ignore"):
    if l.startswith("v "):
        _,x,y,z=l.split()[:4]; v.append((float(x),-float(y),float(z)))
polys=[[v[i+j][:2] for j in range(4)] for i in range(0,len(v),8)]
def segdist(px,py,a,b):
    x1,y1=a;x2,y2=b;dx=x2-x1;dy=y2-y1;den=dx*dx+dy*dy
    t=0 if den==0 else max(0,min(1,((px-x1)*dx+(py-y1)*dy)/den))
    qx=x1+t*dx;qy=y1+t*dy
    return math.hypot(px-qx,py-qy)
def inpoly(px,py,p):
    hit=False
    for i,(x1,y1) in enumerate(p):
        x2,y2=p[(i+1)%len(p)]
        if ((y1>py)!=(y2>py)) and px < (x2-x1)*(py-y1)/(y2-y1+1e-30)+x1: hit=not hit
    return hit
def pdist(px,py,p):
    if inpoly(px,py,p): return 0
    return min(segdist(px,py,p[i],p[(i+1)%len(p)]) for i in range(4))
def clearance(px,py):
    best=1e30
    for p in polys:
        # bbox cheap reject
        xs=[q[0] for q in p]; ys=[q[1] for q in p]
        dx=0 if min(xs)<=px<=max(xs) else min(abs(px-min(xs)),abs(px-max(xs)))
        dy=0 if min(ys)<=py<=max(ys) else min(abs(py-min(ys)),abs(py-max(ys)))
        lb=math.hypot(dx,dy)
        if lb>=best: continue
        d=pdist(px,py,p)
        if d<best: best=d
    return best
for side,(xmin,xmax) in {"W":(-85000,-55000),"E":(55000,85000)}.items():
    cand=[]
    for x in range(xmin,xmax+1,5000):
        for y in range(-70000,70001,5000):
            c=clearance(x,y)
            cand.append((c,x,y))
    cand.sort(reverse=True)
    print(side)
    for c,x,y in cand[:12]: print(round(c,1),x,y)
