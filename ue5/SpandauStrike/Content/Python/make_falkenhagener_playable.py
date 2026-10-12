# -*- coding: utf-8 -*-
import unreal, urllib.request, urllib.parse, json, math, time, traceback

MAP_PATH = "/Game/Maps/BerlinSpandau/falkenhagener_feld"
CENTER_LAT = 52.5524034
CENTER_LON = 13.1668941
HALF_EXTENT_M = 900.0
UU = 100.0
ROOT = "Berlin_Playable"
CUBE = "/Engine/BasicShapes/Cube.Cube"
OVERPASS = "https://overpass-api.de/api/interpreter"

def log(s): unreal.log("[PLAYABLE] " + str(s))

def wgs84_to_utm33(lat, lon):
    a=6378137.0; f=1/298.257223563; k0=0.9996; e2=f*(2-f); ep2=e2/(1-e2)
    p=math.radians(lat); l=math.radians(lon); l0=math.radians(15.0)
    n=a/math.sqrt(1-e2*math.sin(p)**2); t=math.tan(p)**2; c=ep2*math.cos(p)**2
    aa=math.cos(p)*(l-l0)
    m=a*((1-e2/4-3*e2**2/64-5*e2**3/256)*p-(3*e2/8+3*e2**2/32+45*e2**3/1024)*math.sin(2*p)+(15*e2**2/256+45*e2**3/1024)*math.sin(4*p)-(35*e2**3/3072)*math.sin(6*p))
    e=k0*n*(aa+(1-t+c)*aa**3/6+(5-18*t+t*t+72*c-58*ep2)*aa**5/120)+500000
    no=k0*(m+n*math.tan(p)*(aa*aa/2+(5-t+9*c+4*c*c)*aa**4/24+(61-58*t+t*t+600*c-330*ep2)*aa**6/720))
    return e,no

ORIGIN_E, ORIGIN_N = wgs84_to_utm33(CENTER_LAT,CENTER_LON)
def xy(lat,lon,z=0.0):
    e,n=wgs84_to_utm33(lat,lon)
    return unreal.Vector((e-ORIGIN_E)*UU, -(n-ORIGIN_N)*UU, z*UU)

def spawn_box(label, loc, sx, sy, sz, folder, yaw=0.0):
    mesh=unreal.EditorAssetLibrary.load_asset(CUBE)
    a=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor,loc,unreal.Rotator(0,yaw,0))
    a.static_mesh_component.set_static_mesh(mesh)
    a.set_actor_scale3d(unreal.Vector(sx,sy,sz))
    a.set_actor_label(label); a.set_folder_path(folder)
    return a

def segment(a,b,width_m,z_m,folder,prefix,idx):
    dx=b.x-a.x; dy=b.y-a.y; length=math.hypot(dx,dy)/UU
    if length<0.5: return None
    mid=unreal.Vector((a.x+b.x)/2,(a.y+b.y)/2,z_m*UU)
    yaw=math.degrees(math.atan2(dy,dx))
    return spawn_box(f"{prefix}_{idx:05d}",mid,length,width_m,0.08,folder,yaw)

def overpass():
    dlat=HALF_EXTENT_M/111320.0
    dlon=HALF_EXTENT_M/(111320.0*math.cos(math.radians(CENTER_LAT)))
    s,w,n,e=CENTER_LAT-dlat,CENTER_LON-dlon,CENTER_LAT+dlat,CENTER_LON+dlon
    q=f'''[out:json][timeout:45];(
      way["highway"]({s},{w},{n},{e});
      way["waterway"]({s},{w},{n},{e});
      way["natural"="water"]({s},{w},{n},{e});
    );out geom;'''
    req=urllib.request.Request(OVERPASS,data=urllib.parse.urlencode({"data":q}).encode(),headers={"User-Agent":"SpandauStrike-UE5/1.0"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))
def road_width(tags):
    h=tags.get("highway","")
    return {"motorway":12,"trunk":11,"primary":10,"secondary":9,"tertiary":8,
            "residential":6,"living_street":5,"service":4,"cycleway":2.5,"footway":2,
            "path":1.8,"track":3}.get(h,5)

def add_environment():
    spawn_box("Ground",unreal.Vector(0,0,-50),HALF_EXTENT_M*2,HALF_EXTENT_M*2,1,ROOT+"/Ground")
    sun=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,50000),unreal.Rotator(-35,-25,0))
    sun.set_actor_label("Sun"); sun.set_folder_path(ROOT+"/Lighting")
    try: sun.light_component.set_editor_property("intensity",7.0)
    except: pass
    sky=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,2000),unreal.Rotator())
    sky.set_actor_label("SkyLight"); sky.set_folder_path(ROOT+"/Lighting")
    try:
        atm=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere,unreal.Vector(),unreal.Rotator())
        atm.set_actor_label("SkyAtmosphere"); atm.set_folder_path(ROOT+"/Lighting")
    except: pass

def add_osm():
    data=overpass(); rc=wc=0
    for el in data.get("elements",[]):
        g=el.get("geometry") or []; tags=el.get("tags",{})
        if len(g)<2: continue
        pts=[xy(p["lat"],p["lon"],0.04 if "highway" in tags else 0.02) for p in g]
        if "highway" in tags:
            width=road_width(tags)
            for i in range(len(pts)-1):
                if segment(pts[i],pts[i+1],width,0.04,ROOT+"/Roads","Road",rc): rc+=1
        else:
            width=8.0 if "waterway" in tags else 20.0
            for i in range(len(pts)-1):
                if segment(pts[i],pts[i+1],width,0.02,ROOT+"/Water","Water",wc): wc+=1
    log(f"OSM road segments: {rc}, water segments: {wc}")
def add_spawns():
    cls=unreal.load_class(None,"/Script/LyraGame.LyraPlayerStart")
    if not cls: cls=unreal.PlayerStart
    coords=[(-650,-500),(650,500),(-650,500),(650,-500),(-500,0),(500,0),(0,-500),(0,500)]
    for i,(x,y) in enumerate(coords):
        a=unreal.EditorLevelLibrary.spawn_actor_from_class(cls,unreal.Vector(x*UU,y*UU,150),unreal.Rotator())
        a.set_actor_label(f"SS_PlayerStart_{i+1:02d}"); a.set_folder_path(ROOT+"/Gameplay/PlayerStarts")
    log("PlayerStarts: 8")

def add_camera():
    cam=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(-35000,35000,25000),unreal.Rotator(-25,-45,0))
    cam.set_actor_label("SS_OverviewCamera"); cam.set_folder_path(ROOT+"/Cameras")
    return cam

def main():
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP_PATH): raise RuntimeError("Cannot load "+MAP_PATH)
    add_environment(); add_osm(); add_spawns(); add_camera()
    if not sub.save_current_level(): raise RuntimeError("Save failed")
    log("PLAYABLE_BASE_READY")

if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[PLAYABLE] FAILED "+str(e)); unreal.log_error(traceback.format_exc()); raise
