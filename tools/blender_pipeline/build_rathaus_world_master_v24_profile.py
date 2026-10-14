import bpy, math, json
from pathlib import Path
from mathutils import Vector
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v23_GROUNDED_CLEAN.blend")
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v24_PROFILE.blend'); REP=OUT.with_suffix('.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC)); sc=bpy.context.scene
ANG=math.radians(47.5); C=math.cos(ANG); S=math.sin(ANG)
def wxy(u,v): return (u*C-v*S,u*S+v*C)
def mat(name,color,rough=.55,metal=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;return m
STONE=mat('M_V24_Stone',(0.46,0.39,0.31),.7); TRIM=mat('M_V24_Trim',(0.62,0.55,0.45),.58); ROOF=mat('M_V24_RoofTile',(0.29,0.045,0.026),.78); COPPER=mat('M_V24_Copper',(0.13,0.24,0.19),.36,.55); DARK=mat('M_V24_Recess',(0.025,0.028,0.03),.9)
COL=bpy.data.collections.get('PRODUCTION_RATHAUS_V24_PROFILE') or bpy.data.collections.new('PRODUCTION_RATHAUS_V24_PROFILE')
if COL.name not in sc.collection.children:sc.collection.children.link(COL)
def tag(o,kind):
    o['ss_role']='landmark';o['ss_tag']='rathaus_v24_'+kind;o['ss_export']=True;return o
def mesh_obj(name,verts,faces,ma,kind):
    me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(verts,[],faces);me.update();me.materials.append(ma);o=bpy.data.objects.new(name,me);COL.objects.link(o);return tag(o,kind)
def box(name,u,v,z,su,sv,sz,ma,kind='facade',bevel=.06):
    x,y=wxy(u,v);bpy.ops.mesh.primitive_cube_add(location=(x,y,z),rotation=(0,0,ANG));o=bpy.context.object;o.name=name;o.dimensions=(su,sv,sz);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(o.users_collection):c.objects.unlink(o)
    COL.objects.link(o);o.data.materials.append(ma);tag(o,kind)
    if bevel:md=o.modifiers.new('ProfileBevel','BEVEL');md.width=bevel;md.segments=3
    return o
def cylinder(name,u,v,z,r,depth,ma,kind='facade',verts=24):
    x,y=wxy(u,v);bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=(x,y,z));o=bpy.context.object;o.name=name
    for c in list(o.users_collection):c.objects.unlink(o)
    COL.objects.link(o);o.data.materials.append(ma);tag(o,kind);md=o.modifiers.new('EdgeBevel','BEVEL');md.width=.04;md.segments=2;return o
def local_prism(name,points2d,z0,z1,ma,kind):
    # points2d are local (u,v); vertical extrusion
    verts=[]
    for z in (z0,z1):
        for u,v in points2d:
            x,y=wxy(u,v);verts.append((x,y,z))
    n=len(points2d);faces=[];faces.append(tuple(range(n)));faces.append(tuple(range(n,2*n)))
    for i in range(n):j=(i+1)%n;faces.append((i,j,n+j,n+i))
    return mesh_obj(name,verts,faces,ma,kind)
def roof_slope(name,u0,u1,v_outer,v_inner,z_outer,z_inner,ma):
    # sloped rectangular roof plane with thickness .22m
    t=.22;verts=[]
    for dz in (0,-t):
        for u,v,z in ((u0,v_outer,z_outer),(u1,v_outer,z_outer),(u1,v_inner,z_inner),(u0,v_inner,z_inner)):
            x,y=wxy(u,v);verts.append((x,y,z+dz))
    faces=[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    return mesh_obj(name,verts,faces,ma,'roof')
def frustum(name,u,v,z0,z1,r0,r1,sides,ma,kind='tower',rot=math.pi/8):
    verts=[]
    cx,cy=wxy(u,v)
    for z,r in ((z0,r0),(z1,r1)):
        for i in range(sides):
            a=rot+2*math.pi*i/sides;verts.append((cx+r*math.cos(a),cy+r*math.sin(a),z))
    faces=[tuple(range(sides-1,-1,-1)),tuple(range(sides,2*sides))]
    for i in range(sides):j=(i+1)%sides;faces.append((i,j,sides+j,sides+i))
    return mesh_obj(name,verts,faces,ma,kind)
created=[]
# 1. Front/rear mansard planes: articulate the high roof without changing building footprint.
created += [roof_slope('V24_MansardFront',-56,56,-27.15,-19.0,21.0,27.1,ROOF),roof_slope('V24_MansardRear',-56,56,27.15,19.0,21.0,27.1,ROOF)]
# end returns/slopes on west/east edges
# local side roof strips, split to preserve courtyard impression rather than cap entire rectangle
for side,u_outer,u_inner in [('West',-56,-49),('East',56,49)]:
    pts=[(u_outer,-27),(u_inner,-20),(u_inner,20),(u_outer,27)]
    # custom quad shell tilted via z according to u distance
    verts=[]
    for dz in (0,-.22):
        for u,v in pts:
            frac=abs(u_outer-u)/7.0;z=21+6.1*frac;x,y=wxy(u,v);verts.append((x,y,z+dz))
    faces=[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    created.append(mesh_obj('V24_Mansard'+side,verts,faces,ROOF,'roof'))
# 2. Three-step profiled facade cornices across the actual front face.
for k,(z,depth,height) in enumerate(((2.45,.34,.22),(6.65,.38,.24),(10.75,.34,.22),(14.85,.38,.24),(19.05,.48,.3),(20.45,.62,.42))):
    created.append(box(f'V24_FrontCornice_{k}',0,-27.25-depth/2,z,112.6,depth,height,TRIM,'facade',.045))
# Main front plinth with stepped projection.
created += [box('V24_FrontPlinthLower',0,-27.45,0.65,112.6,.85,1.3,TRIM,'facade',.08),box('V24_FrontPlinthCap',0,-27.62,1.48,112.9,1.05,.35,TRIM,'facade',.06)]
# 3. Central risalit articulation: 4 round engaged columns + bases/capitals.
for i,u in enumerate((-9.2,-3.2,3.2,9.2)):
    created.append(cylinder(f'V24_RisalitColumn_{i}',u,-34.25,12.0,.56,16.6,TRIM,'entrance',28))
    created.append(cylinder(f'V24_RisalitBase_{i}',u,-34.25,3.55,.78,.6,TRIM,'entrance',28))
    created.append(cylinder(f'V24_RisalitCapital_{i}',u,-34.25,20.45,.82,.72,TRIM,'entrance',28))
    created.append(cylinder(f'V24_RisalitAbacus_{i}',u,-34.25,20.88,.94,.18,TRIM,'entrance',28))
# central entrance entablature layers
created += [box('V24_RisalitEntablatureA',0,-34.35,21.0,25.5,.72,.55,TRIM,'entrance',.08),box('V24_RisalitEntablatureB',0,-34.5,21.52,26.2,.9,.35,TRIM,'entrance',.08)]
# Dark portal recesses behind existing curved stone arches, giving real depth.
for i,u in enumerate((-5.2,0,5.2)):created.append(box(f'V24_PortalRecess_{i}',u,-34.52,5.0,3.45,.18,7.0,DARK,'entrance',.02))
# 4. Pilaster capital/base profiles at the six major facade articulation positions.
for i,u in enumerate((-49,-33,-17,17,33,49)):
    created += [box(f'V24_FacadePilasterBase_{i}',u,-27.58,2.2,1.45,.82,.55,TRIM,'facade',.08),box(f'V24_FacadePilasterCap_{i}',u,-27.58,19.9,1.6,.88,.62,TRIM,'facade',.08)]
# 5. Tower profile: stepped clock-stage cornices and postwar crown frustums.
# Center is local (u=0,v=5), matching existing tower.
for z,r,h in ((55.0,8.6,.42),(59.1,8.95,.5),(65.3,9.15,.55),(69.9,10.0,.48),(74.9,9.2,.42)):
    created.append(frustum(f'V24_TowerProfile_{int(z*10)}',0,5,z-h/2,z+h/2,r,r,8,TRIM,'tower'))
created += [frustum('V24_TowerCrownLower',0,5,75.0,77.0,8.7,7.8,8,COPPER,'tower'),frustum('V24_TowerCrownMid',0,5,77.0,80.0,7.8,5.6,8,COPPER,'tower'),frustum('V24_TowerCrownUpper',0,5,80.0,81.5,5.6,3.1,8,COPPER,'tower')]
# small capped lantern/finial silhouette, stays below old master max bounds.
created += [frustum('V24_TowerLantern',0,5,81.5,83.0,3.1,2.3,8,COPPER,'tower'),frustum('V24_TowerFinialBase',0,5,83.0,83.55,2.3,.9,8,COPPER,'tower')]
# Disable only the clearly redundant primitive copper cap; retain better V6 cap as hidden reference too to avoid z-fighting with v24 crown.
replaced=[]
for n in ('SM_CopperCap','SM_V6_CopperCap'):
    o=bpy.data.objects.get(n)
    if o:
        o.hide_viewport=True;o.hide_render=True;o['ss_export']=False;o['ss_role']='reference';o['ss_tag']='replaced_tower_cap';replaced.append(n)
# Mark v16 coarse cornice overlays as reference where v24 stepped profiles supersede them.
for n in ('V16_FrontRoofCornice','SM_EavesBand'):
    o=bpy.data.objects.get(n)
    if o:
        o.hide_viewport=True;o.hide_render=True;o['ss_export']=False;o['ss_role']='reference';o['ss_tag']='replaced_profile';replaced.append(n)
sc['ss_master_version']='v24_PROFILE';sc['rathaus_profile_pass']='mansard slopes + stepped facade + engaged columns + portal depth + tower crown';sc['rathaus_dimensions_policy']='do not alter verified 116m facade / 80m-class tower footprint'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
rep={'source':str(SRC),'output':str(OUT),'created_count':len(created),'created_names':[o.name for o in created],'replaced_hidden':replaced,'collection':COL.name}
REP.write_text(json.dumps(rep,indent=2),encoding='utf-8');print('V24_READY',json.dumps({'created':len(created),'replaced_hidden':replaced,'output':str(OUT)}),flush=True)
