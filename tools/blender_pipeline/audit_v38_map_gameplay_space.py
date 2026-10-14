import bpy, json
from mathutils import Vector
print('---COLLISION---')
for o in bpy.data.objects:
    if o.get('ss_role')=='collision' and o.get('ss_export',True):
        print('COLL',o.name,'loc',tuple(round(x,2) for x in o.matrix_world.translation),'dims',tuple(round(x,2) for x in o.dimensions),'cols',[c.name for c in o.users_collection])
print('---PLANNING---')
for o in bpy.data.objects:
    if o.get('ss_role')=='gameplay_planning':
        print('PLAN',o.name,'tag',o.get('ss_tag'),'loc',tuple(round(x,2) for x in o.matrix_world.translation),'dims',tuple(round(x,2) for x in o.dimensions),'export',o.get('ss_export'))
