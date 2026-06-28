from fastapi.testclient import TestClient

from app.main import app


def test_health_contract_shape_documentation():
    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"success", "message", "data", "error", "meta"}
    assert body["success"] is True
    assert body["error"] is None
    assert body["data"]["status"] == "ok"
