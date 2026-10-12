import urllib.request, urllib.parse, xml.etree.ElementTree as ET, csv, json, os

BASE="https://gdi.berlin.de/services/wfs/baumbestand"
BBOX="374816,5823159,376617,5824960,EPSG:25833"
OUTDIR=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\DerivedData\Trees_FalkenhagenerFeld"
NS={"wfs":"http://www.opengis.net/wfs/2.0","gml":"http://www.opengis.net/gml/3.2","b":"baumbestand"}

def fetch(t):
    q={"SERVICE":"WFS","VERSION":"2.0.0","REQUEST":"GetFeature","TYPENAMES":"baumbestand:"+t,
       "SRSNAME":"EPSG:25833","BBOX":BBOX,"COUNT":"10000"}
    u=BASE+"?"+urllib.parse.urlencode(q)
    with urllib.request.urlopen(u,timeout=90) as r:
        return r.read()

def text(e,name):
    x=e.find("b:"+name,NS)
    return (x.text or "").strip() if x is not None else ""

def parse(blob,t):
    root=ET.fromstring(blob)
    out=[]
    for m in root.findall("wfs:member",NS):
        feat=next(iter(m),None)
        if feat is None: continue
        p=feat.find(".//gml:pos",NS)
        if p is None or not p.text: continue
        e,n=map(float,p.text.split()[:2])
        out.append({"type":t,"gisid":text(feat,"gisid"),"species_de":text(feat,"art_dtsch"),
                    "species_bot":text(feat,"art_bot"),"genus":text(feat,"gattung"),
                    "plant_year":text(feat,"pflanzjahr"),"age":text(feat,"standalter"),
                    "crown_m":text(feat,"kronedurch"),"trunk_cm":text(feat,"stammumfg"),
                    "height_m":text(feat,"baumhoehe"),"street":text(feat,"strname"),
                    "district":text(feat,"bezirk"),"easting":e,"northing":n})
    return out

os.makedirs(OUTDIR,exist_ok=True)
rows=[]
for t in ("strassenbaeume","anlagenbaeume"):
    blob=fetch(t)
    open(os.path.join(OUTDIR,t+".gml"),"wb").write(blob)
    part=parse(blob,t)
    print(t,len(part))
    rows.extend(part)

json.dump(rows,open(os.path.join(OUTDIR,"trees.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=2)
with open(os.path.join(OUTDIR,"trees.csv"),"w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
print("TOTAL",len(rows))
