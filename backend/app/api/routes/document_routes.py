from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.response import success_response
from app.schemas.document_schema import IngestDocumentRequest
from app.services import document_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    document_type: str = Form(...),
    campaign_id: str | None = Form(None),
    db: Session = Depends(get_db),
):
    data = await document_service.upload_document(db, file=file, document_type=document_type, campaign_id=campaign_id)
    return success_response("Document uploaded successfully", data.model_dump(mode="json"), request)


@router.post("/{document_id}/ingest")
def ingest_document(
    document_id: str,
    payload: IngestDocumentRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    data = document_service.ingest_document(db, document_id, payload)
    return success_response("Document ingested successfully", data.model_dump(mode="json"), request)


@router.get("/{document_id}")
def get_document(document_id: str, request: Request, db: Session = Depends(get_db)):
    data = document_service.get_document(db, document_id)
    return success_response("Document fetched successfully", data.model_dump(mode="json"), request)


@router.get("")
def list_documents(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    document_type: str | None = None,
    campaign_id: str | None = None,
):
    data = document_service.list_documents(
        db,
        page=page,
        page_size=page_size,
        status=status,
        document_type=document_type,
        campaign_id=campaign_id,
    )
    return success_response("Documents fetched successfully", data.model_dump(mode="json"), request)
