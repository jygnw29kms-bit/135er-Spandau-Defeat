import urllib.request, urllib.parse, xml.etree.ElementTree as ET
import os, glob, math, re

WFS="https://gdi.berlin.de/services/wfs/ua_gebaeudehoehen"
TYPE="ua_gebaeudehoehen:gebaeudehoehen"
LAT=52.5524034
LON=13.1668941
HALF=900.0
STEP=10
DGM=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\DerivedData\DGM1_FalkenhagenerFeld"
OUT=os.path.join(DGM,"falkenhagener_buildings_exact.obj")

def utm(lat,lon):
    a=6378137.0; f=1/298.257223563; k=.9996
    e2=f*(2-f); ep=e2/(1-e2); p=math.radians(lat); l=math.radians(lon); l0=math.radians(15)
    n=a/math.sqrt(1-e2*math.sin(p)**2); t=math.tan(p)**2; c=ep*math.cos(p)**2; aa=math.cos(p)*(l-l0)
    m=a*((1-e2/4-3*e2**2/64-5*e2**3/256)*p-(3*e2/8+3*e2**2/32+45*e2**3/1024)*math.sin(2*p)+(15*e2**2/256+45*e2**3/1024)*math.sin(4*p)-(35*e2**3/3072)*math.sin(6*p))
    return (k*n*(aa+(1-t+c)*aa**3/6+(5-18*t+t*t+72*c-58*ep)*aa**5/120)+500000,
            k*(m+n*math.tan(p)*(aa*aa/2+(5-t+9*c+4*c*c)*aa**4/24+(61-58*t+t*t+600*c-330*ep)*aa**6/720)))
OE,ON=utm(LAT,LON)
def load_dgm():
    pts={}
    emin,emax=OE-HALF-20,OE+HALF+20
    nmin,nmax=ON-HALF-20,ON+HALF+20
    for fn in glob.glob(os.path.join(DGM,"**","*.xyz"),recursive=True):
        with open(fn,"r",encoding="utf-8",errors="ignore") as f:
            for line in f:
                try: e,n,z=map(float,line.split()[:3])
                except: continue
                if e<emin or e>emax or n<nmin or n>nmax: continue
                ei=int(round(e-0.5)); ni=int(round(n-0.5))
                if ei%STEP or ni%STEP: continue
                pts[(ei,ni)]=z
    ck=min(pts,key=lambda k:(k[0]-OE)**2+(k[1]-ON)**2)
    return pts,pts[ck]

def terrain_z(grid,e,n,default):
    ex=int(round(e/STEP)*STEP); ny=int(round(n/STEP)*STEP)
    z=grid.get((ex,ny))
    if z is not None: return z
    best=None; bd=1e99
    for dx in (-STEP,0,STEP):
        for dy in (-STEP,0,STEP):
            v=grid.get((ex+dx,ny+dy))
            if v is not None and dx*dx+dy*dy<bd: best=v; bd=dx*dx+dy*dy
    return best if best is not None else default
def fetch():
    bbox=f"{OE-HALF},{ON-HALF},{OE+HALF},{ON+HALF},EPSG:25833"
    q={"SERVICE":"WFS","VERSION":"2.0.0","REQUEST":"GetFeature","TYPENAMES":TYPE,
       "SRSNAME":"EPSG:25833","BBOX":bbox,"COUNT":"10000"}
    u=WFS+"?"+urllib.parse.urlencode(q)
    req=urllib.request.Request(u,headers={"User-Agent":"SpandauStrike-Buildings/1.0"})
    with urllib.request.urlopen(req,timeout=180) as r: return r.read()

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
        dim=int(x.attrib.get("srsDimension","2"))
        if dim not in (2,3): dim=2
        p=[(vals[i],vals[i+1]) for i in range(0,len(vals)-dim+1,dim)]
        if len(p)>=4: rings.append(p)
    if not rings: return None
    def area(p): return abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))/2)
    rings.sort(key=area,reverse=True)
    p=rings[0]
    if math.hypot(p[0][0]-p[-1][0],p[0][1]-p[-1][1])<0.01: p=p[:-1]
    return p if len(p)>=3 else None
def signed_area(p):
    return sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))/2

def cross(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])

def inside(p,a,b,c):
    c1=cross(a,b,p); c2=cross(b,c,p); c3=cross(c,a,p)
    neg=(c1<0) or (c2<0) or (c3<0); pos=(c1>0) or (c2>0) or (c3>0)
    return not (neg and pos)

def triangulate(poly):
    p=list(poly)
    if signed_area(p)<0: p.reverse()
    idx=list(range(len(p))); out=[]; guard=0
    while len(idx)>3 and guard<len(p)*len(p):
        guard+=1; ear=False
        for k in range(len(idx)):
            i0=idx[k-1]; i1=idx[k]; i2=idx[(k+1)%len(idx)]
            a,b,c=p[i0],p[i1],p[i2]
            if cross(a,b,c)<=1e-9: continue
            if any(inside(p[j],a,b,c) for j in idx if j not in (i0,i1,i2)): continue
            out.append((i0,i1,i2)); del idx[k]; ear=True; break
        if not ear: break
    if len(idx)==3: out.append(tuple(idx))
    return p,out
def feature_members(root):
    for n in root.iter():
        if lname(n.tag) in ("member","featureMember") and list(n):
            yield list(n)[0]

grid,zref=load_dgm()
blob=fetch()
root=ET.fromstring(blob)
print("numberMatched",root.attrib.get("numberMatched"))
verts=[]; faces=[]; buildings=0; skipped=0; fallbacks=0

for feat in feature_members(root):
    poly=ring(feat)
    if not poly: skipped+=1; continue
    try: h=float(attr(feat,"hoehe").replace(",","."))
    except: h=10.0
    if h<2 or h>300: h=10.0
    poly,tris=triangulate(poly)
    if not tris:
        tris=[(0,i,i+1) for i in range(1,len(poly)-1)]
        fallbacks+=1
    ce=sum(x for x,y in poly)/len(poly); cn=sum(y for x,y in poly)/len(poly)
    bz=terrain_z(grid,ce,cn,zref)
    bottom=(bz-zref)*100.0; top=bottom+h*100.0
    base=len(verts)+1
    for e,n in poly:
        verts.append(((e-OE)*100.0,-(n-ON)*100.0,bottom))
    for e,n in poly:
        verts.append(((e-OE)*100.0,-(n-ON)*100.0,top))
    count=len(poly)
    # Y is mirrored for Unreal (north -> -Y), so reverse winding.
    for a,b,c in tris:
        faces.append((base+count+a,base+count+c,base+count+b))
    for i in range(count):
        j=(i+1)%count
        b0=base+i; b1=base+j; t0=base+count+i; t1=base+count+j
        faces.append((b0,t1,b1)); faces.append((b0,t0,t1))
    buildings+=1

with open(OUT,"w",encoding="ascii") as o:
    o.write("o FalkenhagenerFeld_ExactBuildings\n")
    for x,y,z in verts: o.write(f"v {x:.3f} {y:.3f} {z:.3f}\n")
    o.write("vt 0.0 0.0\n")
    for a,b,c in faces: o.write(f"f {a}/1 {b}/1 {c}/1\n")
print("OUT",OUT)
print("buildings",buildings,"skipped",skipped,"fallbacks",fallbacks,"verts",len(verts),"tris",len(faces),"zref",zref)
