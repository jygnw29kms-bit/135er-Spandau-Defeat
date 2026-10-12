import unreal
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld_playable_v8"
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);sub.load_level(MAP)
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if a.get_class().get_name()=="B_ControlPointVolume_C":
  print("[CP]",a.get_actor_label(),a.get_actor_location())
  names=[n for n in dir(a) if any(k in n.lower() for k in ("point","team","capture","letter","index","name","radius","progress","starting"))]
  print("[CPDIR]",names)
  for n in names:
   if n.startswith("_") or callable(getattr(a,n,None)):continue
   try:print("[CPVAL]",a.get_actor_label(),n,"=",getattr(a,n))
   except:pass
 elif a.get_class().get_name()=="PostProcessVolume":
  print("[PP]",a.get_actor_label(),"unbound",a.get_editor_property("unbound"),"priority",a.get_editor_property("priority"))
  s=a.get_editor_property("settings")
  for p in ("auto_exposure_method","auto_exposure_bias","auto_exposure_min_brightness","auto_exposure_max_brightness","auto_exposure_min_ev100","auto_exposure_max_ev100"):
   try:print("[PPVAL]",p,s.get_editor_property(p))
   except Exception as e:print("[PPERR]",p,e)
