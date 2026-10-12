import unreal
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
ROOT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
def log(x): unreal.log("[RATHAUS_WP] "+str(x))
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("map load failed")
assets=unreal.EditorAssetLibrary.list_assets(ROOT,recursive=True,include_folder=False)
log("external_assets="+str(len(assets)))
classes={}
loaded=0
for p in assets:
    try:
        a=unreal.EditorAssetLibrary.load_asset(p)
        if a:
            loaded+=1
            n=a.get_class().get_name()
            classes[n]=classes.get(n,0)+1
    except Exception as e:
        log("load_fail "+p+" "+str(e))
log("loaded_assets="+str(loaded))
for k in sorted(classes): log("class "+k+"="+str(classes[k]))
log("DONE")