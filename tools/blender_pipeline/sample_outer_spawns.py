from pathlib import Path
terrain=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\RathausSpandau_v1\rathaus_terrain.obj")
verts=[]
for line in terrain.open(errors="ignore"):
    if line.startswith("v "):
        _,x,y,z=line.split()[:4];verts.append((float(x),float(y),float(z)))
def ground(x,y):return min(verts,key=lambda v:(v[0]-x)**2+(v[1]-y)**2)[2]
pts=[(5500,-10000),(8000,-10500),(12000,-10500),(14500,-10000),(4500,9000),(7500,9500),(12500,9500),(15500,9000),(1000,-1000),(19000,-1000)]
for x,y in pts: print(x,y,round(ground(x,y)+190,1),round(ground(x,y),1))
