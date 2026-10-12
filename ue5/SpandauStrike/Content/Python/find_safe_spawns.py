import urllib.request, urllib.parse, xml.etree.ElementTree as ET, math, json, os

WFS="https://gdi.berlin.de/services/wfs/ua_gebaeudehoehen"
TYPE="ua_gebaeudehoehen:gebaeudehoehen"
OE=375716.65931339934
ON=5824059.626896084
HALF=900.0
CLEAR=15.0
DESIRED=[
("SS_LyraPlayerStart_01",-760,-240),("SS_LyraPlayerStart_02",-760,-80),
("SS_LyraPlayerStart_03",-760,80),("SS_LyraPlayerStart_04",-760,240),
("SS_LyraPlayerStart_05",760,-240),("SS_LyraPlayerStart_06",760,-80),
("SS_LyraPlayerStart_07",760,80),("SS_LyraPlayerStart_08",760,240)]
OUT=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\DerivedData\safe_spawns.json"

def lname(t): return t.split("}")[-1]
def fetch():
    bbox=f"{OE-HALF},{ON-HALF},{OE+HALF},{ON+HALF},EPSG:25833"
    q={"SERVICE":"WFS","VERSION":"2.0.0","REQUEST":"GetFeature","TYPENAMES":TYPE,
       "SRSNAME":"EPSG:25833","BBOX":bbox,"COUNT":"10000"}
    with urllib.request.urlopen(WFS+"?"+urllib.parse.urlencode(q),timeout=180) as r:return r.read()
def ring(feat):
    rs=[]
    for x in feat.iter():
        if lname(x.tag)!="posList" or not x.text: continue
        vals=list(map(float,x.text.split())); dim=int(x.attrib.get("srsDimension","2"))
        if dim not in (2,3):dim=2
        p=[(vals[i],vals[i+1]) for i in range(0,len(vals)-dim+1,dim)]
        if len(p)>=4:rs.append(p[:-1] if p[0]==p[-1] else p)
    if not rs:return None
    def area(p):return abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))/2)
    return max(rs,key=area)
def point_in(p,poly):
    x,y=p; inside=False; j=len(poly)-1
    for i in range(len(poly)):
        xi,yi=poly[i]; xj,yj=poly[j]
        if ((yi>y)!=(yj>y)) and x < (xj-xi)*(y-yi)/(yj-yi+1e-30)+xi:inside=not inside
        j=i
    return inside
def segdist(p,a,b):
    px,py=p; ax,ay=a; bx,by=b; dx=bx-ax; dy=by-ay
    if dx==dy==0:return math.hypot(px-ax,py-ay)
    t=max(0,min(1,((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy)))
    return math.hypot(px-(ax+t*dx),py-(ay+t*dy))
def free(p,items):
    x,y=p
    for poly,b in items:
        mnx,mny,mxx,mxy=b
        if x<mnx-CLEAR or x>mxx+CLEAR or y<mny-CLEAR or y>mxy+CLEAR:continue
        if point_in(p,poly):return False
        if min(segdist(p,poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly)))<CLEAR:return False
    return True

root=ET.fromstring(fetch()); items=[]
for n in root.iter():
    if lname(n.tag) in ("member","featureMember") and list(n):
        p=ring(list(n)[0])
        if p:
            xs=[x for x,y in p]; ys=[y for x,y in p]
            items.append((p,(min(xs),min(ys),max(xs),max(ys))))
print("buildings",len(items))
result=[]
for name,xm,ym in DESIRED:
    e0=OE+xm; n0=ON-ym
    best=None
    for rad in range(0,241,10):
        candidates=[]
        if rad==0:candidates=[(e0,n0)]
        else:
            for dx in range(-rad,rad+1,10):
                candidates += [(e0+dx,n0-rad),(e0+dx,n0+rad)]
            for dy in range(-rad+10,rad,10):
                candidates += [(e0-rad,n0+dy),(e0+rad,n0+dy)]
        candidates.sort(key=lambda p:(p[0]-e0)**2+(p[1]-n0)**2)
        for p in candidates:
            if free(p,items):
                best=p; break
        if best:break
    if not best:raise RuntimeError("no free spawn "+name)
    ux=(best[0]-OE)*100; uy=-(best[1]-ON)*100
    dist=math.hypot(best[0]-e0,best[1]-n0)
    row={"name":name,"x":ux,"y":uy,"z":160.0,"shift_m":dist}
    result.append(row); print(row)
json.dump(result,open(OUT,"w"),indent=2)
print("OUT",OUT)
