import bpy, math, json
from pathlib import Path
from mathutils import Vector
SRC=Path(bpy.data.filepath)
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v41_URBAN_COVER.blend')
REP=OUT.with_suffix('.json')
sc=bpy.context.scene
# collection
col=bpy.data.collections.get('PRODUCTION_GAMEPLAY_V41_COVER') or bpy.data.collections.new('PRODUCTION_GAMEPLAY_V41_COVER')
if sc.collection.children.get(col.name) is None: sc.collection.children.link(col)
# remove stale if rerun
for o in list(col.objects): bpy.data.objects.remove(o, do_unlink=True)
# materials
mat_low=bpy.data.materials.get('M_PlanterConcrete') or bpy.data.materials.get('M_Stone')
mat_high=bpy.data.materials.get('M_Stone') or mat_low
# shared bottom-origin box meshes
def box_mesh(name, sx, sy, sz, mat):
    me=bpy.data.meshes.get(name)
    if me: bpy.data.meshes.remove(me)
    x,y=sx/2,sy/2; z=sz
    vs=[(-x,-y,0),(x,-y,0),(x,y,0),(-x,y,0),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    fs=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(4,0,3,7)]
    me=bpy.data.meshes.new(name); me.from_pydata(vs,[],fs); me.update()
    if mat: me.materials.append(mat)
    return me
low_me=box_mesh('SM_V41_CoverLow_Module',3.2,0.65,0.86,mat_low)
high_me=box_mesh('SM_V41_CoverHigh_Module',2.6,0.72,1.48,mat_high)
# route polylines for tangent orientation
routes=[]
for o in sc.objects:
    if o.type=='CURVE' and o.name.startswith('ROUTE_'):
        pts=[]
        for sp in o.data.splines:
            for p in sp.points: pts.append(o.matrix_world @ Vector((p.co.x,p.co.y,p.co.z)))
        if len(pts)>1: routes.append((o.name,pts))
def orient_for(pos):
    best=None
    p=Vector((pos.x,pos.y,0))
    for rn,pts in routes:
        for a,b in zip(pts,pts[1:]):
            a2=Vector((a.x,a.y,0)); b2=Vector((b.x,b.y,0)); ab=b2-a2
            if ab.length_squared<1e-6: continue
            t=max(0,min(1,(p-a2).dot(ab)/ab.length_squared)); q=a2+ab*t; d=(p-q).length_squared
            if best is None or d<best[0]: best=(d,math.atan2(ab.y,ab.x)+math.pi/2,rn)
    return (best[1],best[2]) if best else (0.0,'')
created=[]
for m in [o for o in sc.objects if o.get('ss_tag')=='cover_blockout']:
    cls=m.get('ss_cover_class','low'); me=high_me if cls=='high' else low_me
    # preserve marker ground contact
    ground=min((m.matrix_world @ Vector(c)).z for c in m.bound_box)
    obj=bpy.data.objects.new(m.name.replace('V40_COVER_','V41_COVER_'),me); col.objects.link(obj)
    obj.location=(m.matrix_world.translation.x,m.matrix_world.translation.y,ground)
    ang,route=orient_for(obj.location); obj.rotation_euler[2]=ang
    obj['ss_role']='gameplay'; obj['ss_tag']='cover'; obj['ss_export']=True; obj['ss_runtime']=True
    obj['ss_cover_class']=cls; obj['ss_lane']=m.get('ss_lane',''); obj['ss_cover_type']='urban_concrete' if cls=='low' else 'urban_masonry'
    obj['ss_source_marker']=m.name; obj['ss_route_context']=route; obj['ss_replaceable_art']=True
    created.append(obj.name)
sc['ss_master_version']='v41_URBAN_COVER'; sc['ss_cover_runtime_count']=len(created); sc['ss_policy']='Spandau Strike world master -> tagged modular UE5 export'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
REP.write_text(json.dumps({'source':str(SRC),'output':str(OUT),'created':created,'count':len(created)},indent=2),encoding='utf-8')
print('V41_READY',len(created),OUT)

