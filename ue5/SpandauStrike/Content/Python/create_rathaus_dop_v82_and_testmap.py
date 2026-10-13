import unreal, os, json, traceback
TEX='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v61/RathausSpandau_DOP2025_360m'
DIR='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v82'; NAME='M_Rathaus_DOP2025_v82_MATTE'; MAT=DIR+'/'+NAME
FINAL='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'; TEST='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_DOP_v82_TEST'
R=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_dop_v82_create_testmap.json'); out={'ok':False,'errors':[]}
try:
 tex=unreal.load_asset(TEX)
 if not tex: raise RuntimeError('texture missing')
 if unreal.EditorAssetLibrary.does_asset_exist(MAT): unreal.EditorAssetLibrary.delete_asset(MAT)
 m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(NAME,DIR,unreal.Material,unreal.MaterialFactoryNew())
 if not m: raise RuntimeError('material create failed')
 unreal.MaterialEditingLibrary.delete_all_material_expressions(m)
 s=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionTextureSample,-500,0); s.set_editor_property('texture',tex)
 unreal.MaterialEditingLibrary.connect_material_property(s,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
 ro=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-300,180); ro.set_editor_property('r',1.0); unreal.MaterialEditingLibrary.connect_material_property(ro,'',unreal.MaterialProperty.MP_ROUGHNESS)
 sp=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-300,300); sp.set_editor_property('r',0.0); unreal.MaterialEditingLibrary.connect_material_property(sp,'',unreal.MaterialProperty.MP_SPECULAR)
 me=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-300,420); me.set_editor_property('r',0.0); unreal.MaterialEditingLibrary.connect_material_property(me,'',unreal.MaterialProperty.MP_METALLIC)
 m.set_editor_property('used_with_nanite',True); unreal.MaterialEditingLibrary.recompile_material(m); unreal.EditorAssetLibrary.save_loaded_asset(m,False)
 if unreal.EditorAssetLibrary.does_asset_exist(TEST): unreal.EditorAssetLibrary.delete_asset(TEST)
 if not unreal.EditorAssetLibrary.duplicate_asset(FINAL,TEST): raise RuntimeError('test map duplicate failed')
 unreal.EditorAssetLibrary.save_asset(TEST,only_if_is_dirty=False)
 out.update({'material':m.get_path_name(),'used_with_nanite':bool(m.get_editor_property('used_with_nanite')),'test_map':TEST,'ok':True})
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(R),exist_ok=True); open(R,'w',encoding='utf-8').write(json.dumps(out,indent=2,ensure_ascii=False,default=str)); print(json.dumps(out,indent=2,ensure_ascii=False,default=str)); unreal.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')