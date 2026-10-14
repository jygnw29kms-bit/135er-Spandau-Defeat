import bpy, json
for o in bpy.context.scene.objects:
    if o.get('ss_tag')=='cover_blockout':
        print('COVER',o.name,tuple(round(v,2) for v in o.location),o.get('ss_lane'),o.get('ss_cover_class'),o.get('ss_cover_intent'))
