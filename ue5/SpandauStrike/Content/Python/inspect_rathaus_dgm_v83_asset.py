import json, os, unreal
ASSETS=[
'/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v83/SM_RathausSpandau_DGM1_DOP_v83_RAWDGM',
'/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v85/SM_RathausSpandau_ROADS_DGM_v85_PROJECTED_V83',
'/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v77/SM_RathausSpandau_DGM1_DOP_v77',
]
out=[]
for p in ASSETS:
    m=unreal.load_asset(p)
    if not m:
        out.append({'asset':p,'missing':True}); continue
    b=m.get_bounds()
    row={'asset':p,'origin':[b.origin.x,b.origin.y,b.origin.z],'extent':[b.box_extent.x,b.box_extent.y,b.box_extent.z],'radius':b.sphere_radius}
    out.append(row)
    unreal.log('SPANDAU_DGM_ASSET '+json.dumps(row,separators=(',',':')))
rep=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_dgm_assets.json')
os.makedirs(os.path.dirname(rep),exist_ok=True)
with open(rep,'w',encoding='utf-8') as f: json.dump(out,f,indent=2)
