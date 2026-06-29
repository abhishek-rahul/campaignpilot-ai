from types import SimpleNamespace

import pytest

from app.core.exceptions import ValidationError
from app.services import approval_service
from app.schemas.approval_schema import ApproveVariantRequest, RejectVariantRequest


class FakeDb:
    def commit(self):
        pass

    def refresh(self, _obj):
        pass


def _patch_common(monkeypatch, latest_status="PASSED"):
    variant = SimpleNamespace(id="var_1", campaign_id="camp_1", status="COMPLIANCE_PASSED")
    campaign = SimpleNamespace(id="camp_1", status="COMPLIANCE_CHECKED", selected_variant_id=None)
    latest = SimpleNamespace(status=latest_status) if latest_status else None

    monkeypatch.setattr(approval_service.variant_repository, "get_variant", lambda _db, _id: variant)
    monkeypatch.setattr(approval_service.campaign_repository, "get_campaign", lambda _db, _id: campaign)
    monkeypatch.setattr(approval_service.compliance_repository, "latest_compliance_result", lambda _db, _id: latest)
    monkeypatch.setattr(approval_service.variant_repository, "update_variant_status", lambda _db, obj, status: setattr(obj, "status", status) or obj)
    monkeypatch.setattr(approval_service.campaign_repository, "select_variant", lambda _db, obj, variant_id: setattr(obj, "selected_variant_id", variant_id) or obj)
    monkeypatch.setattr(approval_service.campaign_repository, "update_campaign_status", lambda _db, obj, status: setattr(obj, "status", status) or obj)

    def create_approval(_db, values):
        return SimpleNamespace(created_at="2026-06-29T00:00:00Z", **values)

    monkeypatch.setattr(approval_service.approval_repository, "create_approval", create_approval)


def test_approval_allowed_for_passed(monkeypatch):
    _patch_common(monkeypatch, "PASSED")

    result = approval_service.approve_variant(FakeDb(), "var_1", ApproveVariantRequest(reason="ok"))

    assert result.status == "APPROVED"
    assert result.new_status == "APPROVED"


def test_approval_blocked_for_failed_without_override(monkeypatch):
    _patch_common(monkeypatch, "FAILED")

    with pytest.raises(ValidationError) as exc:
        approval_service.approve_variant(FakeDb(), "var_1", ApproveVariantRequest())

    assert exc.value.code == "VARIANT_NOT_COMPLIANT"


def test_approval_allowed_for_failed_with_override(monkeypatch):
    _patch_common(monkeypatch, "FAILED")

    result = approval_service.approve_variant(
        FakeDb(), "var_1", ApproveVariantRequest(reason="manual override", allow_high_risk_override=True)
    )

    assert result.override_used is True


def test_rejection_always_allowed(monkeypatch):
    _patch_common(monkeypatch, None)

    result = approval_service.reject_variant(FakeDb(), "var_1", RejectVariantRequest(reason="too risky"))

    assert result.status == "REJECTED"
