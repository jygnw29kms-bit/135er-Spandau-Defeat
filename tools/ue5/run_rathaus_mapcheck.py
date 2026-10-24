from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]
PROJECT=REPO/'ue5'/'SpandauStrike'
CMD=Path(r'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe')
UPROJECT=PROJECT/'SpandauStrike.uproject'
SCRIPT=PROJECT/'Content'/'Python'/'validate_rathaus_mapcheck.py'
DEFAULT_MAP='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v77_GAMEPLAY_ROADS_V85_QA'

def main() -> int:
    parser=argparse.ArgumentParser(description='Run Unreal MapCheck for a Rathaus map')
    parser.add_argument('--map-path', default=DEFAULT_MAP)
    args=parser.parse_args()
    stamp=datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    log=PROJECT/'Saved'/'Logs'/f'SpandauStrike_mapcheck_{stamp}.log'
    report=PROJECT/'Saved'/'Reports'/'rathaus_mapcheck.json'
    env=os.environ.copy(); env['SPANDAU_VALIDATION_MAP']=args.map_path
    completed=subprocess.run([
        str(CMD),str(UPROJECT),'-run=pythonscript',f'-script={SCRIPT}','-unattended','-nop4','-nosplash','-nullrhi',f'-abslog={log}'
    ],cwd=PROJECT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=False)
    text=log.read_text(encoding='utf-8',errors='replace') if log.exists() else ''
    german_ok=bool(re.search(r'MapCheck: Kartenprüfung abgeschlossen: 0 Fehler, 0 Warnung',text))
    english_ok=bool(re.search(r'MapCheck: Map check complete: 0 Error\(s\), 0 Warning',text))
    trigger='SPANDAU_MAPCHECK_TRIGGERED='+args.map_path in text
    fatal={p:text.count(p) for p in ['Fatal error','Unhandled Exception','Ensure condition failed']}
    passed=completed.returncode==0 and trigger and (german_ok or english_ok) and all(v==0 for v in fatal.values())
    payload={'timestamp':datetime.now().astimezone().isoformat(),'map':args.map_path,'runtime_log':str(log),'returncode':completed.returncode,'mapcheck_zero_errors_zero_warnings':german_ok or english_ok,'trigger_seen':trigger,'fatal_hits':fatal,'passed':passed}
    report.parent.mkdir(parents=True,exist_ok=True); report.write_text(json.dumps(payload,indent=2),encoding='utf-8')
    print('RATHAUS_MAPCHECK='+json.dumps(payload,separators=(',',':')))
    return 0 if passed else 1

if __name__=='__main__':
    raise SystemExit(main())
