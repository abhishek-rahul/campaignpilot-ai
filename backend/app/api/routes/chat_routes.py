from fastapi import APIRouter, Request

from app.core.response import not_implemented_response

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/campaign")
def campaign_chat_message(request: Request):
    return not_implemented_response("Slice 1 - Campaign Chat Message", request)
