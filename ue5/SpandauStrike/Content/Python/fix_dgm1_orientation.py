import unreal
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("map load failed")
found=False
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if a.get_actor_label()=="GIS_DGM1_Terrain":
        a.set_actor_rotation(unreal.Rotator(0,0,90), False)
        a.set_actor_location(unreal.Vector(0,0,-15), False, False)
        found=True
        unreal.log("[DGM1FIX] transform="+str(a.get_actor_transform()))
if not found: raise RuntimeError("DGM actor not found")
if not sub.save_current_level(): raise RuntimeError("save failed")
unreal.log("[DGM1FIX] READY")
