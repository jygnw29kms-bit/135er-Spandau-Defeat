import unreal, collections
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("load failed")
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
cnt=collections.Counter(a.get_class().get_name() for a in actors)
for k,v in sorted(cnt.items()): unreal.log(f"[RATHAUS_INSPECT] {k}={v}")
