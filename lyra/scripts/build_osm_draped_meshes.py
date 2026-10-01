import os, json, math, urllib.parse, urllib.request
import numpy as np
from pyproj import Transformer
from shapely.geometry import Polygon, Point
from shapely.ops import triangulate

CENTER_LAT=52.5524034
CENTER_LON=13.1668941
CENTER_E=375716.66
CENTER_N=5824059.63
HALF=900.0
GRID=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\FalkenhagenerFeld_DGM10m_grid.json"
OUTDIR=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS"
OVERPASS="https://overpass-api.de/api/interpreter"

with open(GRID,"r",encoding="utf-8") as f: G=json.load(f)
H=np.array(G["heights"],dtype=np.float32)
BASE=float(G["base_height"]); XMIN=float(G["xmin"]); YMIN=float(G["ymin"]); STEP=float(G["step"])
tr=Transformer.from_crs(4326,25833,always_xy=True)

def terrain_z_m(e,n):
    fx=(e-XMIN)/STEP; fy=(n-YMIN)/STEP
    ix=max(0,min(H.shape[1]-2,int(math.floor(fx))))
    iy=max(0,min(H.shape[0]-2,int(math.floor(fy))))
    tx=max(0.0,min(1.0,fx-ix)); ty=max(0.0,min(1.0,fy-iy))
    z0=H[iy,ix]*(1-tx)+H[iy,ix+1]*tx
    z1=H[iy+1,ix]*(1-tx)+H[iy+1,ix+1]*tx
    return float(z0*(1-ty)+z1*ty-BASE)
def fetch():
    dlat=HALF/111320.0
    dlon=HALF/(111320.0*math.cos(math.radians(CENTER_LAT)))
    s,w,n,e=CENTER_LAT-dlat,CENTER_LON-dlon,CENTER_LAT+dlat,CENTER_LON+dlon
    q=f'''[out:json][timeout:60];(
way["highway"]({s},{w},{n},{e});
way["waterway"]({s},{w},{n},{e});
way["natural"="water"]({s},{w},{n},{e});
);out geom;'''
    req=urllib.request.Request(OVERPASS,data=urllib.parse.urlencode({"data":q}).encode(),
                               headers={"User-Agent":"SpandauStrike-GIS/1.0"})
    with urllib.request.urlopen(req,timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))

def road_width(tags):
    return {"motorway":12,"trunk":11,"primary":10,"secondary":9,"tertiary":8,
            "residential":6,"living_street":5,"service":4,"cycleway":2.5,
            "footway":2,"path":1.8,"track":3}.get(tags.get("highway",""),4.5)

def local(lat,lon,offset=0.0):
    e,n=tr.transform(lon,lat)
    return (e-CENTER_E, -(n-CENTER_N), terrain_z_m(e,n)+offset)
class Obj:
    def __init__(self): self.v=[]; self.uv=[]; self.f=[]
    def quad(self,p0,p1,width):
        x0,y0,z0=p0; x1,y1,z1=p1
        dx=x1-x0; dy=y1-y0; L=math.hypot(dx,dy)
        if L<0.3 or L>500: return
        px=-dy/L*width/2; py=dx/L*width/2
        pts=[(x0+px,y0+py,z0),(x0-px,y0-py,z0),(x1+px,y1+py,z1),(x1-px,y1-py,z1)]
        base=len(self.v)+1
        self.v.extend(pts); self.uv.extend([(0,0),(0,1),(1,0),(1,1)])
        self.f.extend([(base,base+1,base+2),(base+2,base+1,base+3)])
    def tri(self,p0,p1,p2):
        base=len(self.v)+1
        self.v.extend([p0,p1,p2]); self.uv.extend([(0,0),(1,0),(0,1)])
        self.f.append((base,base+1,base+2))
    def write(self,path):
        with open(path,"w",encoding="ascii",newline="\n") as f:
            f.write("# Spandau Strike GIS draped mesh\n")
            for x,y,z in self.v: f.write(f"v {x*100:.3f} {y*100:.3f} {z*100:.3f}\n")
            for u,v in self.uv: f.write(f"vt {u:.6f} {v:.6f}\n")
            for a,b,c in self.f: f.write(f"f {a}/{a} {b}/{b} {c}/{c}\n")
        print(path,"verts",len(self.v),"tris",len(self.f),"bytes",os.path.getsize(path))
data=fetch()
with open(os.path.join(OUTDIR,"FalkenhagenerFeld_OSM.json"),"w",encoding="utf-8") as f:
    json.dump(data,f,separators=(",",":"))
roads=Obj(); water=Obj()
roadways=waterways=waterpolys=0
for el in data.get("elements",[]):
    geom=el.get("geometry") or []; tags=el.get("tags",{})
    if len(geom)<2: continue
    if "highway" in tags:
        pts=[local(p["lat"],p["lon"],0.06) for p in geom]
        w=road_width(tags)
        for i in range(len(pts)-1): roads.quad(pts[i],pts[i+1],w)
        roadways+=1
    elif tags.get("natural")=="water" and len(geom)>=4:
        ring=[]
        for p in geom:
            e,n=tr.transform(p["lon"],p["lat"]); ring.append((e,n))
        try:
            poly=Polygon(ring)
            if not poly.is_valid: poly=poly.buffer(0)
            for t in triangulate(poly):
                if not poly.covers(t.representative_point()): continue
                cs=list(t.exterior.coords)[:3]
                ps=[(e-CENTER_E,-(n-CENTER_N),terrain_z_m(e,n)+0.08) for e,n in cs]
                water.tri(ps[0],ps[1],ps[2])
            waterpolys+=1
        except Exception: pass
    else:
        pts=[local(p["lat"],p["lon"],0.08) for p in geom]
        for i in range(len(pts)-1): water.quad(pts[i],pts[i+1],8.0)
        waterways+=1
roads.write(os.path.join(OUTDIR,"FalkenhagenerFeld_Roads_DGM.obj"))
water.write(os.path.join(OUTDIR,"FalkenhagenerFeld_Water_DGM.obj"))
print("OSM",len(data.get("elements",[])),"roadways",roadways,"waterways",waterways,"waterpolys",waterpolys)
