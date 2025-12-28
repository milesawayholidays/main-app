from fastapi import APIRouter

from src.config import config
from src.global_state import state

from src.services.email import email

router = APIRouter()

@router.get("/health")
def health_check():
    """
    Health check endpoint to verify API status.
    
    Returns a simple JSON response indicating the API is running.
    
    Returns:
        dict: A dictionary with a message indicating the API is healthy.
    """
    return {"status": "API is running", "version": config.VERSION}

from backend_api.webhook.webhook import webhook_router
from backend_api.flights_system.flights_api import flights_router

router.include_router(webhook_router, prefix="/webhook", tags=["Webhooks"])
router.include_router(flights_router, prefix="/flights",  tags=["Flights System"])

router.prefix = "/api"