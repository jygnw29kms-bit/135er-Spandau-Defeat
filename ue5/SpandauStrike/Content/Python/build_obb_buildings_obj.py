import urllib.request, urllib.parse, xml.etree.ElementTree as ET
import os, glob, math

WFS="https://gdi.berlin.de/services/wfs/ua_gebaeudehoehen"
TYPE="ua_gebaeudehoehen:gebaeudehoehen"
LAT=52.5524034
LON=13.1668941
HALF=900.0
STEP=10
ROOT=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\DerivedData\DGM1_FalkenhagenerFeld"
OUT=os.path.join(ROOT,"falkenhagener_buildings_obb.obj")

def utm(lat,lon):
    a=6378137.; f=1/298.257223563; k=.9996; e2=f*(2-f); ep=e2/(1-e2)
    p=math.radians(lat); l=math.radians(lon); l0=math.radians(15)
    n=a/math.sqrt(1-e2*math.sin(p)**2); t=math.tan(p)**2; c=ep*math.cos(p)**2; aa=math.cos(p)*(l-l0)
    m=a*((1-e2/4-3*e2**2/64-5*e2**3/256)*p-(3*e2/8+3*e2**2/32+45*e2**3/1024)*math.sin(2*p)+(15*e2**2/256+45*e2**3/1024)*math.sin(4*p)-(35*e2**3/3072)*math.sin(6*p))
    return k*n*(aa+(1-t+c)*aa**3/6+(5-18*t+t*t+72*c-58*ep)*aa**5/120)+500000, k*(m+n*math.tan(p)*(aa*aa/2+(5-t+9*c+4*c*c)*aa**4/24+(61-58*t+t*t+600*c-330*ep)*aa**6/720))
OE,ON=utm(LAT,LON)
def load_dgm():
    pts={}; emin,emax=OE-HALF-20,OE+HALF+20; nmin,nmax=ON-HALF-20,ON+HALF+20
    for fn in glob.glob(os.path.join(ROOT,"**","*.xyz"),recursive=True):
        with open(fn,"r",encoding="ascii",errors="ignore") as f:
            for line in f:
                try:e,n,z=map(float,line.split()[:3])
                except:continue
                if not(emin<=e<=emax and nmin<=n<=nmax):continue
                ei=int(round(e-0.5)); ni=int(round(n-0.5))
                if ei%STEP or ni%STEP:continue
                pts[(ei,ni)]=z
    ck=min(pts,key=lambda k:(k[0]-OE)**2+(k[1]-ON)**2)
    return pts,pts[ck]

def terrain_z(g,e,n,d):
    ex=int(round(e/STEP)*STEP); ny=int(round(n/STEP)*STEP)
    if (ex,ny) in g:return g[(ex,ny)]
    best=d; bd=1e9
    for dx in (-STEP,0,STEP):
        for dy in (-STEP,0,STEP):
            if (ex+dx,ny+dy) in g and dx*dx+dy*dy<bd:
                best=g[(ex+dx,ny+dy)]; bd=dx*dx+dy*dy
    return best

def lname(t):return t.split("}")[-1]
def attr(feat,name):
    for x in feat.iter():
        if lname(x.tag).lower()==name.lower() and x.text:return x.text.strip()
    return ""

def ring(feat):
    rings=[]
    for x in feat.iter():
        if lname(x.tag)!="posList" or not x.text:continue
        vals=[float(v.replace(",",".")) for v in x.text.split()]
        p=[(vals[i],vals[i+1]) for i in range(0,len(vals)-1,2)]
        if len(p)>=4:rings.append(p)
    if not rings:return None
    def area(p):return abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))/2)
    p=max(rings,key=area)
    if math.dist(p[0],p[-1])<.01:p=p[:-1]
    return p if len(p)>=3 else None

def members(root):
    for n in root.iter():
        if lname(n.tag) in ("member","featureMember") and list(n):yield list(n)[0]

def dominant_box(p):
    cx=sum(x for x,y in p)/len(p); cy=sum(y for x,y in p)/len(p)
    sxx=syy=sxy=0.
    for x,y in p:
        dx=x-cx; dy=y-cy; sxx+=dx*dx; syy+=dy*dy; sxy+=dx*dy
    a=.5*math.atan2(2*sxy,sxx-syy); ca=math.cos(a); sa=math.sin(a)
    q=[((x-cx)*ca+(y-cy)*sa,-(x-cx)*sa+(y-cy)*ca) for x,y in p]
    xmin=min(x for x,y in q); xmax=max(x for x,y in q); ymin=min(y for x,y in q); ymax=max(y for x,y in q)
    return cx,cy,max(1.,xmax-xmin),max(1.,ymax-ymin),a
def fetch():
    bbox=f"{OE-HALF},{ON-HALF},{OE+HALF},{ON+HALF},EPSG:25833"
    q={"SERVICE":"WFS","VERSION":"2.0.0","REQUEST":"GetFeature","TYPENAMES":TYPE,"SRSNAME":"EPSG:25833","BBOX":bbox,"COUNT":"10000"}
    req=urllib.request.Request(WFS+"?"+urllib.parse.urlencode(q),headers={"User-Agent":"SpandauStrike-OBB/1.0"})
    with urllib.request.urlopen(req,timeout=180) as r:return r.read()

grid,zref=load_dgm(); root=ET.fromstring(fetch())
verts=[]; faces=[]; count=0
for feat in members(root):
    p=ring(feat)
    if not p:continue
    cx,cy,w,dep,a=dominant_box(p)
    try:h=float(attr(feat,"hoehe").replace(",","."))
    except:h=10.
    if h<2 or h>300:h=10.
    bz=(terrain_z(grid,cx,cy,zref)-zref)*100.; tz=bz+h*100.
    ca=math.cos(a); sa=math.sin(a); hw=w/2; hd=dep/2
    corners=[]
    for lx,ly in ((-hw,-hd),(hw,-hd),(hw,hd),(-hw,hd)):
        e=cx+lx*ca-ly*sa; n=cy+lx*sa+ly*ca
        corners.append(((e-OE)*100.,-(n-ON)*100.))
    base=len(verts)+1
    for x,y in corners:verts.append((x,y,bz))
    for x,y in corners:verts.append((x,y,tz))
    # bottom/top + four walls, consistent winding after Y mirror
    local=[(1,3,2),(1,4,3),(5,6,7),(5,7,8),
           (1,2,6),(1,6,5),(2,3,7),(2,7,6),
           (3,4,8),(3,8,7),(4,1,5),(4,5,8)]
    for a0,b0,c0 in local:faces.append((base+a0-1,base+b0-1,base+c0-1))
    count+=1

with open(OUT,"w",encoding="ascii") as o:
    o.write("o FalkenhagenerFeld_OBBBuildings\n")
    for x,y,z in verts:o.write(f"v {x:.3f} {y:.3f} {z:.3f}\n")
    o.write("vt 0.0 0.0\n")
    for a,b,c in faces:o.write(f"f {a}/1 {b}/1 {c}/1\n")
print("OUT",OUT,"buildings",count,"verts",len(verts),"tris",len(faces),"zref",zref)
