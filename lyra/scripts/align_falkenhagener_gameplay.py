import unreal, json, math, traceback

MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
GRID=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\FalkenhagenerFeld_DGM10m_grid.json"
TERRAIN_MAT="/Game/SpandauStrikeGIS/Materials/M_SS_Terrain.M_SS_Terrain"

def log(s): unreal.log("[ALIGN_DGM] "+str(s))

with open(GRID,"r",encoding="utf-8") as f:
    g=json.load(f)
H=g["heights"]; XMIN=g["xmin"]; YMIN=g["ymin"]; STEP=g["step"]
CE=g["center_e"]; CN=g["center_n"]; BASE=g["base_height"]
NY=len(H); NX=len(H[0])

def terrain_z_cm(x_cm,y_cm):
    e=CE+x_cm/100.0
    n=CN-y_cm/100.0
    fx=(e-XMIN)/STEP
    fy=(n-YMIN)/STEP
    ix=max(0,min(NX-2,int(math.floor(fx))))
    iy=max(0,min(NY-2,int(math.floor(fy))))
    tx=max(0.0,min(1.0,fx-ix)); ty=max(0.0,min(1.0,fy-iy))
    z00=H[iy][ix]; z10=H[iy][ix+1]; z01=H[iy+1][ix]; z11=H[iy+1][ix+1]
    z0=z00*(1-tx)+z10*tx; z1=z01*(1-tx)+z11*tx
    return ((z0*(1-ty)+z1*ty)-BASE)*100.0
def main():
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("map load failed")
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    mat=unreal.EditorAssetLibrary.load_asset(TERRAIN_MAT)
    moved=0; terrain_found=0
    for a in actors.get_all_level_actors():
        label=a.get_actor_label()
        if label=="SS_DGM_Terrain":
            terrain_found+=1
            if mat:
                a.static_mesh_component.set_material(0,mat)
                log("terrain material applied")
        if a.get_class().get_name()=="LyraPlayerStart":
            loc=a.get_actor_location()
            z=terrain_z_cm(loc.x,loc.y)+140.0
            a.set_actor_location(unreal.Vector(loc.x,loc.y,z),False,False)
            log(f"spawn {label}: {loc.z:.1f} -> {z:.1f}")
            moved+=1
        if a.get_class().get_name()=="DirectionalLight":
            try: log("sun intensity="+str(a.light_component.get_editor_property("intensity")))
            except: pass
        if a.get_class().get_name()=="SkyLight":
            try: log("sky intensity="+str(a.light_component.get_editor_property("intensity")))
            except: pass
    if terrain_found!=1: log("terrain actors found="+str(terrain_found))
    if not sub.save_current_level(): raise RuntimeError("save failed")
    log(f"ALIGN_READY starts={moved}")
if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[ALIGN_DGM] FAILED "+str(e))
        unreal.log_error(traceback.format_exc())
        raise
