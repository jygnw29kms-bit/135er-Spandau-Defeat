import json, math, os, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike")
SRC2=Path(r"C:\Users\Public\SpandauDefeatMapProduction\rebuild_20260928")
OUT=ROOT/"Saved"/"GIS"/"RathausSpandau_v1"; OUT.mkdir(parents=True,exist_ok=True)
MAPID="rathaus_spandau"; HALF=500.0; STEP=40.0
WFS="https://gdi.berlin.de/services/wfs/ua_gebaeudehoehen"
TYPE="ua_gebaeudehoehen:gebaeudehoehen"
OVERPASS="https://overpass.kumi.systems/api/interpreter"

locs=json.loads((SRC2/"location_tiles.json").read_text(encoding="utf-8"))
samples=json.loads((SRC2/"dgm_samples.json").read_text(encoding="utf-8"))
loc=locs[MAPID]; rec=samples[MAPID]
LAT=float(loc["lat"]); LON=float(loc["lon"]); OE=float(loc["easting"]); ON=float(loc["northing"])
valid=[p for p in rec["pts"] if p.get("z") is not None and float(p["z"])>1]
baseline=sorted(float(p["z"]) for p in valid)[len(valid)//2]
pts=[(float(p["x"]),float(p["y"]),float(p["z"])) for p in valid]

def nearest_z(e,n):
    p=min(pts,key=lambda q:(q[0]-e)**2+(q[1]-n)**2)
    return p[2]

def utm(lat,lon):
    a=6378137.; f=1/298.257223563; k=.9996
    e2=f*(2-f); ep=e2/(1-e2); ph=math.radians(lat); la=math.radians(lon); l0=math.radians(15.)
    nn=a/math.sqrt(1-e2*math.sin(ph)**2); t=math.tan(ph)**2; c=ep*math.cos(ph)**2; aa=math.cos(ph)*(la-l0)
    m=a*((1-e2/4-3*e2**2/64-5*e2**3/256)*ph-(3*e2/8+3*e2**2/32+45*e2**3/1024)*math.sin(2*ph)+(15*e2**2/256+45*e2**3/1024)*math.sin(4*ph)-(35*e2**3/3072)*math.sin(6*ph))
    return (k*nn*(aa+(1-t+c)*aa**3/6+(5-18*t+t*t+72*c-58*ep)*aa**5/120)+500000,
            k*(m+nn*math.tan(ph)*(aa*aa/2+(5-t+9*c+4*c*c)*aa**4/24+(61-58*t+t*t+600*c-330*ep)*aa**6/720)))
def write_obj(path,name,verts,faces):
    with open(path,"w",encoding="ascii") as f:
        f.write("o "+name+"\n")
        for x,y,z in verts: f.write(f"v {x:.3f} {y:.3f} {z:.3f}\n")
        for face in faces: f.write("f "+" ".join(str(i) for i in face)+"\n")

# terrain from already verified Berlin DGM samples used by the Source2 branch
grid=[]; faces=[]
count=int(round((HALF*2)/STEP))+1
for iy in range(count):
    n=ON-HALF+iy*STEP
    for ix in range(count):
        e=OE-HALF+ix*STEP
        z=nearest_z(e,n)
        grid.append(((e-OE)*100.,-(n-ON)*100.,(z-baseline)*100.))
for iy in range(count-1):
    for ix in range(count-1):
        a=iy*count+ix+1; b=a+1; c=a+count; d=c+1
        faces += [(a,c,b),(b,c,d)]
write_obj(OUT/"rathaus_terrain.obj","Rathaus_DGM",grid,faces)

def lname(tag): return tag.split("}")[-1]
def attr(feat,name):
    for x in feat.iter():
        if lname(x.tag).lower()==name.lower() and x.text: return x.text.strip()
    return ""
def ring(feat):
    rings=[]
    for x in feat.iter():
        if lname(x.tag)!="posList" or not x.text: continue
        vals=[float(v.replace(",",".")) for v in x.text.split()]
        dim=int(x.attrib.get("srsDimension","2")); dim=dim if dim in (2,3) else 2
        p=[(vals[i],vals[i+1]) for i in range(0,len(vals)-dim+1,dim)]
        if len(p)>=4: rings.append(p)
    if not rings:return None
    def ar(p):return abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))/2)
    p=max(rings,key=ar)
    if math.hypot(p[0][0]-p[-1][0],p[0][1]-p[-1][1])<.01:p=p[:-1]
    return p
def signed_area(p):
    return sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))/2
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def inside(p,a,b,c):
    c1=cross(a,b,p);c2=cross(b,c,p);c3=cross(c,a,p)
    return not (((c1<0)or(c2<0)or(c3<0)) and ((c1>0)or(c2>0)or(c3>0)))
def triangulate(poly):
    p=list(poly)
    if signed_area(p)<0:p.reverse()
    idx=list(range(len(p))); out=[]; guard=0
    while len(idx)>3 and guard<len(p)*len(p):
        guard+=1;found=False
        for k in range(len(idx)):
            i0,i1,i2=idx[k-1],idx[k],idx[(k+1)%len(idx)]
            a,b,c=p[i0],p[i1],p[i2]
            if cross(a,b,c)<=1e-9:continue
            if any(inside(p[j],a,b,c) for j in idx if j not in (i0,i1,i2)):continue
            out.append((i0,i1,i2));del idx[k];found=True;break
        if not found:break
    if len(idx)==3:out.append(tuple(idx))
    return p,out

bbox=f"{OE-HALF},{ON-HALF},{OE+HALF},{ON+HALF},EPSG:25833"
q={"SERVICE":"WFS","VERSION":"2.0.0","REQUEST":"GetFeature","TYPENAMES":TYPE,"SRSNAME":"EPSG:25833","BBOX":bbox,"COUNT":"10000"}
req=urllib.request.Request(WFS+"?"+urllib.parse.urlencode(q),headers={"User-Agent":"SpandauStrike-Rathaus/1.0"})
blob=urllib.request.urlopen(req,timeout=120).read(); (OUT/"buildings.gml").write_bytes(blob)
root=ET.fromstring(blob)
verts=[]; bfaces=[]; bc=0
for member in root.iter():
    if lname(member.tag) not in ("member","featureMember") or not list(member): continue
    feat=list(member)[0]; poly=ring(feat)
    if not poly:continue
    try:h=float(attr(feat,"hoehe").replace(",","."))
    except:h=10.
    if not 2<=h<=150:h=10.
    poly,tris=triangulate(poly)
    if not tris:tris=[(0,i,i+1) for i in range(1,len(poly)-1)]
    ce=sum(x for x,y in poly)/len(poly);cn=sum(y for x,y in poly)/len(poly)
    bottom=(nearest_z(ce,cn)-baseline)*100.;top=bottom+h*100.;base=len(verts)+1
    verts += [((e-OE)*100.,-(n-ON)*100.,bottom) for e,n in poly]
    verts += [((e-OE)*100.,-(n-ON)*100.,top) for e,n in poly]
    n=len(poly)
    for a,b,c in tris:bfaces.append((base+n+a,base+n+c,base+n+b))
    for i in range(n):
        j=(i+1)%n;b0=base+i;b1=base+j;t0=base+n+i;t1=base+n+j
        bfaces += [(b0,t1,b1),(b0,t0,t1)]
    bc+=1
write_obj(OUT/"rathaus_buildings.obj","Rathaus_ExactBuildings",verts,bfaces)
def road_width(t):
    return {"primary":10,"secondary":9,"tertiary":8,"residential":6,"living_street":5,"service":4,"cycleway":2.5,"footway":2,"path":1.8,"track":3}.get(t.get("highway",""),4.5)
def add_strip(v,f,a,b,width,zoff):
    e1,n1=a;e2,n2=b;dx=e2-e1;dy=n2-n1;ln=math.hypot(dx,dy)
    if ln<.3:return
    px=-dy/ln*width/2;py=dx/ln*width/2
    cs=[(e1+px,n1+py),(e1-px,n1-py),(e2-px,n2-py),(e2+px,n2+py)]
    base=len(v)+1
    for e,n in cs:v.append(((e-OE)*100.,-(n-ON)*100.,(nearest_z(e,n)-baseline)*100.+zoff))
    f += [(base,base+2,base+1),(base,base+3,base+2)]

dlat=HALF/111320.;dlon=HALF/(111320.*math.cos(math.radians(LAT)))
s,w,n,e=LAT-dlat,LON-dlon,LAT+dlat,LON+dlon
oq=f'''[out:json][timeout:60];(way["highway"]({s},{w},{n},{e});way["waterway"]({s},{w},{n},{e});way["natural"="water"]({s},{w},{n},{e}););out geom;'''
oreq=urllib.request.Request(OVERPASS,data=urllib.parse.urlencode({"data":oq}).encode(),headers={"User-Agent":"SpandauStrike-Rathaus/1.0"})
try:
    data=json.loads(urllib.request.urlopen(oreq,timeout=90).read().decode())
except Exception:
    data={"elements":[]}
rv=[];rf=[];wv=[];wf=[];rc=wc=0
for el in data.get("elements",[]):
    g=el.get("geometry")or[];t=el.get("tags",{})
    if len(g)<2:continue
    ps=[utm(p["lat"],p["lon"]) for p in g];isroad="highway" in t
    wid=road_width(t) if isroad else (8 if "waterway" in t else 16)
    for i in range(len(ps)-1):
        if isroad:add_strip(rv,rf,ps[i],ps[i+1],wid,4.);rc+=1
        else:add_strip(wv,wf,ps[i],ps[i+1],wid,2.);wc+=1
write_obj(OUT/"rathaus_roads.obj","Rathaus_Roads",rv,rf)
write_obj(OUT/"rathaus_water.obj","Rathaus_Water",wv,wf)
(OUT/"summary.json").write_text(json.dumps({"center":[LAT,LON],"utm":[OE,ON],"half_m":HALF,"baseline_m":baseline,"buildings":bc,"roads":rc,"water":wc,"terrain_vertices":len(grid)},indent=2),encoding="utf-8")
print((OUT/"summary.json").read_text())

