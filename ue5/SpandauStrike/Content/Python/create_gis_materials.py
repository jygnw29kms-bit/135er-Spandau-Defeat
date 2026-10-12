import unreal, traceback

ROOT="/Game/SpandauStrikeGIS/Materials"

MATS={
 "M_SS_Terrain":((0.18,0.28,0.12,1.0),0.9,0.0),
 "M_SS_Building":((0.42,0.40,0.36,1.0),0.75,0.0),
 "M_SS_Road":((0.055,0.06,0.065,1.0),0.8,0.0),
 "M_SS_Water":((0.025,0.16,0.28,1.0),0.35,0.05),
}

def make(name,base,rough,metal):
    path=ROOT+"/"+name
    old=unreal.EditorAssetLibrary.load_asset(path)
    if old:
        unreal.EditorAssetLibrary.delete_asset(path)
    mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        name,ROOT,unreal.Material,unreal.MaterialFactoryNew())
    if not mat:
        raise RuntimeError("create failed "+name)
    color=unreal.MaterialEditingLibrary.create_material_expression(
        mat,unreal.MaterialExpressionConstant3Vector,-400,0)
    color.set_editor_property("constant",unreal.LinearColor(*base))
    unreal.MaterialEditingLibrary.connect_material_property(
        color,"",unreal.MaterialProperty.MP_BASE_COLOR)
    r=unreal.MaterialEditingLibrary.create_material_expression(
        mat,unreal.MaterialExpressionConstant,-400,120)
    r.set_editor_property("r",rough)
    unreal.MaterialEditingLibrary.connect_material_property(
        r,"",unreal.MaterialProperty.MP_ROUGHNESS)
    m=unreal.MaterialEditingLibrary.create_material_expression(
        mat,unreal.MaterialExpressionConstant,-400,220)
    m.set_editor_property("r",metal)
    unreal.MaterialEditingLibrary.connect_material_property(
        m,"",unreal.MaterialProperty.MP_METALLIC)
    if name=="M_SS_Terrain":
        unreal.MaterialEditingLibrary.set_material_usage(
            mat,unreal.MaterialUsage.MATUSAGE_NANITE)
    unreal.MaterialEditingLibrary.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    unreal.log("[SS_MAT] "+mat.get_path_name())
def main():
    for name,(base,rough,metal) in MATS.items():
        make(name,base,rough,metal)
    unreal.log("[SS_MAT] READY")

if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[SS_MAT] FAILED "+str(e))
        unreal.log_error(traceback.format_exc())
        raise

