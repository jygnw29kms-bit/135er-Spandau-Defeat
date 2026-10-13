import unreal, json, os
asset_path='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v61/SM_RathausSpandau_DGM1_DOP_v60'
out='C:/Users/dezen/Documents/Unreal Projects/SpandauStrike/Saved/Reports/rathaus_dgm_uv_values.json'
r={'ok':False,'asset':asset_path,'errors':[]}
try:
    sm=unreal.load_asset(asset_path)
    sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    r['num_uv_channels']=sub.get_num_uv_channels(sm,0)
    md=sm.get_static_mesh_description(0)
    r['mesh_description_class']=md.get_class().get_name() if md else None
    r['mesh_description_methods']=[x for x in dir(md) if 'uv' in x.lower() or 'vertex' in x.lower() or 'instance' in x.lower()] if md else []
    if md and hasattr(md,'get_vertex_instance_uvs'):
        attrs=md.get_vertex_instance_uvs()
        r['uv_attr_methods']=[x for x in dir(attrs) if not x.startswith('_')]
        vals=[]
        for name in ['get_num_channels','get_num_elements','get','get_uv','get_vertex_instance_uv']:
            if hasattr(attrs,name):
                try: r['probe_'+name]=str(getattr(attrs,name)())
                except Exception as e: r['probe_'+name+'_error']=repr(e)
except Exception as e:
    r['errors'].append(repr(e))
r['ok']=not r['errors']
os.makedirs(os.path.dirname(out),exist_ok=True)
with open(out,'w',encoding='utf-8') as f: json.dump(r,f,indent=2,ensure_ascii=False)
print(json.dumps(r,indent=2,ensure_ascii=False))
unreal.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')