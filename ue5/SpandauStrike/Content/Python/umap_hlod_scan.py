from pathlib import Path
p=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Plugins\GameFeatures\ShooterMaps\Content\Maps\SpandauStrikeGIS\falkenhagener_feld.umap")
b=p.read_bytes()
needles=[b"falkenhagener_feld_HLODLayer_Instanced",b"falkenhagener_feld_HLODLayer_Merged",b"HLODLayer"]
def printable(bs):
    out=[]
    cur=[]
    for x in bs:
        if 32<=x<127:
            cur.append(chr(x))
        else:
            if len(cur)>=3: out.append("".join(cur))
            cur=[]
    if len(cur)>=3: out.append("".join(cur))
    return out
for n in needles:
    start=0
    while True:
        i=b.find(n,start)
        if i<0: break
        lo=max(0,i-1200); hi=min(len(b),i+1800)
        print("\n[UMAPHLOD] needle",n.decode(),"offset",i)
        for s in printable(b[lo:hi]):
            print("[UMAPHLOD]",s)
        start=i+1
