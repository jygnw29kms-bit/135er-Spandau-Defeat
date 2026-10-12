import unreal, os, json, traceback
MAT='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v61/M_Rathaus_DOP2025_v61'
TEX='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v61/RathausSpandau_DOP2025_360m'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_dop_material_audit_2026-10-12.json')
out={'ok':False,'errors':[]}
try:
    m=unreal.load_asset(MAT); t=unreal.load_asset(TEX)
    if not m or not t: raise RuntimeError('material/texture missing')
    out['material_class']=m.get_class().get_name(); out['texture_class']=t.get_class().get_name()
    try: out['used_textures']=[x.get_path_name() for x in unreal.MaterialEditingLibrary.get_used_textures(m)]
    except Exception as e: out['used_textures_error']=str(e)
    for prop in ['blend_mode','shading_model','two_sided','use_material_attributes']:
        try: out[prop]=str(m.get_editor_property(prop))
        except Exception as e: out[prop+'_error']=str(e)
    out['expressions']=[]
    for e in m.get_editor_property('expressions'):
        row={'class':e.get_class().get_name(),'name':e.get_name()}
        for prop in ['texture','sampler_type','const_coordinate','coordinate_index','material_expression_editor_x','material_expression_editor_y']:
            try:
                v=e.get_editor_property(prop); row[prop]=v.get_path_name() if hasattr(v,'get_path_name') else str(v)
            except: pass
        out['expressions'].append(row)
    for prop in ['source','srgb','compression_settings','address_x','address_y']:
        try:
            v=t.get_editor_property(prop); out['texture_'+prop]=str(v)
        except Exception as e: out['texture_'+prop+'_error']=str(e)
    try: out['texture_size']=[int(t.blueprint_get_size_x()),int(t.blueprint_get_size_y())]
    except Exception as e: out['texture_size_error']=str(e)
    out['ok']=True
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
open(REPORT,'w',encoding='utf-8').write(json.dumps(out,indent=2,ensure_ascii=False,default=str))
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
