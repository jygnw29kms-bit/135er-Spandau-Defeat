import unreal
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld_playable_v5"
ASSETS=[
"/ShooterMaps/GeneratedGIS/FalkenhagenerFeld/SM_Falkenhagener_Buildings_OBB.SM_Falkenhagener_Buildings_OBB",
"/ShooterMaps/GeneratedGIS/FalkenhagenerFeld/SM_Falkenhagener_DGM10m.SM_Falkenhagener_DGM10m",
"/ShooterMaps/GeneratedGIS/FalkenhagenerFeld/SM_Falkenhagener_Roads_DGM.SM_Falkenhagener_Roads_DGM",
]
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("load failed")
for p in ASSETS:
    m=unreal.EditorAssetLibrary.load_asset(p)
    if not m:
        unreal.log("[BND] missing "+p); continue
    try:
        b=m.get_bounds()
        unreal.log("[BND] %s origin=%s extent=%s radius=%s"%(p,b.origin,b.box_extent,b.sphere_radius))
    except Exception as e:
        unreal.log("[BND] bounds error %s %s"%(p,e))
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actors.get_all_level_actors():
    n=a.get_actor_label()
    if n in ("SS_ExactBuildings","SS_DGM_Terrain","SS_Roads","SS_Water") or a.get_class().get_name()=="LyraPlayerStart":
        unreal.log("[BND] actor %s class=%s loc=%s rot=%s scale=%s"%(n,a.get_class().get_name(),a.get_actor_location(),a.get_actor_rotation(),a.get_actor_scale3d()))
