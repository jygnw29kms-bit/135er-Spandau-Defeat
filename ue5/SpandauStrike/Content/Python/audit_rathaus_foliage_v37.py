import unreal, os, json, traceback
A='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v38/SM_RathausSpandau_FOLIAGE_v37'
R=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_foliage_v37_audit.json')
out={'ok':False,'errors':[]}
try:
 m=unreal.EditorAssetLibrary.load_asset(A)
 if not m: raise RuntimeError('asset missing')
 out['asset']=m.get_path_name(); out['class']=m.get_class().get_name()
 try: out['vertices_lod0']=int(m.get_num_vertices(0))
 except Exception as e: out['vertices_error']=str(e)
 try: out['lod_count']=int(m.get_num_lods())
 except Exception as e: out['lod_error']=str(e)
 try:
  b=m.get_bounds(); out['bounds_origin']=[float(b.origin.x),float(b.origin.y),float(b.origin.z)]; out['bounds_extent']=[float(b.box_extent.x),float(b.box_extent.y),float(b.box_extent.z)]
 except Exception as e: out['bounds_error']=str(e)
 try:
  idata=m.get_editor_property('asset_import_data'); out['import_source']=idata.get_first_filename() if idata else None
 except Exception as e: out['import_source_error']=str(e)
 try:
  out['materials']=[str(x.material_interface.get_path_name()) if x.material_interface else None for x in m.get_editor_property('static_materials')]
 except Exception as e: out['materials_error']=str(e)
 try:
  sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem); out['uv_channels']=int(sub.get_num_uv_channels(m,0))
 except Exception as e: out['uv_error']=str(e)
 out['ok']=True
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(R),exist_ok=True)
with open(R,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),'QUIT_EDITOR')
