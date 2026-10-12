import unreal,traceback
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld_playable_v7"
MATS=[
"M_Falkenhagener_Terrain_V7","M_Falkenhagener_Buildings_V7","M_Falkenhagener_Road_V7",
"M_Falkenhagener_Water_V7","M_Falkenhagener_TreeTrunk_V7","M_Falkenhagener_TreeBroadleaf_V7",
"M_Falkenhagener_TreeConifer_V7"]
ROOT="/ShooterMaps/Maps/SpandauStrikeGIS/Assets/"
def log(s): unreal.log("[V7FINAL] "+str(s))
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("map load failed")
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for name in MATS:
    m=unreal.EditorAssetLibrary.load_asset(ROOT+name)
    if not m:
        log("missing material "+name); continue
    try:
        m.set_editor_property("used_with_nanite",True)
        unreal.MaterialEditingLibrary.recompile_material(m)
        unreal.EditorAssetLibrary.save_loaded_asset(m,False)
        log("nanite material "+name)
    except Exception as e: log("material "+name+" "+str(e))
navs=[]
for a in actors.get_all_level_actors():
    if a.get_class().get_name()=="NavMeshBoundsVolume":
        a.set_actor_location(unreal.Vector(0,0,500),False,False)
        a.set_actor_scale3d(unreal.Vector(950,950,35))
        try:a.set_editor_property("is_spatially_loaded",False)
        except:pass
        navs.append(a)
        log("nav bounds="+str(a.get_actor_scale3d()))
world=unreal.EditorLevelLibrary.get_editor_world()
unreal.SystemLibrary.execute_console_command(world,"RebuildNavigation")
if not sub.save_current_level(): raise RuntimeError("save failed")
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
log("READY navs=%d"%len(navs))
