import unreal, os, json, traceback
ASSETS=[
'/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v76/M_Rathaus_DOP2025_v76',
'/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v80/M_Rathaus_ROADS_Asphalt_v80'
]
R=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nanite_material_usage_fix.json')
out={'ok':False,'materials':[],'errors':[]}
try:
    for path in ASSETS:
        m=unreal.load_asset(path)
        if not m: raise RuntimeError('missing material '+path)
        row={'asset':m.get_path_name(),'class':m.get_class().get_name()}
        attrs=[x for x in dir(m) if 'nanite' in x.lower() or 'usage' in x.lower()]
        row['matching_methods']=attrs
        before=None
        try: before=m.get_editor_property('used_with_nanite')
        except Exception as e: row['before_error']=repr(e)
        row['before']=before
        m.set_editor_property('used_with_nanite',True)
        unreal.MaterialEditingLibrary.recompile_material(m)
        saved=unreal.EditorAssetLibrary.save_loaded_asset(m,False)
        row['after']=m.get_editor_property('used_with_nanite')
        row['saved']=bool(saved)
        out['materials'].append(row)
    out['ok']=all(x.get('after') is True and x.get('saved') for x in out['materials'])
except Exception as e:
    out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(R),exist_ok=True)
with open(R,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
unreal.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')