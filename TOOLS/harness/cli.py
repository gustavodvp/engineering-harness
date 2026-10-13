"""`harness` command line: lint, list, compose, drift."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import export
from .lint import lint
from .model import default_root, load_repository
from .resolve import TASK_TYPES, compose


def _root(args) -> Path:
    return Path(args.root).resolve() if args.root else default_root()


def cmd_lint(args) -> int:
    root = _root(args)
    findings = lint(root, online=args.online)
    for f in findings:
        print(f.render(root))
    errors = sum(f.level == "error" for f in findings)
    warnings = len(findings) - errors
    print(f"\n{errors} error(s), {warnings} warning(s)")
    return 1 if errors or (args.strict and warnings) else 0


def cmd_list(args) -> int:
    repo = load_repository(_root(args))
    for unit in sorted(repo.units, key=lambda u: u.id):
        if args.type and unit.type != args.type:
            continue
        print(f"{unit.id:48} {unit.m('status'):10} {unit.m('version'):8} {unit.description[:70]}")
    print(f"\nprofiles: {', '.join(sorted(repo.profiles))}")
    return 0


def cmd_compose(args) -> int:
    repo = load_repository(_root(args))
    project = Path(args.project).resolve()
    if not project.is_dir():
        print(f"project folder not found: {project}", file=sys.stderr)
        return 2
    story = Path(args.story).resolve() if args.story else None
    comp = compose(repo, args.profile, args.task, project, story, set(args.stack or []))
    report = export.resolution_report(repo, comp, project)
    print(export.resolution_markdown(report))
    problems = bool(comp.resolution.conflicts or comp.missing_overrides)
    if problems and not args.allow_conflicts:
        print("Unresolved conflicts: nothing was written. Fix the rules or pass --allow-conflicts.", file=sys.stderr)
        return 3
    if args.dry_run:
        return 0
    files = export.render(repo, comp, project)
    for note in export.write(project, files):
        print(f"note: {note}")
    print(f"wrote {len(files)} generated file(s) into {project}")
    return 0


def cmd_drift(args) -> int:
    problems = export.drift(Path(args.project).resolve())
    for p in problems:
        print(p)
    print("no drift" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


def cmd_usage(args) -> int:
    from datetime import datetime, timezone

    from . import usage

    def when(value):
        if not value:
            return None
        ts = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)

    since, until = when(args.since), when(args.until)
    if args.maestri_workspace:
        agents, created = usage.maestri_agents(args.maestri_workspace, args.floor)
        since = since or created
        title = f"{args.maestri_workspace} / {args.floor or 'Ground'}"
    else:
        agents = [usage.Agent(Path(d).name, args.tool, "", Path(d).resolve()) for d in args.dir or []]
        title = ", ".join(a.name for a in agents)
    if not agents:
        print("no agents: pass --maestri-workspace [--floor] or --dir", file=sys.stderr)
        return 2
    results = usage.collect(agents, since, until)
    report = usage.render_markdown(results, title, since, until)
    print(report)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8", newline="\n")
        out.with_suffix(".json").write_text(json.dumps(usage.to_json(results), indent=2, ensure_ascii=False) + "\n",
                                            encoding="utf-8", newline="\n")
        print(f"wrote {out} and {out.with_suffix('.json').name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="harness", description="Engineering harness tooling")
    parser.add_argument("--root", help="harness repository root (default: this checkout)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("lint", help="validate structure, metadata, links, conflicts and confidentiality")
    p.add_argument("--online", action="store_true", help="also check external links")
    p.add_argument("--strict", action="store_true", help="fail on warnings too")
    p.set_defaults(func=cmd_lint)

    p = sub.add_parser("list", help="list units")
    p.add_argument("--type", choices=["skill", "rule", "workflow", "agent"])
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("compose", help="select units for a project and task, resolve, and export adapters")
    p.add_argument("project")
    p.add_argument("--profile", required=True)
    p.add_argument("--task", required=True, choices=TASK_TYPES)
    p.add_argument("--story", help="story file; its frontmatter may declare decides/overrides")
    p.add_argument("--stack", action="append", help="add a stack tag the detector missed (repeatable)")
    p.add_argument("--dry-run", action="store_true", help="print the resolution without writing")
    p.add_argument("--allow-conflicts", action="store_true")
    p.set_defaults(func=cmd_compose)

    p = sub.add_parser("usage", help="measured tokens, cost and tool errors of the agents of a run")
    p.add_argument("--maestri-workspace", help="Maestri workspace name (agents discovered from ~/.maestri)")
    p.add_argument("--floor", help="Maestri floor name (default: ground)")
    p.add_argument("--dir", action="append", help="agent working directory (repeatable, without Maestri)")
    p.add_argument("--tool", default="claude-code", choices=["claude-code", "opencode"], help="tool for --dir")
    p.add_argument("--since", help="ISO time; default: floor creation")
    p.add_argument("--until", help="ISO time; default: now")
    p.add_argument("--out", help="write the Markdown report here (and a .json next to it)")
    p.set_defaults(func=cmd_usage)

    p = sub.add_parser("drift", help="detect hand edits of generated files")
    p.add_argument("project")
    p.set_defaults(func=cmd_drift)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
