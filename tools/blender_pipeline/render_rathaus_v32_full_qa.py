import bpy,math
from mathutils import Vector
from pathlib import Path
sc=bpy.context.scene
keep={'REAL_Rebuilt_Architecture','PRODUCTION_RATHAUS_V16_DETAIL','PRODUCTION_RATHAUS_V24_PROFILE','PRODUCTION_RATHAUS_V25_ACCURACY','PRODUCTION_RATHAUS_V26_CLEAN','PRODUCTION_RATHAUS_V31_FENESTRATION','PRODUCTION_RATHAUS_V32_TOWER'}
for o in sc.objects:
    if o.type!='MESH': continue
    cols={c.name for c in o.users_collection}
    role=o.get('ss_role','')
    o.hide_render=not(bool(cols&keep) and o.get('ss_export',True) and role not in ('reference','blockout','collision','gameplay','gameplay_planning','nav'))
for o in list(sc.objects):
    if o.type=='LIGHT': o.hide_render=True
sunD=bpy.data.lights.new('QA32Sun','SUN');sun=bpy.data.objects.new('QA32Sun',sunD);sc.collection.objects.link(sun);sun.rotation_euler=(math.radians(35),math.radians(-20),math.radians(135));sunD.energy=3.0
areaD=bpy.data.lights.new('QA32Fill','AREA');area=bpy.data.objects.new('QA32Fill',areaD);sc.collection.objects.link(area);areaD.energy=1800;areaD.size=70
camD=bpy.data.cameras.new('QA32Cam');cam=bpy.data.objects.new('QA32Cam',camD);sc.collection.objects.link(cam);sc.camera=cam
A=math.radians(47.5);C=math.cos(A);S=math.sin(A)
def w(u,v,z): return Vector((u*C-v*S,u*S+v*C,z))
def look(o,t): o.rotation_euler=(t-o.location).to_track_quat('-Z','Y').to_euler()
area.location=w(-40,-110,90);look(area,w(0,0,35))
sc.render.engine='BLENDER_EEVEE_NEXT';sc.render.resolution_x=1500;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.world.color=(.055,.065,.085)
out=Path(r'C:\Users\dezen\Documents\SpandauStrike\QA');out.mkdir(parents=True,exist_ok=True)
views=[('full_front',w(0,-260,48),w(0,0,39),52),('full_oblique',w(-165,-220,68),w(0,2,38),55),('tower',w(-65,-145,72),w(0,5,59),62)]
for name,pos,target,lens in views:
 cam.location=pos;camD.lens=lens;look(cam,target);sc.render.filepath=str(out/f'rathaus_v32_{name}.png');bpy.ops.render.render(write_still=True);print('QA32',name,sc.render.filepath,flush=True)
