from fastapi import APIRouter, Request, UploadFile, File, Form

from app.core.response import not_implemented_response

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
def upload_document(request: Request, file: UploadFile = File(...), document_type: str = Form(...), campaign_id: str | None = Form(None)):
    return not_implemented_response("Slice 2 - Upload Document", request)


@router.post("/{document_id}/ingest")
def ingest_document(document_id: str, request: Request):
    return not_implemented_response("Slice 2 - Ingest Document", request)


@router.get("")
def list_documents(request: Request):
    return not_implemented_response("Slice 2 - List Documents", request)
