import unreal
ROOT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"
count=0
for p in unreal.EditorAssetLibrary.list_assets(ROOT,recursive=True,include_folder=False):
    o=unreal.EditorAssetLibrary.load_asset(p)
    if isinstance(o,unreal.StaticMeshActor) and o.get_actor_label()=="SS_ExactBuildings":
        o.static_mesh_component.set_collision_profile_name("NoCollision")
        unreal.EditorAssetLibrary.save_loaded_asset(o,only_if_is_dirty=False)
        count+=1
unreal.log("[CITY_COLLISION] visual_mesh_no_collision count=%d"%count)
if count!=1: raise RuntimeError("Expected one exact building actor")
