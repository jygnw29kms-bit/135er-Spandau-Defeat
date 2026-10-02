import json, math, sys, xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike")
SRC=Path(r"C:\Users\Public\SpandauDefeatMapProduction\rebuild_20260928")
MAPID=sys.argv[1]
HALF=float(sys.argv[2]) if len(sys.argv)>2 else 550.0
OUT=ROOT/"Saved"/"GIS"/f"{MAPID}_v1"
locs=json.loads((SRC/"location_tiles.json").read_text(encoding="utf-8"))
loc=locs[MAPID]; OE=float(loc["easting"]); ON=float(loc["northing"])

def lname(t): return t.split("}")[-1]
def rings():
    root=ET.parse(OUT/"buildings.gml").getroot(); result=[]
    for x in root.iter():
        if lname(x.tag)!="posList" or not x.text: continue
        vals=[float(v.replace(",",".")) for v in x.text.split()]
        dim=int(x.attrib.get("srsDimension","2")); dim=dim if dim in (2,3) else 2
        pts=[((vals[i]-OE)*100.0,-(vals[i+1]-ON)*100.0) for i in range(0,len(vals)-dim+1,dim)]
        if len(pts)>=4:
            xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
            result.append((min(xs)-1500,max(xs)+1500,min(ys)-1500,max(ys)+1500))
    return result
def road_centers():
    verts=[]
    for line in (OUT/f"{MAPID}_roads.obj").read_text().splitlines():
        if line.startswith("v "):
            _,x,y,z=line.split()[:4]; verts.append((float(x),float(y),float(z)))
    return [(sum(q[j][0] for j in range(4))/4,
             sum(q[j][1] for j in range(4))/4,
             sum(q[j][2] for j in range(4))/4)
            for q in [verts[i:i+4] for i in range(0,len(verts)-3,4)]]

boxes=rings()
cands=[]
for p in road_centers():
    x,y,z=p
    if abs(x)>HALF*100*0.92 or abs(y)>HALF*100*0.92: continue
    if any(a<=x<=b and c<=y<=d for a,b,c,d in boxes): continue
    cands.append((x,y,z+160.0))

def spread(pool,n):
    if not pool:return []
    pool=sorted(pool,key=lambda p:(p[0],p[1]))
    chosen=[pool[len(pool)//2]]
    while len(chosen)<n:
        rest=[p for p in pool if p not in chosen]
        if not rest:break
        chosen.append(max(rest,key=lambda p:min((p[0]-q[0])**2+(p[1]-q[1])**2 for q in chosen)))
    return chosen
west=spread([p for p in cands if p[0] < -HALF*100*0.28],4)
east=spread([p for p in cands if p[0] > HALF*100*0.28],4)
if len(west)<4 or len(east)<4:
    ordered=sorted(cands,key=lambda p:p[0])
    west=spread(ordered[:max(8,len(ordered)//3)],4)
    east=spread(ordered[-max(8,len(ordered)//3):],4)

def objective(targetx):
    pool=[p for p in cands if abs(p[0]-targetx)<HALF*100*0.22 and abs(p[1])<HALF*100*0.75]
    if not pool: pool=cands
    return min(pool,key=lambda p:(p[0]-targetx)**2+(p[1]*0.35)**2)

cps=[objective(-HALF*100*0.32),objective(0),objective(HALF*100*0.32)]
data={"map":MAPID,"candidates":len(cands),"west":west,"east":east,"control_points":cps}
(OUT/"gameplay_points.json").write_text(json.dumps(data,indent=2),encoding="utf-8")
print(json.dumps(data,indent=2))
