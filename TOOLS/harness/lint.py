"""Structural, metadata, conflict and confidentiality checks for the harness repository."""

from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass
from datetime import date, timedelta
from importlib import resources
from pathlib import Path

import jsonschema

from .model import CANONICAL_FILES, CONTAINERS, Repository, Unit, load_repository
from .resolve import decisions_of, resolve

STALE_AFTER = timedelta(days=183)
DUPLICATE_THRESHOLD = 0.6
REQUIRED_SECTIONS = {
    "workflow": ("## Inputs", "## Outputs", "## Done when"),
    "agent": ("## Responsibilities", "## Never", "## Handoff"),
}
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
SECRET_PATTERNS = {
    "aws-access-key": re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b"),
    "private-key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "github-token": re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{30,}\b"),
    "api-key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    "assigned-secret": re.compile(r"(?i)\b(password|passwd|secret|token|api[_-]?key)\s*[:=]\s*['\"][^'\"\s]{6,}['\"]"),
}
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
EMAIL_ALLOW = re.compile(r"@(example\.(com|org)|users\.noreply\.github\.com|noreply\.[a-z.]+|vault\.local)$", re.I)
INTERNAL_HOST_RE = re.compile(r"\b[a-z0-9.-]+\.(corp|intranet|internal|local\.lan)\b", re.I)
PRIVATE_IP_RE = re.compile(r"\b(10\.\d{1,3}|192\.168|172\.(1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b")
SCANNED_SUFFIXES = {".md", ".yml", ".yaml", ".json", ".toml", ".py", ".ps1", ".sh", ".txt"}
SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules", ".harness", "fixtures"}


@dataclass
class Finding:
    level: str  # error | warning
    code: str
    path: Path
    message: str

    def render(self, root: Path) -> str:
        try:
            rel = self.path.relative_to(root)
        except ValueError:
            rel = self.path
        return f"{self.level.upper():7} {self.code:24} {rel.as_posix()}: {self.message}"


def _schema(name: str) -> dict:
    return json.loads(resources.files("harness").joinpath("schema", name).read_text(encoding="utf-8"))


def _rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def check_layout(repo: Repository) -> list[Finding]:
    """One canonical Markdown per unit folder; no stray documents in knowledge trees."""
    out: list[Finding] = []
    root = repo.root
    bases = [(root / "GENERIC", None)]
    profiles_dir = root / "PROFILES"
    if profiles_dir.is_dir():
        for p in sorted(profiles_dir.iterdir()):
            if p.is_dir():
                bases.append((p, p.name))
                if not (p / "PROFILE.md").is_file():
                    out.append(Finding("error", "profile-missing", p, "profile folder without PROFILE.md"))
                for extra in p.iterdir():
                    if extra.is_file() and extra.name != "PROFILE.md":
                        out.append(Finding("error", "stray-file", extra, "only PROFILE.md is allowed at the profile root"))
                    if extra.is_dir() and extra.name not in CONTAINERS:
                        out.append(Finding("error", "unknown-container", extra,
                                           f"expected one of {sorted(CONTAINERS)}"))
    for base, _ in bases:
        if not base.is_dir():
            continue
        for container, unit_type in CONTAINERS.items():
            folder = base / container
            if not folder.is_dir():
                continue
            for entry in sorted(folder.iterdir()):
                out += _check_unit_dir(entry, CANONICAL_FILES[unit_type])
    agents = root / "AGENTS"
    if agents.is_dir():
        for entry in sorted(agents.iterdir()):
            out += _check_unit_dir(entry, CANONICAL_FILES["agent"])
    return out


def _check_unit_dir(entry: Path, canonical: str) -> list[Finding]:
    if entry.is_file():
        return [Finding("error", "stray-file", entry, f"units are folders containing {canonical}")]
    out = []
    files = [p for p in entry.rglob("*") if p.is_file()]
    if not (entry / canonical).is_file():
        out.append(Finding("error", "missing-canonical", entry, f"folder has no {canonical}"))
    for f in files:
        if f.name != canonical or f.parent != entry:
            out.append(Finding("error", "one-canonical-per-folder", f,
                               f"only {canonical} is allowed in a unit folder; put tests/examples in TESTS/ or EXAMPLES/"))
    return out


def check_metadata(repo: Repository) -> list[Finding]:
    out: list[Finding] = []
    unit_validator = jsonschema.Draft202012Validator(_schema("unit.schema.json"))
    profile_validator = jsonschema.Draft202012Validator(_schema("profile.schema.json"))
    for path, err in repo.load_errors:
        out.append(Finding("error", "frontmatter", path, err))
    for unit in repo.units:
        for err in sorted(unit_validator.iter_errors(unit.frontmatter), key=lambda e: list(e.path)):
            where = "/".join(str(p) for p in err.path) or "(root)"
            out.append(Finding("error", "schema", unit.path, f"{where}: {err.message}"))
        folder = unit.path.parent.name
        if unit.name != folder:
            out.append(Finding("error", "name-mismatch", unit.path, f"name '{unit.name}' must equal folder '{folder}'"))
        if unit.m("type") and unit.m("type") != unit.type:
            out.append(Finding("error", "type-mismatch", unit.path,
                               f"harness.type '{unit.m('type')}' but file is {CANONICAL_FILES[unit.type]}"))
        expected_scope = "profile" if unit.profile else "generic"
        if unit.m("scope") and unit.m("scope") != expected_scope:
            out.append(Finding("error", "scope-mismatch", unit.path,
                               f"harness.scope '{unit.m('scope')}' but the file lives in a {expected_scope} folder"))
        if unit.profile and unit.m("profile") != unit.profile:
            out.append(Finding("error", "profile-mismatch", unit.path,
                               f"harness.profile must be '{unit.profile}'"))
        if not unit.profile and unit.m("profile"):
            out.append(Finding("error", "profile-mismatch", unit.path, "generic units must not declare harness.profile"))
        for section in REQUIRED_SECTIONS.get(unit.type, ()):
            if not re.search(rf"^{re.escape(section)}\s*$", unit.body, re.M):
                out.append(Finding("error", "missing-section", unit.path, f"missing section '{section}'"))
        if unit.body.count("\n") > 500:
            out.append(Finding("warning", "too-long", unit.path, "body over 500 lines (Agent Skills recommendation)"))
        if unit.type == "skill" and unit.status == "active" and not unit.m("sources"):
            out.append(Finding("error", "missing-sources", unit.path, "active skills must cite harness.sources"))
        reviewed = unit.m("reviewed")
        if unit.status == "active":
            if not reviewed:
                out.append(Finding("warning", "not-reviewed", unit.path, "no harness.reviewed date"))
            else:
                try:
                    if date.today() - date.fromisoformat(reviewed) > STALE_AFTER:
                        out.append(Finding("warning", "stale", unit.path, f"last reviewed {reviewed}"))
                except ValueError:
                    pass
    for name, profile in repo.profiles.items():
        for err in profile_validator.iter_errors(profile.frontmatter):
            where = "/".join(str(p) for p in err.path) or "(root)"
            out.append(Finding("error", "profile-schema", profile.path, f"{where}: {err.message}"))
        if profile.name != name:
            out.append(Finding("error", "name-mismatch", profile.path, f"name '{profile.name}' must equal folder '{name}'"))
        for parent in profile.extends:
            if parent not in repo.profiles:
                out.append(Finding("error", "unknown-profile", profile.path, f"extends unknown profile '{parent}'"))
        personas = {u.name for u in repo.agents()}
        for persona in profile.models:
            if persona not in personas:
                out.append(Finding("error", "unknown-persona", profile.path, f"models.{persona} has no AGENTS/{persona}"))
    return out


def check_uniqueness(repo: Repository) -> list[Finding]:
    out: list[Finding] = []
    seen: dict[str, Unit] = {}
    for unit in repo.units:
        if unit.id in seen:
            out.append(Finding("error", "duplicate-id", unit.path, f"same id as {_rel(repo.root, seen[unit.id].path)}"))
        seen[unit.id] = unit
    words = {u.id: set(re.findall(r"[a-z]{4,}", u.description.lower())) for u in repo.units}
    units = [u for u in repo.units if u.status == "active"]
    for i, a in enumerate(units):
        for b in units[i + 1:]:
            if a.type != b.type or (a.profile and b.profile and a.profile != b.profile):
                continue
            wa, wb = words[a.id], words[b.id]
            if wa and wb and len(wa & wb) / len(wa | wb) >= DUPLICATE_THRESHOLD:
                out.append(Finding("warning", "possible-duplicate", b.path,
                                   f"description overlaps {a.id} ({len(wa & wb) / len(wa | wb):.0%})"))
    return out


def check_overrides_and_conflicts(repo: Repository) -> list[Finding]:
    """Overrides must target existing decisions; each profile must resolve without conflicts."""
    out: list[Finding] = []
    ids = repo.by_id()
    for unit in repo.units:
        for target, key in unit.overrides:
            if target not in ids:
                out.append(Finding("error", "override-target", unit.path, f"overrides unknown unit '{target}'"))
            elif key and key not in ids[target].decides:
                out.append(Finding("error", "override-key", unit.path, f"'{target}' does not decide '{key}'"))
            elif key and key not in unit.decides:
                out.append(Finding("error", "override-key", unit.path, f"overrides '{key}' but does not decide it"))
            elif not unit.profile and ids[target].profile:
                out.append(Finding("error", "override-direction", unit.path,
                                   "generic units must not override profile units"))
    groups: dict[str, list[Unit]] = {"generic": [u for u in repo.units if not u.profile]}
    for name in repo.profiles:
        groups[name] = groups["generic"] + [u for u in repo.units if u.profile == name]
    for group, units in groups.items():
        active = [u for u in units if u.status == "active"]
        res = resolve([d for u in active for d in decisions_of(u)])
        for conflict in res.conflicts:
            first = ids.get(conflict.sources[0][0])
            detail = ", ".join(f"{src}={val}" for src, val in conflict.sources)
            out.append(Finding("error", "conflict", first.path if first else repo.root,
                               f"[{group}] {conflict.key}: {detail} ({conflict.reason})"))
    return out


def check_links(repo: Repository, online: bool = False) -> list[Finding]:
    out: list[Finding] = []
    for path in _markdown_files(repo.root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        for target in LINK_RE.findall(text):
            if target.startswith(("#", "mailto:")):
                continue
            if target.startswith(("http://", "https://")):
                if online and not _url_ok(target):
                    out.append(Finding("warning", "broken-external-link", path, target))
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).exists():
                out.append(Finding("error", "broken-link", path, target))
    return out


def _url_ok(url: str) -> bool:
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "harness-lint"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status < 400
    except Exception:
        return False


def _markdown_files(root: Path):
    for path in root.rglob("*.md"):
        if not SKIP_DIRS & set(path.relative_to(root).parts):
            yield path


def _scanned_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and path.suffix in SCANNED_SUFFIXES and not SKIP_DIRS & set(path.relative_to(root).parts):
            yield path


def load_denylist(root: Path) -> list[str]:
    """Local, git-ignored list of forbidden terms (internal hostnames, product names...)."""
    file = root / ".harness" / "denylist.local"
    if not file.is_file():
        return []
    return [line.strip().lower() for line in file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")]


def check_confidentiality(repo: Repository) -> list[Finding]:
    out: list[Finding] = []
    denylist = load_denylist(repo.root)
    for path in _scanned_files(repo.root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = _rel(repo.root, path)
        for code, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                out.append(Finding("error", f"secret:{code}", path, "possible credential"))
        for email in EMAIL_RE.findall(text):
            if not EMAIL_ALLOW.search(email):
                out.append(Finding("error", "personal-data", path, f"e-mail address '{email}'"))
        strict = rel.startswith("PROFILES/") and not rel.startswith("PROFILES/PERSONAL/")
        if strict:
            for host in INTERNAL_HOST_RE.findall(text):
                out.append(Finding("error", "internal-host", path, f"internal hostname suffix '.{host}'"))
            if PRIVATE_IP_RE.search(text):
                out.append(Finding("error", "internal-ip", path, "private IP address in a company profile"))
        lowered = text.lower()
        for term in denylist:
            if term in lowered:
                out.append(Finding("error", "denylisted-term", path, "contains a term from .harness/denylist.local"))
    return out


def lint(root: Path, online: bool = False) -> list[Finding]:
    repo = load_repository(root)
    findings = (check_layout(repo) + check_metadata(repo) + check_uniqueness(repo)
                + check_overrides_and_conflicts(repo) + check_links(repo, online) + check_confidentiality(repo))
    return sorted(findings, key=lambda f: (f.level != "error", str(f.path), f.code))
