from fastapi import APIRouter

webhook_router = APIRouter()

from backend_api.webhook.clickmassa.clickmassa import clickmassa_router
webhook_router.include_router(clickmassa_router, prefix="/clickmassa", tags=["ClickMassa Webhooks"])