import os, math, numpy as np

ROOT = r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\DGM1"
OUT = r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\FalkenhagenerFeld_DGM10m.obj"
CENTER_E = 375716.66
CENTER_N = 5824059.63
HALF = 900.0
STEP = 10
FILES = [
    os.path.join(ROOT,"374_5822","dgm1_33_374_5822_2_be.xyz"),
    os.path.join(ROOT,"376_5822","dgm1_33_376_5822_2_be.xyz"),
    os.path.join(ROOT,"374_5824","dgm1_33_374_5824_2_be.xyz"),
    os.path.join(ROOT,"376_5824","dgm1_33_376_5824_2_be.xyz"),
]
xmin = math.floor(CENTER_E-HALF)+0.5
xmax = xmin + 1800
ymin = math.floor(CENTER_N-HALF)+0.5
ymax = ymin + 1800
xs = np.arange(xmin, xmax+0.1, STEP)
ys = np.arange(ymin, ymax+0.1, STEP)
heights = np.full((len(ys),len(xs)), np.nan, dtype=np.float32)
print("grid", len(xs), len(ys), "bounds", xmin,xmax,ymin,ymax)
for fn in FILES:
    print("load", fn)
    a=np.loadtxt(fn,dtype=np.float32)
    m=(a[:,0]>=xmin-0.1)&(a[:,0]<=xmax+0.1)&(a[:,1]>=ymin-0.1)&(a[:,1]<=ymax+0.1)
    b=a[m]
    if not len(b):
        continue
    xi=np.rint((b[:,0]-xmin)/STEP).astype(np.int32)
    yi=np.rint((b[:,1]-ymin)/STEP).astype(np.int32)
    keep=(np.abs((b[:,0]-xmin)-xi*STEP)<0.01)&(np.abs((b[:,1]-ymin)-yi*STEP)<0.01)
    b=b[keep]; xi=xi[keep]; yi=yi[keep]
    good=(xi>=0)&(xi<len(xs))&(yi>=0)&(yi<len(ys))
    heights[yi[good],xi[good]]=b[good,2]
    del a,b
print("filled", np.isfinite(heights).sum(), "of", heights.size)
if np.isnan(heights).any():
    raise RuntimeError("DGM crop has gaps: %d" % np.isnan(heights).sum())
cx=int(np.argmin(np.abs(xs-CENTER_E)))
cy=int(np.argmin(np.abs(ys-CENTER_N)))
base=float(heights[cy,cx])
print("height range",float(heights.min()),float(heights.max()),"center",base)
with open(OUT,"w",encoding="ascii",newline="\n") as f:
    f.write("# Spandau Strike Falkenhagener Feld DGM1 -> 10m terrain\n")
    f.write("# EPSG:25833 source, local UE-oriented coordinates in centimeters\n")
    for j,y in enumerate(ys):
        for i,x in enumerate(xs):
            vx=(x-CENTER_E)*100.0
            vy=-(y-CENTER_N)*100.0
            vz=(float(heights[j,i])-base)*100.0
            f.write(f"v {vx:.3f} {vy:.3f} {vz:.3f}\n")
    for j in range(len(ys)):
        v=1.0-j/(len(ys)-1)
        for i in range(len(xs)):
            u=i/(len(xs)-1)
            f.write(f"vt {u:.8f} {v:.8f}\n")
    w=len(xs)
    for j in range(len(ys)-1):
        for i in range(w-1):
            a=j*w+i+1; b=a+1; c=a+w; d=c+1
            f.write(f"f {a}/{a} {c}/{c} {b}/{b}\n")
            f.write(f"f {b}/{b} {c}/{c} {d}/{d}\n")
print("OBJ",OUT,os.path.getsize(OUT))
np.save(os.path.splitext(OUT)[0]+"_heights.npy",heights)
with open(os.path.splitext(OUT)[0]+"_meta.txt","w") as f:
    f.write(f"center_e={CENTER_E}\ncenter_n={CENTER_N}\nbase_height={base}\n")
    f.write(f"min_height={float(heights.min())}\nmax_height={float(heights.max())}\nstep={STEP}\n")
