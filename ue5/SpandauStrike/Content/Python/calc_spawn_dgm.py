import glob, math, os
ROOT=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\DerivedData\DGM1_FalkenhagenerFeld"
OE=375716.66
ON=5824059.63
ZREF=33.3
spawns=[(-76000,-24000),(-76000,-8000),(-74000,5000),(-76000,24000),(76000,-24000),(76000,-6000),(76000,8000),(76000,24000)]
targets=[]
for x,y in spawns:
    targets.append((OE+x/100.0,ON-y/100.0,x,y))
best=[(1e99,None)]*len(targets)
for fn in glob.glob(os.path.join(ROOT,"**","*.xyz"),recursive=True):
    with open(fn,"r",encoding="ascii",errors="ignore") as f:
        for line in f:
            try:e,n,z=map(float,line.split()[:3])
            except:continue
            for i,(te,tn,x,y) in enumerate(targets):
                if abs(e-te)>2 or abs(n-tn)>2:continue
                d=(e-te)**2+(n-tn)**2
                if d<best[i][0]:best[i]=(d,z)
for i,((te,tn,x,y),(dist,z)) in enumerate(zip(targets,best),1):
    local=(z-ZREF)*100.0 if z is not None else 200.0
    print(i,x,y,"elev",z,"local_z",round(local,1),"spawn_z",round(local+180,1))
