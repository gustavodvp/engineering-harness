from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"

FILES = {"skill": "SKILL.md", "rule": "RULE.md", "workflow": "WORKFLOW.md", "agent": "AGENT.md"}
CONTAINERS = {"skill": "SKILLS", "rule": "RULES", "workflow": "WORKFLOWS"}
WORKFLOW_BODY = "# W\n\n## Inputs\n\n- x\n\n## Outputs\n\n- y\n\n## Done when\n\n- [ ] z\n"
AGENT_BODY = "# A\n\n## Responsibilities\n\n- x\n\n## Never\n\n- y\n\n## Handoff\n\n- z\n"


class MiniRepo:
    """Builds a throwaway harness repository for tests."""

    def __init__(self, root: Path):
        self.root = root
        (root / "GENERIC").mkdir(parents=True)

    def unit(self, kind: str, name: str, profile: str | None = None, body: str | None = None,
             **meta: str) -> Path:
        if kind == "agent":
            folder = self.root / "AGENTS" / name
        elif profile:
            folder = self.root / "PROFILES" / profile / CONTAINERS[kind] / name
        else:
            folder = self.root / "GENERIC" / CONTAINERS[kind] / name
        folder.mkdir(parents=True, exist_ok=True)
        metadata = {
            "harness.type": kind,
            "harness.scope": "profile" if profile else "generic",
            "harness.version": "1.0.0",
            "harness.status": "active",
            "harness.reviewed": "2026-10-01",
        }
        if profile:
            metadata["harness.profile"] = profile
        if kind == "skill":
            metadata["harness.sources"] = "https://example.com/docs"
        metadata.update({f"harness.{k.replace('_', '-')}": v for k, v in meta.items()})
        fm = {"name": name, "description": f"Test {kind} {name} used by the harness test-suite.",
              "metadata": metadata}
        if body is None:
            body = {"workflow": WORKFLOW_BODY, "agent": AGENT_BODY}.get(kind, f"# {name}\n\nContent.\n")
        path = folder / FILES[kind]
        path.write_text(f"---\n{yaml.safe_dump(fm, sort_keys=False)}---\n{body}", encoding="utf-8")
        return path

    def profile(self, name: str, models: dict | None = None, **extra) -> Path:
        folder = self.root / "PROFILES" / name
        folder.mkdir(parents=True, exist_ok=True)
        fm = {"name": name, "description": f"Profile {name}", "status": "active",
              "models": models or {}, **extra}
        path = folder / "PROFILE.md"
        path.write_text(f"---\n{yaml.safe_dump(fm, sort_keys=False)}---\n# {name}\n", encoding="utf-8")
        return path


@pytest.fixture
def mini(tmp_path) -> MiniRepo:
    repo = MiniRepo(tmp_path / "harness")
    repo.unit("agent", "developer")
    repo.profile("ACME", models={"developer": {"tool": "opencode", "model": "prov/cheap", "confirmed": False}})
    return repo
