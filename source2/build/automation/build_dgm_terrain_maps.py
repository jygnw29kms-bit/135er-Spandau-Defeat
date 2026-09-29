import json, statistics, sys
from pathlib import Path
sys.path.insert(0, r"E:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive\content\csgo_addons\spandau_defeat\tools")
import berlin_source2_autogen as b

ROOT=Path(r"C:\Users\Public\SpandauDefeatMapProduction\rebuild_20260928")
OUT=ROOT/"dgm_terrain_kv2"; OUT.mkdir(exist_ok=True)
samples=json.loads((ROOT/"dgm_samples.json").read_text(encoding="utf-8"))
locs=json.loads((ROOT/"location_tiles.json").read_text(encoding="utf-8"))
SCALE=8.0
MAT="materials/dev/reflectivity_30.vmat"

def make_terrain(rec, loc):
    raw=rec["pts"]; valid=[p for p in raw if p.get("z") is not None and float(p.get("z",0))>1.0]
    if len(valid)<4: raise ValueError("insufficient DGM")
    xs=sorted(set(float(p["x"]) for p in raw)); ys=sorted(set(float(p["y"]) for p in raw))
    zmap={(float(p["x"]),float(p["y"])):float(p["z"]) for p in valid}
    baseline=statistics.median(zmap.values())
    ox=float(loc["easting"]); oy=float(loc["northing"])
    # nearest valid fallback for rare no-data cells (e.g. Staaken)
    def z_at(x,y):
        if (x,y) in zmap:return zmap[(x,y)]
        return min(valid,key=lambda p:(float(p["x"])-x)**2+(float(p["y"])-y)**2)["z"]
    verts=[]; top={}
    for iy,y in enumerate(ys):
        for ix,x in enumerate(xs):
            top[(ix,iy)]=len(verts)
            z=float(z_at(x,y))
            verts.append(((x-ox)*SCALE,(y-oy)*SCALE,(z-baseline)*SCALE))
    faces=[]
    for iy in range(len(ys)-1):
        for ix in range(len(xs)-1):
            faces.append([top[(ix,iy)],top[(ix+1,iy)],top[(ix+1,iy+1)],top[(ix,iy+1)]])
    boundary=[]
    boundary += [(ix,0) for ix in range(len(xs))]
    boundary += [(len(xs)-1,iy) for iy in range(1,len(ys))]
    boundary += [(ix,len(ys)-1) for ix in range(len(xs)-2,-1,-1)]
    boundary += [(0,iy) for iy in range(len(ys)-2,0,-1)]
    bottom_z=(min(zmap.values())-baseline-5.0)*SCALE
    bottom=[]
    for ix,iy in boundary:
        bottom.append(len(verts))
        verts.append(((xs[ix]-ox)*SCALE,(ys[iy]-oy)*SCALE,bottom_z))
    for k in range(len(boundary)):
        k2=(k+1)%len(boundary)
        faces.append([top[boundary[k2]],top[boundary[k]],bottom[k],bottom[k2]])
    faces.append(list(reversed(bottom)))
    return verts,faces,baseline,len(valid),len(raw),min(zmap.values()),max(zmap.values())

report=[]
for mapid,rec in samples.items():
    try:
        verts,faces,baseline,nvalid,nraw,zmin,zmax=make_terrain(rec,locs[mapid])
        b.build_topology(len(verts),faces)
        mt=b.mesh_text(verts,faces,MAT,2,f"dgm1:{mapid}")
        text=b.vmap_document([mt],MAT)
        out=OUT/f"{mapid}_terrain.vmap"; out.write_text(text,encoding="utf-8",newline="\n")
        item={"id":mapid,"ok":True,"validSamples":nvalid,"sourceSamples":nraw,"baseline_m":baseline,"min_m":zmin,"max_m":zmax,"relief_m":zmax-zmin,"vertices":len(verts),"faces":len(faces),"file":str(out),"bytes":out.stat().st_size}
        report.append(item); print(f"OK {mapid}: {nvalid}/{nraw} relief={zmax-zmin:.2f}m verts={len(verts)} faces={len(faces)}")
    except Exception as e:
        report.append({"id":mapid,"ok":False,"error":str(e)}); print("FAIL",mapid,e)
(ROOT/"dgm_terrain_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("TOTAL",sum(1 for x in report if x.get("ok")),"/",len(report))

