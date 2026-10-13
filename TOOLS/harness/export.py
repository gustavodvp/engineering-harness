"""Write a composition into a target project and detect drift of generated files."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from . import adapters
from .model import LAYER_NAMES, Repository
from .resolve import Composition

SKILL_DIRS = (".agents/skills", ".claude/skills")
LOCK = ".harness/lock.json"
BLOCK_RE = re.compile(re.escape(adapters.AGENTS_BEGIN.split(" (")[0]) + r".*?" + re.escape(adapters.AGENTS_END) + r"\n?",
                      re.S)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def git_relative(project: Path) -> str:
    """Project path relative to its git root ('.' when it is the root or not in a repository)."""
    try:
        top = subprocess.run(["git", "-C", str(project), "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "."
    rel = project.resolve().relative_to(Path(top).resolve()).as_posix()
    return rel or "."


def render(repo: Repository, comp: Composition, project: Path) -> dict[str, str]:
    """Return {relative path: content} for every file that `harness compose` owns."""
    root = repo.root
    files: dict[str, str] = {}
    rules = [s.unit for s in comp.selected if s.unit.type == "rule"]
    skills = [s.unit for s in comp.selected if s.unit.type == "skill"]
    workflows = [s.unit for s in comp.selected if s.unit.type == "workflow"]
    personas = [u for u in repo.agents() if u.status == "active"]
    names: dict[str, str] = {}
    for unit in skills + workflows:
        if unit.name in names:
            raise ValueError(f"skill name collision on export: {unit.id} and {names[unit.name]}")
        names[unit.name] = unit.id
        for d in SKILL_DIRS:
            files[f"{d}/{unit.name}/SKILL.md"] = adapters.agent_skill(unit, root)
    for unit in personas:
        files[f".claude/agents/{unit.name}.md"] = adapters.claude_agent(unit, comp.profile, root)
        files[f".opencode/agents/{unit.name}.md"] = adapters.opencode_agent(unit, comp.profile, root)
        files[f".harness/personas/{unit.name}.md"] = adapters.persona_body(unit, comp.profile, root)
    files[".harness/maestri-roles.ps1"] = adapters.maestri_script(personas, comp.profile, git_relative(project))
    report = resolution_report(repo, comp, project)
    files[".harness/resolution.json"] = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    files[".harness/resolution.md"] = resolution_markdown(report)
    block = adapters.agents_md_block(rules, workflows, skills, personas, comp.profile, root)
    files["AGENTS.md"] = _merge_agents_md(project / "AGENTS.md", block)
    return files


def _merge_agents_md(path: Path, block: str) -> str:
    """Only the marked block is owned by the harness; the project's own text is preserved."""
    if not path.is_file():
        return f"# AGENTS.md\n\n{block}"
    current = path.read_text(encoding="utf-8")
    if BLOCK_RE.search(current):
        return BLOCK_RE.sub(lambda _: block, current, count=1)
    return current.rstrip("\n") + "\n\n" + block


def resolution_report(repo: Repository, comp: Composition, project: Path) -> dict:
    root = repo.root
    res = comp.resolution
    overridden = {(o.loser, o.key) for o in res.overrides}
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "profile": comp.profile.name,
        "context": {k: sorted(v) for k, v in comp.context.items()},
        "layers": {str(k): v for k, v in LAYER_NAMES.items()},
        "loaded": [
            {"id": s.unit.id, "type": s.unit.type, "layer": s.unit.layer, "version": s.unit.m("version"),
             "source": _rel(root, s.unit.path), "reason": s.reason,
             "enforcement": s.unit.m("enforcement", "default"),
             "decides": s.unit.decides,
             "overridden_keys": sorted(k for (src, k) in overridden if src == s.unit.id)}
            for s in comp.selected
        ],
        "not_loaded": [{"id": s.unit.id, "reason": s.reason} for s in comp.skipped],
        "project_instructions": [
            {"file": _rel(project, p), "layer": 4,
             "note": "read-only: reviewed by the agent, never rewritten by the harness (except the marked block)"}
            for p in comp.project_instructions
        ],
        "story": _rel(project, comp.story) if comp.story else None,
        "effective_decisions": {k: {"value": d.value, "source": d.source} for k, d in res.effective.items()},
        "overrides": [o.__dict__ for o in res.overrides],
        "conflicts": [{"key": c.key, "sources": c.sources, "reason": c.reason} for c in res.conflicts],
        "missing_override_targets": [{"unit": u, "target": t} for u, t in comp.missing_overrides],
    }


def resolution_markdown(r: dict) -> str:
    lines = ["<!-- GENERATED by engineering-harness. Do not edit. -->", f"# Harness resolution: profile {r['profile']}",
             "", f"- Generated: {r['generated_at']}",
             f"- Task: {', '.join(r['context']['task'])}; detected stack: {', '.join(r['context']['stack']) or '(none)'}",
             f"- Story: {r['story'] or '(none)'}", "",
             "Precedence (low → high): " + " → ".join(f"{k}. {v}" for k, v in r["layers"].items()) +
             ". Mandatory rules are never overridden.", "", "## Loaded", "",
             "| Unit | Layer | Source | Why | Overridden keys |", "|---|---|---|---|---|"]
    for u in r["loaded"]:
        flag = " (mandatory)" if u["enforcement"] == "mandatory" else ""
        lines.append(f"| `{u['id']}` v{u['version']}{flag} | {u['layer']} | `{u['source']}` | {u['reason']} | "
                     f"{', '.join(u['overridden_keys']) or '-'} |")
    lines += ["", "## Effective decisions", ""]
    lines += [f"- `{k}` = `{v['value']}` (from `{v['source']}`)" for k, v in r["effective_decisions"].items()] or ["- none"]
    lines += ["", "## Overrides applied", ""]
    lines += [f"- `{o['key']}`: `{o['winner']}` (`{o['winner_value']}`) replaces `{o['loser']}` (`{o['loser_value']}`)"
              for o in r["overrides"]] or ["- none"]
    lines += ["", "## Unresolved conflicts", ""]
    lines += [f"- **`{c['key']}`**: " + ", ".join(f"`{s}`=`{v}`" for s, v in c["sources"]) + f" ({c['reason']})"
              for c in r["conflicts"]] or ["- none"]
    lines += ["", "## Project instructions (layer 4)", ""]
    lines += [f"- `{p['file']}`: {p['note']}" for p in r["project_instructions"]] or ["- none found"]
    lines += ["", "## Not loaded", ""]
    lines += [f"- `{u['id']}`: {u['reason']}" for u in r["not_loaded"]] or ["- none"]
    return "\n".join(lines) + "\n"


def write(project: Path, files: dict[str, str]) -> list[str]:
    """Write files, remove ones generated previously and no longer selected, update the lock."""
    lock_path = project / LOCK
    previous = json.loads(lock_path.read_text(encoding="utf-8")).get("files", {}) if lock_path.is_file() else {}
    for rel in previous:
        if rel not in files and rel != "AGENTS.md":
            stale = project / rel
            if stale.is_file():
                stale.unlink()
                parent = stale.parent
                if parent.name and not any(parent.iterdir()):
                    parent.rmdir()
    for rel, content in files.items():
        path = project / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    claude_md = project / "CLAUDE.md"
    notes = []
    if not claude_md.is_file():
        claude_md.write_text("@AGENTS.md\n", encoding="utf-8", newline="\n")
        notes.append("created CLAUDE.md importing AGENTS.md")
    elif "@AGENTS.md" not in claude_md.read_text(encoding="utf-8"):
        notes.append("CLAUDE.md exists without '@AGENTS.md': add that line so Claude Code sees the rules")
    lock = {"files": {rel: _sha(_owned_part(rel, c)) for rel, c in files.items()
                      if not rel.startswith(".harness/resolution")}}
    lock_path.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return notes


def _owned_part(rel: str, content: str) -> str:
    if rel == "AGENTS.md":
        match = BLOCK_RE.search(content)
        return match.group(0) if match else ""
    return content


def drift(project: Path) -> list[str]:
    lock_path = project / LOCK
    if not lock_path.is_file():
        return [f"no {LOCK}: run `harness compose` first"]
    problems = []
    for rel, digest in json.loads(lock_path.read_text(encoding="utf-8"))["files"].items():
        path = project / rel
        if not path.is_file():
            problems.append(f"missing generated file: {rel}")
            continue
        content = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        if _sha(_owned_part(rel, content)) != digest:
            problems.append(f"edited by hand: {rel} (edit the canonical source and re-run compose)")
    return problems
