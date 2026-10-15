import unreal, os
BASE='/Game/SpandauStrike/Maps/Rathaus/Materials/v49'
SRC_MESH='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v49/SM_RathausSpandau_BUILDING_v49'
DST_MESH='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v49/SM_RathausSpandau_BUILDING_v49_MATREF'
OUT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v49_reference_materials.txt')
# Reference-facing palette calibrated against media/theme/rathaus-spandau-photo.jpg.
# Values are linear RGB; intentionally darker/rougher than the schematic v48 set.
specs={
 'M_Rathaus49_Sandstone':((0.215,0.155,0.095,1.0),0.82,0.0),
 'M_Rathaus49_Trim':((0.300,0.225,0.145,1.0),0.78,0.0),
 'M_Rathaus49_RedTile':((0.240,0.028,0.012,1.0),0.80,0.0),
 'M_Rathaus49_Glass':((0.022,0.038,0.048,1.0),0.30,0.03),
 'M_Rathaus49_WindowFrame':((0.075,0.062,0.045,1.0),0.62,0.10),
 'M_Rathaus49_Gold':((0.50,0.255,0.030,1.0),0.32,0.76),
 'M_Rathaus49_Copper':((0.070,0.225,0.145,1.0),0.52,0.62),
 'M_Rathaus49_DarkMetal':((0.018,0.020,0.022,1.0),0.48,0.72),
 'M_Rathaus49_Concrete':((0.205,0.198,0.180,1.0),0.88,0.0),
 'M_Rathaus49_DarkOpening':((0.008,0.010,0.012,1.0),0.95,0.0),
 'M_Rathaus49_Inscription':((0.090,0.060,0.035,1.0),0.72,0.0),
}
asset=unreal.EditorAssetLibrary
asset_tools=unreal.AssetToolsHelpers.get_asset_tools(); mel=unreal.MaterialEditingLibrary
if asset.does_asset_exist(DST_MESH): asset.delete_asset(DST_MESH)
if not asset.duplicate_asset(SRC_MESH,DST_MESH): raise RuntimeError('mesh duplicate failed')
made={}
for name,(rgba,rough,metal) in specs.items():
 path=BASE+'/'+name
 if asset.does_asset_exist(path): asset.delete_asset(path)
 mat=asset_tools.create_asset(name,BASE,unreal.Material,unreal.MaterialFactoryNew())
 if not mat: raise RuntimeError('create material failed '+name)
 c=mel.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-420,0); c.set_editor_property('constant',unreal.LinearColor(*rgba)); mel.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
 r=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-420,120); r.set_editor_property('r',rough); mel.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS)
 m=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-420,240); m.set_editor_property('r',metal); mel.connect_material_property(m,'',unreal.MaterialProperty.MP_METALLIC)
 mel.recompile_material(mat); asset.save_loaded_asset(mat); made[name]=mat

def category(slot):
 s=slot.lower()
 if 'redtile' in s or 'rooftile' in s: return 'M_Rathaus49_RedTile'
 if 'glass' in s: return 'M_Rathaus49_Glass'
 if 'clockgold' in s or s.endswith('_gold') or 'p_gold' in s: return 'M_Rathaus49_Gold'
 if 'copper' in s: return 'M_Rathaus49_Copper'
 if 'crownrail' in s or 'darkmetal' in s or 'steel' in s or s=='pf_dark': return 'M_Rathaus49_DarkMetal'
 if 'opening' in s or 'recess' in s: return 'M_Rathaus49_DarkOpening'
 if 'inscription' in s: return 'M_Rathaus49_Inscription'
 if 'windowframe' in s: return 'M_Rathaus49_WindowFrame'
 if 'trim' in s or 'windowstone' in s: return 'M_Rathaus49_Trim'
 if 'concrete' in s: return 'M_Rathaus49_Concrete'
 return 'M_Rathaus49_Sandstone'
sm=unreal.load_asset(DST_MESH); slots=sm.get_editor_property('static_materials'); lines=[]
for i,e in enumerate(slots):
 slot=str(e.material_slot_name); cat=category(slot); mat=made[cat]
 try: sm.set_material(i,mat)
 except Exception: e.set_editor_property('material_interface',mat); slots[i]=e
 lines.append(f'{i}|{slot}|{cat}')
try: sm.set_editor_property('static_materials',slots)
except Exception: pass
asset.save_loaded_asset(sm)
os.makedirs(os.path.dirname(OUT),exist_ok=True); open(OUT,'w',encoding='utf-8').write('\n'.join(lines))
if len(slots)!=34: raise RuntimeError('expected 34 slots')
