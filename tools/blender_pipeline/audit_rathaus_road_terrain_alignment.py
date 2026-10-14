import bpy, json, math, statistics
from pathlib import Path
src=Path(bpy.data.filepath);out=src.with_name(src.stem+'_ROAD_TERRAIN_ALIGNMENT.json')
terrain=bpy.data.objects.get('SM_Rathaus_DGM1_1000m_v21') or bpy.data.objects.get('SM_Rathaus_DGM1_1000m_v18')
roads=bpy.data.objects.get('SM_Rathaus_ROADS_DGM_v21') or bpy.data.objects.get('SM_Rathaus_ROADS_DGM_v20') or bpy.data.objects.get('SM_Rathaus_ROADS_DGM_v19') or bpy.data.objects.get('SM_REAL_OSM_Roads')
if not terrain or not roads:raise RuntimeError('terrain or roads missing')
N=513;HALF=500.;STEP=1000./(N-1)
def tz(x,y):
    if x<-HALF or x>HALF or y<-HALF or y>HALF:return None
    fx=(x+HALF)/STEP;fy=(y+HALF)/STEP;i0=int(math.floor(fx));j0=int(math.floor(fy));i1=min(N-1,i0+1);j1=min(N-1,j0+1);tx=fx-i0;ty=fy-j0
    def z(i,j):return float((terrain.matrix_world@terrain.data.vertices[j*N+i].co).z)
    return (z(i0,j0)*(1-tx)+z(i1,j0)*tx)*(1-ty)+(z(i0,j1)*(1-tx)+z(i1,j1)*tx)*ty
d=[];inside=outside=0
for v in roads.data.vertices:
    w=roads.matrix_world@v.co;z=tz(float(w.x),float(w.y))
    if z is None:outside+=1;continue
    inside+=1;d.append(float(w.z)-z)
absd=sorted(abs(x) for x in d);sd=sorted(d)
def pct(a,p):
    k=(len(a)-1)*p;i=int(math.floor(k));j=int(math.ceil(k));return a[i] if i==j else a[i]*(j-k)+a[j]*(k-i)
rep={'file':str(src),'terrain_object':terrain.name,'road_object':roads.name,'sampling':'bilinear 513x513 DGM','road_vertices':len(roads.data.vertices),'inside_terrain':inside,'outside_terrain':outside,'delta_z_m':{'min':min(d),'max':max(d),'mean':statistics.fmean(d),'median':statistics.median(d),'abs_median':statistics.median(absd),'abs_p95':pct(absd,.95),'abs_p99':pct(absd,.99)},'threshold_counts':{'>0.05m':sum(abs(x)>.05 for x in d),'>0.10m':sum(abs(x)>.10 for x in d),'>0.25m':sum(abs(x)>.25 for x in d)}}
out.write_text(json.dumps(rep,indent=2),encoding='utf-8');print('ROAD_TERRAIN',json.dumps(rep),flush=True)
