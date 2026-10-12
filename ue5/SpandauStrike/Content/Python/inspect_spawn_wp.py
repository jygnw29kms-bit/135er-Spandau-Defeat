import unreal
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("load failed")
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if a.get_class().get_name()=="LyraPlayerStart":
        vals=[]
        for n in ["is_spatially_loaded","runtime_grid","actor_guid","tags"]:
            try: vals.append("%s=%s"%(n,a.get_editor_property(n)))
            except Exception as e: vals.append("%s=ERR"%(n,))
        try: vals.append("gameplay_tags=%s"%a.get_editor_property("start_point_tags"))
        except: pass
        unreal.log("[SPAWNWP] %s %s"%(a.get_actor_label()," | ".join(vals)))
