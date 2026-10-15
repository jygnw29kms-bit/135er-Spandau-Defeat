import bpy, json, os

EXPECTED_SOURCE_VERSION='v50_CLOCK_SCALE'
OUTPUT_VERSION='v51_PEDIMENT_READABILITY'
INSCRIPTION_VERTICAL_FACTOR=1.50
SHIELD_FACTOR=1.15
source_path=os.path.abspath(bpy.data.filepath)
source_dir=os.path.dirname(source_path)
OUT_BLEND=os.path.join(source_dir,'SpandauStrike_Rathaus_WORLD_MASTER_v51_PEDIMENT_READABILITY.blend')
OUT_REPORT=os.path.splitext(OUT_BLEND)[0]+'_REPORT.json'
source_version=str(bpy.context.scene.get('ss_master_version',''))
if source_version!=EXPECTED_SOURCE_VERSION:
    raise RuntimeError(f'Expected source {EXPECTED_SOURCE_VERSION}, got {source_version!r}')

changed=[]; before={}; after={}
for name in ('V34_InscriptionLeft','V34_InscriptionRight'):
    o=bpy.data.objects.get(name)
    if not o or o.type!='MESH' or not bool(o.get('ss_export')):
        raise RuntimeError('Missing exported '+name)
    before[name]={'location':list(map(float,o.location)),'dimensions':list(map(float,o.dimensions)),'scale':list(map(float,o.scale))}
    # The inscription meshes are rotated 90 deg around local X: local Y is world vertical.
    o.scale.y *= INSCRIPTION_VERTICAL_FACTOR
    bpy.context.view_layer.objects.active=o; o.select_set(True)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.select_set(False)
    o['ss_revision']=OUTPUT_VERSION
    o['ss_tag']='rathaus_pediment_inscription_readability'
    o['ss_reference_basis']='media/theme/rathaus-spandau-photo.jpg'
    after[name]={'location':list(map(float,o.location)),'dimensions':list(map(float,o.dimensions)),'scale':list(map(float,o.scale))}
    changed.append(name)

name='V34_PedimentShield'; o=bpy.data.objects.get(name)
if not o or o.type!='MESH' or not bool(o.get('ss_export')):
    raise RuntimeError('Missing exported '+name)
before[name]={'location':list(map(float,o.location)),'dimensions':list(map(float,o.dimensions)),'scale':list(map(float,o.scale))}
# Keep normal thickness unchanged; enlarge shield only in its facade plane (local X/Z).
o.scale.x *= SHIELD_FACTOR; o.scale.z *= SHIELD_FACTOR
bpy.context.view_layer.objects.active=o; o.select_set(True)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.select_set(False)
o['ss_revision']=OUTPUT_VERSION; o['ss_tag']='rathaus_pediment_shield_readability'; o['ss_reference_basis']='media/theme/rathaus-spandau-photo.jpg'
after[name]={'location':list(map(float,o.location)),'dimensions':list(map(float,o.dimensions)),'scale':list(map(float,o.scale))}; changed.append(name)

bpy.context.scene['ss_master_version']=OUTPUT_VERSION
bpy.context.scene['ss_v51_change']='Reference-driven pediment readability: V34 inscription height x1.50 and shield in-plane size x1.15 only. Round pediment, medallion, facade, clock, gameplay and collision unchanged.'
report={
 'schema':'SpandauStrike.WorldMasterV51PedimentReadability.v1',
 'source_master':os.path.basename(source_path),
 'source_master_version':EXPECTED_SOURCE_VERSION,
 'output_master':os.path.basename(OUT_BLEND),
 'output_master_version':OUTPUT_VERSION,
 'reference':'media/theme/rathaus-spandau-photo.jpg',
 'inscription_vertical_factor':INSCRIPTION_VERTICAL_FACTOR,
 'shield_in_plane_factor':SHIELD_FACTOR,
 'modified_object_count':len(changed),
 'modified_objects':changed,
 'before':before,'after':after,
 'policy':'Transform-only change on three existing V34 exported pediment detail meshes. No topology, material, pediment body, facade, gameplay or collision change.'
}
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
with open(OUT_REPORT,'w',encoding='utf-8') as f: json.dump(report,f,indent=2,ensure_ascii=False)
print('V51_OUT='+OUT_BLEND); print('V51_REPORT='+OUT_REPORT); print('MODIFIED='+str(len(changed)))
