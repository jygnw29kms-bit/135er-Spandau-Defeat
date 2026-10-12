import urllib.request, urllib.parse, json, os, glob, math

LAT=52.5524034
LON=13.1668941
HALF=900.0
STEP=10
SRC=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\DerivedData\DGM1_FalkenhagenerFeld"
OUTDIR=os.path.join(SRC,"OSM_Combined")
OVERPASS="https://overpass-api.de/api/interpreter"
os.makedirs(OUTDIR,exist_ok=True)

def utm(lat,lon):
    a=6378137.0; f=1/298.257223563; k=.9996
    e2=f*(2-f); ep=e2/(1-e2); p=math.radians(lat); l=math.radians(lon); l0=math.radians(15)
    n=a/math.sqrt(1-e2*math.sin(p)**2); t=math.tan(p)**2; c=ep*math.cos(p)**2; aa=math.cos(p)*(l-l0)
    m=a*((1-e2/4-3*e2**2/64-5*e2**3/256)*p-(3*e2/8+3*e2**2/32+45*e2**3/1024)*math.sin(2*p)+(15*e2**2/256+45*e2**3/1024)*math.sin(4*p)-(35*e2**3/3072)*math.sin(6*p))
    return (k*n*(aa+(1-t+c)*aa**3/6+(5-18*t+c)*aa**3*0 + (5-18*t+t*t+72*c-58*ep)*aa**5/120)+500000,
            k*(m+n*math.tan(p)*(aa*aa/2+(5-t+9*c+4*c*c)*aa**4/24+(61-58*t+t*t+600*c-330*ep)*aa**6/720)))
OE,ON=utm(LAT,LON)
# Correct the easting term explicitly (kept separate for transparent parity with UE scripts).
def utm(lat,lon):
    a=6378137.0; f=1/298.257223563; k=.9996
    e2=f*(2-f); ep=e2/(1-e2); p=math.radians(lat); l=math.radians(lon); l0=math.radians(15.0)
    n=a/math.sqrt(1-e2*math.sin(p)**2); t=math.tan(p)**2; c=ep*math.cos(p)**2; aa=math.cos(p)*(l-l0)
    m=a*((1-e2/4-3*e2**2/64-5*e2**3/256)*p-(3*e2/8+3*e2**2/32+45*e2**3/1024)*math.sin(2*p)+(15*e2**2/256+45*e2**3/1024)*math.sin(4*p)-(35*e2**3/3072)*math.sin(6*p))
    return (k*n*(aa+(1-t+c)*aa**3/6+(5-18*t+t*t+72*c-58*ep)*aa**5/120)+500000,
            k*(m+n*math.tan(p)*(aa*aa/2+(5-t+9*c+4*c*c)*aa**4/24+(61-58*t+t*t+600*c-330*ep)*aa**6/720)))
OE,ON=utm(LAT,LON)

def load_dgm():
    pts={}
    emin,emax=OE-HALF-30,OE+HALF+30
    nmin,nmax=ON-HALF-30,ON+HALF+30
    for fn in glob.glob(os.path.join(SRC,"**","*.xyz"),recursive=True):
        with open(fn,"r",encoding="utf-8",errors="ignore") as f:
            for line in f:
                try: e,n,z=map(float,line.split()[:3])
                except: continue
                if not (emin<=e<=emax and nmin<=n<=nmax): continue
                ei=int(round(e-0.5)); ni=int(round(n-0.5))
                if ei%STEP or ni%STEP: continue
                pts[(ei,ni)]=z
    if not pts: raise RuntimeError("no DGM samples")
    ck=min(pts,key=lambda q:(q[0]-OE)**2+(q[1]-ON)**2)
    return pts,pts[ck]
def sample_z(grid,e,n,zref):
    ex=int(round((e-0.5)/STEP)*STEP)
    ny=int(round((n-0.5)/STEP)*STEP)
    best=None; bd=1e30
    for dx in (-STEP,0,STEP):
        for dy in (-STEP,0,STEP):
            q=(ex+dx,ny+dy); v=grid.get(q)
            if v is None: continue
            d=(q[0]+0.5-e)**2+(q[1]+0.5-n)**2
            if d<bd: best=v; bd=d
    return best if best is not None else zref

def fetch():
    dlat=HALF/111320.0
    dlon=HALF/(111320.0*math.cos(math.radians(LAT)))
    s,w,n,e=LAT-dlat,LON-dlon,LAT+dlat,LON+dlon
    q=f'''[out:json][timeout:90];(
      way["highway"]({s},{w},{n},{e});
      way["waterway"]({s},{w},{n},{e});
      way["natural"="water"]({s},{w},{n},{e});
    );out geom;'''
    req=urllib.request.Request(OVERPASS,data=urllib.parse.urlencode({"data":q}).encode(),headers={"User-Agent":"SpandauStrike-GIS/2.0"})
    with urllib.request.urlopen(req,timeout=120) as r: data=json.loads(r.read().decode())
    with open(os.path.join(OUTDIR,"overpass_falkenhagener.json"),"w",encoding="utf-8") as f: json.dump(data,f)
    return data

def road_width(tags):
    return {"motorway":12,"trunk":11,"primary":10,"secondary":9,"tertiary":8,
            "residential":6,"living_street":5,"service":4,"cycleway":2.5,
            "footway":2,"path":1.8,"track":3}.get(tags.get("highway",""),4.5)
def add_segment(verts,faces,a,b,width_m,zoff_cm,grid,zref):
    e1,n1=a; e2,n2=b
    dx=e2-e1; dy=n2-n1; length=math.hypot(dx,dy)
    if length<0.25 or length>2000: return False
    # perpendicular in map meters
    px=-dy/length*width_m*0.5
    py= dx/length*width_m*0.5
    corners=[(e1+px,n1+py),(e1-px,n1-py),(e2-px,n2-py),(e2+px,n2+py)]
    base=len(verts)+1
    for e,n in corners:
        z=(sample_z(grid,e,n,zref)-zref)*100.0+zoff_cm
        verts.append(((e-OE)*100.0,-(n-ON)*100.0,z))
    faces.append((base,base+2,base+1))
    faces.append((base,base+3,base+2))
    return True

def write_obj(path,name,verts,faces):
    with open(path,"w",encoding="ascii") as f:
        f.write("o "+name+"\n")
        for x,y,z in verts: f.write(f"v {x:.3f} {y:.3f} {z:.3f}\n")
        for a,b,c in faces: f.write(f"f {a} {b} {c}\n")

grid,zref=load_dgm()
data=fetch()
rv=[]; rf=[]; wv=[]; wf=[]; roads=waters=0
for el in data.get("elements",[]):
    geom=el.get("geometry") or []; tags=el.get("tags",{})
    if len(geom)<2: continue
    pts=[utm(p["lat"],p["lon"]) for p in geom]
    isroad="highway" in tags
    width=road_width(tags) if isroad else (8.0 if "waterway" in tags else 18.0)
    for i in range(len(pts)-1):
        if isroad:
            if add_segment(rv,rf,pts[i],pts[i+1],width,3.0,grid,zref): roads+=1
        else:
            if add_segment(wv,wf,pts[i],pts[i+1],width,1.5,grid,zref): waters+=1
rpath=os.path.join(OUTDIR,"falkenhagener_roads_dgm.obj")
wpath=os.path.join(OUTDIR,"falkenhagener_water_dgm.obj")
write_obj(rpath,"Falkenhagener_Roads_DGM",rv,rf)
write_obj(wpath,"Falkenhagener_Water_DGM",wv,wf)
allz=[v[2] for v in rv+wv]
print("zref",zref,"grid",len(grid),"elements",len(data.get("elements",[])))
print("roads",roads,"verts",len(rv),"tris",len(rf),rpath)
print("water",waters,"verts",len(wv),"tris",len(wf),wpath)
print("zrange_cm",min(allz) if allz else None,max(allz) if allz else None)
