from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_readme_documents_test_and_quality_commands() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "make check" in readme
    assert "make ci" in readme
    assert "python -m pytest" in readme
    assert "ruff check ." in readme
    assert (
        "python -m pytest --cov=task_management --cov-report=term-missing --cov-fail-under=80"
        in readme
    )
    assert "质量约定" in readme
    assert "CI 的质量守护意图" in readme


def test_contributing_documents_make_targets_consistently() -> None:
    contributing = (PROJECT_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "make check" in contributing
    assert "make ci" in contributing
    assert "ruff check ." in contributing
    assert (
        "python -m pytest --cov=task_management --cov-report=term-missing --cov-fail-under=80"
        in contributing
    )


def test_makefile_defines_documented_quality_targets() -> None:
    makefile = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "check:" in makefile
    assert "ci:" in makefile
    assert "$(PYTHON) -m pytest\n" in makefile
    assert "ruff check ." in makefile
    assert (
        "$(PYTHON) -m pytest --cov=task_management --cov-report=term-missing --cov-fail-under=80"
        in makefile
    )


def test_ci_workflow_exists_and_has_clear_failure_conditions() -> None:
    workflow = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml")
    assert workflow.exists()

    content = workflow.read_text(encoding="utf-8")
    assert "ruff check ." in content
    assert "python -m pytest --cov=task_management" in content
    assert "--cov-fail-under=80" in content
    assert content.count("pytest") == 1


def test_pr_and_issue_templates_exist() -> None:
    assert (PROJECT_ROOT / ".github" / "pull_request_template.md").exists()
    assert (PROJECT_ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.md").exists()
    assert (PROJECT_ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.md").exists()


def test_quality_guard_file_is_tracked_in_repository() -> None:
    assert (PROJECT_ROOT / "tests" / "test_quality.py").exists()
