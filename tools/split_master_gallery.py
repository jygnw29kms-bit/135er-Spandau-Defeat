from PIL import Image, ImageOps, ImageEnhance
from pathlib import Path

SRC=Path("media/source2/masters/all-maps-master-gallery.jpg")
OUT=Path("media/source2/masters/maps")
OUT.mkdir(parents=True,exist_ok=True)
maps=[
("rathaus-spandau","Rathaus Spandau"),("zitadelle-spandau","Zitadelle Spandau"),
("staaken","Staaken"),("rodelberg","Rodelberg"),("kiesteich","Kiesteich"),
("falkenhagener-feld","Falkenhagener Feld"),("lynarstrasse","Lynarstraße"),
("wroehmaennerpark","Wröhmännerpark"),("freiheit","Freiheit"),
("martin-buber-schule","Martin-Buber-Schule"),("askanier-schule","Askanier-Schule"),
("b-traven-schule","B.-Traven-Schule"),("fort-hahneberg-1945","Fort Hahneberg 1945"),
("teufelsberg-kalter-krieg","Teufelsberg – Kalter Krieg"),
("flugplatz-gatow-1945","Flugplatz Gatow 1945"),("gatow-luftbruecke-1948","Gatow – Luftbrücke 1948"),
("radelandstrasse-1945","Radelandstraße 1945"),("hakenfelde-heeresamt-1944","Hakenfelde – Heeresamt 1944"),
("zitadelle-1-mai-1945","Zitadelle Spandau – 1. Mai 1945"),
("britischer-sektor-spandau","Britischer Sektor Spandau")]
im=Image.open(SRC).convert("RGB")
w,h=im.size
cols,rows=5,4
for i,(slug,name) in enumerate(maps):
    r,c=divmod(i,cols)
    x0=round(c*w/cols); x1=round((c+1)*w/cols)
    y0=round(r*h/rows); y1=round((r+1)*h/rows)
    crop=im.crop((x0,y0,x1,y1))
    crop=ImageOps.fit(crop,(1600,900),method=Image.Resampling.LANCZOS)
    crop=ImageEnhance.Sharpness(crop).enhance(1.08)
    crop.save(OUT/f"{slug}-master-reference.jpg","JPEG",quality=92,optimize=True,progressive=True)
print(f"Wrote {len(maps)} master references to {OUT}")
