from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError, ValidationError
from app.core.ids import new_id
from app.db.repositories import (
    campaign_repository,
    compliance_repository,
    delivery_repository,
    evaluation_repository,
    payload_repository,
    variant_repository,
)
from app.evaluation.scoring import grade_for_score, passed_for_checks
from app.evaluation.variant_quality import evaluate_variant_quality
from app.schemas.evaluation_schema import (
    EvaluationCheckData,
    EvaluationListData,
    EvaluationResultData,
    RunEvaluationRequest,
)


def evaluate_variant(db: Session, variant_id: str, request: RunEvaluationRequest) -> EvaluationResultData:
    if request.evaluation_type != "variant_quality":
        raise ValidationError("Only variant_quality evaluation is supported", code="UNSUPPORTED_EVALUATION_TYPE")
    variant = variant_repository.get_variant(db, variant_id)
    if variant is None:
        raise ResourceNotFoundError("Variant not found")
    campaign = campaign_repository.get_campaign(db, variant.campaign_id)
    if campaign is None:
        raise ResourceNotFoundError("Campaign not found")
    brief = campaign_repository.get_brief_for_campaign(db, campaign.id)
    result = evaluate_variant_quality(variant=variant, brief=brief)
    row = evaluation_repository.create_evaluation_result(
        db,
        {
            "id": new_id("evalres"),
            "campaign_id": campaign.id,
            "variant_id": variant.id,
            "evaluation_type": "variant_quality",
            "score": result["score"],
            "grade": result["grade"],
            "passed": result["passed"],
            "checks_json": [check.model_dump(mode="json") for check in result["checks"]],
            "recommendation": result["recommendation"],
        },
    )
    db.commit()
    db.refresh(row)
    return evaluation_result_data(row)


def evaluate_campaign_readiness(db: Session, campaign_id: str) -> EvaluationResultData:
    campaign = campaign_repository.get_campaign(db, campaign_id)
    if campaign is None:
        raise ResourceNotFoundError("Campaign not found")
    brief = campaign_repository.get_brief_for_campaign(db, campaign_id)
    variants = variant_repository.list_variants(db, campaign_id)
    payloads = payload_repository.list_payloads(db, campaign_id)
    delivery_logs = delivery_repository.list_delivery_logs(db, campaign_id)
    latest_compliance = compliance_repository.latest_results_for_campaign(db, campaign_id)
    selected_variant = variant_repository.get_variant(db, campaign.selected_variant_id) if campaign.selected_variant_id else None
    checks = [
        _readiness_check("complete_brief", bool(brief and brief.brief_status == "COMPLETE"), 20, "Campaign brief is complete."),
        _readiness_check("has_variants", bool(variants), 20, "At least one variant exists."),
        _readiness_check("has_compliance", bool(latest_compliance), 20, "At least one compliance result exists."),
        _readiness_check(
            "approved_selected_variant",
            bool(selected_variant and selected_variant.status == "APPROVED"),
            20,
            "An approved selected variant exists.",
        ),
        _readiness_check("has_payloads", bool(payloads), 10, "Payloads have been generated."),
        _readiness_check("delivery_visible", bool(delivery_logs), 10, "Delivery attempts are visible if sending was tested."),
    ]
    score = sum(check.score for check in checks)
    grade = grade_for_score(score)
    passed = passed_for_checks(score, checks)
    recommendation = (
        "Campaign is ready from an observability checklist perspective."
        if passed
        else "Complete missing readiness steps before launch: "
        + " ".join(check.message for check in checks if not check.passed)
    )
    row = evaluation_repository.create_evaluation_result(
        db,
        {
            "id": new_id("evalres"),
            "campaign_id": campaign_id,
            "variant_id": None,
            "evaluation_type": "campaign_readiness",
            "score": score,
            "grade": grade,
            "passed": passed,
            "checks_json": [check.model_dump(mode="json") for check in checks],
            "recommendation": recommendation,
        },
    )
    db.commit()
    db.refresh(row)
    return evaluation_result_data(row)


def list_campaign_evaluations(
    db: Session,
    campaign_id: str,
    *,
    evaluation_type: str | None = None,
    variant_id: str | None = None,
) -> EvaluationListData:
    if campaign_repository.get_campaign(db, campaign_id) is None:
        raise ResourceNotFoundError("Campaign not found")
    rows = evaluation_repository.list_evaluation_results(
        db,
        campaign_id,
        evaluation_type=evaluation_type,
        variant_id=variant_id,
    )
    return EvaluationListData(campaign_id=campaign_id, evaluations=[evaluation_result_data(row) for row in rows])


def get_evaluation_detail(db: Session, evaluation_id: str) -> EvaluationResultData:
    row = evaluation_repository.get_evaluation_result(db, evaluation_id)
    if row is None:
        raise ResourceNotFoundError("Evaluation result not found")
    return evaluation_result_data(row)


def evaluation_result_data(row) -> EvaluationResultData:
    return EvaluationResultData(
        evaluation_id=row.id,
        campaign_id=row.campaign_id,
        variant_id=row.variant_id,
        evaluation_type=row.evaluation_type,
        score=row.score,
        grade=row.grade,
        passed=row.passed,
        checks=[EvaluationCheckData(**check) for check in (row.checks_json or [])],
        recommendation=row.recommendation,
        created_at=row.created_at,
    )


def _readiness_check(check_id: str, passed: bool, max_score: int, pass_message: str) -> EvaluationCheckData:
    return EvaluationCheckData(
        check_id=check_id,
        passed=passed,
        score=max_score if passed else 0,
        max_score=max_score,
        message=pass_message if passed else pass_message.replace(" is ", " is not ").replace(" exists", " is missing"),
        high_risk=False,
    )
