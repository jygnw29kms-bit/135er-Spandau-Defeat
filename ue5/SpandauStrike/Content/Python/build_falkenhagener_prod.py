# -*- coding: utf-8 -*-
import unreal, math, json, urllib.request, urllib.parse, traceback, time
import berlin_spandau_lyra_import as gis

LEVEL="/Game/Maps/BerlinSpandau/falkenhagener_feld_prod_v2"
TERRAIN="/Game/SpandauStrikeGIS/Terrain/falkenhagener_dgm_257.falkenhagener_dgm_257"
OBJ=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\SourceData\DGM1\falkenhagener_dgm_257.obj"
LAT=52.5524034
LON=13.1668941
HALF=900.0
N=257
UU=100.0
STEP=(2.0*HALF)/(N-1)
OVERPASS="https://overpass-api.de/api/interpreter"
ROOT="SpandauStrike_PROD"
def log(s): unreal.log("[SS_PROD] "+str(s))

def load_heights():
    vals=[]
    with open(OBJ,"r",encoding="ascii",errors="ignore") as f:
        for line in f:
            if line.startswith("v "):
                vals.append(float(line.split()[3])/100.0)
                if len(vals)==N*N:
                    break
    if len(vals)!=N*N:
        raise RuntimeError("DGM vertex count %d" % len(vals))
    return vals

HEIGHTS=load_heights()

def hxy(x_m,y_m):
    i=max(0,min(N-1,int(round((x_m+HALF)/STEP))))
    north_m=-y_m
    j=max(0,min(N-1,int(round((north_m+HALF)/STEP))))
    return HEIGHTS[j*N+i]
def h_en(e,n,ce,cn):
    return hxy(e-ce,-(n-cn))

def spawn_mesh(mesh,mat,label,loc,scale,folder,yaw=0):
    a=unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,loc,unreal.Rotator(pitch=0.0,yaw=yaw,roll=0.0))
    a.static_mesh_component.set_static_mesh(mesh)
    if mat: a.static_mesh_component.set_material(0,mat)
    a.set_actor_scale3d(scale)
    a.set_actor_label(label)
    a.set_folder_path(folder)
    try:
        a.static_mesh_component.set_collision_profile_name("BlockAll")
        a.static_mesh_component.set_editor_property("can_ever_affect_navigation",True)
    except Exception: pass
    return a

def fetch_osm():
    dl=HALF/111320.0
    dn=HALF/(111320.0*math.cos(math.radians(LAT)))
    s,w,n,e=LAT-dl,LON-dn,LAT+dl,LON+dn
    q=f'''[out:json][timeout:60];(
way["highway"]({s},{w},{n},{e});
way["waterway"]({s},{w},{n},{e});
way["natural"="water"]({s},{w},{n},{e});
);out geom;'''
    req=urllib.request.Request(OVERPASS,
        data=urllib.parse.urlencode({"data":q}).encode(),
        headers={"User-Agent":"SpandauStrike-PROD/1.0"})
    with urllib.request.urlopen(req,timeout=75) as r:
        return json.loads(r.read().decode())
def road_width(tags):
    return {"motorway":12,"trunk":11,"primary":10,"secondary":9,"tertiary":8,
            "residential":6,"living_street":5,"service":4,"cycleway":2.5,
            "footway":2,"path":1.8,"track":3}.get(tags.get("highway",""),4.5)

def add_segment(mesh,mat,a,b,width,z_m,folder,label):
    dx=b.x-a.x; dy=b.y-a.y
    length=math.hypot(dx,dy)/UU
    if length<0.5 or length>2000: return False
    mid=unreal.Vector((a.x+b.x)/2,(a.y+b.y)/2,z_m*UU+8)
    yaw=math.degrees(math.atan2(dy,dx))
    spawn_mesh(mesh,mat,label,mid,unreal.Vector(length,width,0.08),folder,yaw)
    return True

def add_environment():
    sun=unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.DirectionalLight,unreal.Vector(0,0,50000),unreal.Rotator(pitch=-35.0,yaw=-25.0,roll=0.0))
    sun.set_actor_label("Sun"); sun.set_folder_path(ROOT+"/Environment")
    try: sun.light_component.set_editor_property("intensity",5.0)
    except Exception: pass
    sky=unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SkyLight,unreal.Vector(0,0,2000),unreal.Rotator())
    sky.set_actor_label("SkyLight"); sky.set_folder_path(ROOT+"/Environment")
    for cls,name in ((unreal.SkyAtmosphere,"SkyAtmosphere"),):
        try:
            a=unreal.EditorLevelLibrary.spawn_actor_from_class(cls,unreal.Vector(),unreal.Rotator())
            a.set_actor_label(name); a.set_folder_path(ROOT+"/Environment")
        except Exception as exc: log(name+" skipped "+str(exc))

def add_gameplay():
    cls=unreal.load_class(None,"/Script/LyraGame.LyraPlayerStart") or unreal.PlayerStart
    coords=[(-650,-500),(650,500),(-650,500),(650,-500),
            (-500,0),(500,0),(0,-500),(0,500)]
    for i,(x,y) in enumerate(coords):
        z=hxy(x,y)*UU+160
        a=unreal.EditorLevelLibrary.spawn_actor_from_class(
            cls,unreal.Vector(x*UU,y*UU,z),unreal.Rotator())
        a.set_actor_label("SS_PlayerStart_%02d"%(i+1))
        a.set_folder_path(ROOT+"/Gameplay/PlayerStarts")
    try:
        nav=unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.NavMeshBoundsVolume,unreal.Vector(0,0,10000),unreal.Rotator())
        nav.set_actor_label("SS_NavMeshBounds")
        nav.set_folder_path(ROOT+"/Gameplay")
        nav.set_actor_scale3d(unreal.Vector(1000,1000,250))
    except Exception as exc: log("Nav volume skipped "+str(exc))
def main():
    t0=time.perf_counter()
    ce,cn=gis.wgs84_to_utm33(LAT,LON)
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.new_level(LEVEL,True):
        raise RuntimeError("new_level failed "+LEVEL)
    cube=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube.Cube")
    terrain_mat=unreal.EditorAssetLibrary.load_asset("/Game/SpandauStrikeGIS/Materials/M_SS_Terrain.M_SS_Terrain")
    building_mat=unreal.EditorAssetLibrary.load_asset("/Game/SpandauStrikeGIS/Materials/M_SS_Building.M_SS_Building")
    road_mat=unreal.EditorAssetLibrary.load_asset("/Game/SpandauStrikeGIS/Materials/M_SS_Road.M_SS_Road")
    water_mat=unreal.EditorAssetLibrary.load_asset("/Game/SpandauStrikeGIS/Materials/M_SS_Water.M_SS_Water")
    terrain=unreal.EditorAssetLibrary.load_asset(TERRAIN)
    if not terrain or not cube or not all((terrain_mat,building_mat,road_mat,water_mat)):
        raise RuntimeError("required mesh/material missing")
    ta=spawn_mesh(terrain,terrain_mat,"DGM1_Terrain_Real",unreal.Vector(),
                  unreal.Vector(1,1,1),ROOT+"/Terrain")
    log("terrain actor ready")

    bbox=(ce-HALF,cn-HALF,ce+HALF,cn+HALF)
    ft=gis.discover_feature_type()
    root=gis.download_features(ft,bbox)
    records=[]
    for f in gis.feature_members(root):
        r=gis.build_record(f)
        if r: records.append(r)
    log("buildings records=%d"%len(records))
    bc=0
    for r in records:
        x=(r["cx"]-ce); y=-(r["cy"]-cn)
        base=hxy(x,y)
        loc=unreal.Vector(x*UU,y*UU,(base+r["height"]*0.5)*UU)
        try:
            a=spawn_mesh(cube,building_mat,"BLN_"+str(r["id"])[-36:],
                loc,unreal.Vector(r["width"],r["depth"],r["height"]),
                ROOT+"/Buildings",-r["angle"])
            a.set_editor_property("tags",["BerlinGIS","HeightM=%.2f"%r["height"],
                "RoofType="+r["roof"],"Function="+r["function"]])
            bc+=1
        except Exception as exc:
            if bc<5: log("building failed "+str(exc))

    data=fetch_osm(); roads=waters=0
    for el in data.get("elements",[]):
        geom=el.get("geometry") or []; tags=el.get("tags",{})
        if len(geom)<2: continue
        isroad="highway" in tags
        pts=[]
        for p in geom:
            e,n=gis.wgs84_to_utm33(p["lat"],p["lon"])
            x=(e-ce); y=-(n-cn)
            pts.append((unreal.Vector(x*UU,y*UU,0),hxy(x,y)))
        width=road_width(tags) if isroad else (8.0 if "waterway" in tags else 18.0)
        for i in range(len(pts)-1):
            z=(pts[i][1]+pts[i+1][1])*0.5
            if isroad:
                if add_segment(cube,road_mat,pts[i][0],pts[i+1][0],width,z,
                               ROOT+"/Roads","Road_%05d"%roads): roads+=1
            else:
                if add_segment(cube,water_mat,pts[i][0],pts[i+1][0],width,z-0.10,
                               ROOT+"/Water","Water_%05d"%waters): waters+=1

    add_environment()
    add_gameplay()
    if not sub.save_current_level(): raise RuntimeError("save failed")
    log("READY buildings=%d roads=%d water=%d runtime=%.1fs"%
        (bc,roads,waters,time.perf_counter()-t0))

if __name__=="__main__":
    try: main()
    except Exception as exc:
        unreal.log_error("[SS_PROD] FAILED "+str(exc))
        unreal.log_error(traceback.format_exc())
        raise

