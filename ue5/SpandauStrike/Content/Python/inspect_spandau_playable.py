import unreal, collections
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("load failed")
actors=unreal.EditorLevelLibrary.get_all_level_actors()
classes=collections.Counter()
folders=collections.Counter()
mats=collections.Counter()
for a in actors:
    classes[a.get_class().get_name()]+=1
    folders[str(a.get_folder_path())]+=1
    try:
        c=a.static_mesh_component
        if c:
            for i in range(c.get_num_materials()):
                m=c.get_material(i)
                if m: mats[m.get_path_name()]+=1
    except: pass
unreal.log("[INSPECT] actors=%d"%len(actors))
for k,v in classes.most_common(20): unreal.log("[INSPECT] class %s=%d"%(k,v))
for k,v in folders.most_common(30): unreal.log("[INSPECT] folder %s=%d"%(k,v))
for k,v in mats.most_common(20): unreal.log("[INSPECT] material %s=%d"%(k,v))
