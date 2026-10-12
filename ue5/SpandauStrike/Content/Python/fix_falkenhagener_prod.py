# -*- coding: utf-8 -*-
import unreal, math, traceback
import berlin_spandau_lyra_import as gis

LEVEL="/Game/Maps/BerlinSpandau/falkenhagener_feld_prod_v2"
TERRAIN="/Game/SpandauStrikeGIS/Terrain/falkenhagener_dgm_257.falkenhagener_dgm_257"
OBJ=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\SourceData\DGM1\falkenhagener_dgm_257.obj"
LAT=52.5524034
LON=13.1668941
HALF=900.0
N=257
STEP=(2.0*HALF)/(N-1)
def log(s): unreal.log("[SS_FIX] "+str(s))

def load_heights():
    vals=[]
    with open(OBJ,"r",encoding="ascii",errors="ignore") as f:
        for line in f:
            if line.startswith("v "):
                vals.append(float(line.split()[3])/100.0)
                if len(vals)==N*N: break
    if len(vals)!=N*N: raise RuntimeError("DGM vertex count "+str(len(vals)))
    return vals
HEIGHTS=load_heights()
def hxy(x,y):
    i=max(0,min(N-1,int(round((x+HALF)/STEP))))
    north=-y
    j=max(0,min(N-1,int(round((north+HALF)/STEP))))
    return HEIGHTS[j*N+i]

def records():
    ce,cn=gis.wgs84_to_utm33(LAT,LON)
    bbox=(ce-HALF,cn-HALF,ce+HALF,cn+HALF)
    ft=gis.discover_feature_type()
    root=gis.download_features(ft,bbox)
    out=[]
    for f in gis.feature_members(root):
        r=gis.build_record(f)
        if r:
            r["_x"]=r["cx"]-ce
            r["_y"]=-(r["cy"]-cn)
            r["_rad"]=0.5*math.hypot(r["width"],r["depth"])+12.0
            out.append(r)
    return out

def building_clearance(x,y,recs,pad=10.0):
    best=1e9
    for r in recs:
        dx=x-r["_x"]; dy=y-r["_y"]
        ang=math.radians(r.get("angle",0.0))
        ca=math.cos(ang); sa=math.sin(ang)
        lx=abs(ca*dx + sa*dy) - (r["width"]*0.5 + pad)
        ly=abs(-sa*dx + ca*dy) - (r["depth"]*0.5 + pad)
        if lx <= 0.0 and ly <= 0.0:
            return -min(-lx,-ly)
        if lx > 0.0 and ly > 0.0:
            d=math.hypot(lx,ly)
        else:
            d=max(lx,ly)
        if d < best: best=d
    return best

def choose_side(sign,recs,count=8):
    scored=[]
    for xmag in range(220,861,40):
        x=sign*float(xmag)
        for y in range(-820,821,40):
            score=building_clearance(x,float(y),recs,10.0)
            if score >= 0.0:
                scored.append((score,x,float(y)))
    scored.sort(reverse=True)
    chosen=[]
    for score,x,y in scored:
        if all(math.hypot(x-a,y-b) >= 130.0 for a,b in chosen):
            chosen.append((x,y))
            log("spawn candidate side=%d x=%.0f y=%.0f clearance=%.1f"%(sign,x,y,score))
            if len(chosen)==count: return chosen
    raise RuntimeError("not enough safe spawn candidates side "+str(sign))
def fix_nanite():
    mesh=unreal.EditorAssetLibrary.load_asset(TERRAIN)
    if not mesh: raise RuntimeError("terrain missing")
    try:
        ns=mesh.get_editor_property("nanite_settings")
        ns.enabled=False
        mesh.set_editor_property("nanite_settings",ns)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
        log("terrain Nanite disabled")
    except Exception as e:
        log("Nanite property unavailable: "+str(e))
def move_spawns(recs):
    actors=unreal.EditorLevelLibrary.get_all_level_actors()
    starts=[a for a in actors if a.get_class().get_name()=="LyraPlayerStart"]
    starts.sort(key=lambda a:a.get_actor_label())
    cls=unreal.load_class(None,"/Script/LyraGame.LyraPlayerStart")
    if not cls: cls=unreal.PlayerStart
    while len(starts)<16:
        a=unreal.EditorLevelLibrary.spawn_actor_from_class(cls,unreal.Vector(0,0,500),unreal.Rotator())
        a.set_actor_label("SS_PlayerStart_%02d"%(len(starts)+1))
        a.set_folder_path("SpandauStrike_Gameplay")
        starts.append(a)
    pts=choose_side(-1,recs,8)+choose_side(1,recs,8)
    for a,(x,y) in zip(starts[:16],pts):
        a.modify()
        z=hxy(x,y)*100.0+300.0
        yaw=0.0 if x<0 else 180.0
        a.set_actor_location(unreal.Vector(x*100.0,y*100.0,z),False,False)
        a.set_actor_rotation(unreal.Rotator(0,yaw,0),False)
        log("%s -> %.0f %.0f %.1f"%(a.get_actor_label(),x,y,z/100.0))
    return pts

def main():
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(LEVEL): raise RuntimeError("load failed")
    fix_nanite()
    recs=records()
    pts=move_spawns(recs)
    try:
        world=unreal.EditorLevelLibrary.get_editor_world()
        unreal.SystemLibrary.execute_console_command(world,"RebuildNavigation")
        log("navigation rebuild requested")
    except Exception as e: log("navigation rebuild skipped "+str(e))
    if not sub.save_current_level(): raise RuntimeError("save failed")
    try:
        saved=unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
        log("save_dirty_packages="+str(saved))
    except Exception as e:
        log("save_dirty_packages failed "+str(e))
    log("READY safe_spawns="+str(pts))

if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[SS_FIX] FAILED "+str(e))
        unreal.log_error(traceback.format_exc())
        raise


