from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RetrievedContextData(BaseModel):
    context_id: str
    campaign_id: str
    document_id: str | None = None
    chunk_id: str | None = None
    query_text: str
    retrieved_text: str
    score: float | None = None
    rank_position: int
    source_type: str
    used_for: str
    metadata: dict = Field(default_factory=dict)
    created_at: datetime | None = None


class RetrievedContextListData(BaseModel):
    campaign_id: str
    contexts: list[RetrievedContextData]


class CampaignPlanData(BaseModel):
    campaign_id: str
    plan: dict
    retrieved_contexts: list[RetrievedContextData]
