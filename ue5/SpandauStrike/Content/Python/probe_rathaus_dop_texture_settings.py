import unreal, json, os, traceback
T='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v61/RathausSpandau_DOP2025_360m'
R=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_dop_texture_settings.json')
out={'ok':False,'errors':[]}
try:
    t=unreal.EditorAssetLibrary.load_asset(T)
    if not t: raise RuntimeError('texture missing')
    out['asset']=t.get_path_name(); out['class']=t.get_class().get_name()
    for name in ['size_x','size_y','lod_bias','never_stream','virtual_texture_streaming','compression_settings','mip_gen_settings','filter','lod_group','srgb','max_texture_size','power_of_two_mode','address_x','address_y']:
        try: out[name]=str(t.get_editor_property(name))
        except Exception as e: out[name+'_error']=str(e)
    try: out['blueprint_size']=[int(t.blueprint_get_size_x()),int(t.blueprint_get_size_y())]
    except Exception as e: out['blueprint_size_error']=str(e)
    out['ok']=True
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(R),exist_ok=True)
with open(R,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),'QUIT_EDITOR')
