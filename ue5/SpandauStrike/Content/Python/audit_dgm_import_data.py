import unreal, json, os
ASSET='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v61/SM_RathausSpandau_DGM1_DOP_v60'
sm=unreal.load_asset(ASSET)
out={'ok':bool(sm),'asset':ASSET}
if sm:
    for prop in ['asset_import_data','light_map_coordinate_index','light_map_resolution']:
        try:
            v=sm.get_editor_property(prop)
            if prop=='asset_import_data' and v:
                out['import_data_class']=v.get_class().get_name()
                try: out['first_filename']=v.get_first_filename()
                except Exception as e: out['first_filename_error']=str(e)
                out['import_data_methods']=[x for x in dir(v) if 'file' in x.lower() or 'source' in x.lower()]
            else: out[prop]=str(v)
        except Exception as e: out[prop+'_error']=str(e)
    sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    for lod in [0]:
        for name in ['get_num_uv_channels','get_lod_count']:
            fn=getattr(sub,name,None)
            if fn:
                try: out[name]=fn(sm,lod) if name=='get_num_uv_channels' else fn(sm)
                except Exception as e: out[name+'_error']=str(e)
report=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_dgm_import_data_2026-10-12.json')
open(report,'w',encoding='utf-8').write(json.dumps(out,indent=2,default=str))
print(json.dumps(out,indent=2,default=str))
