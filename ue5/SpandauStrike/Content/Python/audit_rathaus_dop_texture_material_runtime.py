import unreal, os, json, traceback
TEX='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v61/RathausSpandau_DOP2025_360m'
MAT='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v76/M_Rathaus_DOP2025_v76'
R=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_dop_texture_material_runtime.json')
out={'ok':False,'texture':{},'material':{},'errors':[]}
try:
 t=unreal.load_asset(TEX); m=unreal.load_asset(MAT)
 if not t or not m: raise RuntimeError('asset missing')
 out['texture']['asset']=t.get_path_name(); out['material']['asset']=m.get_path_name()
 props=['srgb','compression_settings','mip_gen_settings','lod_bias','filter','max_texture_size','never_stream','virtual_texture_streaming','address_x','address_y','power_of_two_mode']
 for p in props:
  try: out['texture'][p]=str(t.get_editor_property(p))
  except Exception as e: out['texture'][p+'_error']=repr(e)
 for fn in ['blueprint_get_size_x','blueprint_get_size_y','blueprint_get_number_of_mips','blueprint_get_memory_size']:
  if hasattr(t,fn):
   try: out['texture'][fn]=getattr(t,fn)()
   except Exception as e: out['texture'][fn+'_error']=repr(e)
 for p in ['used_with_nanite','blend_mode','shading_model','two_sided']:
  try: out['material'][p]=str(m.get_editor_property(p))
  except Exception as e: out['material'][p+'_error']=repr(e)
 # inspect expressions and material inputs
 exprs=[]
 for e in unreal.MaterialEditingLibrary.get_material_expressions(m):
  row={'class':e.get_class().get_name()}
  for p in ['texture','constant','parameter_name']:
   try: row[p]=str(e.get_editor_property(p))
   except: pass
  exprs.append(row)
 out['material']['expressions']=exprs
 out['ok']=True
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(R),exist_ok=True); open(R,'w',encoding='utf-8').write(json.dumps(out,indent=2,ensure_ascii=False,default=str)); print(json.dumps(out,indent=2,ensure_ascii=False,default=str)); unreal.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')