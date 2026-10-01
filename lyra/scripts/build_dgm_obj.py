import os, math, glob

ROOT = r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\SourceData\DGM1"
OUT = r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\SourceData\DGM1\falkenhagener_dgm_257.obj"
CENTER_E = 375716.66
CENTER_N = 5824059.63
HALF = 900.0
N = 257
MIN_E = CENTER_E - HALF
MAX_E = CENTER_E + HALF
MIN_N = CENTER_N - HALF
MAX_N = CENTER_N + HALF
STEP = (2.0 * HALF) / (N - 1)

sums = [[0.0] * N for _ in range(N)]
counts = [[0] * N for _ in range(N)]
files = sorted(glob.glob(os.path.join(ROOT, "*", "*.xyz")))
print("tiles", len(files))

for fn in files:
    kept = 0
    with open(fn, "r", encoding="ascii", errors="ignore", buffering=1024*1024) as f:
        for line in f:
            try:
                xs, ys, zs = line.split()
                x = float(xs); y = float(ys)
                if x < MIN_E or x > MAX_E or y < MIN_N or y > MAX_N:
                    continue
                z = float(zs)
                i = int(round((x - MIN_E) / STEP))
                j = int(round((y - MIN_N) / STEP))
                if 0 <= i < N and 0 <= j < N:
                    sums[j][i] += z
                    counts[j][i] += 1
                    kept += 1
            except ValueError:
                pass
    print(os.path.basename(fn), "kept", kept)
heights = [[None] * N for _ in range(N)]
for j in range(N):
    for i in range(N):
        if counts[j][i]:
            heights[j][i] = sums[j][i] / counts[j][i]

for _ in range(8):
    changed = 0
    nxt = [row[:] for row in heights]
    for j in range(N):
        for i in range(N):
            if heights[j][i] is not None:
                continue
            vals = []
            for dj, di in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
                y=j+dj; x=i+di
                if 0 <= x < N and 0 <= y < N and heights[y][x] is not None:
                    vals.append(heights[y][x])
            if vals:
                nxt[j][i] = sum(vals)/len(vals); changed += 1
    heights = nxt
    if not changed:
        break
valid = [h for row in heights for h in row if h is not None]
fallback = sum(valid)/len(valid)
for j in range(N):
    for i in range(N):
        if heights[j][i] is None:
            heights[j][i] = fallback

ci = (N-1)//2
datum = heights[ci][ci]
print("datum", datum, "min", min(valid), "max", max(valid), "fallback", fallback)

with open(OUT, "w", encoding="ascii", newline="\n") as o:
    o.write("# Spandau Strike Falkenhagener Feld DGM1 terrain\n")
    o.write("o SM_DGM1_FalkenhagenerFeld\n")
    for j in range(N):
        north = MIN_N + j * STEP
        y_cm = -(north - CENTER_N) * 100.0
        for i in range(N):
            east = MIN_E + i * STEP
            x_cm = (east - CENTER_E) * 100.0
            z_cm = (heights[j][i] - datum) * 100.0
            o.write(f"v {x_cm:.3f} {y_cm:.3f} {z_cm:.3f}\n")
    for j in range(N):
        v = j/(N-1)
        for i in range(N):
            u = i/(N-1)
            o.write(f"vt {u:.6f} {v:.6f}\n")
    for j in range(N-1):
        for i in range(N-1):
            a = j*N+i+1
            b = a+1
            c = a+N
            d = c+1
            o.write(f"f {a}/{a} {c}/{c} {b}/{b}\n")
            o.write(f"f {b}/{b} {c}/{c} {d}/{d}\n")
print("wrote", OUT, os.path.getsize(OUT))
