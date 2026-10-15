import unreal, os
SRC='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v69_MATREF'
DST='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v70_CLOCK_QA'
MESH='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v50/SM_RathausSpandau_BUILDING_v50_MATREF'
OUT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v70_clock_qa_build.txt')
asset=unreal.EditorAssetLibrary
if asset.does_asset_exist(DST): asset.delete_asset(DST)
if not asset.duplicate_asset(SRC,DST): raise RuntimeError('duplicate v69->v70 failed')
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not level.load_level(DST): raise RuntimeError('load v70 failed')
sm=unreal.load_asset(MESH)
if not sm: raise RuntimeError('v50 reference material mesh missing')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors(); targets=[]; starts=[]
for a in actors:
    if 'PlayerStart' in a.get_class().get_name(): starts.append(a)
    if isinstance(a,unreal.StaticMeshActor) and a.get_actor_label()=='Rathaus_BUILDING_v49_MATREF': targets.append(a)
if len(targets)!=1: raise RuntimeError('expected one Rathaus_BUILDING_v49_MATREF, got '+str(len(targets)))
a=targets[0]; a.static_mesh_component.set_editor_property('static_mesh',sm); a.set_actor_label('Rathaus_BUILDING_v50_MATREF')
if not level.save_current_level(): raise RuntimeError('save v70 failed')
lines=['SRC='+SRC,'DST='+DST,'MESH='+MESH,'PLAYERSTARTS='+str(len(starts)),'LOC='+str(a.get_actor_location()),'ROT='+str(a.get_actor_rotation()),'SCALE='+str(a.get_actor_scale3d())]
os.makedirs(os.path.dirname(OUT),exist_ok=True); open(OUT,'w',encoding='utf-8').write('\n'.join(lines))
if len(starts)!=8: raise RuntimeError('expected 8 PlayerStarts, got '+str(len(starts)))
