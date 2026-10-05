import bpy, math, os
BASE=r'C:\Users\dezen\Desktop\135er-Spandau-Defeat\side-projects\F14_TOMCAT_RC'
OUT=os.path.join(BASE,'cad','exports'); os.makedirs(OUT,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def make_mesh(name, verts, faces, collection):
    me=bpy.data.meshes.new(name+'Mesh'); me.from_pydata(verts,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); collection.objects.link(ob); return ob

def box(name,x0,x1,y0,y1,z0,z1,collection):
    v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    f=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(4,0,3,7)]
    return make_mesh(name,v,f,collection)

def cyl(name,r,depth,loc,axis,collection):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=depth,location=loc)
    ob=bpy.context.object; ob.name=name
    if axis=='X': ob.rotation_euler[1]=math.radians(90)
    elif axis=='Y': ob.rotation_euler[0]=math.radians(90)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    collection.objects.link(ob); return ob

def extruded_polygon(name,pts,z0,th,collection):
    n=len(pts); v=[(x,y,z0) for x,y in pts]+[(x,y,z0+th) for x,y in pts]
    f=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
    for i in range(n): f.append((i,(i+1)%n,(i+1)%n+n,i+n))
    return make_mesh(name,v,f,collection)

oml=bpy.data.collections.new('OML_ORIGINAL_SOURCE_BASED'); bpy.context.scene.collection.children.link(oml)
structure=bpy.data.collections.new('RC_PRIMARY_STRUCTURE'); bpy.context.scene.collection.children.link(structure)
envelopes=bpy.data.collections.new('RC_COMPONENT_ENVELOPES'); bpy.context.scene.collection.children.link(envelopes)
refs=bpy.data.collections.new('REFERENCE_GEOMETRY'); bpy.context.scene.collection.children.link(refs)

st=[(8.793,8.401,25.046,-23.248,.010),(38.507,19.602,36.703,-23.248,.043793),(68.220,25.202,41.699,-24.913,.077586),(97.934,32.670,53.357,-23.248,.111379),(127.648,34.537,70.010,-23.248,.145172),(157.362,38.270,81.667,-21.582,.178966),(187.075,38.270,88.328,-21.582,.212759),(216.789,38.270,89.993,-21.582,.246552),(246.503,40.137,89.993,-19.917,.280345),(276.216,83.075,86.663,-18.252,.314138),(305.930,86.808,83.332,-16.586,.347931),(335.644,96.143,76.671,-16.586,.381724),(365.358,107.344,71.675,-14.921,.415517),(395.071,120.411,65.014,-28.244,.449310),(424.785,133.479,60.018,-31.574,.483103),(454.499,144.680,56.687,-33.240,.516897),(484.213,159.615,53.357,-34.905,.550690),(513.926,159.615,56.687,-36.570,.584483),(543.640,150.281,56.687,-36.570,.618276),(573.354,135.346,53.357,-38.236,.652069),(603.067,114.811,46.695,-39.901,.685862),(632.781,109.210,45.030,-39.901,.719655),(662.495,109.210,38.369,-39.901,.753448),(692.209,112.944,45.030,-36.570,.787241),(721.922,112.944,50.026,-34.905,.821034),(751.636,112.944,51.691,-31.574,.854828),(781.350,111.077,53.357,-29.909,.888621),(811.064,105.477,51.691,-28.244,.922414),(840.777,98.009,40.034,-24.913,.956207),(870.491,19.602,33.373,-19.917,.990)]

def sec(x,w,zt,zb,frac,n=48):
    if frac<.30:
        pts=[]; cz=(zt+zb)/2; h=max(1,(zt-zb)/2); expo=2+max(0,(frac-.18)/.12)*.6; pear=max(0,min(1,(frac-.10)/.18))*.16
        for i in range(n):
            t=2*math.pi*i/n; ct,ss=math.cos(t),math.sin(t); y=w*(1 if ct>=0 else -1)*(abs(ct)**(2/expo)); z=cz+h*(1 if ss>=0 else -1)*(abs(ss)**(2/2.15));
            if ss<0: y*=1+pear*abs(ss)
            pts.append((x,y,z))
        return pts
    half=n//2; H=max(2,zt-zb); lobe=max(0,min(1,(frac-.32)/.18)); aft=max(0,min(1,(frac-.68)/.20)); top=[]; bot=[]
    for i in range(half):
        u=-1+2*i/(half-1); edge=H*(.12+.05*aft)*(abs(u)**2.8); crown=H*.025*(1-aft)*math.exp(-(u/.28)**2); top.append((x,u*w,zt-edge+crown))
    for i in range(half):
        u=1-2*i/(half-1); ell=zb+H*.28*(1-math.sqrt(max(0,1-u*u))); bell=math.exp(-((abs(u)-.55)/.23)**2); twins=zb+H*(.36*(1-bell)); bot.append((x,u*w,ell*(1-lobe)+twins*lobe))
    return top+bot

rings=[sec(.5,.8,1,-1,0)]+[sec(*s) for s in st]+[sec(879,1.2,1.2,-1.2,1)]
n=len(rings[0]); v=[p for r in rings for p in r]; f=[]
for r in range(len(rings)-1):
    a=r*n; b=(r+1)*n
    for i in range(n): f.append((a+i,a+(i+1)%n,b+(i+1)%n,b+i))
f.append(tuple(range(n-1,-1,-1))); off=(len(rings)-1)*n; f.append(tuple(off+i for i in range(n)))
fus=make_mesh('OML_F14_Fuselage_UPC_30Station',v,f,oml)

yr,yt,xp,rc,tc=131.,450.,456.5,150.15,55.03; rle=xp-20.4; tle=rle+math.tan(math.radians(20))*(yt-yr)
def wing(sign,label):
    m=36
    def ring(y,ch,xle,thick):
        pts=[]
        for i in range(m//2):
            u=i/(m//2-1); pts.append((xle+u*ch,sign*y,24+math.sin(math.pi*u)*ch*thick*.5))
        for i in range(m//2):
            u=1-i/(m//2-1); pts.append((xle+u*ch,sign*y,24-math.sin(math.pi*u)*ch*thick*.5))
        return pts
    a=ring(yr,rc,rle,.0965); b=ring(yt,tc,tle,.0891); vv=a+b; ff=[]
    for i in range(m): ff.append((i,(i+1)%m,m+(i+1)%m,m+i))
    ff+=[tuple(range(m-1,-1,-1)),tuple(m+i for i in range(m))]; make_mesh('OML_Wing_'+label+'_20deg',vv,ff,oml)
wing(1,'R'); wing(-1,'L')
stab=[(841.45,-209.79),(802.38,-224.73),(662.14,-104.09),(750.29,-72.06),(804.39,-76.33),(825.42,-112.63)]
extruded_polygon('OML_Stabilator_L',stab,-2.75,5.5,oml); extruded_polygon('OML_Stabilator_R',[(x,-y) for x,y in stab],-2.75,5.5,oml)

def extrude_xz(name,pts,y0,th):
    n=len(pts); vv=[(x,y0,z) for x,z in pts]+[(x,y0+th,z) for x,z in pts]; ff=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
    for i in range(n): ff.append((i,(i+1)%n,(i+1)%n+n,i+n))
    return make_mesh(name,vv,ff,oml)
vt=[(595.5,18.9),(690,124.4),(725.3,135.6),(742.8,-5.6)]
extrude_xz('OML_VTail_L',vt,-80.25,4.5); extrude_xz('OML_VTail_R',vt,75.75,4.5)

box('STR_WingBox_CenterPlate',425,500,-155,155,6,12,structure); box('STR_WingBox_FrontWeb',425,435,-150,150,-8,20,structure); box('STR_WingBox_RearWeb',490,500,-150,150,-8,20,structure)
for side,label in [(1,'R'),(-1,'L')]:
    cyl('STR_PivotBoss_'+label+'_24OD',12,34,(456.5,side*131,7),'Z',structure); box('STR_CarbonSocket_'+label,438,492,min(side*117,side*145),max(side*117,side*145),-3,11,structure); cyl('REF_PivotMetal_'+label+'_12mm',6,40,(456.5,side*131,7),'Z',refs)
box('RC_SweepServo_Envelope',408,450,-21,21,-14,26,envelopes); box('RC_Battery_4S_Adjustable',330,540,-23,23,-25,15,envelopes)
box('STR_Battery_Stop_Fwd',326,332,-27,27,-27,17,structure); box('STR_Battery_Stop_Aft',538,544,-27,27,-27,17,structure)
for side,label in [(1,'R'),(-1,'L')]:
    cyl('RC_EDF50_'+label+'_Envelope',26,85,(577.5,side*79,-8),'X',envelopes); box('RC_ESC50_'+label+'_Envelope',515,585,side*79-15,side*79+15,22,37,envelopes)
for i,x in enumerate([210,420,620,790],1): box('REF_PrintSplit_%02d'%i,x-.3,x+.3,-190,190,-80,155,refs)

bpy.context.scene.unit_settings.system='METRIC'; bpy.context.scene.unit_settings.length_unit='MILLIMETERS'; bpy.context.scene.unit_settings.scale_length=.001
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'F14_Tomcat_RC_Engineering_v06.blend'))
for ob in bpy.context.scene.objects: ob.select_set(False)
for ob in oml.objects: ob.select_set(True)
bpy.context.view_layer.objects.active=fus
try: bpy.ops.wm.stl_export(filepath=os.path.join(OUT,'F14_Tomcat_RC_OML_v06_preview.stl'),export_selected_objects=True)
except Exception as e: print('STL export warning',e)
print('DONE',len(oml.objects),len(structure.objects),len(envelopes.objects),len(refs.objects))
