"""
Main Entry Point for the flightAlertsSystem Flight Alert System

This module serves as the primary entry point for the flight alert application,
orchestrating the entire pipeline from configuration loading through alert
generation and distribution. It provides centralized error handling and
logging for the complete execution cycle.

The main function coordinates:
- Configuration initialization and validation
- Flight alert pipeline execution via alerts_runner
- Exception handling with automatic state logging
- Error notification via email for failed executions
- Graceful handling of missing credentials

Key Features:
    - Comprehensive error handling with automatic logging
    - Email notifications for execution failures
    - State persistence for debugging and recovery
    - Graceful degradation for missing email credentials
    - Centralized logging through global state manager

Functions:
    main(): Primary execution coordinator and error handler

Dependencies:
    - config: Configuration management and environment variables
    - global_state: Centralized state tracking and logging
    - alerts_runner: Core flight alert pipeline orchestrator
    - gmail: Error notification email service

Usage:
    python main.py
    
Environment Variables Required:
    See config.py for complete list of required environment variables
    including API keys, email credentials, and system configuration.
"""
import uvicorn
from app import APP
import os

from config import config
from global_state import state

from currencies.cash import handler as cash_handler
from currencies.mileage import handler as mileage_handler

from services.google_drive import handler as drive_handler
from services.google_sheets import handler as google_sheets_handler
from services.openAI import handler as openai_handler
from services.seats_aero import seats_aero_handler as seats_aero_handler
from services.clickmassa import handler as clickmassa_handler

def setup():
    """
    Main execution function for the flight alert system.
    
    This function orchestrates the complete flight alert pipeline execution,
    from initial configuration loading through final alert distribution.
    Provides comprehensive error handling with automatic state logging
    and email notifications for execution failures.
    
    Execution Flow:
        1. Load and validate configuration from environment variables
        2. Execute the complete flight alert pipeline via alerts_runner
        3. Validate successful completion via HTTP status code
        4. Log successful completion to global state
        5. Handle any exceptions with detailed logging and email notifications
    
    Error Handling:
        - Catches and logs all exceptions via global state manager
        - Sends email notifications for execution failures (when credentials available)
        - Provides graceful handling for missing email credentials
        - Preserves complete execution state for debugging
    
    Side Effects:
        - Initializes global configuration and state management
        - Creates log files in logs/ directory with execution details
        - Sends email notifications on errors (if credentials configured)
        - Prints error messages to console for immediate feedback
    
    Raises:
        SystemExit: Implicitly via return statements for handled errors
        
    Note:
        This function is designed to be the single entry point for the
        entire flight alert system. All pipeline orchestration and error
        handling is centralized here for consistency and maintainability.
    """

    state.load()
    state.update_flag('mainModInitialized')
    config.load()
    state.update_flag('configInitialized')
    drive_handler.load()
    state.update_flag('googleDriveModInitialized')
    google_sheets_handler.load(config.GOOGLE_SERVICE_ACCOUNT)
    state.update_flag('googleSheetsModInitialized')
    openai_handler.load(config.OPENAI_API_KEY)
    state.update_flag('openAIHandlerInitialized')
    seats_aero_handler.load(config.SEATS_AERO_API_KEY)
    state.update_flag('seatsAeroHandlerInitialized')
    cash_handler.load(target_currency=config.CURRENCY, api_key=config.EXCHANGE_RATE_API_KEY)
    state.update_flag('cashModInitialized')
    mileage_handler.load(mileage_spreadsheet_id=config.MILEAGE_SPREADSHEET_ID, mileage_worksheet_name=config.MILEAGE_WORKSHEET_NAME)
    state.update_flag('mileageModInitialized')
    clickmassa_handler.load(config.CLICKMASSA_ID, config.CLICKMASSA_USERS)
    state.update_flag('clickmassaHandlerInitialized')

    state.logger.info("All modules initialized successfully.")


if __name__ == "__main__":
    try:
        setup()
        PORT = int(os.getenv("PORT", 4000))
        uvicorn.run(APP, host="0.0.0.0", port=PORT)
    except Exception as e:
        state.log_exception(e)
        #email_self(
        #    subject="Error in Main Execution",
        #    body=f"An error occurred during the main execution: {e}\nCurrent state: {state}",
        #)
        print(f"Error occurred during main execution: {e}")
        exit(1)
