from __future__ import annotations

from conftest import FIXTURES, REPO_ROOT

from harness.model import load_repository
from harness.resolve import compose, detect_stack


def ids(comp):
    return {s.unit.id for s in comp.selected}


def test_detects_java_spring_fixture():
    stack = detect_stack(FIXTURES / "java-service")
    assert {"java", "maven", "spring", "sql"} <= stack


def test_itau_composition_for_java_feature():
    repo = load_repository(REPO_ROOT)
    comp = compose(repo, "ITAU", "feature", FIXTURES / "java-service")
    loaded = ids(comp)
    assert "itau/rule/sonar-quality-gate" in loaded
    assert "generic/skill/java-spring-boot" in loaded
    assert "generic/workflow/story-delivery" in loaded
    assert not any(i.startswith("personal/") for i in loaded), "personal rules must never load in ITAU"
    assert "generic/skill/python-pytest" not in loaded
    assert comp.resolution.conflicts == []
    merge = [o for o in comp.resolution.overrides if o.key == "git.merge-strategy"]
    assert merge and merge[0].winner == "itau/rule/pull-requests" and merge[0].loser == "generic/rule/git-commits"


def test_complementary_rules_are_not_conflicts():
    repo = load_repository(REPO_ROOT)
    comp = compose(repo, "ITAU", "feature", FIXTURES / "java-service")
    decision = comp.resolution.effective["ci.disable-checks"]
    assert decision.value == "forbidden"


def test_personal_composition_never_loads_itau_rules():
    repo = load_repository(REPO_ROOT)
    comp = compose(repo, "PERSONAL", "feature", FIXTURES / "java-service")
    assert not any(i.startswith("itau/") for i in ids(comp))
    assert "personal/rule/personal-git-flow" in ids(comp)


def test_support_task_selects_support_workflow():
    repo = load_repository(REPO_ROOT)
    comp = compose(repo, "ITAU", "support", FIXTURES / "java-service")
    loaded = ids(comp)
    assert "generic/workflow/support-ticket" in loaded
    assert "generic/workflow/story-delivery" not in loaded
    assert "itau/rule/sonar-quality-gate" not in loaded


def test_unresolved_conflict_is_reported(mini, tmp_path):
    mini.unit("rule", "merge", decides="git.merge-strategy=merge-commit")
    mini.unit("rule", "squash", profile="ACME", decides="git.merge-strategy=squash")
    comp = compose(load_repository(mini.root), "ACME", "feature", tmp_path)
    assert [c.key for c in comp.resolution.conflicts] == ["git.merge-strategy"]


def test_story_can_override_default_but_not_mandatory(mini, tmp_path):
    mini.unit("rule", "merge", decides="git.merge-strategy=merge-commit")
    mini.unit("rule", "auth", decides="change.publish=explicit-authorization", enforcement="mandatory")
    story = tmp_path / "story.md"
    story.write_text(
        "---\nmetadata:\n  harness.decides: \"git.merge-strategy=rebase; change.publish=automatic\"\n"
        "  harness.overrides: \"generic/rule/merge#git.merge-strategy, generic/rule/auth#change.publish\"\n---\n",
        encoding="utf-8")
    comp = compose(load_repository(mini.root), "ACME", "feature", tmp_path, story)
    assert comp.resolution.effective["git.merge-strategy"].value == "rebase"
    assert [c.key for c in comp.resolution.conflicts] == ["change.publish"]


def test_selectors_filter_by_stack(mini, tmp_path):
    mini.unit("skill", "java", applies_to="stack:java")
    mini.unit("skill", "python", applies_to="stack:python")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    comp = compose(load_repository(mini.root), "ACME", "feature", tmp_path)
    assert ids(comp) == {"generic/skill/python"}
    assert any(s.unit.id == "generic/skill/java" for s in comp.skipped)


def test_draft_units_are_not_loaded(mini, tmp_path):
    mini.unit("rule", "experimental", status="draft")
    comp = compose(load_repository(mini.root), "ACME", "feature", tmp_path)
    assert "generic/rule/experimental" not in ids(comp)
