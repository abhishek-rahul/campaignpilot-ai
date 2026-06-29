from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.response import success_response
from app.services import observability_service

router = APIRouter(tags=["observability"])


@router.get("/llm-traces/{trace_id}")
def get_llm_trace_detail(trace_id: str, request: Request, db: Session = Depends(get_db)):
    data = observability_service.get_llm_trace_detail(db, trace_id)
    return success_response("LLM trace fetched successfully", data.model_dump(mode="json"), request)


@router.get("/tool-calls/{tool_call_id}")
def get_tool_call_detail(tool_call_id: str, request: Request, db: Session = Depends(get_db)):
    data = observability_service.get_tool_call_detail(db, tool_call_id)
    return success_response("Tool call log fetched successfully", data.model_dump(mode="json"), request)
