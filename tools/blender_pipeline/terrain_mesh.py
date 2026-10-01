from pathlib import Path
import math

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "terrain_src"
OUT = ROOT / "output" / "master"
OUT.mkdir(parents=True, exist_ok=True)

CENTER_X = 375716.66
CENTER_Y = 5824059.63
HALF = 900.0
STEP = 4
MIN_X, MAX_X = CENTER_X-HALF, CENTER_X+HALF
MIN_Y, MAX_Y = CENTER_Y-HALF, CENTER_Y+HALF

tiles = [
    SRC/"374_5822"/"dgm1_33_374_5822_2_be.xyz",
    SRC/"376_5822"/"dgm1_33_376_5822_2_be.xyz",
    SRC/"374_5824"/"dgm1_33_374_5824_2_be.xyz",
    SRC/"376_5824"/"dgm1_33_376_5824_2_be.xyz",
]

points = {}
zmin = float("inf")
zmax = float("-inf")
for tile in tiles:
    print("READ", tile.name, flush=True)
    with tile.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                sx, sy, sz = line.split()
                x, y, z = float(sx), float(sy), float(sz)
            except ValueError:
                continue
            if x < MIN_X or x > MAX_X or y < MIN_Y or y > MAX_Y:
                continue
            ix = int(round(x - 0.5))
            iy = int(round(y - 0.5))
            if ix % STEP or iy % STEP:
                continue
            points[(ix,iy)] = z
            zmin = min(zmin,z)
            zmax = max(zmax,z)

xs = sorted({k[0] for k in points})
ys = sorted({k[1] for k in points})
print("GRID", len(xs), "x", len(ys), "points", len(points), "z", zmin, zmax, flush=True)
x_index={x:i for i,x in enumerate(xs)}
y_index={y:i for i,y in enumerate(ys)}
obj = OUT / "falkenhagener_feld_DGM1_4m.obj"
meta = OUT / "falkenhagener_feld_DGM1_4m.txt"
origin_x = (MIN_X+MAX_X)/2
origin_y = (MIN_Y+MAX_Y)/2
origin_z = zmin

valid = {}
verts = []
for y in ys:
    for x in xs:
        z = points.get((x,y))
        if z is None:
            continue
        valid[(x,y)] = len(verts)+1
        verts.append((x+0.5-origin_x, y+0.5-origin_y, z-origin_z))

faces=[]
for yi in range(len(ys)-1):
    y0,y1=ys[yi],ys[yi+1]
    if y1-y0 != STEP: continue
    for xi in range(len(xs)-1):
        x0,x1=xs[xi],xs[xi+1]
        if x1-x0 != STEP: continue
        a=valid.get((x0,y0)); b=valid.get((x1,y0))
        c=valid.get((x1,y1)); d=valid.get((x0,y1))
        if all((a,b,c,d)):
            faces.append((a,b,c,d))
with obj.open("w", encoding="utf-8", newline="\n") as f:
    f.write("# Berlin ATKIS DGM1 - Falkenhagener Feld\n")
    f.write("# local metres, EPSG:25833 source\n")
    f.write("o Terrain_DGM1_FalkenhagenerFeld\n")
    for x,y,z in verts:
        f.write(f"v {x:.3f} {y:.3f} {z:.3f}\n")
    for a,b,c,d in faces:
        f.write(f"f {a} {b} {c} {d}\n")

meta.write_text(
    f"EPSG=25833\nCENTER={CENTER_X},{CENTER_Y}\n"
    f"BBOX={MIN_X},{MIN_Y},{MAX_X},{MAX_Y}\nSTEP_M={STEP}\n"
    f"ORIGIN_Z={origin_z}\nVERTICES={len(verts)}\nFACES={len(faces)}\n"
    f"Z_MIN={zmin}\nZ_MAX={zmax}\n",
    encoding="utf-8")

print("WROTE", obj, len(verts), "verts", len(faces), "faces", flush=True)
