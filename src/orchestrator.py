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

from datetime import date
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.global_state import state
from src.config import config
from src.helpers import load_raw_results_from_file, save_raw_results_to_file

from src.logic.flight_search_processor import flight_processor


"""
THIS SHALL REMAIN HERE AS A MONUMENT TO HUMAN ERROR,
A TESTAMENT TO HUBRIS, AND A WARNING TO FUTURE GENERATIONS.

Behold: the relics of a time when data structures were forged
in nested dicts, when O(n³) loops roamed free, and when
performance was but a distant dream.


# Type aliases for cleaner code <----- THIS IDIOT WROTE THIS LMAO
summary_round_trip_list_by_city_pairing_by_cabin = dict[CABIN, dict[tuple[str, str], list[summary_round_trip]]]
summary_trip_list_by_cabin = dict[CABIN, list[summary_trip]]
"""

from src.logic.trip_builder import RoundTrip, format_availability_object, TripOption
from src.logic.trip_builder import Route

from src.services.seats_aero import seats_aero_handler
from src.services.google_sheets import handler as sheets_handler  

from src.currencies.cash import handler as cash_handler
from src.currencies.mileage import handler as mileage_handler

from src.data_types.enums import SOURCE, REGION
from src.data_types.Flight import FlightFilterResult, FlightQuery, RawFlightResult, FilteredFlightList, FlightOptions

MAX_N = 8
MAX_DEEPNESS = 3


def _clamp_int(value: int, *, min_value: int, max_value: int) -> int:
    try:
        value_int = int(value)
    except Exception:
        value_int = min_value
    return max(min_value, min(value_int, max_value))

def find_trips(
        query: FlightQuery = None, 
        oneway: bool = False,
        start_date: str = None,
        end_date: str = None,
        n: int = 1,
        deepness: int = 1,
    ) -> dict:
    """
    Fetch and process flight data based on specified filters.
    This function orchestrates the retrieval and processing of flight data
    based on the provided filter criteria. It fetches flight availability from multiple
    sources, filters for the best round trips, formats the results, and broadcasts
    the flight options.
    Args:
        filter (FlightFilter, optional): Filter criteria for flight search
        oneway (bool, optional): Whether to search for one-way trips only
        start_date (str, optional): Search start date in YYYY-MM-DD format
        end_date (str, optional): Search end date in YYYY-MM-DD format
        n (int, optional): Number of top results to return
        deepness (int, optional): Depth of search for availability data
    Returns:
        dict: A dictionary containing the status of the operation and any relevant messages.
    """

    # Initialization is handled by the API layer (per-request) and by the CLI entrypoint.

    if query is None:
        query = FlightQuery()

    n = _clamp_int(n, min_value=1, max_value=MAX_N)
    deepness = _clamp_int(deepness, min_value=1, max_value=MAX_DEEPNESS)

    state.logger.info("Starting flight alert pipeline for round trips with filter")

    origin_regions = query.get('origin_regions', REGION.get_region_values())
    destination_regions = query.get('destination_regions', REGION.get_region_values())
    sources = query.get('sources', SOURCE.get_source_values())

    tasks = []
    for source in sources:
        for origin in origin_regions:
            for destination in destination_regions:
                tasks.append((
                    source,
                    origin,
                    destination,
                    start_date,
                    end_date,
                    deepness
                ))

    search_result = []

    MAX_WORKERS = min(20, len(tasks))

    search_result: list[RawFlightResult] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(_fetch_single_combo, t): t for t in tasks}

        for future in as_completed(futures):
            source, origin, destination, availability_list = future.result()

            if not availability_list:
                continue

            state.logger.info(
                f"[PARALLEL] Fetched {len(availability_list)} for "
                f"{source} / {origin} → {destination}"
            )

            search_result.extend(
                RawFlightResult.from_list(
                    origin_region=origin,
                    destination_region=destination,
                    availability_list=availability_list
                )
            )
                
    
    if len(search_result) == 0:
        state.logger.error("No data found in bulk availability search for any source.")
        return {"status": 204, "data": {"error": "No data found in bulk availability search for any source."}}
    
    state.logger.info(f"Total search results after bulk availability fetch: {len(search_result)}")
    
    state.update_flag('flightsRetrieved')
    state.logger.info("Flights retrieved successfully")

    filter_result: FilteredFlightList
    if oneway:
        filter_result = flight_processor.find_top_oneway_trips(
            flight_search_results=search_result,
            n=n,
            query=query
        )
    else:
        filter_result = flight_processor.find_top_round_trips(
            search_results=search_result,
            n=n,
            query=query
        )

    if not filter_result or len(filter_result) == 0:
        state.logger.error("No data found in top N flights.")
        return {"status": 204, "data": {"error": "No valid round trips found"}}
    
    flight_options = format_flights(filter_result)
    if not flight_options:
        return {"status": 204, "data": {"error": "No valid flight options found"}}
    
    #broadcast_flights(flight_options)

    return {"status": 200, "data": flight_options}



##########################################################
##########################################################
####################### TESTING ##########################
##########################################################
##########################################################


def generate_raw_cache(
    query: FlightQuery = None,
    start_date: str = None,
    end_date: str = None,
    deepness: int = 1,
    cache_path: str = "cached_raw_results.json"
):
    """
    Fetches all availability data (parallelized), builds RawFlightResult objects,
    and saves them to disk for later processing without API usage.
    """

    # Initialization is handled by the API layer (per-request) and by the CLI entrypoint.

    if query is None:
        query = FlightQuery()

    deepness = _clamp_int(deepness, min_value=1, max_value=MAX_DEEPNESS)

    state.logger.info("Starting cache generation run (no filtering, no processing)")

    # Default values if not provided
    origin_regions = query.get('origin_regions', REGION.get_region_values())
    destination_regions = query.get('destination_regions', REGION.get_region_values())
    sources = query.get('sources', SOURCE.get_source_values())

    # Build all combinations
    tasks = []
    for source in sources:
        for origin in origin_regions:
            for destination in destination_regions:
                tasks.append((source, origin, destination, start_date, end_date, deepness))

    state.logger.info(f"Total fetch tasks: {len(tasks)}")

    MAX_WORKERS = min(20, len(tasks))

    all_raw_results: list[RawFlightResult] = []

    # --------------- PARALLEL FETCHING ----------------
    state.logger.info("Starting parallel availability fetch...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(_fetch_single_combo, t): t for t in tasks}

        for future in as_completed(futures):
            try:
                source, origin, destination, availability_list = future.result()

                if not availability_list:
                    continue

                state.logger.info(
                    f"[CACHE] Fetched {len(availability_list)} for "
                    f"{source} / {origin} → {destination}"
                )

                raw_items = RawFlightResult.from_list(
                    origin_region=origin,
                    destination_region=destination,
                    availability_list=availability_list
                )

                all_raw_results.extend(raw_items)

            except Exception as e:
                state.logger.error(f"Error during parallel fetch: {e}")

    # --------------- SAVE TO DISK ----------------
    if not all_raw_results:
        state.logger.error("No results fetched. Cache file will NOT be generated.")
        return {"status": 204, "data": "No results to cache"}

    state.logger.info(f"Fetched total of {len(all_raw_results)} RawFlightResult items")
    save_raw_results_to_file(all_raw_results, cache_path)

    state.logger.info(f"Cache saved successfully → {cache_path}")
    return {"status": 200, "data": {"count": len(all_raw_results), "file": cache_path}}



def find_trips_from_cache( query: FlightQuery, filepath: str = "cached_raw_results.json", oneway=True, n=1):
    n = _clamp_int(n, min_value=1, max_value=MAX_N)
    raw_results = load_raw_results_from_file(filepath)

    filter_result: FilteredFlightList
    if oneway:
        filter_result = flight_processor.find_top_oneway_trips(
            flight_search_results=raw_results,
            n=n,
            query=query
        )
    else:
        filter_result = flight_processor.find_top_round_trips(
            search_results=raw_results,
            n=n,
            query=query
        )

    # pipeline continues unchanged
    #print all trips as json
    trips_json = [trip.__dict__ for trip in filter_result]

    # OPTIONAL: pretty-print in logs
    #state.logger.info(json.dumps(trips_json, indent=2, ensure_ascii=False))

    # OPTIONAL: save to file
    with open("debug_trips.json", "w", encoding="utf-8") as f:
        json.dump(trips_json, f, indent=2, ensure_ascii=False)
       
    flight_options = format_flights(filter_result)
    #broadcast_flights(flight_options)

    return {"status": 200, "data": flight_options}



###############
###############
### HELPERS ###
###############
###############



def format_flights(trips: FilteredFlightList) -> FlightOptions:

    def _process_trip(trip: FlightFilterResult):
        """
        Process a single trip: fetch outbound+return availability,
        create TripOptions and RoundTrip, and return structured result.
        Returns None for skipped trips.
        """
        try:
            out = seats_aero_handler.fetch_availability(trip.outbound_id)
            if not out:
                return None

            ret = (seats_aero_handler.fetch_availability(trip.return_id)
                   if trip.return_id else None)
            if trip.return_id and not ret:
                return None

            formatted_out = TripOption(
                release_date=date.today().strftime('%Y-%m-%d'),
                trip=format_availability_object(out, trip.origin_region)
            )
            if not formatted_out:
                return None

            formatted_ret = (TripOption(
                release_date=date.today().strftime('%Y-%m-%d'),
                trip=format_availability_object(ret, trip.destination_region)
            ) if ret else None)

            if trip.return_id and not formatted_ret:
                return None

            city_pairing = (trip.origin_city, trip.destination_city)

            return {
                "formatted_out": formatted_out,
                "formatted_ret": formatted_ret,
                "city_pairing": city_pairing
            }

        except Exception as e:
            state.logger.error(f"Error processing trip {trip}: {e}")
            return None

    # -----------------------------
    # PARALLEL LOOP
    # -----------------------------
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(_process_trip, trip) for trip in trips]

        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    # ---------------------------------------------
    # BUILD FINAL STRUCTURES (single-threaded)
    # ---------------------------------------------
    single_trips: list[TripOption] = []
    round_relation_trips: list[RoundTrip] = []
    round_options: dict[tuple[str, str], list[RoundTrip]] = {}

    for r in results:
        formatted_out = r["formatted_out"]
        formatted_ret = r["formatted_ret"]
        city_pairing = r["city_pairing"]

        # Add single trips
        single_trips.append(formatted_out)
        if formatted_ret:
            single_trips.append(formatted_ret)
        else:
            continue

        # Round-trip pairing logic
        if city_pairing not in round_options:
            round_options[city_pairing] = []
            optionID = str(hash(f"{city_pairing}-{date.today()}"))
        else:
            optionID = round_options[city_pairing][0].option_id

        round_trip = RoundTrip(
            outbound=formatted_out,
            return_=formatted_ret,
            OptionID=optionID
        )

        round_relation_trips.append(round_trip)
        round_options[city_pairing].append(round_trip)

    # Build Route list
    round_options_list = [
        Route(
            ID=round_trips[0].option_id,
            roundTrips=round_trips,
            origin_city=pair[0],
            destination_city=pair[1],
            origin_country=round_trips[0].outbound.origin_country,
            destination_country=round_trips[0].outbound.destination_country,
            release_date=date.today().strftime('%Y-%m-%d'),
            cabin=round_trips[0].outbound.cabin
        )
        for pair, round_trips in round_options.items()
    ]

    state.logger.info(f"Formatted {len(single_trips)} single trips")
    state.update_flag('flightsFormatted')

    return FlightOptions(
        single_trips=single_trips,
        round_trips=round_relation_trips,
        round_options=round_options_list
    )

def broadcast_flights(options: FlightOptions) -> None:
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
    
    if len(singles_rows) > 0:
        sheets_handler.get_sheet(config.RESULT_SHEET_ID).get_worksheet('singles').add_rows(rows=singles_rows)  
        state.logger.info(f"Added {len(singles_rows)} single trip rows to Google Sheet")
    
    if len(singles_rounds_relation_rows) > 0:
        sheets_handler.get_sheet(config.RESULT_SHEET_ID).get_worksheet('singles_rounds_relational').add_rows(rows=singles_rounds_relation_rows)
        state.logger.info(f"Added {len(singles_rounds_relation_rows)} single-round relation rows to Google Sheet")

    if len(round_rows) > 0:
        sheets_handler.get_sheet(config.RESULT_SHEET_ID).get_worksheet('rounds').add_rows(rows=round_rows)
        state.logger.info(f"Added {len(round_rows)} round trip rows to Google Sheet")

    state.logger.info("Top N round trips written to Google Sheet successfully")
    state.update_flag('sentToGoogleSheets')


def _fetch_single_combo(args):
    source, region, other_region, start, end, deep = args

    availability = seats_aero_handler.fetch_bulk_availability(
        source=source,
        start_date=start,
        end_date=end,
        origin_region=region,
        destination_region=other_region,
        deepness=deep
    )
    return (source, region, other_region, availability)

import json

def save_raw_results_to_file(raw_results: list[RawFlightResult], filepath: str):
    serialised = [r.to_dict() for r in raw_results]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(serialised, f, ensure_ascii=False, indent=2)

    state.logger.info(f"Saved {len(raw_results)} RawFlightResult items to {filepath}")
