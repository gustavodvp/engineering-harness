"""Selection of units for a task context and resolution of conflicting decisions."""

from __future__ import annotations

import re

from dataclasses import dataclass, field
from pathlib import Path

from .model import LAYER_STORY, Profile, Repository, Unit, split_frontmatter

STACK_MARKERS = {
    "pom.xml": {"java", "maven"},
    "build.gradle": {"java", "gradle"},
    "build.gradle.kts": {"java", "gradle"},
    "pyproject.toml": {"python"},
    "requirements.txt": {"python"},
    "go.mod": {"go"},
    "package.json": {"javascript"},
    "Dockerfile": {"docker"},
    "docker-compose.yml": {"docker"},
    "compose.yaml": {"docker"},
}
STACK_GLOBS = {
    "*.tf": {"terraform"},
    "**/*.sql": {"sql"},
    "**/db/migration/*": {"sql"},
    ".github/workflows/*.yml": {"github-actions"},
}
CONTENT_HINTS = {
    "spring-boot": "spring",
    "fastapi": "fastapi",
    "pytest": "pytest",
    "aws-sdk": "aws",
    "boto3": "aws",
    "react": "react",
}
TASK_TYPES = ("feature", "bugfix", "refactor", "review", "support", "incident", "analysis", "docs")
PROJECT_INSTRUCTION_FILES = ("AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md", "CONTRIBUTING.md")


HARNESS_BLOCK_RE = re.compile(r"<!-- harness:begin.*?<!-- harness:end -->", re.S)
HARNESS_ONLY_LINES = {"# AGENTS.md", "@AGENTS.md"}


def _has_project_text(path: Path) -> bool:
    """True when an instruction file has content written by the project, not only by the harness."""
    if not path.is_file():
        return False
    text = HARNESS_BLOCK_RE.sub("", path.read_text(encoding="utf-8", errors="ignore"))
    return any(line.strip() and line.strip() not in HARNESS_ONLY_LINES for line in text.splitlines())


def detect_stack(project: Path) -> set[str]:
    stack: set[str] = set()
    for marker, tags in STACK_MARKERS.items():
        path = project / marker
        if path.is_file():
            stack |= tags
            try:
                text = path.read_text(encoding="utf-8", errors="ignore").lower()
            except OSError:
                continue
            stack |= {tag for hint, tag in CONTENT_HINTS.items() if hint in text}
    for pattern, tags in STACK_GLOBS.items():
        if any(p for p in project.glob(pattern) if ".harness" not in p.parts):
            stack |= tags
    return stack


def matches(unit: Unit, context: dict[str, set[str]]) -> tuple[bool, str]:
    """A unit matches when every selector it declares intersects the context ('*' = any)."""
    selectors = unit.selectors
    if not selectors:
        return True, "applies to every task (no selector)"
    reasons = []
    for key, wanted in selectors.items():
        if "*" in wanted:
            reasons.append(f"{key}:*")
            continue
        hit = wanted & context.get(key, set())
        if not hit:
            return False, f"{key} not in {sorted(wanted)}"
        reasons.append(f"{key}:{','.join(sorted(hit))}")
    return True, "matched " + "; ".join(reasons)


@dataclass
class Decision:
    key: str
    value: str
    source: str  # unit id or pseudo-id (project/story)
    layer: int
    mandatory: bool
    overrides: set[tuple[str, str]] = field(default_factory=set)


@dataclass
class Override:
    key: str
    winner: str
    loser: str
    winner_value: str
    loser_value: str


@dataclass
class Conflict:
    key: str
    sources: list[tuple[str, str]]  # (source id, value)
    reason: str


@dataclass
class Resolution:
    effective: dict[str, Decision] = field(default_factory=dict)
    overrides: list[Override] = field(default_factory=list)
    conflicts: list[Conflict] = field(default_factory=list)


def decisions_of(unit: Unit) -> list[Decision]:
    return [
        Decision(key, value, unit.id, unit.layer, unit.mandatory, set(unit.overrides))
        for key, value in unit.decides.items()
    ]


def resolve(decisions: list[Decision]) -> Resolution:
    """Resolve decisions per key.

    - Same value from several sources: complementary, no conflict.
    - Different values: the higher layer wins only if it declares `overrides: <loser>#<key>`.
    - A mandatory decision can never be overridden.
    - Anything else is an unresolved conflict; the generic content is never changed.
    """
    res = Resolution()
    by_key: dict[str, list[Decision]] = {}
    for d in decisions:
        by_key.setdefault(d.key, []).append(d)
    for key, group in sorted(by_key.items()):
        values = {d.value for d in group}
        if len(values) == 1:
            res.effective[key] = max(group, key=lambda d: d.layer)
            continue
        winners = []
        for cand in group:
            beaten = [d for d in group if d.value != cand.value]
            if all((d.source, key) in cand.overrides and cand.layer >= d.layer for d in beaten):
                winners.append(cand)
        if len(winners) != 1:
            res.conflicts.append(Conflict(key, [(d.source, d.value) for d in group],
                                          "different values and no declared override resolves them"))
            continue
        winner = winners[0]
        blocked = [d for d in group if d.value != winner.value and d.mandatory]
        if blocked:
            res.conflicts.append(Conflict(key, [(d.source, d.value) for d in group],
                                          f"{blocked[0].source} is mandatory and cannot be overridden"))
            continue
        res.effective[key] = winner
        for d in group:
            if d.value != winner.value:
                res.overrides.append(Override(key, winner.source, d.source, winner.value, d.value))
    return res


@dataclass
class Selected:
    unit: Unit
    reason: str


@dataclass
class Composition:
    profile: Profile
    context: dict[str, set[str]]
    selected: list[Selected]
    skipped: list[Selected]
    project_instructions: list[Path]
    story: Path | None
    resolution: Resolution
    missing_overrides: list[tuple[str, str]]  # (unit id, missing target)


def profile_chain(repo: Repository, name: str) -> list[str]:
    """Profile plus the profiles it extends (closest last)."""
    chain: list[str] = []

    def visit(n: str, stack: tuple[str, ...]) -> None:
        if n in stack:
            raise ValueError(f"profile cycle: {' -> '.join(stack + (n,))}")
        if n not in repo.profiles:
            raise ValueError(f"unknown profile '{n}' (known: {', '.join(sorted(repo.profiles))})")
        for parent in repo.profiles[n].extends:
            visit(parent, stack + (n,))
        if n not in chain:
            chain.append(n)

    visit(name, ())
    return chain


def story_decisions(story: Path) -> list[Decision]:
    try:
        fm, _ = split_frontmatter(story.read_text(encoding="utf-8"))
    except Exception:
        return []
    meta = fm.get("metadata") or fm
    unit_like = Unit(story, "story", "story", None, {"metadata": meta}, "")
    overrides = set(unit_like.overrides)
    return [Decision(k, v, "story", LAYER_STORY, False, overrides) for k, v in unit_like.decides.items()]


def compose(repo: Repository, profile_name: str, task: str | set[str], project: Path,
            story: Path | None = None, extra_stack: set[str] | None = None) -> Composition:
    """`task` is one task type or a set of them (a shared workspace serves several kinds of task)."""
    chain = profile_chain(repo, profile_name)
    stack = detect_stack(project) | (extra_stack or set())
    tasks = {task} if isinstance(task, str) else set(task)
    context = {"task": tasks, "stack": stack}
    selected, skipped = [], []
    for unit in repo.units:
        if unit.status != "active" or unit.type == "agent":
            continue
        if unit.scope == "profile" and unit.profile not in chain:
            continue  # other environments are never loaded
        ok, why = matches(unit, context)
        origin = f"profile {unit.profile}" if unit.profile else "generic"
        (selected if ok else skipped).append(Selected(unit, f"{origin}: {why}"))
    selected.sort(key=lambda s: (s.unit.layer, s.unit.id))
    decisions = [d for s in selected for d in decisions_of(s.unit)]
    if story:
        decisions += story_decisions(story)
    ids = repo.by_id()
    missing = [(s.unit.id, target) for s in selected for target, _ in s.unit.overrides if target not in ids]
    instructions = [project / f for f in PROJECT_INSTRUCTION_FILES if _has_project_text(project / f)]
    return Composition(repo.profiles[profile_name], context, selected, skipped, instructions, story,
                       resolve(decisions), missing)



