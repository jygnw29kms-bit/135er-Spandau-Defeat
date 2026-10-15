import unreal, os
asset=unreal.EditorAssetLibrary
SRC='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v51/SM_RathausSpandau_BUILDING_v51'
DST='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v51/SM_RathausSpandau_BUILDING_v51_MATREF'
BASE='/Game/SpandauStrike/Maps/Rathaus/Materials/v49'
OUT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v51_reference_materials.txt')
if not asset.does_asset_exist(SRC): raise RuntimeError('missing '+SRC)
if asset.does_asset_exist(DST): asset.delete_asset(DST)
if not asset.duplicate_asset(SRC,DST): raise RuntimeError('duplicate failed')

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
sm=unreal.load_asset(DST); slots=sm.get_editor_property('static_materials'); lines=[]
for i,e in enumerate(slots):
 slot=str(e.material_slot_name); mat=unreal.load_asset(BASE+'/'+category(slot))
 if not mat: raise RuntimeError('missing material for '+slot)
 try: sm.set_material(i,mat)
 except Exception:
  e.set_editor_property('material_interface',mat); slots[i]=e
 lines.append(f'{i}|{slot}|{mat.get_path_name()}')
try: sm.set_editor_property('static_materials',slots)
except Exception: pass
asset.save_loaded_asset(sm)
os.makedirs(os.path.dirname(OUT),exist_ok=True); open(OUT,'w',encoding='utf-8').write('\n'.join(lines))
if len(slots)!=34: raise RuntimeError('expected 34 slots')
