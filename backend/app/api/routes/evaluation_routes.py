from fastapi import APIRouter, Request

from app.core.response import not_implemented_response

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.post("/run")
def run_evaluation(request: Request):
    return not_implemented_response("Slice 6 - Run Evaluation", request)


@router.get("/{evaluation_run_id}")
def get_evaluation_run(evaluation_run_id: str, request: Request):
    return not_implemented_response("Slice 6 - Get Evaluation Run", request)
