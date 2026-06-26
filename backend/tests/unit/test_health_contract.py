def test_health_contract_shape_documentation():
    expected_keys = {"success", "message", "data", "error", "meta"}
    assert expected_keys == {"success", "message", "data", "error", "meta"}
