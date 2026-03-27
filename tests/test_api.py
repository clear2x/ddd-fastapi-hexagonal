from fastapi.testclient import TestClient

from task_management.application import assemblers
from task_management.infrastructure.repository import TaskReadModelModel
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


def test_returns_standard_validation_error_when_title_is_blank() -> None:
    response = client.post(
        "/api/v1/tasks",
        json={"title": "   ", "description": "demo"},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert body["error"]["message"] == "请求参数校验失败"
    assert body["error"]["details"][0]["field"] == "title"


def test_validation_error_details_are_translated_to_public_contract() -> None:
    response = client.post(
        "/api/v1/tasks",
        json={"description": "demo"},
    )

    assert response.status_code == 422
    body = response.json()
    detail = body["error"]["details"][0]
    assert set(detail.keys()) == {"field", "message", "type"}
    assert detail["field"] == "title"
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"


def test_create_task_normalizes_blank_description_to_none() -> None:
    response = client.post(
        "/api/v1/tasks",
        json={"title": "Normalize description", "description": "   "},
    )

    assert response.status_code == 201
    assert response.json()["data"]["description"] is None


def test_create_task_returns_validation_error_when_title_is_missing() -> None:
    response = client.post(
        "/api/v1/tasks",
        json={"description": "demo"},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert body["error"]["details"][0]["field"] == "title"


def test_assign_task_returns_validation_error_when_assignee_is_blank() -> None:
    create_response = client.post("/api/v1/tasks", json={"title": "Need assignee"})
    task_id = create_response.json()["data"]["id"]

    response = client.post(
        f"/api/v1/tasks/{task_id}/assignments",
        json={"assignee_id": "   "},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert body["error"]["details"][0]["field"] == "assignee_id"


def test_assign_task_returns_validation_error_when_assignee_is_missing() -> None:
    create_response = client.post("/api/v1/tasks", json={"title": "Need assignee field"})
    task_id = create_response.json()["data"]["id"]

    response = client.post(
        f"/api/v1/tasks/{task_id}/assignments",
        json={},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert body["error"]["details"][0]["field"] == "assignee_id"


def test_completion_conflict_expresses_state_conflict_not_validation_failure() -> None:
    create_response = client.post("/api/v1/tasks", json={"title": "Conflict semantics"})
    task_id = create_response.json()["data"]["id"]

    client.post(f"/api/v1/tasks/{task_id}/completion")
    response = client.post(f"/api/v1/tasks/{task_id}/completion")

    assert response.status_code == 409
    body = response.json()
    assert body["error"] == {
        "code": "TASK_ALREADY_COMPLETED",
        "message": "任务已完成，不能重复完成。",
        "details": [],
    }


def test_assign_task_returns_projection_specific_error_when_read_model_is_missing() -> None:
    broken_client = TestClient(create_app())
    original_event_bus = assemblers._event_bus

    def create_only_event_bus():
        bus = original_event_bus()
        original_publish = bus.publish

        def publish_once(events):
            original_publish(events)
            task_id = next(event.task_id for event in events if hasattr(event, "task_id"))
            session = assemblers.session_factory()
            try:
                model = session.get(TaskReadModelModel, task_id)
                assert model is not None
                session.delete(model)
                session.commit()
            finally:
                session.close()

            bus.publish = original_publish

        bus.publish = publish_once
        return bus

    assemblers._event_bus = create_only_event_bus
    try:
        create_response = broken_client.post("/api/v1/tasks", json={"title": "Projection gap"})
        task_id = create_response.json()["data"]["id"]

        response = broken_client.post(
            f"/api/v1/tasks/{task_id}/assignments",
            json={"assignee_id": "user_001"},
        )
    finally:
        assemblers._event_bus = original_event_bus

    assert create_response.status_code == 201
    assert response.status_code == 409
    body = response.json()
    assert body["error"]["code"] == "TASK_READ_MODEL_NOT_PROJECTED"
    assert task_id in body["error"]["message"]
    assert body["error"]["details"] == []
