src=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\DerivedData\DGM1_FalkenhagenerFeld\falkenhagener_buildings_exact.obj"
tmp=src+".tmp"
with open(src,"r",encoding="ascii") as i, open(tmp,"w",encoding="ascii") as o:
    inserted=False
    for line in i:
        if line.startswith("f ") and not inserted:
            o.write("vt 0.0 0.0\n")
            inserted=True
        if line.startswith("f "):
            parts=line.strip().split()
            o.write("f "+" ".join(p.split("/")[0]+"/1" for p in parts[1:])+"\n")
        else:
            o.write(line)
import os
os.replace(tmp,src)
print("UV_FIXED",src)
