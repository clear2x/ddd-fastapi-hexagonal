from fastapi.testclient import TestClient

from task_management.interfaces.http.api import create_app


client = TestClient(create_app())


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_task_lifecycle() -> None:
    create_response = client.post(
        "/api/v1/tasks",
        json={"title": "Implement API", "description": "Build the demo endpoints"},
    )
    assert create_response.status_code == 201
    task = create_response.json()
    task_id = task["id"]

    get_response = client.get(f"/api/v1/tasks/{task_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Implement API"

    assign_response = client.post(
        f"/api/v1/tasks/{task_id}/assignments",
        json={"assignee_id": "user_001"},
    )
    assert assign_response.status_code == 200
    assert assign_response.json()["status"] == "assigned"

    complete_response = client.post(f"/api/v1/tasks/{task_id}/completion")
    assert complete_response.status_code == 200
    assert complete_response.json()["status"] == "completed"

    list_response = client.get("/api/v1/tasks")
    assert list_response.status_code == 200
    assert any(item["id"] == task_id for item in list_response.json())
