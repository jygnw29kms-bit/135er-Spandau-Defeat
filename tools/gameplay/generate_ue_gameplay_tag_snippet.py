#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TAGS = ROOT / "tools" / "gameplay" / "spandau_strike_gameplay_tags.json"


def main():
    parser = argparse.ArgumentParser(description="Generate Unreal GameplayTagList lines from the canonical Spandau Strike tag list.")
    parser.add_argument("--tags", type=Path, default=DEFAULT_TAGS)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    data = json.loads(args.tags.read_text(encoding="utf-8-sig"))
    tags = data.get("tags", [])
    if not tags:
        raise SystemExit("no gameplay tags found")
    if len(tags) != len(set(tags)):
        raise SystemExit("duplicate gameplay tags found")
    if any(not tag.startswith("SpandauStrike.") for tag in tags):
        raise SystemExit("all generated tags must use the SpandauStrike.* namespace")

    lines = [
        '; Generated from tools/gameplay/spandau_strike_gameplay_tags.json',
        '; Append these entries under [/Script/GameplayTags.GameplayTagsSettings] in DefaultGameplayTags.ini',
    ]
    lines.extend(
        f'+GameplayTagList=(Tag="{tag}",DevComment="Spandau Strike runtime gameplay")'
        for tag in tags
    )
    output = "\n".join(lines) + "\n"

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
        print(args.out)
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
