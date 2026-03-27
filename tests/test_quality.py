from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_readme_documents_current_quality_commands() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "python -m pytest" in readme
    assert "python -m pytest --cov=task_management --cov-report=term-missing --cov-fail-under=80" in readme
    assert "ruff check ." in readme
    assert "make quality" in readme
    assert "质量约定" in readme
    assert "CI 的质量守护意图" in readme


def test_ci_workflow_exists_and_matches_current_quality_guard() -> None:
    workflow = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml")
    assert workflow.exists()

    content = workflow.read_text(encoding="utf-8")
    assert "ruff check ." in content
    assert "python -m pytest --cov=task_management --cov-report=term-missing --cov-fail-under=80" in content
    assert "Pytest 质量守护" in content
    assert "Ruff 格式检查" not in content


def test_makefile_defines_the_same_quality_entrypoints() -> None:
    makefile = (PROJECT_ROOT / "Makefile")
    assert makefile.exists()

    content = makefile.read_text(encoding="utf-8")
    assert "$(PYTHON) -m pytest" in content
    assert "$(PYTHON) -m pytest --cov=task_management --cov-report=term-missing --cov-fail-under=80" in content
    assert "$(PYTHON) -m pytest tests/test_quality.py" in content
    assert "ruff check ." in content
    assert "quality:" in content


def test_pr_and_issue_templates_exist() -> None:
    assert (PROJECT_ROOT / ".github" / "pull_request_template.md").exists()
    assert (PROJECT_ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.md").exists()
    assert (PROJECT_ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.md").exists()


def test_quality_guard_file_is_tracked_in_repository() -> None:
    assert (PROJECT_ROOT / "tests" / "test_quality.py").exists()
