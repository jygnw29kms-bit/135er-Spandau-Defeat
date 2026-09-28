#!/usr/bin/env python3
import base64, json, os, time, urllib.request, urllib.error
from pathlib import Path
from PIL import Image, ImageStat

API="https://api.openai.com/v1/images/generations"
MODEL="gpt-image-2.5-sunburst"
SIZE="2048x1152"
QUALITY="xhigh"
OUT=Path("media/source2/masters/maps")
OUT.mkdir(parents=True, exist_ok=True)

BASE=(
"Create ONE standalone 16:9 full-resolution optical master reference for a Source 2 / Counter-Strike 2 map. "
"Photorealistic grounded environment visualization, believable Berlin materials, sharp architecture, physically plausible light, "
"clear tactical routes, cover silhouettes and sightlines, realistic scale, subtle wet-surface reflections where appropriate, "
"high micro-detail, crisp distance detail. No collage, no split screen, no contact sheet, no borders, no captions, no UI, "
"no logos, no watermark, no readable invented signage, no people. This is reference art, not an in-engine screenshot. "
)

MAPS=[
("rathaus-spandau","Rathaus Spandau", "Faithfully recognizable Rathaus Spandau at Carl-Schurz-Straße: long early-20th-century brick civic facade, prominent tall clock tower and the real forecourt/urban context. Autumn Berlin atmosphere after light rain. Do not substitute a generic town hall."),
("zitadelle-spandau","Zitadelle Spandau", "Faithfully recognizable Renaissance fortress geometry of Zitadelle Spandau: red brick ramparts, moat, bridge approach, bastions and Juliusturm presence. Tactical exterior routes but preserve the real landmark identity."),
("staaken","Staaken", "Berlin-Staaken residential urban environment: authentic west-Berlin edge-city mix, apartment blocks, local streets, mature trees and practical courtyards. Grounded, recognizable Spandau character, not a generic US city."),
("rodelberg","Rodelberg", "Spandau Rodelberg landscape: elevated grassy/wooded recreation hill, paths, stairs, embankments and nearby Berlin residential context. Strong elevation changes and tactical sightlines; autumn, damp ground."),
("kiesteich","Kiesteich", "Spandau Kiesteich: recognizable gravel-pit lake/pond landscape with reeds, shoreline paths, trees and adjacent urban context. Water and vegetation must dominate; realistic Berlin autumn."),
("falkenhagener-feld","Falkenhagener Feld", "Falkenhagener Feld in Spandau: recognizable large post-war residential blocks, broad pedestrian spaces, greenery, local transit/street furniture and courtyards. Dense but realistic Berlin housing-estate character."),
("lynarstrasse","Lynarstraße", "Lynarstraße Spandau: dense Berlin residential street with authentic brick/plaster apartment facades, parked cars, courtyards and local street proportions. Wet pavement, restrained dusk light, tactical cross-connections."),
("wroehmaennerpark","Wröhmännerpark", "Wröhmännerpark Spandau: real riverside park character, mature trees, paths, lawns, Havel-side edges and nearby urban fabric. Preserve open park sightlines and recognizable Berlin-Spandau atmosphere."),
("freiheit","Freiheit", "Freiheit Spandau industrial corridor: authentic Berlin industrial/rail-adjacent landscape, warehouses, service roads, fencing, utility structures and broad sightlines. No sci-fi industry; grounded German infrastructure."),
("martin-buber-schule","Martin-Buber-Schule", "Faithfully recognizable Martin-Buber-Oberschule campus in Spandau: modern low-rise school architecture, grey structural bays, courtyard landscaping and sports/campus context. Preserve the real architectural language; no students."),
("askanier-schule","Askanier-Schule", "Faithfully recognizable Askanier school campus in Spandau: low-rise school buildings, glazed classroom/corridor facades, brick-edged landscaped courtyard and mature trees. Preserve real proportions and campus identity; no students."),
("b-traven-schule","B.-Traven-Schule", "B.-Traven school campus in Spandau: believable and location-specific Berlin school architecture, connected low/mid-rise blocks, courtyards, sports/open areas and mature trees. Crisp architectural detail; no students."),
("fort-hahneberg-1945","Fort Hahneberg 1945", "Fort Hahneberg in spring 1945: faithfully recognizable brick-and-earth Prussian fort, overgrown ramparts, casemates, ditches and wooded approaches. Period-correct 1945 environment, weathering and limited battle damage; no modern objects, no propaganda symbols."),
("teufelsberg-kalter-krieg","Teufelsberg – Kalter Krieg", "Cold War Teufelsberg listening-station environment: hilltop compound, distinctive radar domes/radomes, service structures, perimeter routes and Berlin forest. Period-authentic Cold War mood, no modern tourist clutter."),
("flugplatz-gatow-1945","Flugplatz Gatow 1945", "Gatow airfield in 1945: period-correct runway/taxiway, hangars, airfield service buildings and open grass field in west Berlin. Historically grounded late-war wear and damage, no modern aircraft or objects, no propaganda symbols."),
("gatow-luftbruecke-1948","Gatow – Luftbrücke 1948", "RAF Gatow during the 1948 Berlin Airlift: period-correct airfield, runway, hangars, stacked cargo and transport-aircraft operations visible only as environmental context; no close-up people. Historically grounded late-1940s materials and vehicles."),
("radelandstrasse-1945","Radelandstraße 1945", "Radelandstraße Spandau in 1945: period-correct suburban/wooded Berlin road environment, brick and plaster buildings, fences, damaged street surfaces and restrained wartime debris. No modern objects, no propaganda symbols."),
("hakenfelde-heeresamt-1944","Hakenfelde – Heeresamt 1944", "Hakenfelde military-administration complex context in 1944: period-correct German institutional brick architecture, courtyards, service roads, forest edge and utility structures. Neutral historical depiction, no people, no propaganda symbols."),
("zitadelle-1-mai-1945","Zitadelle – 1. Mai 1945", "Zitadelle Spandau on 1 May 1945: faithfully recognizable fortress, moat, bridge and brick ramparts with historically plausible late-war damage and debris. Somber neutral historical environment, no people, no flags or propaganda symbols."),
("britischer-sektor-spandau","Britischer Sektor Spandau", "Post-war British Sector Spandau, late 1940s/1950s: recognizable west-Spandau urban fabric with period-correct British occupation infrastructure, checkpoints/administrative details, brick streetscape and vehicles as distant props. Neutral historical depiction, no people.")
]

def generate(prompt):
    key=os.environ["OPENAI_API_KEY"]
    payload=json.dumps({
        "model":MODEL,"prompt":prompt,"size":SIZE,"quality":QUALITY,
        "output_format":"jpeg","output_compression":92,"background":"opaque","moderation":"auto"
    }).encode()
    req=urllib.request.Request(API,data=payload,method="POST",headers={
        "Authorization":f"Bearer {key}","Content-Type":"application/json"
    })
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req,timeout=420) as resp:
                data=json.loads(resp.read())
            return base64.b64decode(data["data"][0]["b64_json"])
        except Exception as e:
            if attempt==2: raise
            print(f"retry after {e}", flush=True); time.sleep(8*(attempt+1))

def verify(path):
    if path.stat().st_size < 250_000:
        raise RuntimeError(f"{path}: suspiciously small ({path.stat().st_size} bytes)")
    with Image.open(path) as im:
        if im.size != (2048,1152):
            raise RuntimeError(f"{path}: wrong dimensions {im.size}")
        gray=im.convert("L").resize((512,288))
        stat=ImageStat.Stat(gray)
        if stat.var[0] < 250:
            raise RuntimeError(f"{path}: insufficient tonal/detail variance {stat.var[0]:.1f}")
    return True

for idx,(slug,name,specific) in enumerate(MAPS,1):
    path=OUT/f"{slug}-master-reference.jpg"
    prompt=BASE+specific+f" Map identity: {name}. Render one coherent camera view only."
    print(f"[{idx:02d}/20] rendering {name}",flush=True)
    raw=generate(prompt)
    tmp=path.with_suffix(".tmp.jpg")
    tmp.write_bytes(raw)
    verify(tmp)
    tmp.replace(path)
    print(f"  OK {path} {path.stat().st_size//1024} KiB",flush=True)

# README gallery: only publish after all 20 passed verification.
readme=Path("README.md")
text=readme.read_text(encoding="utf-8")
start=text.index("### MASTER-REFERENCE QUALITY GATE")
end=text.index("\\nThe optical master defines:",start)
rows="\\n".join(f'| {name} | <img src="media/source2/masters/maps/{slug}-master-reference.jpg" width="560" alt="{name} AI optical master"> |' for slug,name,_ in MAPS)
section=f"""### FULL-RESOLUTION MAP MASTER REFERENCES

All 20 images below are individually generated **2048×1152** AI optical-master references. They are not crops, not upscaled contact-sheet cells and not genuine Source 2 screenshots. Each file passed the repository resolution/file/detail gate before publication.

| Map | Master reference |
|---|---|
{rows}

"""
text=text[:start]+section+text[end+1:]
readme.write_text(text,encoding="utf-8")
print("All 20 masters verified; README gallery updated.",flush=True)

# workflow trigger: full-resolution master render
