#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SCAN_ROOTS = [ROOT / "docs", ROOT / "tools", ROOT / "ue5", ROOT / "web"]
TEXT_SUFFIXES = {
    ".md", ".txt", ".py", ".json", ".ini", ".yml", ".yaml", ".cpp", ".h", ".cs",
    ".html", ".css", ".js", ".ts", ".tsx", ".php", ".xml", ".toml", ".cfg", ".sh", ".ps1"
}

# Keep this list specific enough to avoid false positives in normal engine/source code.
FORBIDDEN = {
    "f14": "foreign F14 project",
    "tomcat": "foreign F14/Tomcat project",
    "grow-central": "foreign Grow-Central project",
    "growcentral": "foreign Grow-Central project",
    "135er touran": "foreign Touran project",
    "werkstattplaner": "foreign workshop planner project",
    "etes autoservice": "foreign workshop project",
    "lackreparatur kemper": "foreign Kemper project",
    "printbench": "foreign Printbench project",
    "source2": "retired engine path",
    "source 2": "retired engine path",
    "counter-strike 2": "retired/foreign engine reference",
    "day of defeat": "external inspiration must not be named in project assets",
    "dod:s": "external inspiration must not be named in project assets",
    "dods": "external inspiration must not be named in project assets",
}

EXCLUDED_PARTS = {".git", "__pycache__", "node_modules", "Binaries", "Intermediate", "Saved", "DerivedDataCache"}


def should_scan(path: Path) -> bool:
    if path.resolve() == SELF:
        return False
    if any(part in EXCLUDED_PARTS for part in path.parts):
        return False
    return path.suffix.lower() in TEXT_SUFFIXES


def main():
    violations = []
    for base in SCAN_ROOTS:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or not should_scan(path):
                continue
            rel = path.relative_to(ROOT).as_posix()
            rel_lower = rel.lower()
            for token, reason in FORBIDDEN.items():
                if token in rel_lower:
                    violations.append((rel, 0, token, reason))
            try:
                text = path.read_text(encoding="utf-8-sig", errors="strict")
            except UnicodeDecodeError:
                continue
            for line_no, line in enumerate(text.splitlines(), 1):
                lower = line.lower()
                for token, reason in FORBIDDEN.items():
                    if token in lower:
                        violations.append((rel, line_no, token, reason))

    if violations:
        for rel, line_no, token, reason in violations:
            where = f"{rel}:{line_no}" if line_no else rel
            print(f"SCOPE ERROR {where}: {token!r} ({reason})")
        raise SystemExit(f"repository scope validation failed with {len(violations)} violation(s)")

    print("Spandau Strike repository scope: ok")


if __name__ == "__main__":
    main()
