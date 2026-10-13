from __future__ import annotations

import json

import pytest

from harness import usage


@pytest.fixture
def homes(tmp_path, monkeypatch):
    claude = tmp_path / "claude-projects"
    maestri = tmp_path / "maestri"
    monkeypatch.setattr(usage, "CLAUDE_PROJECTS", claude)
    monkeypatch.setattr(usage, "MAESTRI_HOME", maestri)
    return claude, maestri


def write_transcript(claude_root, directory, entries):
    folder = usage.claude_project_dir(directory)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "s1.jsonl").write_text("\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8")


def assistant(msg_id, ts, tokens, tools=(), model="claude-sonnet-5-5"):
    content = [{"type": "tool_use", "name": t, "id": f"{msg_id}-{t}", "input": {"command": f"run {t.lower()}"}}
               for t in tools]
    return {"type": "assistant", "timestamp": ts,
            "message": {"id": msg_id, "model": model, "content": content,
                        "usage": {"input_tokens": tokens, "output_tokens": tokens * 2,
                                  "cache_read_input_tokens": 100, "cache_creation_input_tokens": 10}}}


def test_claude_usage_dedups_messages_counts_errors_and_respects_window(homes, tmp_path):
    claude, _ = homes
    workdir = tmp_path / "proj" / ".maestri" / "roles" / "abc"
    workdir.mkdir(parents=True)
    write_transcript(claude, workdir, [
        assistant("m0", "2026-10-12T10:00:00Z", 999),               # before the window
        assistant("m1", "2026-10-13T01:00:00Z", 10, tools=["Bash"]),
        assistant("m1", "2026-10-13T01:00:01Z", 10, tools=["Read"]),  # same API message, second block
        {"type": "user", "timestamp": "2026-10-13T01:00:02Z",
         "message": {"content": [{"type": "tool_result", "is_error": True, "tool_use_id": "m1-Bash",
                                  "content": "Exit code 2\nboom"}]}},
        assistant("m2", "2026-10-13T01:01:00Z", 5),
    ])
    agent = usage.Agent("Plumb", "claude-code", "claude --model claude-sonnet-5-5", workdir)
    since = usage._parse_time("2026-10-13T00:00:00Z")
    u = usage.claude_usage(agent, since, None)
    assert (u.turns, u.input_tokens, u.output_tokens) == (2, 15, 30)
    assert u.tools == {"Bash": 1, "Read": 1}
    assert u.tool_errors == ["Bash: run bash — Exit code 2"]
    assert u.cost_usd is None and u.sessions == 1


def test_opencode_usage_sums_tokens_cost_and_failed_commands(homes, tmp_path, monkeypatch):
    workdir = tmp_path / "roles" / "dev"
    workdir.mkdir(parents=True)
    sessions = [{"id": "ses_1", "directory": str(workdir), "created": 1791852701271},
                {"id": "ses_other", "directory": str(tmp_path / "elsewhere"), "created": 1791852701271}]
    export = {"info": {"id": "ses_1"}, "messages": [
        {"info": {"role": "assistant", "providerID": "opencode-go", "modelID": "deepseek-v4.1-flash", "cost": 0.01,
                  "tokens": {"input": 100, "output": 20, "reasoning": 5, "cache": {"read": 1000, "write": 0}}},
         "parts": [{"type": "tool", "tool": "bash",
                    "state": {"status": "completed", "input": {"command": "maestri check Rivet"},
                              "metadata": {"exit": 1}}},
                   {"type": "tool", "tool": "read", "state": {"status": "completed"}}]},
    ]}

    def fake(args, cwd):
        return json.dumps(sessions) if args[0] == "session" else "Exporting...\n" + json.dumps(export)

    monkeypatch.setattr(usage, "_opencode", fake)
    u = usage.opencode_usage(usage.Agent("Rivet", "opencode", "opencode -m x", workdir), None, None)
    assert (u.sessions, u.turns, u.input_tokens, u.output_tokens, u.cache_read_tokens) == (1, 1, 100, 25, 1000)
    assert u.cost_usd == pytest.approx(0.01)
    assert u.tools == {"bash": 1, "read": 1}
    assert u.tool_errors == ["bash: maestri check Rivet (exit 1)"]


def test_maestri_agents_maps_recruits_to_role_dirs_and_adds_maestro(homes, tmp_path):
    _, maestri = homes
    clone = tmp_path / "floors" / "demo"
    ws = {"payload": {
        "name": "Engineering Harness", "workingDirectory": str(tmp_path / "ground"),
        "nodes": [{"content": {"terminal": {"_0": {"name": "Claude Code", "agentType": "claude_code",
                                                   "command": "claude", "isManager": True,
                                                   "workingDirectory": ""}}}}],
        "floors": [{"name": "DEMO-1", "clonePath": str(clone), "createdAt": "2026-10-13T00:47:16Z",
                    "nodes": [{"content": {"terminal": {"_0": {
                        "name": "Rivet", "agentType": "open_code", "command": "opencode -m x",
                        "assignedRoleId": "48082A3E-1EFD"}}}}]}]}}
    folder = maestri / "workspaces" / "id1"
    folder.mkdir(parents=True)
    (folder / "workspace.json").write_text(json.dumps(ws), encoding="utf-8")
    agents, created = usage.maestri_agents("Engineering Harness", "DEMO-1")
    assert [a.name for a in agents] == ["Rivet", "Claude Code (Maestro)"]
    assert agents[0].tool == "opencode" and agents[0].directory == clone / ".maestri" / "roles" / "48082a3e-1efd"
    assert agents[1].directory == tmp_path / "ground"
    assert created.isoformat() == "2026-10-13T00:47:16+00:00"
    with pytest.raises(ValueError):
        usage.maestri_agents("Engineering Harness", "NOPE")


def test_report_lists_errors_and_unmeasured_agents(tmp_path):
    a = usage.Usage(usage.Agent("Rivet", "opencode", "", tmp_path), turns=1, cost_usd=0.5,
                    tool_errors=["bash: x (exit 1)"])
    b = usage.Usage(usage.Agent("Devin", "devin", "", tmp_path), note="usage source for 'devin' not supported")
    md = usage.render_markdown([a, b], "t", None, None)
    assert "| Rivet | opencode |" in md and "0.5000" in md
    assert "**Rivet**: bash: x (exit 1)" in md and "not supported" in md
