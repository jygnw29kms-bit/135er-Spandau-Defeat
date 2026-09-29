# -*- coding: utf-8 -*-
import unreal
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import math
import re
import time
import traceback

ACTIVE_MAP = "falkenhagener_feld"
HALF_EXTENT_M = 900.0
EPSG = "EPSG:25833"
UU_PER_M = 100.0
DEFAULT_HEIGHT_M = 10.0
ROOT_FOLDER = "Berlin_LoD2_Autonomous_Import"
LEVEL_ROOT = "/Game/Maps/BerlinSpandau"
CREATE_PARTITIONED_WORLD = True
CUBE_MESH = "/Engine/BasicShapes/Cube.Cube"
GRID_MATERIAL = "/Engine/EngineMaterials/WorldGridMaterial.WorldGridMaterial"
WFS_BASE_URL = "https://gdi.berlin.de/services/wfs/ua_gebaeudehoehen"
TIMEOUT = 45
RETRIES = 3

MAP_QUERIES = {
    "rathaus_spandau": "Rathaus Spandau, Berlin",
    "zitadelle": "Zitadelle Spandau, Berlin",
    "staaken": "Staaken, Berlin",
    "rodelberg": "Rodelberg Spandau, Berlin",
    "kiesteich": "Kiesteich Spandau, Berlin",
    "falkenhagener_feld": "Falkenhagener Feld, Berlin",
    "lynarstrasse": "Lynarstraße Spandau, Berlin",
    "wroehmaennerpark": "Wröhmännerpark, Berlin",
    "freiheit": "Freiheit Spandau, Berlin",
    "martin_buber_schule": "Martin-Buber-Oberschule Berlin Spandau",
    "askanier_schule": "Askanier-Grundschule Berlin Spandau",
    "b_traven_schule": "B.-Traven-Gemeinschaftsschule Berlin Spandau",
    "fort_hahneberg_1945": "Fort Hahneberg, Berlin",
    "teufelsberg_coldwar": "Teufelsberg, Berlin",
    "flugplatz_gatow_1945": "Flugplatz Gatow, Berlin",
    "gatow_luftbruecke_1948": "Flugplatz Gatow, Berlin",
    "radeland_1945": "Radelandstraße Spandau, Berlin",
    "hakenfelde_heeresamt_1944": "Hakenfelde, Berlin",
    "zitadelle_1945": "Zitadelle Spandau, Berlin",
    "britischer_sektor_spandau": "Spandau, Berlin",
}

def log(msg):
    unreal.log("[LYRA_GIS] " + str(msg))

def warn(msg):
    unreal.log_warning("[LYRA_GIS] " + str(msg))

def lname(tag):
    return tag.split("}", 1)[-1]

def http_get(url, accept="*/*"):
    last = None
    for attempt in range(RETRIES):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "UE5-Lyra-Berlin-Spandau-GIS/1.0",
                "Accept": accept})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                return response.read()
        except Exception as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError("HTTP failed: %s" % last)

def geocode_map(map_id):
    query = MAP_QUERIES[map_id]
    params = urllib.parse.urlencode({
        "q": query,
        "format": "jsonv2",
        "limit": 1,
        "countrycodes": "de",
        "viewbox": "13.05,52.65,13.35,52.40",
        "bounded": 1})
    data = http_get(
        "https://nominatim.openstreetmap.org/search?" + params,
        "application/json")
    hits = json.loads(data.decode("utf-8"))
    if not hits:
        raise RuntimeError("No geocoding result for " + query)
    return float(hits[0]["lat"]), float(hits[0]["lon"])
def wgs84_to_utm33(lat, lon):
    a = 6378137.0
    f = 1 / 298.257223563
    k0 = 0.9996
    e2 = f * (2 - f)
    ep2 = e2 / (1 - e2)
    phi = math.radians(lat)
    lam = math.radians(lon)
    lam0 = math.radians(15.0)
    n = a / math.sqrt(1 - e2 * math.sin(phi) ** 2)
    t = math.tan(phi) ** 2
    c = ep2 * math.cos(phi) ** 2
    aa = math.cos(phi) * (lam - lam0)
    m = a * ((1 - e2/4 - 3*e2**2/64 - 5*e2**3/256) * phi
        - (3*e2/8 + 3*e2**2/32 + 45*e2**3/1024) * math.sin(2*phi)
        + (15*e2**2/256 + 45*e2**3/1024) * math.sin(4*phi)
        - (35*e2**3/3072) * math.sin(6*phi))
    e = k0 * n * (aa + (1-t+c) * aa**3 / 6
        + (5-18*t+t*t+72*c-58*ep2) * aa**5 / 120) + 500000
    no = k0 * (m + n * math.tan(phi) * (
        aa*aa/2 + (5-t+9*c+4*c*c) * aa**4/24
        + (61-58*t+t*t+600*c-330*ep2) * aa**6/720))
    return e, no

def discover_feature_type():
    params = urllib.parse.urlencode({
        "SERVICE": "WFS",
        "REQUEST": "GetCapabilities"})
    root = ET.fromstring(http_get(
        WFS_BASE_URL + "?" + params,
        "application/xml"))
    scored = []
    for node in root.iter():
        if lname(node.tag) != "FeatureType":
            continue
        name = title = ""
        for child in node:
            if lname(child.tag) == "Name" and child.text:
                name = child.text.strip()
            if lname(child.tag) == "Title" and child.text:
                title = child.text.strip()
        if name:
            text = (name + " " + title).lower()
            score = (10 if "geb" in text else 0)
            score += (10 if "hoehe" in text or "höhe" in text else 0)
            scored.append((score, name))
    if not scored:
        raise RuntimeError("No WFS feature type found")
    scored.sort(reverse=True)
    return scored[0][1]

def download_features(feature_type, bbox):
    bbox_text = "%f,%f,%f,%f,%s" % (*bbox, EPSG)
    for version, key in (("2.0.0","TYPENAMES"),("1.1.0","TYPENAME")):
        params = {
            "SERVICE": "WFS",
            "VERSION": version,
            "REQUEST": "GetFeature",
            key: feature_type,
            "SRSNAME": EPSG,
            "BBOX": bbox_text}
        try:
            data = http_get(
                WFS_BASE_URL + "?" + urllib.parse.urlencode(params),
                "application/xml")
            root = ET.fromstring(data)
            if "exception" not in lname(root.tag).lower():
                return root
        except Exception as exc:
            warn("WFS %s failed: %s" % (version, exc))
    raise RuntimeError("All WFS queries failed")

def safe_float(value, default=None):
    if value is None:
        return default
    match = re.search(r"[-+]?\d+(?:[.,]\d+)?", str(value))
    return float(match.group(0).replace(",", ".")) if match else default

def attr(feature, names):
    wanted = {n.lower() for n in names}
    for node in feature.iter():
        if lname(node.tag).lower() in wanted and node.text and node.text.strip():
            return node.text.strip()
    return None

def parse_ring(feature):
    rings = []
    for node in feature.iter():
        if lname(node.tag) != "posList" or not node.text:
            continue
        vals = [safe_float(x) for x in node.text.split()]
        vals = [x for x in vals if x is not None]
        dim = int(node.attrib.get("srsDimension", "2"))
        if dim not in (2, 3):
            dim = 2
        pts = []
        for i in range(0, len(vals) - dim + 1, dim):
            pts.append((
                vals[i],
                vals[i+1],
                vals[i+2] if dim == 3 else 0.0))
        if len(pts) >= 3:
            rings.append(pts)
    if not rings:
        return None

    def area(points):
        total = 0.0
        for i in range(len(points)):
            x1, y1, _ = points[i]
            x2, y2, _ = points[(i+1) % len(points)]
            total += x1*y2 - x2*y1
        return abs(total) * 0.5

    rings.sort(key=area, reverse=True)
    return rings[0]

def feature_members(root):
    out = []
    for node in root.iter():
        if lname(node.tag) in ("member", "featureMember") and list(node):
            out.append(list(node)[0])
    return out
def dominant_box(points):
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    sxx = syy = sxy = 0.0
    for x, y, _ in points:
        dx = x - cx
        dy = y - cy
        sxx += dx*dx
        syy += dy*dy
        sxy += dx*dy
    angle = 0.5 * math.atan2(2*sxy, sxx-syy)
    ca, sa = math.cos(angle), math.sin(angle)
    rotated = [
        ((x-cx)*ca + (y-cy)*sa, -(x-cx)*sa + (y-cy)*ca)
        for x, y, _ in points]
    width = max(x for x,y in rotated) - min(x for x,y in rotated)
    depth = max(y for x,y in rotated) - min(y for x,y in rotated)
    return cx, cy, width, depth, math.degrees(angle)

def build_record(feature):
    ring = parse_ring(feature)
    if not ring:
        return None
    cx, cy, width, depth, angle = dominant_box(ring)
    if width < 1.0 or depth < 1.0:
        return None
    height = safe_float(attr(feature, ["hoehe"]), DEFAULT_HEIGHT_M)
    if not height or height < 2.0 or height > 300.0:
        height = DEFAULT_HEIGHT_M

    z_values = [p[2] for p in ring if abs(p[2]) > 0.001]
    base_z = min(z_values) if z_values else 0.0

    return {
        "id": attr(feature, ["gml_id"]) or attr(feature, ["gisid"]) or "building",
        "name": attr(feature, ["name"]) or "",
        "function": attr(feature, ["funktion_txt", "efunktion_txt", "funktion"]) or "",
        "roof": attr(feature, ["dachart_txt", "edachart_txt", "dachart"]) or "unknown",
        "floors": attr(feature, ["geschosse"]) or "",
        "street": attr(feature, ["strasse"]) or "",
        "house_number": attr(feature, ["hnr"]) or "",
        "cx": cx, "cy": cy, "width": width, "depth": depth,
        "height": height, "base_z": base_z, "angle": angle
    }

def remove_previous(folder):
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        try:
            current = str(actor.get_folder_path())
            if current == folder or current.startswith(folder + "/"):
                unreal.EditorLevelLibrary.destroy_actor(actor)
        except Exception:
            pass
def spawn_building(record, origin, folder, mesh, material):
    x = (record["cx"] - origin[0]) * UU_PER_M
    y = -(record["cy"] - origin[1]) * UU_PER_M
    z = (record["base_z"] - origin[2]) * UU_PER_M
    z += record["height"] * UU_PER_M * 0.5

    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(x, y, z),
        unreal.Rotator(0.0, -record["angle"], 0.0))
    if not actor:
        raise RuntimeError("StaticMeshActor spawn failed")

    component = actor.static_mesh_component
    component.set_static_mesh(mesh)
    actor.set_actor_scale3d(unreal.Vector(
        record["width"], record["depth"], record["height"]))

    if material:
        component.set_material(0, material)

    actor.set_folder_path(folder)
    clean_id = re.sub(r"[^A-Za-z0-9_]+", "_", str(record["id"]))[-48:]
    actor.set_actor_label("BLN_" + clean_id)

    tags = [
        "BerlinGIS",
        "GML_ID=" + str(record["id"]),
        "HeightM=%.2f" % record["height"],
        "RoofType=" + record["roof"],
        "Function=" + record["function"],
        "Floors=" + record["floors"]]
    if record["name"]:
        tags.append("Name=" + record["name"])
    address = (record["street"] + " " + record["house_number"]).strip()
    if address:
        tags.append("Address=" + address)
    actor.set_editor_property("tags", tags)

    try:
        component.set_editor_property("can_ever_affect_navigation", True)
    except Exception:
        pass
    return actor

def main():
    started = time.perf_counter()

    if ACTIVE_MAP not in MAP_QUERIES:
        raise RuntimeError("Unknown ACTIVE_MAP: " + ACTIVE_MAP)

    log("Active map: " + ACTIVE_MAP)
    lat, lon = geocode_map(ACTIVE_MAP)
    center_e, center_n = wgs84_to_utm33(lat, lon)
    bbox = (
        center_e - HALF_EXTENT_M,
        center_n - HALF_EXTENT_M,
        center_e + HALF_EXTENT_M,
        center_n + HALF_EXTENT_M)

    log("Resolved %.6f, %.6f -> EPSG:25833 %.2f, %.2f" % (
        lat, lon, center_e, center_n))
    feature_type = discover_feature_type()
    log("WFS feature type: " + feature_type)

    root = download_features(feature_type, bbox)
    raw_features = feature_members(root)
    records = []
    for feature in raw_features:
        record = build_record(feature)
        if record:
            records.append(record)

    if not records:
        raise RuntimeError("No usable buildings returned for selected map")

    valid_bases = [r["base_z"] for r in records if abs(r["base_z"]) > 0.001]
    origin_z = sorted(valid_bases)[len(valid_bases)//2] if valid_bases else 0.0
    origin = (center_e, center_n, origin_z)

    mesh = unreal.EditorAssetLibrary.load_asset(CUBE_MESH)
    material = unreal.EditorAssetLibrary.load_asset(GRID_MATERIAL)
    if not mesh:
        raise RuntimeError("Missing engine cube mesh: " + CUBE_MESH)

    level_path = LEVEL_ROOT + "/" + ACTIVE_MAP
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not level_subsystem:
        raise RuntimeError("LevelEditorSubsystem unavailable")

    if not level_subsystem.new_level(level_path, CREATE_PARTITIONED_WORLD):
        raise RuntimeError("Failed to create level: " + level_path)

    log("Created World Partition level: " + level_path)

    map_root = ROOT_FOLDER + "/" + ACTIVE_MAP
    folder = map_root + "/Buildings"

    created = []
    with unreal.ScopedSlowTask(
            len(records), "Importing Berlin GIS: " + ACTIVE_MAP) as task:
        task.make_dialog(True)
        for index, record in enumerate(records, 1):
            if task.should_cancel():
                warn("Import cancelled by user")
                break
            task.enter_progress_frame(
                1.0, "Building %d/%d" % (index, len(records)))
            try:
                created.append(spawn_building(
                    record, origin, folder, mesh, material))
            except Exception as exc:
                warn("Building %s failed: %s" % (record["id"], exc))

    if not level_subsystem.save_current_level():
        warn("Automatic level save returned false")
    else:
        log("Saved level: " + level_path)

    elapsed = time.perf_counter() - started
    log("BBOX: %.0f m x %.0f m" % (
        HALF_EXTENT_M * 2.0, HALF_EXTENT_M * 2.0))
    log("WFS features received: %d" % len(raw_features))
    log("Usable building records: %d" % len(records))
    log("Actors created: %d" % len(created))
    log("Outliner: " + folder)
    log("Runtime: %.2f seconds" % elapsed)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        unreal.log_error("[LYRA_GIS] FAILED: " + str(exc))
        unreal.log_error(traceback.format_exc())
        raise
