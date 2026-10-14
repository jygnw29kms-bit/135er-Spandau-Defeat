import bpy,json
from pathlib import Path
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v34_FACADE_RELIEF_FIX.blend")
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v35_GAMEPLAY_METADATA.blend');REP=OUT.with_suffix('.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene
changes=[]
def lane(y):
    if y>140:return 'north'
    if y<-140:return 'south'
    return 'mid'
for o in bpy.data.objects:
    n=o.name
    role=o.get('ss_role','')
    tag=o.get('ss_tag','')
    if n.startswith('SM_SPAWN_WEST_'):
        o['ss_team']='west';o['ss_lane']=lane(o.location.y);o['ss_phase']='spawn';o['ss_export']=True;changes.append((n,'spawn','west',o['ss_lane']))
    elif n.startswith('SM_SPAWN_EAST_'):
        o['ss_team']='east';o['ss_lane']=lane(o.location.y);o['ss_phase']='spawn';o['ss_export']=True;changes.append((n,'spawn','east',o['ss_lane']))
    elif n=='SM_OBJECTIVE_A':
        o['ss_objective']='A';o['ss_phase']='objective';o['ss_priority']='primary';changes.append((n,'objective','A','primary'))
    elif n=='SM_OBJECTIVE_B':
        o['ss_objective']='B';o['ss_phase']='objective';o['ss_priority']='primary';changes.append((n,'objective','B','primary'))
    elif tag=='cover' and o.get('ss_export',True):
        h=float(o.dimensions.z)
        cls='low' if h<=1.45 else ('high' if h>=2.1 else 'medium')
        o['ss_cover_class']=cls;o['ss_cover_height_m']=round(h,3);o['ss_phase']='combat';changes.append((n,'cover',cls,round(h,3)))
# Existing gameplay-planning anchors receive explicit non-runtime semantics.
for o in bpy.data.objects:
    if o.get('ss_role')=='gameplay_planning':
        o['ss_runtime']=False;o['ss_planning_only']=True
# Scene-level policy for future additions.
sc['ss_master_version']='v35_GAMEPLAY_METDATA'
sc['gameplay_metadata_policy']='team west/east; lanes north/mid/south; objectives A/B; cover low/medium/high; planning markers non-runtime'
sc['gameplay_balance_status']='metadata only; routes/chokes require geometry-aware review before runtime export'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
REP.write_text(json.dumps({'source':str(SRC),'output':str(OUT),'changed_count':len(changes),'changes':changes,'policy':sc['gameplay_metadata_policy']},indent=2),encoding='utf-8')
print('V35_READY',len(changes),str(OUT),flush=True)
