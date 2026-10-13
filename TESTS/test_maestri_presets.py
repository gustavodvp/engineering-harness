from __future__ import annotations

import json
import shutil

import pytest
from conftest import FIXTURES, REPO_ROOT

from harness import adapters, maestri, usage
from harness.model import load_repository


@pytest.fixture
def personal():
    return load_repository(REPO_ROOT).profiles["PERSONAL"]


def test_one_preset_per_model_with_pinned_command_and_stable_id(personal):
    presets = {p["name"]: p for p in adapters.maestri_presets(personal)}
    assert set(presets) == {"Claude Code · opus-5-5", "Claude Code · sonnet-5-5", "OpenCode · deepseek-v4.1-flash"}
    sonnet = presets["Claude Code · sonnet-5-5"]
    assert sonnet["command"] == "claude --model claude-sonnet-5-5" and sonnet["agentType"] == "claude_code"
    assert set(sonnet["personas"]) == {"orchestrator", "reviewer", "support", "harness-curator",
                                       "frontend", "devops", "dba"}
    assert presets["Claude Code · opus-5-5"]["personas"] == ["analyst"]
    assert presets["OpenCode · deepseek-v4.1-flash"]["agentType"] == "open_code"
    again = {p["name"]: p["id"] for p in adapters.maestri_presets(personal)}
    assert again == {n: p["id"] for n, p in presets.items()}


def test_devin_personas_get_no_maestri_preset():
    itau = load_repository(REPO_ROOT).profiles["ITAU"]
    names = {p["name"] for p in adapters.maestri_presets(itau)}
    assert names == {"Claude Code · opus-5-5", "Claude Code · sonnet-5-5"}


def prefs(tmp_path):
    home = tmp_path / ".maestri"
    home.mkdir()
    doc = {"payload": {"agentPresets": [
        {"agentType": "claude_code", "command": "claude", "id": "STOCK-1", "name": "Claude Code"},
        {"agentType": "claude_code", "command": "claude --model old", "id": "X", "name": "Claude Code · sonnet-5-5"},
    ], "rolePresets": []}, "schemaVersion": 1, "type": "preferences"}
    (home / "preferences.json").write_text(json.dumps(doc), encoding="utf-8")
    return home


def test_install_adds_updates_keeps_stock_presets_and_backs_up(tmp_path, monkeypatch, personal):
    home = prefs(tmp_path)
    monkeypatch.setattr(maestri, "maestri_running", lambda: False)
    changes = maestri.install(adapters.maestri_presets(personal), home)
    doc = json.loads((home / "preferences.json").read_text(encoding="utf-8"))
    by_name = {p["name"]: p for p in doc["payload"]["agentPresets"]}
    assert by_name["Claude Code"]["command"] == "claude"  # stock preset untouched
    assert by_name["Claude Code · sonnet-5-5"]["command"] == "claude --model claude-sonnet-5-5"  # updated by name
    assert "personas" not in by_name["Claude Code · opus-5-5"]  # only Maestri's own keys are written
    assert len(doc["payload"]["agentPresets"]) == 4
    assert any(c.startswith("add") for c in changes) and any(c.startswith("update") for c in changes)
    assert list((home / "backups").glob("preferences-*.before-harness.json"))
    second = maestri.install(adapters.maestri_presets(personal), home)
    assert all(c.startswith(("keep", "backup")) for c in second)


def test_install_refuses_while_maestri_runs(tmp_path, monkeypatch, personal):
    home = prefs(tmp_path)
    before = (home / "preferences.json").read_text(encoding="utf-8")
    monkeypatch.setattr(maestri, "maestri_running", lambda: True)
    with pytest.raises(RuntimeError, match="close it"):
        maestri.install(adapters.maestri_presets(personal), home)
    assert (home / "preferences.json").read_text(encoding="utf-8") == before


def test_roles_script_recruits_by_preset_and_states_expected_model(tmp_path):
    from harness import export
    from harness.resolve import compose

    project = tmp_path / "svc"
    shutil.copytree(FIXTURES / "java-service", project)
    repo = load_repository(REPO_ROOT)
    files = export.render(repo, compose(repo, "PERSONAL", "feature", project), project)
    script = files[".harness/maestri-roles.ps1"]
    assert '--role "Reviewer" --preset "Claude Code · sonnet-5-5"' in script
    assert "expected to run on the model claude-sonnet-5-5" in script
    assert json.loads(files[".harness/maestri-presets.json"])[0]["command"].startswith(("claude", "opencode"))


def test_model_mismatch_is_reported(tmp_path):
    ok = usage.Usage(usage.Agent("Plumb", "claude-code", "claude --model claude-sonnet-5-5", tmp_path,
                                 persona="reviewer"), models={"claude-sonnet-5-5": 8})
    # orchestrator opened with a bare `claude`, which fell back to the CLI default (Opus)
    wrong = usage.Usage(usage.Agent("Maestro", "claude-code", "claude", tmp_path, persona="orchestrator"),
                        models={"claude-opus-5-5": 25})
    dev = usage.Usage(usage.Agent("Rivet", "opencode", "opencode", tmp_path, persona="developer"),
                      models={"opencode-go/deepseek-v4.1-flash": 50})
    models = {"reviewer": {"model": "claude-sonnet-5-5"}, "orchestrator": {"model": "claude-sonnet-5-5"},
              "developer": {"model": "opencode-go/deepseek-v4.1-flash"}}
    found = usage.model_mismatches([ok, wrong, dev], models)
    assert len(found) == 1 and "Maestro" in found[0] and "expected `claude-sonnet-5-5`" in found[0]


def test_personal_orchestrator_runs_lighter_model_than_analyst(personal):
    assert personal.models["orchestrator"]["model"] == "claude-sonnet-5-5"
    assert personal.models["analyst"]["model"] == "claude-opus-5-5"
    opus = [p for p, a in personal.models.items() if "opus" in a["model"]]
    assert opus == ["analyst"]
