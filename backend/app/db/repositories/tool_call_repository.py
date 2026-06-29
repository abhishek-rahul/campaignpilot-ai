from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ToolCallLog


def create_tool_call_log(db: Session, values: dict[str, Any]) -> ToolCallLog:
    log = ToolCallLog(**values)
    db.add(log)
    db.flush()
    db.refresh(log)
    return log


def get_tool_call_log(db: Session, tool_call_id: str) -> ToolCallLog | None:
    return db.get(ToolCallLog, tool_call_id)


def list_tool_call_logs(
    db: Session,
    campaign_id: str,
    *,
    tool_name: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> list[ToolCallLog]:
    stmt = select(ToolCallLog).where(ToolCallLog.campaign_id == campaign_id)
    if tool_name:
        stmt = stmt.where(ToolCallLog.tool_name == tool_name)
    if status:
        stmt = stmt.where(ToolCallLog.status == status)
    return list(db.scalars(stmt.order_by(ToolCallLog.created_at.desc(), ToolCallLog.id.desc()).limit(limit)).all())
