from app.rag.retriever import build_campaign_query


class BriefStub:
    goal = "Reactivate inactive customers"
    target_audience = "inactive customers"
    offer_details = "25% discount"
    tone = "friendly"
    preferred_channels = ["telegram", "whatsapp_mock"]


def test_build_campaign_query_uses_brief_fields():
    query = build_campaign_query(BriefStub())

    assert "Reactivate inactive customers" in query
    assert "25% discount" in query
    assert "telegram" in query
