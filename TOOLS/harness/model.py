"""Loading of canonical knowledge units (skills, rules, workflows, agents) and profiles."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

CANONICAL_FILES = {
    "skill": "SKILL.md",
    "rule": "RULE.md",
    "workflow": "WORKFLOW.md",
    "agent": "AGENT.md",
}
# Container folder name -> unit type.
CONTAINERS = {"SKILLS": "skill", "RULES": "rule", "WORKFLOWS": "workflow"}

# Precedence layers: a higher number is more specific and wins a declared override.
LAYER_GENERIC_RULE = 1
LAYER_SKILL = 2
LAYER_PROFILE = 3
LAYER_PROJECT = 4
LAYER_STORY = 5
LAYER_NAMES = {
    LAYER_GENERIC_RULE: "generic rules",
    LAYER_SKILL: "specialized skills and workflows",
    LAYER_PROFILE: "active profile",
    LAYER_PROJECT: "project instructions",
    LAYER_STORY: "story criteria",
}

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?(.*)\Z", re.DOTALL)


class HarnessError(Exception):
    pass


def split_frontmatter(text: str) -> tuple[dict, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise HarnessError("missing YAML frontmatter delimited by '---'")
    data = yaml.safe_load(match.group(1)) or {}
    if not isinstance(data, dict):
        raise HarnessError("frontmatter must be a YAML mapping")
    return data, match.group(2)


def parse_list(value: str | None) -> list[str]:
    """'a, b,c' -> ['a', 'b', 'c']."""
    if not value:
        return []
    return [item.strip() for item in str(value).split(",") if item.strip()]


def parse_pairs(value: str | None, sep: str) -> list[tuple[str, str]]:
    """'k1=v1; k2=v2' (sep '=') -> [('k1', 'v1'), ('k2', 'v2')]."""
    pairs = []
    for chunk in str(value or "").split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        if sep not in chunk:
            raise HarnessError(f"expected '{sep}' in '{chunk}'")
        key, val = chunk.split(sep, 1)
        pairs.append((key.strip(), val.strip()))
    return pairs


def parse_selectors(value: str | None) -> dict[str, set[str]]:
    """'task:feature,bugfix; stack:java' -> {'task': {...}, 'stack': {...}}."""
    return {key: set(parse_list(vals)) for key, vals in parse_pairs(value, ":")}


@dataclass
class Unit:
    path: Path
    type: str
    scope: str  # generic | profile
    profile: str | None
    frontmatter: dict
    body: str

    @property
    def name(self) -> str:
        return str(self.frontmatter.get("name", ""))

    @property
    def description(self) -> str:
        return str(self.frontmatter.get("description", ""))

    @property
    def meta(self) -> dict:
        meta = self.frontmatter.get("metadata") or {}
        return meta if isinstance(meta, dict) else {}

    def m(self, key: str, default: str = "") -> str:
        return str(self.meta.get(f"harness.{key}", default))

    @property
    def id(self) -> str:
        owner = self.profile.lower() if self.profile else "generic"
        return f"{owner}/{self.type}/{self.path.parent.name}"

    @property
    def status(self) -> str:
        return self.m("status", "active")

    @property
    def mandatory(self) -> bool:
        return self.m("enforcement", "default") == "mandatory"

    @property
    def layer(self) -> int:
        if self.scope == "profile":
            return LAYER_PROFILE
        return LAYER_GENERIC_RULE if self.type == "rule" else LAYER_SKILL

    @property
    def selectors(self) -> dict[str, set[str]]:
        return parse_selectors(self.m("applies-to"))

    @property
    def decides(self) -> dict[str, str]:
        return dict(parse_pairs(self.m("decides"), "="))

    @property
    def overrides(self) -> list[tuple[str, str]]:
        """[(target unit id, decision key)]"""
        result = []
        for item in parse_list(self.m("overrides")):
            target, _, key = item.partition("#")
            result.append((target.strip(), key.strip()))
        return result


@dataclass
class Profile:
    path: Path
    frontmatter: dict
    body: str

    @property
    def name(self) -> str:
        return str(self.frontmatter.get("name", ""))

    @property
    def models(self) -> dict[str, dict]:
        return self.frontmatter.get("models") or {}

    @property
    def extends(self) -> list[str]:
        return list(self.frontmatter.get("extends") or [])


@dataclass
class Repository:
    root: Path
    units: list[Unit] = field(default_factory=list)
    profiles: dict[str, Profile] = field(default_factory=dict)
    load_errors: list[tuple[Path, str]] = field(default_factory=list)

    def by_id(self) -> dict[str, Unit]:
        return {u.id: u for u in self.units}

    def agents(self) -> list[Unit]:
        return [u for u in self.units if u.type == "agent"]


def _load_unit(path: Path, unit_type: str, scope: str, profile: str | None, repo: Repository) -> None:
    try:
        fm, body = split_frontmatter(path.read_text(encoding="utf-8"))
    except (HarnessError, yaml.YAMLError) as exc:
        repo.load_errors.append((path, str(exc)))
        return
    repo.units.append(Unit(path, unit_type, scope, profile, fm, body))


def _load_containers(base: Path, scope: str, profile: str | None, repo: Repository) -> None:
    for container, unit_type in CONTAINERS.items():
        folder = base / container
        if not folder.is_dir():
            continue
        for unit_dir in sorted(p for p in folder.iterdir() if p.is_dir()):
            canonical = unit_dir / CANONICAL_FILES[unit_type]
            if canonical.is_file():
                _load_unit(canonical, unit_type, scope, profile, repo)


def load_repository(root: Path) -> Repository:
    root = Path(root).resolve()
    repo = Repository(root)
    _load_containers(root / "GENERIC", "generic", None, repo)
    agents_dir = root / "AGENTS"
    if agents_dir.is_dir():
        for unit_dir in sorted(p for p in agents_dir.iterdir() if p.is_dir()):
            canonical = unit_dir / CANONICAL_FILES["agent"]
            if canonical.is_file():
                _load_unit(canonical, "agent", "generic", None, repo)
    profiles_dir = root / "PROFILES"
    if profiles_dir.is_dir():
        for profile_dir in sorted(p for p in profiles_dir.iterdir() if p.is_dir()):
            profile_file = profile_dir / "PROFILE.md"
            if profile_file.is_file():
                try:
                    fm, body = split_frontmatter(profile_file.read_text(encoding="utf-8"))
                    repo.profiles[profile_dir.name] = Profile(profile_file, fm, body)
                except (HarnessError, yaml.YAMLError) as exc:
                    repo.load_errors.append((profile_file, str(exc)))
            _load_containers(profile_dir, "profile", profile_dir.name, repo)
    return repo


def default_root() -> Path:
    """The harness repository containing this package (TOOLS/harness -> repo root)."""
    return Path(__file__).resolve().parents[2]
