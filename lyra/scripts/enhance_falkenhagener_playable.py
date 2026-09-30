# -*- coding: utf-8 -*-
import unreal, urllib.request, urllib.parse, json, math, traceback

MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
LAT=52.5524034
LON=13.1668941
HALF=900.0
UU=100.0
ROOT="SpandauStrike_GIS_Overlay"
CUBE="/Engine/BasicShapes/Cube.Cube"
MAT="/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"
OVERPASS="https://overpass-api.de/api/interpreter"

def log(s): unreal.log("[SS_GIS] "+str(s))

def utm(lat,lon):
    a=6378137.0; f=1/298.257223563; k=.9996
    e2=f*(2-f); ep=e2/(1-e2); p=math.radians(lat); l=math.radians(lon); l0=math.radians(15)
    n=a/math.sqrt(1-e2*math.sin(p)**2); t=math.tan(p)**2; c=ep*math.cos(p)**2; aa=math.cos(p)*(l-l0)
    m=a*((1-e2/4-3*e2**2/64-5*e2**3/256)*p-(3*e2/8+3*e2**2/32+45*e2**3/1024)*math.sin(2*p)+(15*e2**2/256+45*e2**3/1024)*math.sin(4*p)-(35*e2**3/3072)*math.sin(6*p))
    return (k*n*(aa+(1-t+c)*aa**3/6+(5-18*t+t*t+72*c-58*ep)*aa**5/120)+500000,
            k*(m+n*math.tan(p)*(aa*aa/2+(5-t+9*c+4*c*c)*aa**4/24+(61-58*t+t*t+600*c-330*ep)*aa**6/720)))
OE,ON=utm(LAT,LON)
def pos(lat,lon,zcm):
    e,n=utm(lat,lon)
    return unreal.Vector((e-OE)*UU,-(n-ON)*UU,zcm)

def fetch():
    dl=HALF/111320.0; dn=HALF/(111320.0*math.cos(math.radians(LAT)))
    s,w,n,e=LAT-dl,LON-dn,LAT+dl,LON+dn
    q=f'''[out:json][timeout:60];(
      way["highway"]({s},{w},{n},{e});
      way["waterway"]({s},{w},{n},{e});
      way["natural"="water"]({s},{w},{n},{e});
    );out geom;'''
    data=urllib.parse.urlencode({"data":q}).encode()
    req=urllib.request.Request(OVERPASS,data=data,headers={"User-Agent":"SpandauStrike-GIS/1.0"})
    with urllib.request.urlopen(req,timeout=75) as r: return json.loads(r.read().decode())

def width(tags):
    return {"motorway":12,"trunk":11,"primary":10,"secondary":9,"tertiary":8,
            "residential":6,"living_street":5,"service":4,"cycleway":2.5,
            "footway":2,"path":1.8,"track":3}.get(tags.get("highway",""),4.5)
def add_segment(mesh,mat,a,b,w,z,folder,label):
    dx=b.x-a.x; dy=b.y-a.y; length=math.hypot(dx,dy)/UU
    if length<0.5 or length>2000: return False
    mid=unreal.Vector((a.x+b.x)/2,(a.y+b.y)/2,z)
    yaw=math.degrees(math.atan2(dy,dx))
    actor=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor,mid,unreal.Rotator(0,yaw,0))
    actor.static_mesh_component.set_static_mesh(mesh)
    actor.static_mesh_component.set_material(0,mat)
    actor.set_actor_scale3d(unreal.Vector(length,w,0.08))
    actor.set_actor_label(label); actor.set_folder_path(folder)
    try: actor.static_mesh_component.set_collision_profile_name("BlockAll")
    except: pass
    return True

def main():
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("Map load failed")
    mesh=unreal.EditorAssetLibrary.load_asset(CUBE); mat=unreal.EditorAssetLibrary.load_asset(MAT)
    if not mesh or not mat: raise RuntimeError("base mesh/material missing")
    data=fetch(); roads=waters=0
    for el in data.get("elements",[]):
        geom=el.get("geometry") or []; tags=el.get("tags",{})
        if len(geom)<2: continue
        isroad="highway" in tags
        z=12.0 if isroad else 8.0
        pts=[pos(p["lat"],p["lon"],z) for p in geom]
        ww=width(tags) if isroad else (8.0 if "waterway" in tags else 18.0)
        for i in range(len(pts)-1):
            if isroad:
                if add_segment(mesh,mat,pts[i],pts[i+1],ww,z,ROOT+"/Roads",f"GIS_Road_{roads:05d}"): roads+=1
            else:
                if add_segment(mesh,mat,pts[i],pts[i+1],ww,z,ROOT+"/Water",f"GIS_Water_{waters:05d}"): waters+=1
    try:
        atm=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere,unreal.Vector(0,0,0),unreal.Rotator())
        atm.set_actor_label("SS_SkyAtmosphere"); atm.set_folder_path(ROOT+"/Environment")
    except Exception as exc: log("SkyAtmosphere skipped: "+str(exc))
    if not sub.save_current_level(): raise RuntimeError("Map save failed")
    log(f"roads={roads} water={waters} elements={len(data.get('elements',[]))}")
    log("ENHANCE_READY")

if __name__=="__main__":
    try: main()
    except Exception as exc:
        unreal.log_error("[SS_GIS] FAILED "+str(exc)); unreal.log_error(traceback.format_exc()); raise
