"""
Core logic pipeline for fetching, filtering, formatting, generating, and sending flight alert data.

This module contains the main orchestration logic for the flight alert system. It coordinates
all components to fetch flight data from multiple sources, filter for the best deals, format
trip information, generate marketing content and PDFs, store data in Google Sheets, and
deliver final reports via email.

Pipeline Overview:
1. Fetch bulk flight availability from multiple airline sources
2. Filter and identify the top N cheapest round trips by cabin class
3. Retrieve detailed availability for selected trips
4. Format trips into RoundTripOptions with marketing content
5. Generate WhatsApp posts and travel images via external APIs
6. Create PDF reports for each trip option
7. Store data in Google Sheets for tracking and analysis
8. Email PDFs to administrators for distribution

The module handles:
- Multi-source data aggregation and processing
- Error handling and logging throughout the pipeline
- Release scheduling with time-based distribution
- Content randomization for marketing variety
- Integration with external services (OpenAI, Unsplash, Gmail, Google Sheets)
- State management and progress tracking

Key Features:
- Supports multiple airline sources simultaneously
- Flexible cabin class filtering (Economy, Business)
- Automated content generation and formatting
- Comprehensive error handling and recovery
- Detailed logging for monitoring and debugging
"""

import os
from datetime import date, timedelta
from requests import Response

from global_state import state
from config import config

from logic.filter import flight_Filter
from data_types.summary_objs import summary_round_trip, summary_trip
from data_types.enums import CABIN

# Type aliases for cleaner code
summary_round_trip_list_by_city_pairing_by_cabin = dict[CABIN, dict[tuple[str, str], list[summary_round_trip]]]
summary_trip_list_by_cabin = dict[CABIN, list[summary_trip]]


from logic.trip_builder import RoundTrip, format_availability_object, TripOption
from logic.pdf_generator import generate_pdf_for_round_trips, generate_pdf_for_single_trips
from logic.trip_builder import Route

from currencies.cash import cents_to_str

from services.seats_aero import seats_aero_handler
from services.email import email_self
from services.google_sheets import handler as sheets_handler  

from data_types.enums import SOURCE, REGION, CABIN
from data_types.pdf_types import PDF_OBJ
from data_types.flight_options import FlightOptions


def GET_round_from_region_to_region(
        origin: REGION, 
        destination: REGION, 
        start_date: str = None, 
        end_date: str = None,
        cabins: list[CABIN] = None, 
        min_return_days: int = 1, 
        max_return_days: int = 60,
        n: int = 1,
        deepness: int = 1
    ) -> dict:
    """
    Execute the complete flight alerts pipeline from data fetching to email delivery.
    
    This is the main orchestration function that coordinates all components of the
    flight alert system. It fetches flight data from multiple sources, processes
    and filters for the best deals, generates marketing content, creates PDFs,
    stores data, and delivers final reports.
    
    Pipeline Steps:
    1. **Data Fetching**: Retrieves bulk flight availability from all configured sources
    2. **Filtering**: Identifies top N cheapest round trips using filtering algorithms
    3. **Detail Retrieval**: Fetches complete trip details for selected flights
    4. **Content Generation**: Creates marketing content (WhatsApp posts, images)
    5. **PDF Creation**: Generates formatted PDF reports for each trip option
    6. **Data Storage**: Writes trip data to Google Sheets for tracking
    7. **Email Delivery**: Sends PDF reports to administrators
    
    Args:
        origin (REGION): Origin region enum (e.g., REGION.SOUTH_AMERICA)
        destination (REGION): Destination region enum (e.g., REGION.EUROPE)
        source (SOURCE): Mileage source enum (e.g., SOURCE.azul)
        start_date (str): Search start date in YYYY-MM-DD format
        end_date (str): Search end date in YYYY-MM-DD format
        cabins (list[CABIN], optional): List of cabin classes to include (e.g., [CABIN.ECONOMY, CABIN.BUSINESS])
        min_return_days (int): Minimum days between outbound and return flights (default: 1)
        max_return_days (int): Maximum days between outbound and return flights (default: 60)
        n (int): Number of top trips to process (default: 1)
        deepness (int): Pagination depth for results (default: 1)

    Returns:
        int: HTTP status code indicating success (200) or failure (non-200)
            
    Raises:
        ValueError: If no flight data is found from any source or no top trips
            are identified during filtering
        Exception: Re-raises any service-level errors (API failures, email issues, etc.)
        
    Note:
        - Uses configuration settings for regions, dates, cabins, and limits
        - Updates global state flags for progress tracking
        - Implements time-based release scheduling (morning/noon/night cycles)
        - Randomizes trip order for marketing variety
        - Handles partial failures gracefully where possible
        - Logs all major steps for monitoring and debugging
        
    Configuration Dependencies:
        - ORIGIN_REGION, DESTINATION_REGION: Geographic search areas
        - START_DATE, END_DATE: Date range for flight searches
        - CABINS: List of cabin classes to include
        - N: Number of top trips to process
        - TAKE: Maximum results per source query
        
    State Management:
        - Sets state.flightsRetrieved after successful data fetching
        - Sets state.flightsAnalysed after successful filtering
        - Updates logger with progress throughout pipeline
        
    Example:
        >>> response = alerts_runner()
        >>> if response == 200:
        ...     print("Flight alerts processed successfully")
        ... else:
        ...     print(f"Error processing flight alerts: {response}")   
    """
    state.logger.info("Starting flight alert pipeline execution")
    sources = [source for source in SOURCE]

    bulk_availability_search_by_source_list: dict[SOURCE, list] = dict()
    for source in sources:
        bulk_availability_search_result = seats_aero_handler.fetch_bulk_availability(
            source=source,
            start_date=start_date,
            end_date=end_date,
            origin_region=origin,
            destination_region=destination,
            deepness=deepness
        )

        if not bulk_availability_search_result:
            state.logger.error(f"No data found for source: {source}")
            continue

        state.logger.info(f"Bulk availability search completed for source: {source}")

        bulk_availability_search_by_source_list[source] = bulk_availability_search_result

    if not bulk_availability_search_by_source_list or len(bulk_availability_search_by_source_list) == 0:
        state.logger.error("No data found in bulk availability search for any source.")
        return Response(status=204, data={"error": "No data found in bulk availability search for any source."})
    
    state.update_flag('flightsRetrieved')
    state.logger.info("Flights retrieved successfully")


    topNRoundTrips: summary_round_trip_list_by_city_pairing_by_cabin = flight_Filter.get_best_round_trips_from_multiple_sources(
        bulk_availability_by_source=bulk_availability_search_by_source_list,
        cabins=cabins,
        min_return_days=min_return_days,
        max_return_days=max_return_days,
        n = n
    )

    if not topNRoundTrips:
        state.logger.error("No data found in top N flights.")
        return Response(status=204, data={"error": "No valid round trips found"})

    state.update_flag('flightsAnalysed')
    state.logger.info(f"Flights analysed")

    ''' 
    for cabin, city_pairings_round_trips in topNRoundTrips.items():
        state.logger.info(f"Found {len(city_pairings_round_trips)} city pairings for cabin: {cabin}")
        for city_pairing, round_trips in city_pairings_round_trips.items():
            state.logger.info(f"City pairing {city_pairing} has {len(round_trips)} round trips")   
            state.logger.info(f"First 5 are: : {round_trips[:5]}")
    '''

        
    flight_options = format_round_flights(topNRoundTrips)
    if not flight_options or len(flight_options) == 0:
        return Response(status=204, data={"error": "No valid flight options found"})

    pdfs = broadcast_round_flights(flight_options, n)

    # Delete the files used in the response so the server isn't overloaded with files
    clear_round(flight_options, pdfs)

    return Response(status=200, data={"message": "Flight options processed successfully"})

#TODO: Since it will be necessary to fetch both outgoing and incoming flights for each region pair, might as well make this a general function with a filter param. 
def GET_round_from_country_to_world(
        country: str, 
        start_date: str = None, 
        end_date: str = None,
        cabin: list[CABIN] = None, 
        min_return_days: int = 1, 
        max_return_days: int = 60,
        n: int = 1,
        deepness: int = 1
    ) -> dict:
    """
    Fetch flight data from a specific country to all world regions.
    
    This function is a wrapper around the main flight alert pipeline to handle
    requests for flights originating from a specific country to all world regions.
    
    Args:
        country (str): Country name or code to fetch flights from
        source (SOURCE): Mileage source enum (e.g., SOURCE.azul)
        start_date (str): Search start date in YYYY-MM-DD format
        end_date (str): Search end date in YYYY-MM-DD format
        cabins (list[CABIN], optional): List of cabin classes to include
        min_return_days (int): Minimum days between outbound and return flights (default: 1)
        max_return_days (int): Maximum days between outbound and return flights (default: 60)
        n (int): Number of top trips to process (default: 1)
        deepness (int): Pagination depth for results (default: 1)

    Returns:
        dict: A dictionary containing the status of the operation and any relevant messages.

    Raises:
        ValueError: If no flight data is found for the specified country
    """
    state.logger.info(f"Starting flight alert pipeline for country: {country}")

    if not country:
        return Response(status=400, data={"error": "Country must be specified."})

    try:
        origin_region = REGION.from_country(country, config.COUNTRY_REGION)
    except ValueError as e:
        state.logger.error(f"Could not find a valid region for the specified country: {country}. Error: {str(e)}")
        return {"status": 400, "data": {"error": "Could not find a valid region for the specified country."}}

    state.logger.info(f"Fetching flights from {country} ({origin_region.value}) to all world regions")

    bulk_availability_search_by_source_by_region_list: dict[REGION, dict[SOURCE, list]] = dict()
    hasTrips = False
    for region in REGION:
        if region not in bulk_availability_search_by_source_by_region_list:
            bulk_availability_search_by_source_by_region_list[region] = dict()
        for source in SOURCE:
            new_deepness = deepness if region != origin_region else deepness * 2
            response = seats_aero_handler.fetch_bulk_availability(
                source=source,
                start_date=start_date,
                end_date=end_date,
                origin_region=origin_region,
                destination_region=region,
                deepness=new_deepness,
                cabin=cabin
            )
            if not response and len(response) == 0:
                continue
            if region not in bulk_availability_search_by_source_by_region_list:
                bulk_availability_search_by_source_by_region_list[region] = dict()
            if source not in bulk_availability_search_by_source_by_region_list[region]:
                bulk_availability_search_by_source_by_region_list[region][source] = []
            bulk_availability_search_by_source_by_region_list[region][source].extend(response)

            if region == origin_region:
                hasTrips = True
                continue

            response = seats_aero_handler.fetch_bulk_availability(
                source=source,
                start_date=start_date,
                end_date=end_date,
                origin_region=region,
                destination_region=origin_region,
                deepness=new_deepness,
                cabin=cabin
            )
            if not response and len(response) == 0:
                continue
            if source not in bulk_availability_search_by_source_by_region_list[region]:
                bulk_availability_search_by_source_by_region_list[region][source] = []
            bulk_availability_search_by_source_by_region_list[region][source].extend(response)

            hasTrips = True


    if not hasTrips:
        state.logger.error(f"No data found in bulk availability search for country: {country}.")
        return {"status": 404, "data": {"error": "No data found in bulk availability search for country."}}

    state.update_flag('flightsRetrieved')
    state.logger.info(f"Flights retrieved successfully with length: {len(bulk_availability_search_by_source_by_region_list)}")

    state.logger.info("Starting to filter top N round trips from multiple sources")
    best_trips_by_region: dict[REGION, dict[CABIN, dict[tuple[str, str], list[summary_trip_list_by_cabin]]]] = dict()
    hasTrips = False
    for region, bulk_availability in bulk_availability_search_by_source_by_region_list.items():
        result = flight_Filter.get_best_round_trips_from_multiple_sources(
            bulk_availability_by_source=bulk_availability,
            cabins=cabin,
            min_return_days=min_return_days,
            max_return_days=max_return_days,
            n=n,
            filter={"origin_country": country}
        )
        if not result:
            state.logger.warning(f"No best trips found for region: {region}")
            continue
        if region not in best_trips_by_region:
            best_trips_by_region[region] = dict()
        best_trips_by_region[region] = result
        hasTrips = True

    if not hasTrips:
        state.logger.error("No data found in getBestRoundTrips")
        return {"status": 204, "data": {"error": "No valid flights found."}}

    state.update_flag('flightsAnalysed')
    state.logger.info(f"Flights analysed")

    hasTrips = False
    flight_options_by_region: dict[REGION, FlightOptions] = dict()
    for region, trips in best_trips_by_region.items():
        if trips is None or len(trips) == 0:
            state.logger.warning(f"No trips found for region: {region}")
            continue
        result = format_round_flights(trips, region.name)
        if not result:
            state.logger.warning(f"No flight options found for region: {region}")
            continue
        flight_options_by_region[region] = result     
        hasTrips = True

    if not hasTrips:
        return {"status": 204, "data":{"error": "No valid flight options found"}}
    
    for options in flight_options_by_region.values():
        # Generate PDFs for each flight option
        state.logger.info(f"Generating PDFs for flight options")
        broadcast_round_flights(options, n)

    # Delete the files used in the response so the server isn't overloaded with files
    #for options in flight_options_by_region.values():
    #    clear_round(options.round_options)

    #clear_pdfs(*pdfs_list)
    
    return {"status": 200, "data": {"message": "Flight options processed successfully"}}

def GET_single_from_country_to_world(
        country: str,
        start_date: str = None,
        end_date: str = None,
        cabins: list[CABIN] = None,
        n: int = 1,
        deepness: int = 1
    ) -> int:
    """
    Fetch flight data from a specific country to all world regions, processing only the top single trip
    This function is a wrapper around the main flight alert pipeline to handle
    requests for flights originating from a specific country to all world regions, but only processes
    the top single trip.
    Args:
        country (str): Country name or code to fetch flights from
        source (SOURCE): Mileage source enum (e.g., SOURCE.azul)
        start_date (str): Search start date in YYYY-MM-DD format
        end_date (str): Search end date in YYYY-MM-DD format
        cabins (list[CABIN], optional): List of cabin classes to include
        min_return_days (int): Minimum days between outbound and return flights (default: 1
        max_return_days (int): Maximum days between outbound and return flights (default: 60)
        n (int): Number of top trips to process (default: 1)
        deepness (int): Pagination depth for results (default: 1)
    Returns:
        int: HTTP status code indicating success (200) or failure (non-200)
    Raises:
        ValueError: If no flight data is found for the specified country
    """

    state.logger.info(f"Starting flight alert pipeline for country: {country} with single trip processing")
    if not country:
        return {"status": 400, "message": "Country must be specified."}

    try:
        origin_region = REGION.from_country(country, config.COUNTRY_REGION)
    except ValueError as e:
        return {"status": 400, "message": str(e)}   

    state.logger.info(f"Fetching flights from {country} ({origin_region.value}) to all world regions")

    # Call the main pipeline function with the specified country and region
    search_result: dict[REGION, dict[SOURCE, list]] = dict()
    for region in REGION:
        if region not in search_result:
            search_result[region] = dict()
        for source in SOURCE:
            response = seats_aero_handler.fetch_bulk_availability(
                source=source,
                start_date=start_date,
                end_date=end_date,
                origin_region=origin_region,
                destination_region=region,
                deepness=deepness
            )
            if source not in search_result:
                search_result[region][source] = []
            if response:  # Only extend if response is not empty
                search_result[region][source].extend(response)

    if not search_result or len(search_result) == 0:
        state.logger.error(f"No data found in bulk availability search for country: {country}.")
        raise ValueError(f"No data found in bulk availability search for country: {country}.")
    
    state.update_flag('flightsRetrieved')
    state.logger.info(f"Flights retrieved successfully with length: {len(search_result)}")

    state.logger.info("Starting to filter top N round trips from multiple sources")

    best_trips_by_cabin_by_region: dict[REGION, dict[CABIN, list[summary_trip]]] = dict()
    for region, bulk_availability in search_result.items():
        best_trips_by_cabin_by_region[region] = flight_Filter.getTopNTripsFromMultipleSources(
            bulk_availability_by_source=bulk_availability,
            cabins=cabins,
            n=n,
            filter={"origin_country": country}
        )

    state.update_flag('flightsAnalysed')
    state.logger.info(f"Flights analysed.")

    flight_options: dict[REGION, dict[CABIN, list[TripOption]]] = dict()
    for region, options_by_cabin in best_trips_by_cabin_by_region.items():
        flight_options[region] = format_single_flights(options_by_cabin, region.name)

    if (not flight_options) or (len(flight_options) == 0):
        state.logger.error("No valid flight options found.")
        return {"status": 404, "message": "No valid flight options found."}

    for region, options_by_cabin in flight_options.items():
        broadcast_single_flights(options_by_cabin, n)
    # Delete the files used in the response so the server isn't overloaded with files

    for cabin_option in flight_options.values():
        for option in cabin_option.values():
            clear_single(option)

    return {"status": 200, "message": "Success"}

def format_single_flights(trips_by_cabin: dict[CABIN, list[summary_trip]], region: str) -> dict[CABIN, list[TripOption]]:
    """
    Format top N round trips into RoundTripOptions.
    
    This function takes the filtered top N round trips and formats them into
    RoundTripOptions for further processing.

    Args:
        trips_by_cabin dict[CABIN, list[summary_trip]]: Filtered trips listed by cabin
    Returns:
        dict[CABIN, list[TripOption]]: Dictionary of formatted trips by cabin class
    Note: 
        overloaded method to handle both summary_round_trip_list_by_city_pairing_by_cabin
        and summary_trip_list_by_cabin types
    """
    if not trips_by_cabin or len(trips_by_cabin.items()) == 0:
        state.logger.warning("No trips found for formatting.")
        return {}

    tripOptions: dict[CABIN, list[TripOption]] = dict()
    for cabin, trips in trips_by_cabin.items():
        state.logger.info(f"Formatting top N round trips for cabin: {cabin.name}")
        if cabin not in tripOptions:
                tripOptions[cabin] = []
        for trip in trips:
            formatted_trip = format_availability_object(seats_aero_handler.fetch_availability(trip.ID), region)
            
            tripOptions[cabin].append(TripOption(
                release_date=f"{(date.today().strftime("%Y-%m-%d"))}",
                trip=formatted_trip
            ))
        
    state.logger.info("Top N round trips formatted successfully")
    state.update_flag('flightsFormatted')
    return tripOptions



def format_round_flights(trips_by_cabin: summary_round_trip_list_by_city_pairing_by_cabin, region: str) -> FlightOptions:
    """
    Format top N round trips into RoundTripOptions.
    This function takes the filtered top N round trips and formats them into
    RoundTripOptions for further processing.
    Args:
        topNRoundTrips (summary_round_trip_list_by_cabin): Filtered top N round
        trips
    Returns:
        dict[CABIN, list[RoundTripOptions]]: Dictionary of formatted round trips by cabin class
    Note:
        overloaded method to handle both summary_round_trip_list_by_city_pairing_by_cabin
        and summary_trip_list_by_cabin types
    """

    single_trips: list[TripOption] = []
    round_relation_trips: list[RoundTrip] = []
    round_options: list[Route] = [] 
    
    for cabin, city_pairings_round_trips in trips_by_cabin.items():
        state.logger.info(f"Formatting top N round trips for cabin: {cabin.name}")

        for city_pairing, round_trips in city_pairings_round_trips.items():
            optionID = str(hash(f"{city_pairing}-{cabin}-{date.today()}"))
            state.logger.info(f"Formatting {len(round_trips)} round trips for city pairing: {city_pairing}")
            formmatted_round_trips: list[RoundTrip] = []
            for round_trip in round_trips:
                if round_trip.outbound is None or round_trip.return_ is None:
                    state.logger.warning(f"Missing availability for round trip")
                    continue
                outbound = seats_aero_handler.fetch_availability(round_trip.outbound.ID)
                return_ = seats_aero_handler.fetch_availability(round_trip.return_.ID)
                state.logger.info(f"Fetched availability for outbound ID: {round_trip.outbound.ID} and return ID: {round_trip.return_.ID}")
                if not outbound or not return_:
                    continue

                formatted_outbound = TripOption(
                    release_date=f"{(date.today().strftime('%Y-%m-%d'))}",
                    trip=format_availability_object(outbound, region)
                )

                formatted_return = TripOption(
                    release_date=f"{(date.today().strftime('%Y-%m-%d'))}",
                    trip=format_availability_object(return_, region)
                )
                state.logger.info(f"Formatted availability for outbound ID: {round_trip.outbound.ID} and return ID: {round_trip.return_.ID}")

                if formatted_outbound is None or formatted_return is None:
                    state.logger.warning(f"Failed to format availability for round trip")
                    continue

                single_trips.append(formatted_outbound)
                single_trips.append(formatted_return)
                state.logger.info(f"Appended formatted single trips for outbound ID: {round_trip.outbound.ID} and return ID: {round_trip.return_.ID}")

                formmatted_round_trips.append(RoundTrip(
                    outbound=TripOption(
                        release_date=f"{(date.today().strftime('%Y-%m-%d'))}",
                        trip=formatted_outbound
                    ),
                    return_=TripOption(
                        release_date=f"{(date.today().strftime('%Y-%m-%d'))}",
                        trip=formatted_return
                    ),
                    OptionID=optionID
                ))
                state.logger.info(f"Appended formatted round trip for outbound ID: {round_trip.outbound.ID} and return ID: {round_trip.return_.ID}")

            if len(formmatted_round_trips) == 0:
                state.logger.warning(f"No valid round trips found for city pairing: {city_pairing}")
                continue

            round_relation_trips.extend(formmatted_round_trips)
            state.logger.info(f"Total formatted round trips so far: {len(round_relation_trips)}")

            round_options.append(Route(
                ID=optionID,
                roundTrips=formmatted_round_trips,
                origin_city=city_pairing[0],
                destination_city=city_pairing[1],
                origin_country= config.IATA_COUNTRY.get(formmatted_round_trips[0].outbound.origin_airport, "Unknown"),
                destination_country= config.IATA_COUNTRY.get(formmatted_round_trips[0].outbound.destination_airport, "Unknown"),
                release_date=f"{(date.today().strftime('%Y-%m-%d'))}",
                cabin=cabin.value
            ))
            state.logger.info(f"Created RoundTripOptions for city pairing: {city_pairing} with {len(formmatted_round_trips)} round trips")

    state.logger.info("Top N round trips formatted successfully")
    state.update_flag('flightsFormatted')

    state.logger.info("Top N round trips shuffled successfully")

    return FlightOptions(
        single_trips=single_trips,
        round_trips=round_relation_trips,
        round_options=round_options
    )

HEADERS = [
    "Outbound ID", "Return ID", "Origin Airport", "Destination Airport", 
    "Outbound Departure", "Outbound Arrival", "Return Departure", "Return Arrival",
    "Outbound Mileage Cost", "Outbound Taxes", "Outbound Normal Taxes",
    "Outbound Total Cost", "Outbound Normal Total Cost",
    "Return Mileage Cost", "Return Taxes", "Return Normal Taxes",
    "Return Total Cost", "Return Normal Total Cost",
    "Normal Selling Price", "Outbound Booking Links", "Return Booking Links"
    ]


def broadcast_single_flights(tripOptions: dict[CABIN, list[TripOption]], n: int):
    """
    Generate marketing content, PDFs, store data, and email reports for flight options.
    This function processes the formatted trip options to generate WhatsApp
    posts, travel images, PDFs, store data in Google Sheets, and email the reports.
    Args:
        dict[CABIN, list[TripOption]]: Formatted trip options by cabin class
    Returns:
        list[PDF_OBJ]: List of generated PDF objects
    Note:
        overloaded method to handle both summary_round_trip_list_by_city_pairing_by_cabin
        and summary_trip_list_by_cabin types
    """

    state.logger.info("Starting broadcast of flight options")
    
    rows = [option.to_row() for options in tripOptions.values() for option in options]
    sheets_handler.get_sheet(config.RESULT_SHEET_ID).get_worksheet('singles').add_rows(rows=rows)
        
    state.logger.info("Top N round trips written to Google Sheet successfully")
    state.update_flag('sentToGoogleSheets')

    pdfs = [generate_pdf_for_single_trips(option, option.release_date) for options in tripOptions.values() for option in options]

    #TODO: whatsapp_post no longer exists in TripOption,, figure out a work around. 
    email_self(
        subject=f"{date.today()} - {date.today() + timedelta(days=n - 1)} Top {n} Combos de Voos Single",
        body=f"\
                Attached are the top N combos of flights.\n \
                Whatsapp Posts:\n \
                {format_whatsapp_posts(opt.whatsapp_post for opts in tripOptions.values() for opt in opts)} \
                \n\nThis email was sent automatically by the flight alert system.",
        attachments=pdfs
    )
    state.update_flag('emailSent')

    clear_pdfs(*pdfs)

def broadcast_round_flights(options: FlightOptions, n: int) -> None:
    """
    Generate marketing content, PDFs, store data, and email reports for flight options.
    This function processes the formatted RoundTripOptions to generate WhatsApp
    posts, travel images, PDFs, store data in Google Sheets, and email the reports.
    Args:
        dict[CABIN, list[RoundTripOptions]]: Formatted round trip options by cabin class
    Returns:
        list[PDF_OBJ]: List of generated PDF objects
    Note:
        overloaded method to handle both summary_round_trip_list_by_city_pairing_by_cabin
        and summary_trip_list_by_cabin types
    """
    state.logger.info("Starting broadcast of flight options")

    singles_rows = [options.single_trips[i].to_row() for i in range(len(options.single_trips))]
    singles_rounds_relation_rows = [options.round_trips[i].to_row() for i in range(len(options.round_trips))]
    round_rows = [options.round_options[i].to_row() for i in range(len(options.round_options))]

    state.logger.info(f"FINISHED Prepared {len(singles_rows)} single trip rows for Google Sheet")
    state.logger.info(f"FINISHED Prepared {len(singles_rounds_relation_rows)} single-round relation rows for Google Sheet")
    state.logger.info(f"FINISHED Prepared {len(round_rows)} round trip rows for Google Sheet")
    
    sheets_handler.get_sheet(config.RESULT_SHEET_ID).get_worksheet('singles').add_rows(rows=singles_rows)  
    state.logger.info(f"Added {len(singles_rows)} single trip rows to Google Sheet")

    sheets_handler.get_sheet(config.RESULT_SHEET_ID).get_worksheet('singles_rounds_relational').add_rows(rows=singles_rounds_relation_rows)
    state.logger.info(f"Added {len(singles_rounds_relation_rows)} single-round relation rows to Google Sheet")

    sheets_handler.get_sheet(config.RESULT_SHEET_ID).get_worksheet('rounds').add_rows(rows=round_rows)
    state.logger.info(f"Added {len(round_rows)} round trip rows to Google Sheet")
    state.logger.info("Top N round trips written to Google Sheet successfully")
    state.update_flag('sentToGoogleSheets')
    '''
    pdfs = [generate_pdf_for_round_trips(option, option.release_date) for option in options]
    state.logger.info("PDFs generated successfully")
        
    email_self(
        subject=f"{date.today()} - {date.today() + timedelta(days=n - 1)} Top {n} Combos de Voos Round",
        body=f"\
                Attached are the top N combos of flights.\n \
                Whatsapp Posts:\n \
                {format_whatsapp_posts([option.whatsapp_post for option in options])} \
                \n\nThis email was sent automatically by the flight alert system.",
        attachments=pdfs
    )
    state.update_flag('emailSent')
    state.logger.info("Email sent successfully with attached PDFs")

    return pdfs
    '''

def clear_round(options: list[Route]) -> None:
    """
    Clean up temporary files used in the flight alert process.
    
    This function deletes any temporary images and PDF files generated
    during the flight alert pipeline to prevent server overload.
    
    Args:
        options (RoundTripOptions): List of RoundTripOptions containing image references
        pdfs (list[PDF_OBJ]): List of PDF objects with file paths to delete
        
    Returns:
        None
    """
    state.logger.info("Cleaning up temporary files")

    for option in options:
        for image in option.images:
            if image and image.filePath and os.path.exists(image.filePath):
                os.remove(image.filePath)

    return

def clear_single(options: list[TripOption]) -> None:
    """
    Clean up temporary files used in the flight alert process for single trip options.

    This function deletes any temporary images and PDF files generated
    during the flight alert pipeline to prevent server overload.

    Args:
        options (list[TripOption]): List of TripOption containing image references

    Returns:
        None
    """
    state.logger.info("Cleaning up temporary files for single trips")

    for option in options:
        for image in option.images:
            if image and image.filePath and os.path.exists(image.filePath):
                os.remove(image.filePath)

    return

def clear_pdfs(*pdfs: PDF_OBJ) -> None:
    """
    Clean up temporary PDF files used in the flight alert process.
    
    This function deletes any temporary PDF files generated during the
    flight alert pipeline to prevent server overload.
    
    Args:
        pdfs (PDF_OBJ): List of PDF objects with file paths to delete
        
    Returns:
        None
    """
    state.logger.info("Cleaning up temporary PDF files")
    
    for pdf in pdfs:
        if pdf and pdf.filePath and os.path.exists(pdf.filePath):
            os.remove(pdf.filePath)
    
    return

def format_whatsapp_posts(posts: list[str]) -> str:
        return "\n\n".join(posts)