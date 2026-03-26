from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_readme_documents_test_and_quality_commands() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "python -m pytest" in readme
    assert "ruff check ." in readme
    assert "质量约定" in readme


def test_ci_workflow_exists() -> None:
    assert (PROJECT_ROOT / ".github" / "workflows" / "ci.yml").exists()


def test_pr_and_issue_templates_exist() -> None:
    assert (PROJECT_ROOT / ".github" / "pull_request_template.md").exists()
    assert (PROJECT_ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.md").exists()
    assert (PROJECT_ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.md").exists()
