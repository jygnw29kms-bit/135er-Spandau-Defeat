import unreal, project_osm_to_dgm as m
g,z=m.load_dgm()
reg=unreal.AssetRegistryHelpers.get_asset_registry()
assets=reg.get_assets_by_path(m.EXT,recursive=True)
seen=0
for a in assets:
    lab=str(a.get_tag_value("ActorLabel") or "")
    if not lab.startswith("GIS_Road_"): continue
    o=a.get_asset(); loc=o.get_actor_location()
    e=m.OE+loc.x/100.0; n=m.ON-loc.y/100.0
    ex=int(round(e/m.STEP)*m.STEP); ny=int(round(n/m.STEP)*m.STEP)
    near=min(g,key=lambda k:(k[0]-e)**2+(k[1]-n)**2)
    unreal.log("[SAMPLEDBG] %s loc=%s e=%.3f n=%.3f key=(%d,%d) hit=%s nearest=%s dz=%.2f val=%.2f"%(lab,loc,e,n,ex,ny,(ex,ny) in g,near,((near[0]-e)**2+(near[1]-n)**2)**0.5,g[near]))
    seen+=1
    if seen>=5: break
