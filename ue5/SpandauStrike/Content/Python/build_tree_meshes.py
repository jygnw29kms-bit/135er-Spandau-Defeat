import json, os, glob, math

BASE=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike"
TREE_JSON=os.path.join(BASE,"DerivedData","Trees_FalkenhagenerFeld","trees.json")
DGM=os.path.join(BASE,"DerivedData","DGM1_FalkenhagenerFeld")
OUTDIR=os.path.join(BASE,"DerivedData","Trees_FalkenhagenerFeld")
LAT=52.5524034
LON=13.1668941
HALF=900.0
STEP=10

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
    for fn in glob.glob(os.path.join(DGM,"**","*.xyz"),recursive=True):
        with open(fn,"r",encoding="ascii",errors="ignore") as f:
            for line in f:
                try: e,n,z=map(float,line.split()[:3])
                except: continue
                if not (emin<=e<=emax and nmin<=n<=nmax): continue
                ei=int(round(e-0.5)); ni=int(round(n-0.5))
                if ei%STEP or ni%STEP: continue
                pts[(ei,ni)]=z
    ck=min(pts,key=lambda q:(q[0]-OE)**2+(q[1]-ON)**2)
    return pts,pts[ck]

def terrain_z(grid,e,n,zref):
    ex=int(round((e-0.5)/STEP)*STEP)
    ny=int(round((n-0.5)/STEP)*STEP)
    best=None; bd=1e30
    for dx in (-STEP,0,STEP):
        for dy in (-STEP,0,STEP):
            q=(ex+dx,ny+dy); v=grid.get(q)
            if v is None: continue
            dist=(q[0]+0.5-e)**2+(q[1]+0.5-n)**2
            if dist<bd: best=v; bd=dist
    return zref if best is None else best
def num(v,default):
    try: return float(str(v).replace(",","."))
    except: return default

def add_trunk(verts,faces,x,y,z,h,diam):
    sides=6
    r=max(0.08,min(0.75,diam*0.5))
    top=z+h*0.62
    base=len(verts)+1
    for zz in (z,top):
        for i in range(sides):
            a=2*math.pi*i/sides
            verts.append((x+math.cos(a)*r*100,y+math.sin(a)*r*100,zz))
    for i in range(sides):
        j=(i+1)%sides
        b0=base+i; b1=base+j; t0=base+sides+i; t1=base+sides+j
        faces.append((b0,b1,t1)); faces.append((b0,t1,t0))

def add_crown(verts,faces,x,y,z,h,crown):
    sides=8
    r=max(0.8,min(6.0,crown*0.5))*100
    bot=z+h*0.40; mid=z+h*0.72; top=z+h
    base=len(verts)+1
    verts.append((x,y,top))
    for i in range(sides):
        a=2*math.pi*i/sides
        verts.append((x+math.cos(a)*r,y+math.sin(a)*r,mid))
    verts.append((x,y,bot))
    topi=base; boti=base+sides+1
    for i in range(sides):
        a=base+1+i; b=base+1+((i+1)%sides)
        faces.append((topi,a,b))
        faces.append((boti,b,a))
def write_obj(path,name,verts,faces):
    with open(path,"w",encoding="ascii",newline="\n") as f:
        f.write("o "+name+"\n")
        for v in verts: f.write("v %.3f %.3f %.3f\n"%v)
        for a,b,c in faces: f.write("f %d %d %d\n"%(a,b,c))

grid,zref=load_dgm()
trees=json.load(open(TREE_JSON,"r",encoding="utf-8"))
tv=[]; tf=[]; cv=[]; cf=[]
used=0
for t in trees:
    e=num(t.get("easting"),0); n=num(t.get("northing"),0)
    if abs(e-OE)>HALF or abs(n-ON)>HALF: continue
    h=max(3.0,min(28.0,num(t.get("height_m"),8.0)))
    crown=max(1.5,min(12.0,num(t.get("crown_m"),4.0)))
    circ=max(20.0,min(450.0,num(t.get("trunk_cm"),80.0)))
    diam=(circ/100.0)/math.pi
    x=(e-OE)*100.0; y=-(n-ON)*100.0
    z=(terrain_z(grid,e,n,zref)-zref)*100.0
    add_trunk(tv,tf,x,y,z,h*100.0,diam)
    add_crown(cv,cf,x,y,z,h*100.0,crown)
    used+=1
tp=os.path.join(OUTDIR,"falkenhagener_tree_trunks.obj")
cp=os.path.join(OUTDIR,"falkenhagener_tree_crowns.obj")
write_obj(tp,"Falkenhagener_TreeTrunks",tv,tf)
write_obj(cp,"Falkenhagener_TreeCrowns",cv,cf)
print("trees",used,"zref",zref)
print("trunks",len(tv),"verts",len(tf),"tris",tp,os.path.getsize(tp))
print("crowns",len(cv),"verts",len(cf),"tris",cp,os.path.getsize(cp))
