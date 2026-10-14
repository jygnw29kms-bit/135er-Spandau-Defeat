import bpy,json,re
from pathlib import Path
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v35_GAMEPLAY_METADATA.blend")
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v36_GAMEPLAY_CLEAN.blend');REP=OUT.with_suffix('.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene
changes=[]
def lane(y):
    if y>140:return 'north'
    if y<-140:return 'south'
    return 'mid'
for o in bpy.data.objects:
    n=o.name
    if n.startswith('SM_SPAWN_RING_WEST_') or n.startswith('SM_SPAWN_RING_EAST_'):
        team='west' if '_WEST_' in n else 'east'
        o['ss_role']='gameplay_planning';o['ss_export']=False;o['ss_runtime']=False;o['ss_planning_only']=True;o['ss_visual_helper']='spawn_ring';o['ss_team']=team;o['ss_lane']=lane(o.location.y);changes.append((n,'spawn_ring_planning',team,o['ss_lane']))
    elif n.startswith('SM_COVER_PALLET_'):
        m=re.search(r'_(\d+)$',n);idx=m.group(1) if m else ''
        o['ss_role']='gameplay_planning';o['ss_export']=False;o['ss_runtime']=False;o['ss_planning_only']=True;o['ss_visual_helper']='legacy_cover_placeholder';o['ss_replaced_by']='P_CrateShell_COVER_CASE_'+idx;changes.append((n,'cover_placeholder_retired',idx))
    elif n.startswith('P_Crate') and 'COVER_CASE_' in n:
        m=re.search(r'COVER_CASE_(\d+)',n);grp='CASE_'+(m.group(1) if m else 'X')
        o['ss_role']='gameplay';o['ss_tag']='cover';o['ss_export']=True;o['ss_runtime']=True;o['ss_cover_group']=grp;o['ss_cover_class']='low';o['ss_phase']='combat';changes.append((n,'runtime_cover',grp))
sc['ss_master_version']='v36_GAMEPLAY_CLEAN'
sc['gameplay_cleanup']='spawn rings and legacy pallet placeholders planning-only; detailed P_Crate cover remains runtime'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
REP.write_text(json.dumps({'source':str(SRC),'output':str(OUT),'changed_count':len(changes),'changes':changes},indent=2),encoding='utf-8')
print('V36_READY',len(changes),str(OUT),flush=True)
