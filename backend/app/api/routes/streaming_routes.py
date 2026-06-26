from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/chat", tags=["streaming"])


@router.get("/campaign/{campaign_id}/stream")
def stream_campaign_chat(campaign_id: str):
    async def event_generator():
        yield 'event: error\ndata: {"code":"NOT_IMPLEMENTED_YET","message":"Slice 5 - Streaming Chat"}\n\n'

    return StreamingResponse(event_generator(), media_type="text/event-stream")
