"""Measured usage of the agents that worked on a run: tokens, cost, tool calls and tool errors.

Sources (read-only, verified 2026-10-13):
- Claude Code: ~/.claude/projects/<cwd with non-alphanumerics replaced by '-'>/*.jsonl. Assistant entries carry
  `message.usage`; one API message may span several lines with the same `message.id` (deduplicated here).
  Tool failures are `tool_result` blocks with `is_error: true`.
- OpenCode: `opencode session list --format json` (run inside the project) + `opencode export <id>`.
  Assistant messages carry `tokens` and `cost`; tool parts carry `state.status` and, for bash, the exit code.
- Maestri: ~/.maestri/workspaces/*/workspace.json maps each terminal (codename, agent type, command, role) to
  its floor clone; recruits run in `<clone>/.maestri/roles/<role id>`.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

MAESTRI_HOME = Path(os.environ.get("MAESTRI_HOME", Path.home() / ".maestri"))
CLAUDE_PROJECTS = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude")) / "projects"


@dataclass
class Agent:
    name: str
    tool: str  # claude-code | opencode | other
    command: str
    directory: Path
    role_id: str = ""


@dataclass
class Usage:
    agent: Agent
    sessions: int = 0
    turns: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    cost_usd: float | None = None
    models: dict[str, int] = field(default_factory=dict)
    tools: dict[str, int] = field(default_factory=dict)
    tool_errors: list[str] = field(default_factory=list)
    note: str = ""

    @property
    def tool_calls(self) -> int:
        return sum(self.tools.values())


def _parse_time(value) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc)
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _in_window(ts: datetime | None, since: datetime | None, until: datetime | None) -> bool:
    if ts is None:
        return True
    return (since is None or ts >= since) and (until is None or ts <= until)


def _tool_of(agent_type: str, command: str) -> str:
    if agent_type == "claude_code" or command.startswith("claude"):
        return "claude-code"
    if agent_type == "open_code" or command.startswith("opencode"):
        return "opencode"
    return agent_type or "other"


def maestri_agents(workspace: str, floor: str | None) -> tuple[list[Agent], datetime | None]:
    """Terminals of a Maestri workspace floor (or the ground when floor is None) and the floor creation time."""
    for path in (MAESTRI_HOME / "workspaces").glob("*/workspace.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))["payload"]
        if payload.get("name") != workspace:
            continue
        ground_dir = Path(payload.get("workingDirectory", "."))
        agents: list[Agent] = []
        created = None
        if floor:
            match = [f for f in payload.get("floors", []) if f.get("name") == floor]
            if not match:
                raise ValueError(f"floor '{floor}' not found in workspace '{workspace}'")
            nodes, base, created = match[0]["nodes"], Path(match[0]["clonePath"]), _parse_time(match[0].get("createdAt"))
        else:
            nodes, base = payload.get("nodes", []), ground_dir
        for node in nodes:
            term = (node.get("content") or {}).get("terminal", {}).get("_0")
            if not term:
                continue
            role = (term.get("assignedRoleId") or "").lower()
            directory = base / ".maestri" / "roles" / role if role else Path(term.get("workingDirectory") or base)
            agents.append(Agent(term.get("name", "?"), _tool_of(term.get("agentType", ""), term.get("command", "")),
                                term.get("command", ""), directory, role))
        if floor:
            # The Maestro (manager) normally stays on the ground and coordinates the floor.
            for node in payload.get("nodes", []):
                term = (node.get("content") or {}).get("terminal", {}).get("_0")
                if term and term.get("isManager"):
                    agents.append(Agent(f"{term.get('name', 'Maestro')} (Maestro)",
                                        _tool_of(term.get("agentType", ""), term.get("command", "")),
                                        term.get("command", ""), Path(term.get("workingDirectory") or ground_dir)))
        return agents, created
    raise ValueError(f"Maestri workspace '{workspace}' not found under {MAESTRI_HOME}")


def _describe_input(tool_input) -> str:
    """The part of a tool call that identifies what failed: the command, path or pattern."""
    if not isinstance(tool_input, dict):
        return ""
    for key in ("command", "file_path", "path", "pattern", "url", "query"):
        if tool_input.get(key):
            return str(tool_input[key]).splitlines()[0][:150]
    return ""


def claude_project_dir(directory: Path) -> Path:
    return CLAUDE_PROJECTS / re.sub(r"[^A-Za-z0-9]", "-", str(directory))


def claude_usage(agent: Agent, since: datetime | None, until: datetime | None) -> Usage:
    usage = Usage(agent, cost_usd=None, note="Claude Code reports tokens, not cost (subscription or API billing)")
    folder = claude_project_dir(agent.directory)
    if not folder.is_dir():
        usage.note = f"no Claude Code transcripts in {folder.name}"
        return usage
    seen: set[str] = set()
    calls: dict[str, tuple[str, str]] = {}  # tool_use id -> (tool name, short description of its input)
    for transcript in folder.glob("*.jsonl"):
        counted = False
        for line in transcript.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not _in_window(_parse_time(entry.get("timestamp")), since, until):
                continue
            message = entry.get("message") if isinstance(entry.get("message"), dict) else {}
            content = message.get("content") if isinstance(message.get("content"), list) else []
            if entry.get("type") == "assistant":
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        usage.tools[block["name"]] = usage.tools.get(block["name"], 0) + 1
                        calls[block.get("id")] = (block["name"], _describe_input(block.get("input")))
                msg_id = message.get("id")
                if message.get("usage") and msg_id not in seen:
                    seen.add(msg_id)
                    counted = True
                    u = message["usage"]
                    usage.turns += 1
                    usage.input_tokens += u.get("input_tokens") or 0
                    usage.output_tokens += u.get("output_tokens") or 0
                    usage.cache_read_tokens += u.get("cache_read_input_tokens") or 0
                    usage.cache_write_tokens += u.get("cache_creation_input_tokens") or 0
                    model = message.get("model", "?")
                    usage.models[model] = usage.models.get(model, 0) + 1
            elif entry.get("type") == "user":
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result" and block.get("is_error"):
                        text = block.get("content")
                        text = text if isinstance(text, str) else json.dumps(text, ensure_ascii=False)
                        first = text.strip().splitlines()[0][:160] if text.strip() else "(empty)"
                        # Same shape as OpenCode errors: "<tool>: <command> — <first line of the error>".
                        name, what = calls.get(block.get("tool_use_id"), ("?", ""))
                        usage.tool_errors.append(f"{name}: {what} — {first}" if what else f"{name}: {first}")
        usage.sessions += counted
    return usage


def _opencode(args: list[str], cwd: Path) -> str:
    result = subprocess.run(["opencode", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                            errors="ignore", timeout=180, shell=os.name == "nt")
    return result.stdout


def _json_from(text: str):
    start = min((i for i in (text.find("{"), text.find("[")) if i >= 0), default=-1)
    return json.loads(text[start:]) if start >= 0 else None


def opencode_usage(agent: Agent, since: datetime | None, until: datetime | None) -> Usage:
    usage = Usage(agent, cost_usd=0.0)
    if not agent.directory.is_dir():
        usage.note = f"directory not found: {agent.directory}"
        return usage
    sessions = _json_from(_opencode(["session", "list", "--format", "json"], agent.directory)) or []
    wanted = os.path.normcase(str(agent.directory))
    for s in sessions:
        if os.path.normcase(s.get("directory", "")) != wanted:
            continue
        if not _in_window(_parse_time(s.get("created")), since, until):
            continue
        data = _json_from(_opencode(["export", s["id"]], agent.directory)) or {}
        usage.sessions += 1
        for message in data.get("messages", []):
            info = message.get("info", {})
            if info.get("role") == "assistant":
                usage.turns += 1
                tokens = info.get("tokens") or {}
                usage.input_tokens += tokens.get("input", 0)
                usage.output_tokens += tokens.get("output", 0) + tokens.get("reasoning", 0)
                usage.cache_read_tokens += (tokens.get("cache") or {}).get("read", 0)
                usage.cache_write_tokens += (tokens.get("cache") or {}).get("write", 0)
                usage.cost_usd += info.get("cost") or 0
                model = f"{info.get('providerID', '?')}/{info.get('modelID', '?')}"
                usage.models[model] = usage.models.get(model, 0) + 1
            for part in message.get("parts", []):
                if part.get("type") != "tool":
                    continue
                name = part.get("tool", "?")
                usage.tools[name] = usage.tools.get(name, 0) + 1
                state = part.get("state") or {}
                exit_code = (state.get("metadata") or {}).get("exit")
                if state.get("status") == "error" or exit_code not in (None, 0):
                    detail = state.get("error") or (state.get("input") or {}).get("command") or ""
                    usage.tool_errors.append(f"{name}: {str(detail).splitlines()[0][:150] if detail else 'failed'}"
                                             + (f" (exit {exit_code})" if exit_code not in (None, 0) else ""))
    return usage


def collect(agents: list[Agent], since: datetime | None, until: datetime | None) -> list[Usage]:
    result = []
    for agent in agents:
        if agent.tool == "claude-code":
            result.append(claude_usage(agent, since, until))
        elif agent.tool == "opencode":
            result.append(opencode_usage(agent, since, until))
        else:
            result.append(Usage(agent, note=f"usage source for '{agent.tool}' not supported"))
    return result


def render_markdown(usages: list[Usage], title: str, since: datetime | None, until: datetime | None) -> str:
    lines = [f"# Usage — {title}", "",
             f"- window: {since.isoformat() if since else '-'} → {until.isoformat() if until else 'now'}",
             "- source: local transcripts (Claude Code) and session exports (OpenCode); measured, not estimated", "",
             "| Agent | Tool | Models | Sessions | Turns | Input | Output | Cache read | Cache write | Cost (USD) "
             "| Tool calls | Tool errors |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for u in usages:
        cost = "-" if u.cost_usd is None else f"{u.cost_usd:.4f}"
        models = ", ".join(f"{m}×{n}" for m, n in u.models.items()) or "-"
        lines.append(f"| {u.agent.name} | {u.agent.tool} | {models} | {u.sessions} | {u.turns} | {u.input_tokens:,} "
                     f"| {u.output_tokens:,} | {u.cache_read_tokens:,} | {u.cache_write_tokens:,} | {cost} "
                     f"| {u.tool_calls} | {len(u.tool_errors)} |")
    lines += ["", "## Tool errors", ""]
    any_error = False
    for u in usages:
        for err in u.tool_errors:
            any_error = True
            lines.append(f"- **{u.agent.name}**: {err}")
    if not any_error:
        lines.append("- none")
    notes = [f"- {u.agent.name}: {u.note}" for u in usages if u.note]
    if notes:
        lines += ["", "## Notes", "", *notes]
    return "\n".join(lines) + "\n"


def to_json(usages: list[Usage]) -> list[dict]:
    return [{"agent": u.agent.name, "tool": u.agent.tool, "command": u.agent.command,
             "directory": str(u.agent.directory), "sessions": u.sessions, "turns": u.turns,
             "input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
             "cache_read_tokens": u.cache_read_tokens, "cache_write_tokens": u.cache_write_tokens,
             "cost_usd": u.cost_usd, "models": u.models, "tools": u.tools, "tool_errors": u.tool_errors,
             "note": u.note} for u in usages]
