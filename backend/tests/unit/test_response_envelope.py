from app.core.response import error_response, success_response


def test_success_response_shape():
    body = success_response("ok", {"value": 1})
    assert set(body.keys()) == {"success", "message", "data", "error", "meta"}
    assert body["success"] is True
    assert body["data"] == {"value": 1}
    assert body["error"] is None


def test_error_response_shape():
    body = error_response("bad", "BAD_REQUEST", details=[{"field": "message"}])
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "BAD_REQUEST"
    assert body["error"]["details"] == [{"field": "message"}]
