import bpy, math
from mathutils import Vector
from pathlib import Path
sc=bpy.context.scene
keep={'REAL_Rebuilt_Architecture','REAL_Rebuilt_Detail','PRODUCTION_RATHAUS_V16_DETAIL','PRODUCTION_RATHAUS_V24_PROFILE','PRODUCTION_RATHAUS_V25_ACCURACY','ARCH_MICRODETAIL'}
for o in sc.objects:
 if o.type in {'CAMERA','LIGHT'}: continue
 cols={c.name for c in o.users_collection}; n=o.name.lower(); r=('rathaus' in n or 'tower' in n or 'clock' in n or 'dormer' in n or 'risalit' in n or 'pediment' in n or 'cornice' in n or 'facade' in n or 'portal' in n or 'frontstep' in n or 'window' in n or bool(cols & keep)); o.hide_render=(not r) or o.get('ss_export',True)==False or o.get('ss_role','') in ('reference','blockout','collision','gameplay','gameplay_planning','nav')
for o in list(sc.objects):
 if o.type=='LIGHT': o.hide_render=True
sunD=bpy.data.lights.new('QA25_Sun','SUN');sun=bpy.data.objects.new('QA25_Sun',sunD);sc.collection.objects.link(sun);sun.rotation_euler=(math.radians(35),math.radians(-20),math.radians(135));sunD.energy=3.2
areaD=bpy.data.lights.new('QA25_Fill','AREA');area=bpy.data.objects.new('QA25_Fill',areaD);sc.collection.objects.link(area);areaD.energy=1500;areaD.size=50
camD=bpy.data.cameras.new('QA25_Cam');cam=bpy.data.objects.new('QA25_Cam',camD);sc.collection.objects.link(cam);sc.camera=cam
A=math.radians(47.5);C=math.cos(A);S=math.sin(A)
def w(u,v,z): return Vector((u*C-v*S,u*S+v*C,z))
def look(o,t): o.rotation_euler=(t-o.location).to_track_quat('-Z','Y').to_euler()
area.location=w(-20,-80,60);look(area,w(0,-5,28))
sc.render.engine='BLENDER_EEVEE_NEXT';sc.render.resolution_x=1400;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.world.color=(0.055,0.065,0.085)
out=Path(r'C:\Users\dezen\Documents\SpandauStrike\QA');out.mkdir(parents=True,exist_ok=True)
views=[('front',w(0,-185,40),w(0,-5,30),58),('oblique',w(-105,-150,60),w(0,-3,31),55)]
for name,pos,target,lens in views:
 cam.location=pos;camD.lens=lens;look(cam,target);sc.render.filepath=str(out/f'rathaus_v30_cleanqa_{name}.png');bpy.ops.render.render(write_still=True);print('QA25',name,sc.render.filepath,flush=True)






