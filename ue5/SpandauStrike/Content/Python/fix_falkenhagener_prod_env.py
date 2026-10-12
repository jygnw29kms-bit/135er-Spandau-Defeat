import unreal, traceback

LEVEL="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld_prod"

def main():
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(LEVEL):
        raise RuntimeError("load failed")
    actors=unreal.EditorLevelLibrary.get_all_level_actors()
    removed=0
    for a in actors:
        if a.get_class().get_name()=="ExponentialHeightFog":
            unreal.EditorLevelLibrary.destroy_actor(a)
            removed+=1
    for a in actors:
        if a.get_class().get_name()=="DirectionalLight":
            try:
                a.light_component.set_editor_property("intensity",3.5)
            except Exception:
                pass
        if a.get_class().get_name()=="SkyLight":
            try:
                a.light_component.set_editor_property("intensity",0.7)
            except Exception:
                pass
    if not sub.save_current_level():
        raise RuntimeError("save failed")
    unreal.log("[SS_ENVFIX] READY fog_removed=%d"%removed)

if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[SS_ENVFIX] FAILED "+str(e))
        unreal.log_error(traceback.format_exc())
        raise
