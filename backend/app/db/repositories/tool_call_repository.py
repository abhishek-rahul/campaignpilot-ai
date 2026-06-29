from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.db.models import ToolCallLog


def create_tool_call_log(db: Session, values: dict[str, Any]) -> ToolCallLog:
    log = ToolCallLog(**values)
    db.add(log)
    db.flush()
    db.refresh(log)
    return log
