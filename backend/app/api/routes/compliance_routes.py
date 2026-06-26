from fastapi import APIRouter

# Endpoint paths for compliance are currently exposed through campaign_routes.py or variant_routes.py.
# This module is reserved for future grouped endpoints.
router = APIRouter(tags=["compliance"])
