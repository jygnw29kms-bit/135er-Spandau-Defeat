import unreal
lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
path="/ShooterMaps/Maps/L_Convolution_Blockout"
unreal.log("[SS_INSPECT] load "+path)
ok=lvl.load_level(path)
unreal.log("[SS_INSPECT] load="+str(ok))
world=unreal.EditorLevelLibrary.get_editor_world()
ws=world.get_world_settings()
unreal.log("[SS_INSPECT] worldsettings_class="+ws.get_class().get_name())
for prop in ["default_game_mode","game_mode_override","default_game_mode_class","default_gameplay_experience","force_standalone_net_mode"]:
    try: unreal.log("[SS_INSPECT] world."+prop+"="+str(ws.get_editor_property(prop)))
    except Exception as e: pass
actors=unreal.EditorLevelLibrary.get_all_level_actors()
unreal.log("[SS_INSPECT] actors="+str(len(actors)))
for a in actors:
    cn=a.get_class().get_name()
    lab=a.get_actor_label()
    unreal.log("[SS_INSPECT] ACTOR class="+cn+" label="+lab+" loc="+str(a.get_actor_location()))
