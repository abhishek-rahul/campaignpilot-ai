from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.response import success_response
from app.services import evaluation_service

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.get("/{evaluation_id}")
def get_evaluation_result(evaluation_id: str, request: Request, db: Session = Depends(get_db)):
    data = evaluation_service.get_evaluation_detail(db, evaluation_id)
    return success_response("Evaluation fetched successfully", data.model_dump(mode="json"), request)
