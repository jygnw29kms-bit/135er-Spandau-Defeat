import unreal, os, json
TEX='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v61/RathausSpandau_DOP2025_360m'
MAT='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v76/M_Rathaus_DOP2025_v76'
R=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_dop_simple.json')
out={'texture':{},'material':{},'errors':[]}
try:
 t=unreal.load_asset(TEX); m=unreal.load_asset(MAT)
 out['texture']['asset']=t.get_path_name(); out['material']['asset']=m.get_path_name()
 for p in ['srgb','compression_settings','mip_gen_settings','lod_bias','filter','max_texture_size','never_stream','virtual_texture_streaming']:
  try: out['texture'][p]=str(t.get_editor_property(p))
  except Exception as e: out['texture'][p+'_error']=repr(e)
 for fn in ['blueprint_get_size_x','blueprint_get_size_y','blueprint_get_number_of_mips']:
  try: out['texture'][fn]=getattr(t,fn)()
  except Exception as e: out['texture'][fn+'_error']=repr(e)
 for p in ['used_with_nanite','blend_mode','two_sided']:
  try: out['material'][p]=str(m.get_editor_property(p))
  except Exception as e: out['material'][p+'_error']=repr(e)
 out['ok']=True
except Exception as e:
 out['ok']=False; out['errors'].append(repr(e))
os.makedirs(os.path.dirname(R),exist_ok=True)
with open(R,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
print(json.dumps(out,indent=2,ensure_ascii=False))
unreal.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')