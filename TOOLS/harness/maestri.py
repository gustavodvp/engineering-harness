"""Install the profile's per-model agent presets into Maestri (~/.maestri/preferences.json).

Maestri has no CLI verb to create presets, and it rewrites preferences.json while running, so this
refuses to touch the file while the app is open. It always backs the file up first, keeps every
preset it doesn't own, and only adds or updates presets by their stable id (or by name).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MAESTRI_HOME = Path(os.environ.get("MAESTRI_HOME", Path.home() / ".maestri"))
PRESET_KEYS = ("agentType", "codexDaemonMigration", "command", "icon", "id", "isActive", "maestroMode", "name",
               "startInChatMode")


def maestri_running() -> bool:
    try:
        if sys.platform == "win32":
            out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Maestri.exe", "/NH"], capture_output=True,
                                 text=True, errors="ignore").stdout
            return "maestri.exe" in out.lower()
        return subprocess.run(["pgrep", "-x", "Maestri"], capture_output=True).returncode == 0
    except OSError:
        return False


def plan(presets: list[dict], home: Path = MAESTRI_HOME) -> tuple[dict, list[str]]:
    """Return the new preferences document and a human-readable list of changes."""
    path = home / "preferences.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    current = doc["payload"].setdefault("agentPresets", [])
    changes = []
    for wanted in presets:
        clean = {k: wanted[k] for k in PRESET_KEYS}
        match = next((p for p in current if p.get("id") == clean["id"] or p.get("name") == clean["name"]), None)
        if match is None:
            current.append(clean)
            changes.append(f"add    {clean['name']}: {clean['command']}")
        elif any(match.get(k) != clean[k] for k in ("agentType", "command", "name")):
            match.update(clean)
            changes.append(f"update {clean['name']}: {clean['command']}")
        else:
            changes.append(f"keep   {clean['name']}")
    return doc, changes


def install(presets: list[dict], home: Path = MAESTRI_HOME, allow_running: bool = False) -> list[str]:
    path = home / "preferences.json"
    if not path.is_file():
        raise FileNotFoundError(f"{path} not found: open Maestri once so it creates its preferences")
    if maestri_running() and not allow_running:
        raise RuntimeError("Maestri is running and would overwrite preferences.json: close it (also from the "
                           "tray) and run again")
    doc, changes = plan(presets, home)
    backup_dir = home / "backups"
    backup_dir.mkdir(exist_ok=True)
    backup = backup_dir / f"preferences-{datetime.now():%Y%m%d-%H%M%S}.before-harness.json"
    shutil.copy2(path, backup)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    json.loads(tmp.read_text(encoding="utf-8"))  # never leave Maestri with an unreadable file
    os.replace(tmp, path)
    return changes + [f"backup {backup}"]
