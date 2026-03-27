from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_readme_documents_beginner_friendly_quality_commands() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "make lint" in readme
    assert "make test" in readme
    assert "make ci" in readme
    assert "质量约定" in readme
    assert "教学型仓库" in readme


def test_ci_workflow_exists_and_matches_make_targets() -> None:
    workflow = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml")
    assert workflow.exists()

    content = workflow.read_text(encoding="utf-8")
    assert "python -m ruff check src tests" in content
    assert "python -m ruff format --check src tests" in content
    assert "python -m pytest --cov=task_management --cov-report=term-missing" in content
    assert "--cov-fail-under" not in content


def test_makefile_exposes_consistent_quality_entrypoints() -> None:
    makefile = (PROJECT_ROOT / "Makefile")
    assert makefile.exists()

    content = makefile.read_text(encoding="utf-8")
    assert "test-cov:" in content
    assert "format-check:" in content
    assert "ci: lint format-check test-cov" in content
    assert "$(PYTHON) -m ruff check $(RUFF_TARGETS)" in content


def test_contributing_documents_real_pr_checks() -> None:
    contributing = (PROJECT_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "make check" in contributing
    assert "make ci" in contributing
    assert "先跑通最小检查" in contributing
    assert "覆盖率数字" in contributing


def test_pr_and_issue_templates_exist() -> None:
    assert (PROJECT_ROOT / ".github" / "pull_request_template.md").exists()
    assert (PROJECT_ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.md").exists()
    assert (PROJECT_ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.md").exists()


def test_quality_guard_file_is_tracked_in_repository() -> None:
    assert (PROJECT_ROOT / "tests" / "test_quality.py").exists()
