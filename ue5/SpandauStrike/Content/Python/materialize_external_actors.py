import unreal, traceback

ROOT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"
ASSET_DIR="/ShooterMaps/Maps/SpandauStrikeGIS/Assets"
ROAD=ASSET_DIR+"/M_Falkenhagener_Road"
WATER=ASSET_DIR+"/M_Falkenhagener_Water"

def log(s): unreal.log("[MATPASS] "+str(s))

def make_mat(name,color,rough=0.9,metal=0.0):
    path=ASSET_DIR+"/"+name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.EditorAssetLibrary.load_asset(path)
    at=unreal.AssetToolsHelpers.get_asset_tools()
    m=at.create_asset(name,ASSET_DIR,unreal.Material,unreal.MaterialFactoryNew())
    c=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-250,-50)
    c.set_editor_property("constant",unreal.LinearColor(*color,1.0))
    r=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-250,80)
    r.set_editor_property("r",rough)
    me=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-250,180)
    me.set_editor_property("r",metal)
    unreal.MaterialEditingLibrary.connect_material_property(c,"",unreal.MaterialProperty.MP_BASE_COLOR)
    unreal.MaterialEditingLibrary.connect_material_property(r,"",unreal.MaterialProperty.MP_ROUGHNESS)
    unreal.MaterialEditingLibrary.connect_material_property(me,"",unreal.MaterialProperty.MP_METALLIC)
    unreal.MaterialEditingLibrary.recompile_material(m)
    unreal.EditorAssetLibrary.save_asset(path)
    return m
def save_obj(o):
    try:
        return unreal.EditorAssetLibrary.save_loaded_asset(o, only_if_is_dirty=False)
    except Exception:
        try:
            return unreal.EditorAssetLibrary.save_loaded_assets([o], only_if_is_dirty=False)
        except Exception as e:
            log("save failed %s"%e)
            return False

def main():
    road=make_mat("M_Falkenhagener_Road",(0.035,0.04,0.045),0.96,0.0)
    water=make_mat("M_Falkenhagener_Water",(0.025,0.16,0.30),0.25,0.0)
    assets=unreal.EditorAssetLibrary.list_assets(ROOT,recursive=True,include_folder=False)
    roads=waters=terrains=changed=0
    terrain_objs=[]
    for p in assets:
        o=unreal.EditorAssetLibrary.load_asset(p)
        if not isinstance(o,unreal.StaticMeshActor):
            continue
        label=o.get_actor_label()
        if label.startswith("GIS_Road_"):
            o.static_mesh_component.set_material(0,road); roads+=1
            if save_obj(o): changed+=1
        elif label.startswith("GIS_Water_"):
            o.static_mesh_component.set_material(0,water); waters+=1
            if save_obj(o): changed+=1
        elif label=="SS_DGM1_Terrain":
            terrain_objs.append(o); terrains+=1
    log("roads=%d water=%d terrains=%d changed=%d"%(roads,waters,terrains,changed))
    if len(terrain_objs)>1:
        # keep newest object by name sort, delete older duplicates
        terrain_objs.sort(key=lambda x:x.get_name())
        for o in terrain_objs[:-1]:
            try:
                unreal.get_editor_subsystem(unreal.EditorActorSubsystem).destroy_actor(o)
                save_obj(o)
                log("removed duplicate terrain "+o.get_name())
            except Exception as e:
                log("duplicate remove failed "+str(e))
    log("MATPASS_READY")

if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[MATPASS] FAILED "+str(e))
        unreal.log_error(traceback.format_exc())
        raise
