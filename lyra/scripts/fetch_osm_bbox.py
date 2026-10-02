import json,math,sys,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
MAPID=sys.argv[1]
HALF=float(sys.argv[2]) if len(sys.argv)>2 else 550.0
ROOT=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike")
SRC=Path(r"C:\Users\Public\SpandauDefeatMapProduction\rebuild_20260928")
OUT=ROOT/"Saved"/"GIS"/(MAPID+"_v1")
locs=json.loads((SRC/"location_tiles.json").read_text(encoding="utf-8"))
samples=json.loads((SRC/"dgm_samples.json").read_text(encoding="utf-8"))
loc=locs[MAPID]; rec=samples[MAPID]
LAT=float(loc["lat"]);LON=float(loc["lon"]);OE=float(loc["easting"]);ON=float(loc["northing"])
valid=[p for p in rec["pts"] if p.get("z") is not None and float(p["z"])>1]
baseline=sorted(float(p["z"]) for p in valid)[len(valid)//2]
dgm=[(float(p["x"]),float(p["y"]),float(p["z"])) for p in valid]
def nz(e,n):return min(dgm,key=lambda q:(q[0]-e)**2+(q[1]-n)**2)[2]
def utm(lat,lon):
    a=6378137.;f=1/298.257223563;k=.9996;e2=f*(2-f);ep=e2/(1-e2)
    ph=math.radians(lat);la=math.radians(lon);l0=math.radians(15.)
    nn=a/math.sqrt(1-e2*math.sin(ph)**2);t=math.tan(ph)**2;c=ep*math.cos(ph)**2;aa=math.cos(ph)*(la-l0)
    m=a*((1-e2/4-3*e2**2/64-5*e2**3/256)*ph-(3*e2/8+3*e2**2/32+45*e2**3/1024)*math.sin(2*ph)+(15*e2**2/256+45*e2**3/1024)*math.sin(4*ph)-(35*e2**3/3072)*math.sin(6*ph))
    return k*nn*(aa+(1-t+c)*aa**3/6)+500000,k*(m+nn*math.tan(ph)*(aa*aa/2))
def write_obj(path,name,v,f):
    with open(path,"w",encoding="ascii") as h:
        h.write("o "+name+"\n")
        for x,y,z in v:h.write(f"v {x:.3f} {y:.3f} {z:.3f}\n")
        for face in f:h.write("f "+" ".join(str(i) for i in face)+"\n")
def strip(v,f,a,b,w,z):
    e1,n1=a;e2,n2=b;dx=e2-e1;dy=n2-n1;ln=math.hypot(dx,dy)
    if ln<.3:return False
    px=-dy/ln*w/2;py=dx/ln*w/2;cs=[(e1+px,n1+py),(e1-px,n1-py),(e2-px,n2-py),(e2+px,n2+py)]
    base=len(v)+1
    for e,n in cs:v.append(((e-OE)*100.,-(n-ON)*100.,(nz(e,n)-baseline)*100.+z))
    f += [(base,base+2,base+1),(base,base+3,base+2)]
    return True
dlat=HALF/111320.0
dlon=HALF/(111320.0*math.cos(math.radians(LAT)))
south,west,north,east=LAT-dlat,LON-dlon,LAT+dlat,LON+dlon
url=f"https://api.openstreetmap.org/api/0.6/map?bbox={west},{south},{east},{north}"
req=urllib.request.Request(url,headers={"User-Agent":"SpandauStrike-GIS/1.0"})
blob=urllib.request.urlopen(req,timeout=120).read()
(OUT/"osm_bbox.osm").write_bytes(blob)
root=ET.fromstring(blob)
nodes={}
for n in root.findall("node"):
    nodes[n.attrib["id"]]=(float(n.attrib["lat"]),float(n.attrib["lon"]))
rv=[];rf=[];wv=[];wf=[];rc=wc=0
widths={"primary":10,"secondary":9,"tertiary":8,"residential":6,"living_street":5,"service":4,"cycleway":2.5,"footway":2,"path":1.8,"track":3}
for way in root.findall("way"):
    tags={t.attrib.get("k",""):t.attrib.get("v","") for t in way.findall("tag")}
    road="highway" in tags
    water=("waterway" in tags) or tags.get("natural")=="water"
    if not road and not water:continue
    ll=[nodes[x.attrib["ref"]] for x in way.findall("nd") if x.attrib.get("ref") in nodes]
    if len(ll)<2:continue
    pts=[utm(a,b) for a,b in ll]
    wid=widths.get(tags.get("highway",""),4.5) if road else (8 if "waterway" in tags else 16)
    for i in range(len(pts)-1):
        if road:
            if strip(rv,rf,pts[i],pts[i+1],wid,4):rc+=1
        else:
            if strip(wv,wf,pts[i],pts[i+1],wid,2):wc+=1
write_obj(OUT/(MAPID+"_roads.obj"),MAPID+"_Roads",rv,rf)
write_obj(OUT/(MAPID+"_water.obj"),MAPID+"_Water",wv,wf)
print(json.dumps({"roads":rc,"water":wc,"ways":len(root.findall("way")),"nodes":len(nodes)}))
