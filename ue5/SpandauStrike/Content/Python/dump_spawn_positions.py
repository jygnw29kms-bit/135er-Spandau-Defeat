import unreal
ROOT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"
for p in unreal.EditorAssetLibrary.list_assets(ROOT,recursive=True,include_folder=False):
    o=unreal.EditorAssetLibrary.load_asset(p)
    if isinstance(o,unreal.LyraPlayerStart):
        v=o.get_actor_location()
        unreal.log("[SPAWN_POS] %s %.2f %.2f %.2f"%(o.get_actor_label(),v.x,v.y,v.z))
