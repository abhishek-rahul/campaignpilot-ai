from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
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


@app.get("/")
def root():
    return {"service": settings.app_name, "docs": f"{prefix}/health"}
