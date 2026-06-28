from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import CampaignPilotError
from app.core.response import error_response
from app.api.routes import (
    health_routes,
    campaign_routes,
    chat_routes,
    streaming_routes,
    document_routes,
    variant_routes,
    compliance_routes,
    approval_routes,
    channel_routes,
    delivery_routes,
    observability_routes,
    evaluation_routes,
)

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix = settings.api_v1_prefix
app.include_router(health_routes.router, prefix=prefix)
app.include_router(campaign_routes.router, prefix=prefix)
app.include_router(chat_routes.router, prefix=prefix)
app.include_router(streaming_routes.router, prefix=prefix)
app.include_router(document_routes.router, prefix=prefix)
app.include_router(variant_routes.router, prefix=prefix)
app.include_router(compliance_routes.router, prefix=prefix)
app.include_router(approval_routes.router, prefix=prefix)
app.include_router(channel_routes.router, prefix=prefix)
app.include_router(delivery_routes.router, prefix=prefix)
app.include_router(observability_routes.router, prefix=prefix)
app.include_router(evaluation_routes.router, prefix=prefix)


@app.exception_handler(CampaignPilotError)
def campaignpilot_exception_handler(request: Request, exc: CampaignPilotError):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.message, exc.code, request=request),
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = [
        {"field": ".".join(str(part) for part in error.get("loc", [])), "message": error.get("msg", "Invalid value")}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=error_response("Validation failed", "VALIDATION_ERROR", details=details, request=request),
    )


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    message = str(exc.detail) if exc.detail else "Request failed"
    code = "RESOURCE_NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR"
    return JSONResponse(status_code=exc.status_code, content=error_response(message, code, request=request))


@app.exception_handler(Exception)
def unexpected_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=error_response("Unexpected backend error", "INTERNAL_SERVER_ERROR", request=request),
    )


@app.get("/")
def root():
    return {"service": settings.app_name, "docs": f"{prefix}/health"}
