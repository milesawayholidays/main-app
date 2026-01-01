from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.config import config
from src.global_state import state

from src.services.email import email
from src.services.openAI import handler as openai_handler

router = APIRouter()


class PostRow(BaseModel):
    id: str | None = None
    origin_city: str | None = None
    origin_country: str | None = None
    destination_city: str | None = None
    destination_country: str | None = None
    departure_date: str | None = None
    return_date: str | None = None
    cabin: str | None = None
    program: str | None = None
    mileage_cost: str | None = None
    taxes: str | None = None
    total_cost: str | None = None
    remaining_seats: str | None = None
    booking_link: str | None = None


class GetPostRequest(BaseModel):
    rows: list[PostRow] = Field(default_factory=list)

@router.get("/health")
def health_check():
    """
    Health check endpoint to verify API status.
    
    Returns a simple JSON response indicating the API is running.
    
    Returns:
        dict: A dictionary with a message indicating the API is healthy.
    """
    return {"status": "API is running", "version": config.VERSION}


@router.post("/get-post")
def get_post(payload: GetPostRequest):
    """Generate WhatsApp post(s) from selected (toggled) rows."""

    if not payload.rows:
        return {"status": 400, "error": "No rows provided", "data": {"posts": []}}

    # Lazy-init OpenAI client.
    if not getattr(openai_handler, "client", None):
        openai_handler.load(config.OPENAI_API_KEY)

    posts: list[dict] = []
    skipped: list[dict] = []

    for r in payload.rows:
        if not r.origin_city or not r.destination_city:
            skipped.append({"id": r.id, "reason": "missing origin_city or destination_city"})
            continue

        try:
            post = openai_handler.generateWhatsAppPost(
                origin_city=r.origin_city,
                origin_country=r.origin_country or "",
                destination_city=r.destination_city,
                destination_country=r.destination_country or "",
                departure_dates=[r.departure_date] if r.departure_date else [],
                return_dates=[r.return_date] if r.return_date else [],
                cabin=r.cabin or "",
                miles_cost=(
                    f"{r.mileage_cost} {r.program} miles" if r.mileage_cost and r.program else (r.mileage_cost or "")
                ),
                taxes=r.taxes or "",
                source=r.program or "",
                # Module expects selling_price; we use total_cost as the cost to buy with us.
                selling_price=r.total_cost or "",
                remaining_seats=r.remaining_seats or "",
                booking_link=r.booking_link or "",
            )
            posts.append({"id": r.id, "post": post})
        except Exception as e:
            skipped.append({"id": r.id, "reason": f"failed to generate post: {str(e)}"})

    return {"status": 200, "data": {"posts": posts, "skipped": skipped}}

from backend_api.webhook.webhook import webhook_router
from backend_api.flights_system.flights_api import flights_router

router.include_router(webhook_router, prefix="/webhook", tags=["Webhooks"])
router.include_router(flights_router, prefix="/flights",  tags=["Flights System"])