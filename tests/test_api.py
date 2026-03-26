from fastapi.testclient import TestClient

from task_management.interfaces.http.api import create_app


client = TestClient(create_app())


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"data": {"status": "ok"}}


def test_task_lifecycle() -> None:
    create_response = client.post(
        "/api/v1/tasks",
        json={"title": "Implement API", "description": "Build the demo endpoints"},
    )
    assert create_response.status_code == 201
    task = create_response.json()["data"]
    task_id = task["id"]

    get_response = client.get(f"/api/v1/tasks/{task_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["title"] == "Implement API"

    assign_response = client.post(
        f"/api/v1/tasks/{task_id}/assignments",
        json={"assignee_id": "user_001"},
    )
    assert assign_response.status_code == 200
    assert assign_response.json()["data"]["status"] == "assigned"

    complete_response = client.post(f"/api/v1/tasks/{task_id}/completion")
    assert complete_response.status_code == 200
    assert complete_response.json()["data"]["status"] == "completed"

    list_response = client.get("/api/v1/tasks")
    assert list_response.status_code == 200
    assert any(item["id"] == task_id for item in list_response.json()["data"])


def test_returns_standard_error_when_task_not_found() -> None:
    response = client.get("/api/v1/tasks/task_missing")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TASK_NOT_FOUND"
    assert response.json()["error"]["details"] == []


def test_returns_standard_error_when_completion_repeated() -> None:
    create_response = client.post("/api/v1/tasks", json={"title": "Repeat completion"})
    task_id = create_response.json()["data"]["id"]

    first_response = client.post(f"/api/v1/tasks/{task_id}/completion")
    second_response = client.post(f"/api/v1/tasks/{task_id}/completion")

    assert first_response.status_code == 200
    assert second_response.status_code == 409
    assert second_response.json()["error"]["code"] == "TASK_ALREADY_COMPLETED"


def test_returns_standard_validation_error() -> None:
    response = client.post(
        "/api/v1/tasks",
        json={"title": "   ", "description": "demo"},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert body["error"]["message"] == "请求参数校验失败"
    assert body["error"]["details"][0]["field"] == "title"
