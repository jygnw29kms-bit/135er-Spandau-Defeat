import unreal, os
BASE='/Game/SpandauStrike/Maps/Rathaus/Materials/v48'
MESH='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v48/SM_RathausSpandau_BUILDING_v48'
OUT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v48_materials.txt')
# Colors deliberately simple and reference-driven; no external texture dependency.
specs={
 'M_Rathaus48_Sandstone':((0.34,0.25,0.16,1.0),0.72,0.0),
 'M_Rathaus48_Trim':((0.52,0.42,0.29,1.0),0.68,0.0),
 'M_Rathaus48_RedTile':((0.42,0.055,0.025,1.0),0.62,0.0),
 'M_Rathaus48_Glass':((0.035,0.060,0.075,1.0),0.22,0.05),
 'M_Rathaus48_WindowFrame':((0.12,0.10,0.075,1.0),0.48,0.15),
 'M_Rathaus48_Gold':((0.62,0.34,0.045,1.0),0.25,0.82),
 'M_Rathaus48_Copper':((0.105,0.33,0.235,1.0),0.42,0.70),
 'M_Rathaus48_DarkMetal':((0.025,0.028,0.03,1.0),0.32,0.82),
 'M_Rathaus48_Concrete':((0.28,0.275,0.255,1.0),0.82,0.0),
 'M_Rathaus48_DarkOpening':((0.012,0.014,0.016,1.0),0.92,0.0),
 'M_Rathaus48_Inscription':((0.16,0.11,0.065,1.0),0.60,0.0),
}
asset_tools=unreal.AssetToolsHelpers.get_asset_tools()
mel=unreal.MaterialEditingLibrary
made={}
for name,(rgba,rough,metal) in specs.items():
 path=BASE+'/'+name
 mat=unreal.load_asset(path)
 if not mat:
  mat=asset_tools.create_asset(name,BASE,unreal.Material,unreal.MaterialFactoryNew())
  if not mat: raise RuntimeError('create material failed '+name)
  c=mel.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-420,0); c.set_editor_property('constant',unreal.LinearColor(*rgba))
  mel.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
  r=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-420,120); r.set_editor_property('r',rough); mel.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS)
  m=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-420,240); m.set_editor_property('r',metal); mel.connect_material_property(m,'',unreal.MaterialProperty.MP_METALLIC)
  mel.recompile_material(mat); unreal.EditorAssetLibrary.save_loaded_asset(mat)
 made[name]=mat

def category(slot):
 s=slot.lower()
 if 'redtile' in s or 'rooftile' in s: return 'M_Rathaus48_RedTile'
 if 'glass' in s: return 'M_Rathaus48_Glass'
 if 'clockgold' in s or s.endswith('_gold') or 'p_gold' in s: return 'M_Rathaus48_Gold'
 if 'copper' in s: return 'M_Rathaus48_Copper'
 if 'crownrail' in s or 'darkmetal' in s or 'steel' in s or s=='pf_dark': return 'M_Rathaus48_DarkMetal'
 if 'opening' in s or 'recess' in s: return 'M_Rathaus48_DarkOpening'
 if 'inscription' in s: return 'M_Rathaus48_Inscription'
 if 'windowframe' in s: return 'M_Rathaus48_WindowFrame'
 if 'trim' in s or 'windowstone' in s: return 'M_Rathaus48_Trim'
 if 'concrete' in s: return 'M_Rathaus48_Concrete'
 if 'stone' in s or 'sandstone' in s: return 'M_Rathaus48_Sandstone'
 return 'M_Rathaus48_Sandstone'
sm=unreal.load_asset(MESH)
if not sm: raise RuntimeError('v48 mesh missing')
slots=sm.get_editor_property('static_materials'); lines=[]
for i,entry in enumerate(slots):
 slot=str(entry.material_slot_name); cat=category(slot); mat=made[cat]
 try:
  sm.set_material(i,mat)
 except Exception:
  entry.set_editor_property('material_interface',mat); slots[i]=entry
 lines.append(f'{i}|{slot}|{cat}')
try: sm.set_editor_property('static_materials',slots)
except Exception: pass
unreal.EditorAssetLibrary.save_loaded_asset(sm)
os.makedirs(os.path.dirname(OUT),exist_ok=True); open(OUT,'w',encoding='utf-8').write('\n'.join(lines))
