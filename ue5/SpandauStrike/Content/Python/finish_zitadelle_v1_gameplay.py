import unreal, traceback
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/zitadelle_spandau_playable_v1"
CPCLASS="/ShooterCore/Blueprint/B_ControlPointVolume.B_ControlPointVolume_C"
SP=[
(-36830.154,46582.332,258.0),(-29157.678,-47998.541,325.0),(-21697.456,20.783,333.5),(-47854.894,15671.467,472.75),
(33933.855,40938.000,210.0),(45256.078,-3078.071,144.0),(18376.598,15243.043,260.0),(47808.336,26103.650,231.5)]
CPS=[(-22302.0,-677.6,168.0),(2214.2,564.4,167.5),(32516.6,1499.0,155.0)]
def log(s):unreal.log("[ZITADELLE_GAMEPLAY] "+str(s))
try:
 sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
 if not sub.load_level(MAP):raise RuntimeError("map load failed")
 actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 actors=actor_sub.get_all_level_actors()
 starts=sorted([a for a in actors if a.get_class().get_name()=="LyraPlayerStart"],key=lambda x:x.get_actor_label())
 for a,xyz in zip(starts,SP):
  a.set_actor_location(unreal.Vector(*xyz),False,False);a.set_actor_rotation(unreal.Rotator(0,0 if xyz[0]<0 else 180,0),False);a.modify()
  log("spawn "+a.get_actor_label()+" "+str(xyz))
 for a in actors:
  if a.get_class().get_name()=="B_ControlPointVolume_C":actor_sub.destroy_actor(a)
 cls=unreal.load_class(None,CPCLASS)
 if not cls:raise RuntimeError("control point class missing")
 for i,xyz in enumerate(CPS):
  a=actor_sub.spawn_actor_from_class(cls,unreal.Vector(*xyz),unreal.Rotator())
  a.set_actor_label("Zitadelle_ControlPoint_"+chr(65+i));a.set_folder_path("Zitadelle_V1/Gameplay/ControlPoints")
  try:a.set_editor_property("is_spatially_loaded",False)
  except:pass
  try:a.set_actor_scale3d(unreal.Vector(1.35,1.35,1.0))
  except:pass
  log("CP "+a.get_actor_label()+" "+str(xyz))
 actors=actor_sub.get_all_level_actors()
 pps=[a for a in actors if a.get_class().get_name()=="PostProcessVolume"]
 pp=pps[0] if pps else actor_sub.spawn_actor_from_class(unreal.PostProcessVolume,unreal.Vector(),unreal.Rotator())
 pp.set_actor_label("Zitadelle_DaylightPostProcess");pp.set_folder_path("Zitadelle_V1/Lighting")
 pp.set_editor_property("unbound",True)
 s=pp.get_editor_property("settings")
 try:s.set_editor_property("auto_exposure_bias",1.0)
 except Exception as e:log("exposure bias "+str(e))
 try:s.set_editor_property("override_auto_exposure_bias",True)
 except Exception as e:log("override exposure "+str(e))
 pp.set_editor_property("settings",s)
 for a in actors:
  if a.get_class().get_name()=="DirectionalLight":
   try:a.light_component.set_editor_property("intensity",1.4)
   except:pass
  elif a.get_class().get_name()=="SkyLight":
   try:a.light_component.set_editor_property("intensity",0.65);a.light_component.set_editor_property("real_time_capture",True)
   except:pass
  elif a.get_class().get_name()=="ExponentialHeightFog":
   try:a.component.set_editor_property("fog_density",0.002);a.component.set_editor_property("fog_height_falloff",0.22);a.component.set_editor_property("start_distance",3500.0)
   except:pass
 if not sub.save_current_level():raise RuntimeError("save failed")
 unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 log("READY")
except Exception as e:
 unreal.log_error("[ZITADELLE_GAMEPLAY] FAILED "+str(e));unreal.log_error(traceback.format_exc());raise

