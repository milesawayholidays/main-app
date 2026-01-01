from __future__ import annotations

from fastapi import Request

from src.config import config
from src.global_state import state


def ensure_request_initialized(request: Request) -> None:
    """Centralized per-request initialization.

    Requests can arrive before all modules/handlers have been initialized,
    so we make sure state/config + required handlers are ready per request.

    Notes:
    - Keep `/health` lightweight.
    - Only initialize the heavier flight pipeline dependencies for `/flights` routes.
    """

    path = request.url.path
    if path.endswith("/health"):
        return

    # Ensure state file/logging is initialized for non-health requests.
    state.ensure_loaded()

    # Airport mappings are needed by enrichment paths.
    config.ensure_airport_mappings_loaded()

    # Full env-backed config (secrets, sheet IDs, etc.).
    config.ensure_loaded()

    # Flight routes depend on partner handlers.
    if "/flights" in path:
        from src.services.seats_aero import seats_aero_handler
        from src.currencies.cash import handler as cash_handler
        from src.services.google_sheets import handler as sheets_handler
        from src.currencies.mileage import handler as mileage_handler

        if not seats_aero_handler.headers.get("Partner-Authorization"):
            seats_aero_handler.load(config.SEATS_AERO_API_KEY)
            state.update_flag("seatsAeroHandlerInitialized")

        if not hasattr(cash_handler, "target_currency"):
            cash_handler.load(target_currency=config.CURRENCY, api_key=config.EXCHANGE_RATE_API_KEY)
            state.update_flag("cashModInitialized")

        if not hasattr(sheets_handler, "client"):
            if not getattr(config, "GOOGLE_SERVICE_ACCOUNT", None):
                raise ValueError("Missing GOOGLE_SERVICE_ACCOUNT; cannot initialize Google Sheets")
            sheets_handler.load(config.GOOGLE_SERVICE_ACCOUNT)
            state.update_flag("googleSheetsModInitialized")

        if not getattr(mileage_handler, "mileage_values", None):
            mileage_handler.load(
                mileage_spreadsheet_id=config.MILEAGE_SPREADSHEET_ID,
                mileage_worksheet_name=config.MILEAGE_WORKSHEET_NAME,
            )
            state.update_flag("mileageModInitialized")
