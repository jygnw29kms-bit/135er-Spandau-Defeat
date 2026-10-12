import unreal,json,os
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lvl.load_level(MAP)
actors=sorted([a for a in eas.get_all_level_actors() if a.get_actor_label().startswith('NAV10M_')],key=lambda a:a.get_actor_label())
rows=[]
for a in actors:
 p=a.get_actor_location(); s=a.get_actor_scale3d(); c=a.static_mesh_component
 rows.append({'label':a.get_actor_label(),'loc':[p.x,p.y,p.z],'scale':[s.x,s.y,s.z],'pawn':str(c.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN)),'nav':str(c.get_editor_property('can_ever_affect_navigation'))})
out={'count':len(rows),'min':[min(r['loc'][0] for r in rows),min(r['loc'][1] for r in rows),min(r['loc'][2] for r in rows)],'max':[max(r['loc'][0] for r in rows),max(r['loc'][1] for r in rows),max(r['loc'][2] for r in rows)],'first':rows[:5],'middle':rows[len(rows)//2:len(rows)//2+5],'last':rows[-5:]}
p=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav10m_actor_audit.json'); os.makedirs(os.path.dirname(p),exist_ok=True)
open(p,'w',encoding='utf-8').write(json.dumps(out,indent=2)); unreal.log('[RATHAUS_NAV10M_AUDIT] '+json.dumps(out))
