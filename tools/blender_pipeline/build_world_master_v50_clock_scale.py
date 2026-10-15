import bpy, json, os
from mathutils import Vector

EXPECTED_SOURCE_VERSION='v49_CROWN_PROPORTIONS'
OUTPUT_VERSION='v50_CLOCK_SCALE'
FACTOR=1.45
CENTERS={
 'Front':Vector((2.197,-2.013,61.1)),
 'Rear':Vector((-9.570,8.769,61.1)),
 'West':Vector((-8.740,-2.137,61.1)),
 'East':Vector((1.367,8.893,61.1)),
}
source_path=os.path.abspath(bpy.data.filepath)
source_dir=os.path.dirname(source_path)
OUT_BLEND=os.path.join(source_dir,'SpandauStrike_Rathaus_WORLD_MASTER_v50_CLOCK_SCALE.blend')
OUT_REPORT=os.path.splitext(OUT_BLEND)[0]+'_REPORT.json'
source_version=str(bpy.context.scene.get('ss_master_version',''))
if source_version!=EXPECTED_SOURCE_VERSION:
    raise RuntimeError(f'Expected source {EXPECTED_SOURCE_VERSION}, got {source_version!r}')

before={}; after={}; changed=[]
for face,center in CENTERS.items():
    candidates=[]
    suffix='_'+face
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH': continue
        if not obj.name.startswith('V33_Clock') or suffix not in obj.name: continue
        if not bool(obj.get('ss_export')) or obj.get('ss_role')!='landmark': continue
        candidates.append(obj)
    if len(candidates)!=15:
        raise RuntimeError(f'Expected 15 V33 clock meshes for {face}, got {len(candidates)}')
    for obj in candidates:
        before[obj.name]={
            'location':[float(v) for v in obj.location],
            'dimensions':[float(v) for v in obj.dimensions],
        }
        obj.location=center+(obj.location-center)*FACTOR
        obj.scale*=FACTOR
        bpy.context.view_layer.objects.active=obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        obj.select_set(False)
        obj['ss_revision']=OUTPUT_VERSION
        obj['ss_reference_basis']='media/theme/rathaus-spandau-photo.jpg + public Rathaus Spandau facade references'
        obj['ss_tag']='rathaus_clock_reference_scale'
        after[obj.name]={
            'location':[float(v) for v in obj.location],
            'dimensions':[float(v) for v in obj.dimensions],
        }
        changed.append(obj.name)

bpy.context.scene['ss_master_version']=OUTPUT_VERSION
bpy.context.scene['ss_v50_change']='Reference-driven scale correction of the existing four V33 open radial clocks only; no clock face/ring added; shaft, crown, facade, gameplay and collision unchanged.'
report={
 'schema':'SpandauStrike.WorldMasterV50ClockScale.v1',
 'source_master':os.path.basename(source_path),
 'source_master_version':EXPECTED_SOURCE_VERSION,
 'output_master':os.path.basename(OUT_BLEND),
 'output_master_version':OUTPUT_VERSION,
 'reference':'media/theme/rathaus-spandau-photo.jpg',
 'scale_factor':FACTOR,
 'clock_centers_m':{k:list(map(float,v)) for k,v in CENTERS.items()},
 'modified_object_count':len(changed),
 'modified_objects':sorted(changed),
 'before':before,
 'after':after,
 'policy':'Transform-only correction on existing exported V33 clock boss, 12 marks and two hands per face. No added dial/ring, no topology edits, no gameplay/collision/spawn/objective/cover changes.'
}
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
with open(OUT_REPORT,'w',encoding='utf-8') as f: json.dump(report,f,indent=2,ensure_ascii=False)
print('V50_OUT='+OUT_BLEND)
print('V50_REPORT='+OUT_REPORT)
print('MODIFIED='+str(len(changed)))

