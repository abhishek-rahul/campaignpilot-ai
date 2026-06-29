from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RunEvaluationRequest(BaseModel):
    evaluation_type: str = "variant_quality"


class EvaluationCheckData(BaseModel):
    check_id: str
    passed: bool
    score: int
    max_score: int
    message: str
    high_risk: bool = False


class EvaluationResultData(BaseModel):
    evaluation_id: str
    campaign_id: str
    variant_id: str | None = None
    evaluation_type: str
    score: int
    grade: str
    passed: bool
    checks: list[EvaluationCheckData]
    recommendation: str
    created_at: datetime


class EvaluationListData(BaseModel):
    campaign_id: str
    evaluations: list[EvaluationResultData] = Field(default_factory=list)
