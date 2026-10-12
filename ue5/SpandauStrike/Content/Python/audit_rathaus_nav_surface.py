import unreal, json, os, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
OUT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav_surface_audit.json')
spawns=[(-12000.0,-12000.0),(12000.0,-12000.0)]
r={'ok':False,'actors':[],'candidates':[],'errors':[]}
try:
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    for a in actors:
        loc=a.get_actor_location(); o,e=a.get_actor_bounds(False)
        row={'label':a.get_actor_label(),'class':a.get_class().get_name(),'location':[loc.x,loc.y,loc.z],
             'bounds_min':[o.x-e.x,o.y-e.y,o.z-e.z],'bounds_max':[o.x+e.x,o.y+e.y,o.z+e.z],
             'components':[],'covers_spawn':[]}
        for i,(sx,sy) in enumerate(spawns,1):
            if o.x-e.x <= sx <= o.x+e.x and o.y-e.y <= sy <= o.y+e.y:
                row['covers_spawn'].append(i)
        for c in a.get_components_by_class(unreal.PrimitiveComponent):
            cr={'class':c.get_class().get_name(),'name':c.get_name()}
            try: cr['collision_enabled']=str(c.get_collision_enabled())
            except: pass
            try: cr['collision_profile']=str(c.get_collision_profile_name())
            except: pass
            try: cr['hidden_in_game']=bool(c.get_editor_property('hidden_in_game'))
            except: pass
            try: cr['visible']=bool(c.get_editor_property('visible'))
            except: pass
            try:
                if isinstance(c,unreal.StaticMeshComponent) and c.static_mesh:
                    cr['mesh']=c.static_mesh.get_path_name()
            except: pass
            row['components'].append(cr)
        r['actors'].append(row)
        active=[c for c in row['components'] if c.get('collision_enabled') and 'NO_COLLISION' not in c.get('collision_enabled','').upper() and c.get('collision_profile')!='NoCollision']
        zmin,zmax=row['bounds_min'][2],row['bounds_max'][2]
        if row['covers_spawn'] and active and zmin <= 550 and zmax >= 430:
            r['candidates'].append(row)
    r['ok']=True
except Exception as e:
    r['errors'].append(str(e)); r['traceback']=traceback.format_exc()
with open(OUT,'w',encoding='utf-8') as f: json.dump(r,f,ensure_ascii=False,indent=2)
unreal.log('[NAV_SURFACE_AUDIT] '+json.dumps({'ok':r['ok'],'candidate_count':len(r['candidates']),'candidates':r['candidates']}))
