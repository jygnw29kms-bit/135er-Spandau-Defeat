import unreal
MAPS=["/ShooterMaps/Maps/L_Convolution_Blockout","/ShooterMaps/Maps/L_Expanse_Blockout","/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld_playable_v6"]
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for mp in MAPS:
    if not sub.load_level(mp):
        unreal.log("[PSREF] load failed "+mp); continue
    unreal.log("[PSREF] MAP "+mp)
    n=0
    for a in actors.get_all_level_actors():
        if a.get_class().get_name()=="LyraPlayerStart":
            n+=1
            loc=a.get_actor_location()
            try: spt=a.get_editor_property("start_point_tags")
            except Exception as e: spt="ERR:"+str(e)
            try: tags=a.get_editor_property("tags")
            except Exception as e: tags="ERR:"+str(e)
            try: tp=a.get_editor_property("player_start_tag")
            except Exception as e: tp="ERR:"+str(e)
            unreal.log("[PSREF] %s loc=(%.1f,%.1f,%.1f) tags=%s start_point_tags=%s player_start_tag=%s"%(a.get_actor_label(),loc.x,loc.y,loc.z,tags,spt,tp))
    unreal.log("[PSREF] count="+str(n))
