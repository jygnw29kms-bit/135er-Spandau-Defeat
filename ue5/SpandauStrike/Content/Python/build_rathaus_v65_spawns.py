import unreal, json, os
SRC='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v64_PLAYABLE'
DST='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v65_PLAYABLE'
HANDOFF=r'C:\Users\anony\Documents\SpandauStrike\repo\ue5\SpandauStrike\Design\RathausSpandau\runtime_gameplay_handoff_v47.json'; REPORT=r'C:\Users\anony\Documents\SpandauStrike\repo\ue5\SpandauStrike\Saved\Reports\rathaus_v65_spawn_build.txt'
asset=unreal.EditorAssetLibrary
if asset.does_asset_exist(DST): asset.delete_asset(DST)
if not asset.duplicate_asset(SRC,DST): raise RuntimeError('duplicate failed')
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not level.load_level(DST): raise RuntimeError('load v65 failed')
actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
removed=[]
for a in list(actor_sub.get_all_level_actors()):
    if 'PlayerStart' in a.get_class().get_name():
        removed.append(a.get_actor_label()); actor_sub.destroy_actor(a)
cls=unreal.load_class(None,'/Script/LyraGame.LyraPlayerStart')
if not cls: raise RuntimeError('LyraPlayerStart class missing')
data=json.load(open(HANDOFF,encoding='utf-8')); created=[]
for s in data['spawns']:
    loc=s['transform']['location_cm']; a=actor_sub.spawn_actor_from_class(cls,unreal.Vector(float(loc[0]),float(loc[1]),float(loc[2])),unreal.Rotator(0,0,0),False)
    if not a: raise RuntimeError('spawn failed '+s['source_name'])
    team=s['metadata']['ss_team'].upper(); lane=s['metadata']['ss_lane'].upper()
    a.set_actor_label('SS_'+s['source_name']+'_'+team+'_'+lane+'_v65')
    created.append((a.get_actor_label(),str(a.get_actor_location())))
if not level.save_current_level(): raise RuntimeError('save failed')
lines=['SOURCE='+SRC,'DEST='+DST,'REMOVED='+repr(removed),'CREATED_COUNT='+str(len(created))]
for c in created: lines.append('CREATED|'+c[0]+'|'+c[1])
os.makedirs(os.path.dirname(REPORT),exist_ok=True); open(REPORT,'w',encoding='utf-8').write('\n'.join(lines))