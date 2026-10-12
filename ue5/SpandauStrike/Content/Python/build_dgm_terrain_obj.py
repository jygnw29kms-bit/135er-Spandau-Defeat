import os, math, glob

SRC = r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\DerivedData\DGM1_FalkenhagenerFeld"
OUT = r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\DerivedData\DGM1_FalkenhagenerFeld\falkenhagener_terrain.obj"
LAT=52.5524034
LON=13.1668941
HALF=900.0
STEP=10

def utm(lat,lon):
    a=6378137.0; f=1/298.257223563; k=.9996
    e2=f*(2-f); ep=e2/(1-e2); p=math.radians(lat); l=math.radians(lon); l0=math.radians(15)
    n=a/math.sqrt(1-e2*math.sin(p)**2); t=math.tan(p)**2; c=ep*math.cos(p)**2; aa=math.cos(p)*(l-l0)
    m=a*((1-e2/4-3*e2**2/64-5*e2**3/256)*p-(3*e2/8+3*e2**2/32+45*e2**3/1024)*math.sin(2*p)+(15*e2**2/256+45*e2**3/1024)*math.sin(4*p)-(35*e2**3/3072)*math.sin(6*p))
    return (k*n*(aa+(1-t+c)*aa**3/6+(5-18*t+t*t+72*c-58*ep)*aa**5/120)+500000,
            k*(m+n*math.tan(p)*(aa*aa/2+(5-t+9*c+4*c*c)*aa**4/24+(61-58*t+t*t+600*c-330*ep)*aa**6/720)))

OE,ON=utm(LAT,LON)
emin,emax=OE-HALF,OE+HALF
nmin,nmax=ON-HALF,ON+HALF

samples={}
for fn in glob.glob(os.path.join(SRC,"**","*.xyz"),recursive=True):
    print("READ",fn)
    with open(fn,"r",encoding="utf-8",errors="ignore") as f:
        for line in f:
            try:
                e,n,z=map(float,line.split()[:3])
            except:
                continue
            if e<emin or e>emax or n<nmin or n>nmax:
                continue
            ei=int(round(e-0.5)); ni=int(round(n-0.5))
            if ei % STEP or ni % STEP:
                continue
            samples[(ei,ni)]=z

xs=sorted({k[0] for k in samples})
ys=sorted({k[1] for k in samples})
if not xs or not ys:
    raise RuntimeError("no samples")
print("GRID",len(xs),len(ys),"samples",len(samples))

# reference = nearest sampled height to map center
ck=min(samples,key=lambda k:(k[0]-OE)**2+(k[1]-ON)**2)
zref=samples[ck]
print("CENTER",OE,ON,"REF",ck,zref)

# OBJ coordinate system: X=east cm, Y=south cm to match UE importer, Z up cm
index={}
verts=[]
for j,n in enumerate(reversed(ys)):
    for i,e in enumerate(xs):
        z=samples.get((e,n))
        if z is None:
            continue
        idx=len(verts)+1
        index[(e,n)]=idx
        verts.append(((e-OE)*100.0, -(n-ON)*100.0, (z-zref)*100.0))

faces=[]
ys_desc=list(reversed(ys))
for j in range(len(ys_desc)-1):
    n0,n1=ys_desc[j],ys_desc[j+1]
    for i in range(len(xs)-1):
        e0,e1=xs[i],xs[i+1]
        a=index.get((e0,n0)); b=index.get((e1,n0)); c=index.get((e1,n1)); d=index.get((e0,n1))
        if a and b and c and d:
            faces.append((a,b,c))
            faces.append((a,c,d))

with open(OUT,"w",encoding="ascii") as o:
    o.write("o FalkenhagenerFeld_DGM1\n")
    for x,y,z in verts:
        o.write(f"v {x:.3f} {y:.3f} {z:.3f}\n")
    for a,b,c in faces:
        o.write(f"f {a} {b} {c}\n")
print("OUT",OUT,"verts",len(verts),"tris",len(faces),"zref",zref)
