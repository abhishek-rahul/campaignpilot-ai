from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.response import success_response
from app.services import channel_service, delivery_service

router = APIRouter(tags=["delivery"])


@router.get("/payloads/{payload_id}")
def get_payload(payload_id: str, request: Request, db: Session = Depends(get_db)):
    data = channel_service.get_payload_detail(db, payload_id)
    return success_response("Payload fetched successfully", data.model_dump(mode="json"), request)


@router.post("/payloads/{payload_id}/send")
def send_payload(payload_id: str, request: Request, db: Session = Depends(get_db)):
    data = delivery_service.send_payload(db, payload_id)
    return success_response("Payload sent successfully", data.model_dump(mode="json"), request)


@router.get("/delivery-logs/{delivery_id}")
def get_delivery_log(delivery_id: str, request: Request, db: Session = Depends(get_db)):
    data = delivery_service.get_delivery_detail(db, delivery_id)
    return success_response("Delivery log fetched successfully", data.model_dump(mode="json"), request)
