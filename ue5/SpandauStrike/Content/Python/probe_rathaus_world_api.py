import unreal
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
sub.load_level("/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1")
w=unreal.EditorLevelLibrary.get_editor_world()
ws=w.get_world_settings()
unreal.log("[PROBE] WS_HLOD="+",".join(x for x in dir(ws) if "hlod" in x.lower()))
for clsname in ("StaticMeshEditorSubsystem","EditorStaticMeshLibrary"):
    cls=getattr(unreal,clsname,None)
    unreal.log("[PROBE] "+clsname+"="+str(cls))
    if cls:
        unreal.log("[PROBE] "+clsname+"_LOD="+",".join(x for x in dir(cls) if "lod" in x.lower()))
try:
    inst=unreal.StaticMeshEditorSubsystem()
    unreal.log("[PROBE] SME_INSTANCE="+str(inst))
    unreal.log("[PROBE] SME_LOD="+",".join(x for x in dir(inst) if "lod" in x.lower()))
except Exception as e: unreal.log_error("[PROBE] SME_FAIL="+str(e))
