import unreal, os
SRC='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v65_PLAYABLE'
DST='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v66_PLAYABLE'
MESH='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v48/SM_RathausSpandau_BUILDING_v48'
OUT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v66_build.txt')
asset=unreal.EditorAssetLibrary
if asset.does_asset_exist(DST): asset.delete_asset(DST)
if not asset.duplicate_asset(SRC,DST): raise RuntimeError('duplicate v65->v66 failed')
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not level.load_level(DST): raise RuntimeError('load v66 failed')
sm=unreal.load_asset(MESH)
if not sm: raise RuntimeError('v48 mesh missing')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
targets=[]; starts=[]
for a in actors:
    if 'PlayerStart' in a.get_class().get_name(): starts.append(a)
    if isinstance(a,unreal.StaticMeshActor) and a.get_actor_label()=='Rathaus_BUILDING_v32': targets.append(a)
if len(targets)!=1: raise RuntimeError('expected exactly one Rathaus_BUILDING_v32, got '+str(len(targets)))
a=targets[0]
a.static_mesh_component.set_editor_property('static_mesh',sm)
a.set_actor_label('Rathaus_BUILDING_v48')
if not level.save_current_level(): raise RuntimeError('save v66 failed')
lines=['SRC='+SRC,'DST='+DST,'MESH='+MESH,'REPLACED=Rathaus_BUILDING_v32->Rathaus_BUILDING_v48','PLAYERSTARTS='+str(len(starts)),'LOC='+str(a.get_actor_location()),'ROT='+str(a.get_actor_rotation()),'SCALE='+str(a.get_actor_scale3d())]
os.makedirs(os.path.dirname(OUT),exist_ok=True); open(OUT,'w',encoding='utf-8').write('\n'.join(lines))
