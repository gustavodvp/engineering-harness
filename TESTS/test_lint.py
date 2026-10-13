from __future__ import annotations

from conftest import REPO_ROOT

from harness.lint import lint


def codes(root):
    return {f.code for f in lint(root) if f.level == "error"}


def test_real_repository_has_no_errors():
    errors = [f.render(REPO_ROOT) for f in lint(REPO_ROOT) if f.level == "error"]
    assert errors == []


def test_valid_mini_repository_is_clean(mini):
    mini.unit("rule", "commits", decides="git.style=conventional")
    mini.unit("skill", "java", applies_to="stack:java")
    mini.unit("workflow", "delivery")
    assert codes(mini.root) == set()


def test_name_must_match_folder(mini):
    path = mini.unit("rule", "commits")
    path.write_text(path.read_text(encoding="utf-8").replace("name: commits", "name: other"), encoding="utf-8")
    assert "name-mismatch" in codes(mini.root)


def test_only_one_canonical_file_per_folder(mini):
    path = mini.unit("skill", "java")
    (path.parent / "notes.md").write_text("extra", encoding="utf-8")
    (path.parent / "references").mkdir()
    (path.parent / "references" / "REFERENCE.md").write_text("extra", encoding="utf-8")
    findings = [f for f in lint(mini.root) if f.code == "one-canonical-per-folder"]
    assert len(findings) == 2


def test_folder_without_canonical_file(mini):
    (mini.root / "GENERIC" / "RULES" / "empty").mkdir(parents=True)
    assert "missing-canonical" in codes(mini.root)


def test_schema_rejects_unknown_top_level_field_and_bad_values(mini):
    path = mini.unit("rule", "commits", status="published")
    text = path.read_text(encoding="utf-8").replace("metadata:", "tags: [x]\nmetadata:")
    path.write_text(text, encoding="utf-8")
    findings = [f for f in lint(mini.root) if f.code == "schema"]
    messages = " ".join(f.message for f in findings)
    assert "tags" in messages and "published" in messages


def test_metadata_values_must_be_strings(mini):
    path = mini.unit("rule", "commits")
    path.write_text(path.read_text(encoding="utf-8").replace("'2026-10-01'", "2026-10-01"), encoding="utf-8")
    assert "schema" in codes(mini.root)


def test_scope_and_profile_must_match_location(mini):
    mini.unit("rule", "branches", profile="ACME", scope="generic")
    assert "scope-mismatch" in codes(mini.root)


def test_workflow_requires_inputs_outputs_done_when(mini):
    mini.unit("workflow", "delivery", body="# W\n\n## Inputs\n\n- x\n")
    assert "missing-section" in codes(mini.root)


def test_active_skill_requires_sources(mini):
    mini.unit("skill", "java", sources="")
    assert "missing-sources" in codes(mini.root)


def test_conflict_without_override_is_an_error(mini):
    mini.unit("rule", "merge", decides="git.merge-strategy=merge-commit")
    mini.unit("rule", "squash", profile="ACME", decides="git.merge-strategy=squash")
    findings = [f for f in lint(mini.root) if f.code == "conflict"]
    assert findings and "ACME" in findings[0].message


def test_declared_override_resolves_conflict(mini):
    mini.unit("rule", "merge", decides="git.merge-strategy=merge-commit")
    mini.unit("rule", "squash", profile="ACME", decides="git.merge-strategy=squash",
              overrides="generic/rule/merge#git.merge-strategy")
    assert "conflict" not in codes(mini.root)


def test_mandatory_rule_cannot_be_overridden(mini):
    mini.unit("rule", "auth", decides="change.publish=explicit-authorization", enforcement="mandatory")
    mini.unit("rule", "yolo", profile="ACME", decides="change.publish=automatic",
              overrides="generic/rule/auth#change.publish")
    findings = [f for f in lint(mini.root) if f.code == "conflict"]
    assert findings and "mandatory" in findings[0].message


def test_override_must_point_to_existing_decision(mini):
    mini.unit("rule", "squash", profile="ACME", decides="git.merge-strategy=squash",
              overrides="generic/rule/missing#git.merge-strategy")
    assert "override-target" in codes(mini.root)


def test_broken_relative_link(mini):
    mini.unit("rule", "commits", body="# C\n\nSee [guide](../../nowhere.md).\n")
    assert "broken-link" in codes(mini.root)


def test_secret_and_email_detection(mini):
    fake_key = "AKIA" + "ABCDEFGHIJKLMNOP"
    fake_mail = "someone" + "@" + "company.com"
    mini.unit("rule", "commits", body=f"# C\n\nkey {fake_key} mail {fake_mail}\n")
    found = codes(mini.root)
    assert "secret:aws-access-key" in found and "personal-data" in found


def test_company_profile_rejects_internal_hosts(mini):
    host = "build" + ".corp"
    mini.unit("rule", "ci", profile="ACME", body=f"# CI\n\nUse https://{host}/jobs\n")
    assert "internal-host" in codes(mini.root)


def test_local_denylist(mini):
    (mini.root / ".harness").mkdir()
    (mini.root / ".harness" / "denylist.local").write_text("project-zeta\n", encoding="utf-8")
    mini.unit("rule", "ci", profile="ACME", body="# CI\n\nUsed by Project-Zeta.\n")
    assert "denylisted-term" in codes(mini.root)


def test_profile_models_must_reference_personas(mini):
    mini.profile("ACME", models={"wizard": {"tool": "opencode", "model": "x", "confirmed": False}})
    assert "unknown-persona" in codes(mini.root)


def test_possible_duplicate_is_a_warning(mini):
    mini.unit("skill", "java")
    mini.unit("skill", "java-copy")
    warnings = [f for f in lint(mini.root) if f.code == "possible-duplicate"]
    assert warnings and warnings[0].level == "warning"
