from fastapi import APIRouter

from config import config
from global_state import state
from alerts_runner import GET_round_from_region_to_region, GET_round_from_country_to_world, GET_single_from_country_to_world

from api.helpers import convert_region_to_enum, convert_cabins_str_to_enum

from data_types.enums import REGION, CABIN

from services.email import email_self, email
from services.clickmassa import clickmassa_handler

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

@router.get("/round-from-region-to-region")
def get_from_region_to_region(
    origin: str = None, 
    destination: str = None, 
    start_date: str = None, 
    end_date: str = None, 
    cabins: str = None, 
    min_return_days: int = 1, 
    max_return_days: int = 60,
    n: int = 1,
    deepness: int = 1
    ):
    """
    Endpoint to trigger the flight alert pipeline execution.
    
    This endpoint is used to start the flight alert system, which includes
    fetching flight data, processing alerts, and sending notifications.

    Args:
        origin (str): Origin city or region for the flight search
        destination (str): Destination city or region for the flight search 
        source (str): Airline source to filter results (optional)
        start_date (str): Start date for the flight search in YYYY-MM-DD format (optional
        end_date (str): End date for the flight search in YYYY-MM-DD format (optional)
        cabins (list[str]): List of cabin classes to filter results (optional)
        min_return_days (int): Minimum number of days for return flight (default: 1
        max_return_days (int): Maximum number of days for return flight (default: 60)
        n (int): Number of top results to return (default: 1)
        deepness (int): Pagination depth for results (default: 1)
    
    Returns:
        dict: A dictionary containing the status of the operation and any relevant messages.
    """
    if origin is None or destination is None:
        return {"status_code": 400, "message": "Origin and destination must be specified."}

    try:
        # Convert origin and destination to REGION enum
        state.logger.info(f"Converting origin '{origin}' and destination '{destination}' to REGION enum")
        originAsREGION: REGION = convert_region_to_enum(origin)
        destinationAsREGION: REGION = convert_region_to_enum(destination)
    except ValueError as e:
        state.logger.error(f"Invalid region provided: {e}")
        return {"status_code": 400, "message": f"Invalid region provided: {e}"}

    cabinAsCABIN: list[CABIN] = []
    if cabins:
        try:  
            cabinAsCABIN = convert_cabins_str_to_enum(cabins)
        except ValueError as e:
            state.logger.error(f"Invalid cabin class provided: {e}")
            return {"status_code": 400, "message": f"Invalid cabin class provided: {e}"}
 
    
    
    try:
        response = GET_round_from_region_to_region(
            origin=originAsREGION,
            destination=destinationAsREGION,
            start_date=start_date,
            end_date=end_date,
            cabins=cabinAsCABIN,
            min_return_days=min_return_days,
            max_return_days=max_return_days,
            n=n,
            deepness=deepness
        )
        state.logger.info("Alerts runner executed successfully.")
        if response.status_code != 200:
           raise ValueError(f"Alerts runner failed with status code: {response}")
        
        state.logger.info("Alerts runner completed successfully.")
    except Exception as e:
        state.log_exception(e)
        email_self(
            subject="Error in Alerts Runner",
            body=f"An error occurred while running the alerts: {e}\nCurrent state: {state}",
        )
        print(f"Error occurred: {e}")
        return {"status_code": 500, "message": str(e)}

    return {"status_code": 200, "message": "Alerts runner executed successfully."}

@router.get("/round-from-country-to-world")
def get_from_country_to_world(
    country: str = None, # Needs to be a country code
    start_date: str = None, 
    end_date: str = None, 
    cabin: str = None, 
    min_return_days: int = 1, 
    max_return_days: int = 60,
    n: int = 1,
    deepness: int = 1
):
    """
    Endpoint to trigger the flight alert pipeline execution for a country to world search.
    
    This endpoint is used to start the flight alert system for searching flights from a specific country
    to various destinations worldwide.

    Args:
        country (str): Country for the flight search
        start_date (str): Start date for the flight search in YYYY-MM-DD format (optional)
        end_date (str): End date for the flight search in YYYY-MM-DD format (optional)
        cabins (list[str]): List of cabin classes to filter results (optional)
        min_return_days (int): Minimum number of days for return flight (default: 1)
        max_return_days (int): Maximum number of days for return flight (default: 60)
        n (int): Number of top results to return (default: 1)
        deepness (int): Pagination depth for results (default: 1)
    
    Returns:
        dict: A dictionary containing the status of the operation and any relevant messages.
    """
    if country is None:
        return {"status_code": 400, "message": "Country must be specified."}

    cabinAsCABIN: CABIN = None
    if cabin:
        try:  
           cabinAsCABIN = CABIN(cabin)
        except ValueError as e:
            state.logger.error(f"Invalid cabin class provided: {e}")
            return {"status_code": 400, "message": 'Internal server error. Please try again later.'}
        
    try:
        response = GET_round_from_country_to_world(
            country=country,
            start_date=start_date,
            end_date=end_date,
            cabin=cabinAsCABIN,
            min_return_days=min_return_days,
            max_return_days=max_return_days,
            n=n,
            deepness=deepness
        )
        state.logger.info("Alerts runner executed successfully.")

        return response

    except Exception as e:
        state.log_exception(e)
        email_self(
            subject="Error in Alerts Runner",
            body=f"An error occurred while running the alerts: {e}\nCurrent state: {state}"
        )
        print(f"Error occurred: {e}")
        return {"status_code": 500, "message": 'Internal server error. Please try again later.'}

@router.get('/single-from-country-to-world')
def get_single_from_country_to_world(
    country: str = None, # Needs to be a country code
    start_date: str = None, 
    end_date: str = None, 
    cabins: list[str] = None, 
    n: int = 1,
    deepness: int = 1
):
    '''
    Endpoint to trigger the flight alert pipeline execution for a country to world search.
    This endpoint is used to start the flight alert system for searching flights from a specific country
    to various destinations worldwide.

    Args:
        country (str): Country for the flight search
        start_date (str): Start date for the flight search in YYYY-MM-DD format (optional)
        end_date (str): End date for the flight search in YYYY-MM-DD format (optional)
        cabins (list[str]): List of cabin classes to filter results (optional)
        min_return_days (int): Minimum number of days for return flight (default: 1)
        max_return_days (int): Maximum number of days for return flight (default: 60)
        n (int): Number of top results to return (default: 1)
        deepness (int): Pagination depth for results (default: 1)
    Returns:
        dict: A dictionary containing the status of the operation and any relevant messages.
    
    '''
    if country is None:
        return {"status_code": 400, "message": "Country must be specified."}
    
    cabinAsCABIN: list[CABIN] = []
    if cabins:
        try:  
            cabinAsCABIN = convert_cabins_str_to_enum(cabins)
        except ValueError as e:
            state.logger.error(f"Invalid cabin class provided: {e}")
            return {"status_code": 400, "message": 'Internal server error. Please try again later.'}
        
    try:
        response = GET_single_from_country_to_world(
            country=country,
            start_date=start_date,
            end_date=end_date,
            cabins=cabinAsCABIN,
            n=n,
            deepness=deepness,
        )
        state.logger.info("Alerts runner executed successfully.")
        
        return response
    except Exception as e:
        state.log_exception(e)
        email_self(
            subject="Error in Alerts Runner",
            body=f"An error occurred while running the alerts: {e}\nCurrent state: {state}"
        )
        print(f"Error occurred: {e}")
        return {"status_code": 500, "message": 'Internal server error. Please try again later.'}
    finally:
        state.logger.info("Alerts runner finished.")


@router.post("/clickmassa-message-alert")
def clickmassa_message_alert(
    request: dict
):
    try:
        state.logger.info(f"ClickMassa message alert triggered.")

        message = request.get('message', {})

        if not message:
            state.logger.warning("Message not found in the request.")
            return {"status_code": 400, "message": "Message not found in the request."}

        fromMe = message.get('fromMe', False)
        if fromMe:
            state.logger.info("Message is from the user, ignoring it.")
            return {"status_code": 200, "message": "ClickMassa message alert processed successfully."}

        ticket = message.get('ticket', "Unknown")
        if ticket == "Unknown":
            state.logger.warning("User ID not found in the message.")
            return {"status_code": 400, "message": "User ID not found in the message."}
        
        user = ticket.get('user', "Unknown")
        if user == "Unknown":
            state.logger.warning("User not found in the ticket.")
            return {"status_code": 400, "message": "User not found in the ticket."}

        user_email = user.get('email', None)
        if not user_email:
            state.logger.warning("User email not found.")
            return {"status_code": 400, "message": "User email not found."}
        
        email(
            subject="ALERTA DE MENSAGEM CLICKMASSA",
            body=f"Nova mensagem recebida.\nVerifique o clickmassa assim que puder",
            to=user_email
        )

        state.logger.info("ClickMassa message alert processed successfully.")
        return {"status_code": 200, "message": "ClickMassa message alert processed successfully."}
    except Exception as e:
        state.logger.error(f"Failed to process ClickMassa message alert: {e}")
        return {"status_code": 500, "message": "Internal server error. Please try again later."}