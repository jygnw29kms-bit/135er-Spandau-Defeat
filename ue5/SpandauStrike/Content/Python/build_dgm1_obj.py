from pathlib import Path
import math

ROOT=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\DGM1")
OUT=ROOT/"falkenhagener_terrain_10m.obj"
CX=375716.66
CY=5824059.63
HALF=900.0
STEP=10.0
MINX=CX-HALF
MAXX=CX+HALF
MINY=CY-HALF
MAXY=CY+HALF

files=list(ROOT.glob("*/*.xyz"))
samples={}
def key_for(x,y):
    ix=round((x-MINX)/STEP)
    iy=round((y-MINY)/STEP)
    tx=MINX+ix*STEP
    ty=MINY+iy*STEP
    if abs(x-tx)<=0.51 and abs(y-ty)<=0.51:
        return ix,iy
    return None

for fp in files:
    print("reading",fp)
    with fp.open("r",encoding="ascii",errors="ignore") as f:
        for line in f:
            try:
                xs,ys,zs=line.split()
                x=float(xs); y=float(ys)
            except Exception:
                continue
            if x<MINX-1 or x>MAXX+1 or y<MINY-1 or y>MAXY+1:
                continue
            k=key_for(x,y)
            if k is not None:
                samples[k]=float(zs)
nx=int(round((MAXX-MINX)/STEP))+1
ny=int(round((MAXY-MINY)/STEP))+1
print("grid",nx,ny,"samples",len(samples))

center_key=(round((CX-MINX)/STEP),round((CY-MINY)/STEP))
baseline=samples.get(center_key)
if baseline is None:
    baseline=sum(samples.values())/len(samples)
print("baseline",baseline)

def nearest(ix,iy):
    z=samples.get((ix,iy))
    if z is not None:
        return z
    for r in range(1,5):
        for dy in range(-r,r+1):
            for dx in range(-r,r+1):
                z=samples.get((ix+dx,iy+dy))
                if z is not None:
                    return z
    return baseline
with OUT.open("w",encoding="ascii") as o:
    o.write("# Falkenhagener Feld DGM1 terrain 10m\n")
    o.write("o Falkenhagener_DGM1_10m\n")
    for iy in range(ny):
        y=MINY+iy*STEP
        for ix in range(nx):
            x=MINX+ix*STEP
            z=nearest(ix,iy)
            ux=(x-CX)*100.0
            uy=-(y-CY)*100.0
            uz=(z-baseline)*100.0
            o.write(f"v {ux:.3f} {uy:.3f} {uz:.3f}\n")
    for iy in range(ny-1):
        for ix in range(nx-1):
            a=iy*nx+ix+1
            b=a+1
            c=a+nx
            d=c+1
            o.write(f"f {a} {c} {b}\n")
            o.write(f"f {b} {c} {d}\n")
print("wrote",OUT,OUT.stat().st_size)
