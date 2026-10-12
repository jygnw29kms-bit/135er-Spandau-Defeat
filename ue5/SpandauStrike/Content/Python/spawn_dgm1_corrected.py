import unreal, traceback
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
MESH="/ShooterMaps/Maps/SpandauStrikeGIS/Generated/Terrain/falkenhagener_feld_DGM1_4m_UE5.falkenhagener_feld_DGM1_4m_UE5"
def main():
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("map load failed")
    mesh=unreal.EditorAssetLibrary.load_asset(MESH)
    if not mesh: raise RuntimeError("mesh missing")
    actor=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,-15),unreal.Rotator(0,0,90))
    actor.set_actor_label("GIS_DGM1_Terrain")
    actor.set_folder_path("SpandauStrike_GIS_Terrain")
    actor.static_mesh_component.set_static_mesh(mesh)
    actor.static_mesh_component.set_collision_profile_name("BlockAll")
    actor.static_mesh_component.set_editor_property("mobility",unreal.ComponentMobility.STATIC)
    if not sub.save_current_level(): raise RuntimeError("save failed")
    unreal.log("[DGM1FIX] actor="+actor.get_path_name())
    unreal.log("[DGM1FIX] transform="+str(actor.get_actor_transform()))
    unreal.log("[DGM1FIX] READY")
if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[DGM1FIX] FAILED "+str(e)); unreal.log_error(traceback.format_exc()); raise
