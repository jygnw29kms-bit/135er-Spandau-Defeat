import unreal
MESH="/ShooterMaps/Maps/SpandauStrikeGIS/Assets/SM_Falkenhagener_ExactBuildings"
ROOT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"
m=unreal.EditorAssetLibrary.load_asset(MESH)
if not m: raise RuntimeError("mesh missing")
try:
    bs=m.get_editor_property("body_setup")
    bs.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    unreal.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False)
    unreal.log("[FINAL_BLDG] collision_saved")
except Exception as e:
    unreal.log_error("[FINAL_BLDG] collision_failed "+str(e))
count=0
for p in unreal.EditorAssetLibrary.list_assets(ROOT,recursive=True,include_folder=False):
    o=unreal.EditorAssetLibrary.load_asset(p)
    if isinstance(o,unreal.StaticMeshActor) and o.get_actor_label()=="SS_ExactBuildings":
        count+=1
unreal.log("[FINAL_BLDG] actor_count=%d"%count)
if count!=1: raise RuntimeError("expected one exact building actor")
