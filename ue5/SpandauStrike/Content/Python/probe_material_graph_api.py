import unreal, os, json
mat=unreal.load_asset('/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v76/M_Rathaus_DOP2025_v76')
out={'library_methods':[x for x in dir(unreal.MaterialEditingLibrary) if 'material' in x.lower() or 'expression' in x.lower() or 'texture' in x.lower() or 'property' in x.lower()]}
for name in ['get_material_property_input_node','get_material_property_input_node_output_name','get_all_material_expressions','get_used_textures']:
    fn=getattr(unreal.MaterialEditingLibrary,name,None)
    if fn:
        try:
            if 'property' in name: r=fn(mat,unreal.MaterialProperty.MP_BASE_COLOR)
            else: r=fn(mat)
            out[name]=repr(r)
        except Exception as e: out[name+'_error']=str(e)
report=os.path.join(unreal.Paths.project_saved_dir(),'Reports','material_graph_api_probe.json')
open(report,'w',encoding='utf-8').write(json.dumps(out,indent=2,default=str))
print(json.dumps(out,indent=2,default=str))
