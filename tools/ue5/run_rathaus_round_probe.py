from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PROJECT = REPO / 'ue5' / 'SpandauStrike'
EDITOR = Path(r'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe')
UPROJECT = PROJECT / 'SpandauStrike.uproject'
DEFAULT_MAP = '/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v77_GAMEPLAY_ROADS_V85_QA'


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate the full four-sector Rathaus capture round')
    parser.add_argument('--map-path', default=DEFAULT_MAP)
    parser.add_argument('--num-bots', type=int, default=15)
    parser.add_argument('--timeout-seconds', type=int, default=90)
    args = parser.parse_args()

    stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    log = PROJECT / 'Saved' / 'Logs' / f'SpandauStrike_round_probe_{stamp}.log'
    report = PROJECT / 'Saved' / 'Reports' / 'rathaus_round_probe.json'
    log.parent.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    url = f'{args.map_path}?Experience=B_ShooterGame_Elimination?NumBots={args.num_bots}'
    command = [
        str(EDITOR), str(UPROJECT), url, '-game', '-nullrhi', '-nosound', '-unattended', '-nop4',
        f'-abslog={log}', '-SpandauRoundProbe'
    ]
    proc = subprocess.Popen(command, cwd=PROJECT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.time() + args.timeout_seconds
    text = ''
    try:
        while time.time() < deadline:
            if log.exists():
                text = log.read_text(encoding='utf-8', errors='replace')
                if 'Spandau round probe complete:' in text:
                    time.sleep(1.0)
                    break
            if proc.poll() is not None:
                break
            time.sleep(0.5)
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)

    if log.exists():
        text = log.read_text(encoding='utf-8', errors='replace')

    captures = [(int(a), int(b)) for a, b in re.findall(r'SpandauCapturePoint captured: sector=(\d+) point=(\d+) team=', text)]
    advances = [int(x) for x in re.findall(r'Spandau sector advanced: sector=(\d+) tickets=', text)]
    routing = [tuple(map(int, match)) for match in re.findall(r'Spandau objective routing: sector=(\d+) routed=(\d+) failed=(\d+) combatHeld=(\d+)', text)]
    routing_by_sector = {
        sector: next((entry for entry in reversed(routing) if entry[0] == sector), None)
        for sector in range(1, 5)
    }
    complete = re.search(r'Spandau round probe complete: activeSector=(\d+) totalSectors=(\d+) captured=(\d+) attackersWon=(\d+) tickets=(\d+)', text)
    expected_captures = [(sector, point) for sector in range(1, 5) for point in (1, 2)]
    access_none_lines = [line for line in text.splitlines() if 'Accessed None' in line]
    known_access_none = [line for line in access_none_lines if 'CallFunc_SpawnSystemAttached_ReturnValue' in line]
    unexpected_access_none = [line for line in access_none_lines if line not in known_access_none]
    fatal_patterns = ['Fatal error', 'Unhandled Exception', 'FellOutOfWorld', 'KillZ', 'Ensure condition failed']
    fatal_hits = {p: text.count(p) for p in fatal_patterns}
    complete_values = tuple(map(int, complete.groups())) if complete else None

    passed = (
        'Warmup Phase Ended' in text
        and 'Playing Phase' in text
        and 'Spandau round probe initialized:' in text
        and captures == expected_captures
        and advances == [2, 3, 4]
        and all(routing_by_sector[sector] == (sector, 15, 0, 0) for sector in range(1, 5))
        and complete_values == (4, 4, 8, 1, 450)
        and not unexpected_access_none
        and all(v == 0 for v in fatal_hits.values())
    )
    payload = {
        'timestamp': datetime.now().astimezone().isoformat(),
        'map': args.map_path,
        'runtime_log': str(log),
        'warmup_to_playing_seen': 'Warmup Phase Ended' in text and 'Playing Phase' in text,
        'probe_initialized': 'Spandau round probe initialized:' in text,
        'captures': captures,
        'sector_advances': advances,
        'routing_by_sector': routing_by_sector,
        'complete': complete_values,
        'known_nullrhi_access_none': len(known_access_none),
        'unexpected_access_none': len(unexpected_access_none),
        'fatal_hits': fatal_hits,
        'passed': passed,
    }
    report.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print('RATHAUS_ROUND_PROBE=' + json.dumps(payload, separators=(',', ':')))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
