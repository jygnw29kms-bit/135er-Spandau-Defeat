from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

DEFAULT_MAP = json.loads(
    Path(__file__).with_suffix(".json").read_text(encoding="utf-8-sig")
)["map_path"]


def source_revision(repo: Path) -> dict:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    diff = subprocess.check_output(["git", "diff", "--binary", "HEAD", "--"], cwd=repo)
    untracked = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=repo).decode("utf-8").split("\0")
    excluded = {"Saved", "Binaries", "Intermediate", "DerivedDataCache", "__pycache__"}
    inputs = {}
    for relative in filter(None, untracked):
        path = Path(relative)
        if not excluded.intersection(path.parts) and path.suffix.lower() in {".py", ".cpp", ".h", ".cs", ".json", ".ini", ".uasset", ".umap", ".ps1", ".cmd", ".yml", ".yaml", ".md", ".js"}:
            inputs[relative] = hashlib.sha256((repo / path).read_bytes()).hexdigest()
    return {
        "git_head": head,
        "tracked_worktree_dirty": bool(diff),
        "tracked_diff_sha256": hashlib.sha256(diff).hexdigest(),
        "untracked_input_sha256": inputs,
    }
