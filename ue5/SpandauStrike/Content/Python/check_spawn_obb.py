from pathlib import Path
OBJ=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\DerivedData\DGM1_FalkenhagenerFeld\falkenhagener_buildings_obb.obj")
spawns=[(-76000,-24000),(-76000,-8000),(-74000,5000),(-76000,24000),(76000,-24000),(76000,-6000),(76000,8000),(76000,24000)]
v=[]
for line in OBJ.open("r",encoding="ascii",errors="ignore"):
    if line.startswith("v "):
        _,x,y,z=line.split()[:4]; v.append((float(x),float(y),float(z)))
def inside(px,py,poly,margin=120):
    # polygon test + distance-to-edges margin
    hit=False
    for i,(x1,y1) in enumerate(poly):
        x2,y2=poly[(i+1)%len(poly)]
        if ((y1>py)!=(y2>py)) and px < (x2-x1)*(py-y1)/(y2-y1+1e-30)+x1: hit=not hit
        dx=x2-x1; dy=y2-y1; den=dx*dx+dy*dy
        t=0 if den==0 else max(0,min(1,((px-x1)*dx+(py-y1)*dy)/den))
        qx=x1+t*dx; qy=y1+t*dy
        if (px-qx)**2+(py-qy)**2 <= margin*margin: return True
    return hit
for si,(x,y) in enumerate(spawns,1):
    hits=[]
    for bi in range(len(v)//8):
        poly=[v[bi*8+j][:2] for j in range(4)]
        if inside(x,y,poly): hits.append(bi)
    print(si,(x,y),"hits",hits[:10],"count",len(hits))
