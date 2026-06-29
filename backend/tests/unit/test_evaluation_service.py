from datetime import datetime, timezone
from types import SimpleNamespace

from app.schemas.evaluation_schema import RunEvaluationRequest
from app.services import evaluation_service


class FakeDb:
    def commit(self):
        self.committed = True

    def refresh(self, _row):
        return None


def test_evaluation_service_saves_result_without_mutating_variant(monkeypatch):
    variant = SimpleNamespace(
        id="var_1",
        campaign_id="camp_1",
        message_body="Claim 25% discount now: https://example.com/sale",
        channel="telegram",
        tone="friendly",
        status="GENERATED",
    )
    campaign = SimpleNamespace(id="camp_1")
    brief = SimpleNamespace(tone="friendly", offer_details="25% discount", cta_link="https://example.com/sale")
    saved = {}

    monkeypatch.setattr(evaluation_service.variant_repository, "get_variant", lambda _db, _variant_id: variant)
    monkeypatch.setattr(evaluation_service.campaign_repository, "get_campaign", lambda _db, _campaign_id: campaign)
    monkeypatch.setattr(evaluation_service.campaign_repository, "get_brief_for_campaign", lambda _db, _campaign_id: brief)

    def fake_create(_db, values):
        saved.update(values)
        return SimpleNamespace(created_at=datetime.now(timezone.utc), **values)

    monkeypatch.setattr(evaluation_service.evaluation_repository, "create_evaluation_result", fake_create)

    data = evaluation_service.evaluate_variant(FakeDb(), "var_1", RunEvaluationRequest())

    assert data.variant_id == "var_1"
    assert data.evaluation_type == "variant_quality"
    assert variant.status == "GENERATED"
    assert saved["checks_json"]
