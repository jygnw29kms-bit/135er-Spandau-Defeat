import unreal, math, os
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v71_PEDIMENT_QA'
OUT=os.path.join(os.environ.get('SPANDAU_WORK_HOME', unreal.Paths.project_saved_dir()),'Staging','v71_front_qa.png')
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','v71_front_qa.txt')
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not level.load_level(MAP): raise RuntimeError('load failed')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
b=[a for a in actors if a.get_actor_label()=='Rathaus_BUILDING_v51_MATREF']
if len(b)!=1: raise RuntimeError('expected one Rathaus_BUILDING_v51_MATREF, got '+str(len(b)))
a=b[0]
sm=a.static_mesh_component.static_mesh
bounds=sm.get_bounds(); center=bounds.origin
facade=math.radians(47.5)
outvec=unreal.Vector(math.sin(facade), math.cos(facade), 0.0)
camloc=unreal.Vector(center.x+outvec.x*24000.0, center.y+outvec.y*24000.0, center.z+1800.0)
target=unreal.Vector(center.x,center.y,center.z+500.0)
rot=unreal.MathLibrary.find_look_at_rotation(camloc,target)
cam=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(unreal.CameraActor,camloc,rot,False)
cam.set_actor_label('TEMP_Rathaus_v71_Front_QA')
try: cam.camera_component.set_editor_property('field_of_view',38.0)
except Exception: pass
os.makedirs(os.path.dirname(OUT),exist_ok=True)
task=unreal.AutomationLibrary.take_high_res_screenshot(1800,1100,OUT,cam,False,False,unreal.ComparisonTolerance.LOW,'Rathaus v71 front QA',0.0,True)
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
open(REPORT,'w',encoding='utf-8').write('camera='+str(camloc)+'\nrotation='+str(rot)+'\ntarget='+str(target)+'\noutput='+OUT+'\ntask='+str(task))
