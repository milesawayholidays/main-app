"""
Seats.aero API integration service for flight data retrieval and processing.

This module handles all interactions with the Seats.aero API, which provides
comprehensive flight availability data from multiple airline sources. It manages
API authentication, request formatting, response processing, and error handling
for reliable flight data retrieval.

Key Features:
- Partner API authentication and authorization
- Cached search queries for specific routes
- Bulk availability data retrieval across regions
- Individual trip availability lookup
- Comprehensive error handling and logging
- Support for multiple airline sources and cabin classes

The module integrates with:
- Seats.aero Partner API endpoints
- Configuration management for API credentials
- Global state for logging and error tracking
- Enum types for regions, sources, and cabin classes

API Endpoints:
- Cached Search: Query pre-indexed flight data
- Bulk Availability: Retrieve large datasets by region/source
- Trip Availability: Get detailed information for specific trips
"""

from time import sleep
import requests

from global_state import state

from data_types.enums import REGION, SOURCE, CABIN


class SeatsAeroHandler:
    """
    Handler class for Seats.aero API operations and flight data management.
    
    This class manages all interactions with the Seats.aero Partner API,
    providing methods to fetch flight availability data, cached searches,
    and bulk data retrieval. It handles API authentication, request formatting,
    and response processing for reliable flight data access.
    
    Attributes:
        headers (dict): API authentication headers with partner authorization
        cached_search_url (str): URL endpoint for cached search queries
        bulk_availability_url (str): URL endpoint for bulk availability data
        availability_url (str): URL endpoint for individual trip availability
        
    Note:
        - Requires valid Seats.aero Partner API key in configuration
        - All methods include comprehensive error handling and logging
        - Designed for high-volume flight data processing
    """
    
    def __init__(self):
        """
        Initialize the Seats.aero API handler with authentication and endpoints.
        
        Sets up API authentication headers using the partner API key from
        configuration and initializes all required API endpoint URLs.
        
        Note:
            - Sets JSON accept header for consistent response format
        """
        self.headers = {
            "accept": "application/json",
        }
        self.cached_search_url = "https://seats.aero/partnerapi/search?"
        self.bulk_availability_url = "https://seats.aero/partnerapi/availability"
        self.availability_url = "https://seats.aero/partnerapi/trips/"
    
    def load(self, api_key):
        """
        Load Seats.aero API key for authentication.
        
        This method initializes the API handler with the provided partner API key,
        allowing subsequent calls to the Seats.aero API for flight data retrieval.
        
        Args:
            api_key (str): The Seats.aero Partner API key for authentication
            
        Note:
            - Should be called before any API interaction methods
        """
        self.headers["Partner-Authorization"] = api_key

        params = {
            "origin_airport": "GRU",
            "destination_airport": "CDG",
            "take": 1
        }
        response = requests.get(self.cached_search_url, headers=self.headers, params=params)
        if response.status_code != 200:
            state.logger.error(f"Failed to authenticate with Seats.aero: {response.status_code} - {response.text}")
            raise ValueError(f"Failed to authenticate with Seats.aero: {response.status_code} - {response.text}")
        
        state.logger.info("Seats.aero API handler initialized successfully with provided API key.")
        state.update_flag('seatsAeroHandlerInitialized')

    def fetch_cached_search(self, origin_airport, destination_airport, start_date, end_date, take, order_by):
        """
        Fetch cached flight search results for a specific route and date range.
        
        Queries the Seats.aero cached search endpoint to retrieve pre-indexed
        flight data for a specific origin-destination pair within a date range.
        This is typically faster than real-time searches but may have slightly
        less current data.
        
        Args:
            origin_airport (str): IATA code for origin airport (e.g., 'GRU')
            destination_airport (str): IATA code for destination airport (e.g., 'CDG')
            start_date (str): Search start date in YYYY-MM-DD format
            end_date (str): Search end date in YYYY-MM-DD format
            take (int): Maximum number of results to return
            order_by (str): Sorting criteria for results (e.g., 'price', 'date')
            
        Returns:
            list: List of flight availability objects from the API response data
            
        Raises:
            ValueError: If any required parameter is missing or if the API request fails
            
        Note:
            - Uses cached data for faster response times
            - Excludes filtered results by default
            - Returns empty list if no data found
            - Logs all errors for debugging purposes
        """
        if not all([origin_airport, destination_airport, start_date, end_date]):
            raise ValueError("All parameters (origin_airport, destination_airport, start_date, end_date) must be provided.")
        params = {
            "origin": origin_airport,
            "destination": destination_airport,
            "start_date": start_date,
            "end_date": end_date,
            "take": take,
            "order_by": order_by,
            "include_filtered": "false"
        }
        response = requests.get(self.cached_search_url, headers=self.headers, params=params)
        json_response = response.json()
        if response.status_code == 200 and json_response:
            return json_response.get("data", [])
        else:
            state.logger.error(f"Failed to fetch cached search: {response.status_code} - {response.text}")
            raise ValueError(f"Failed to fetch cached search: {response.status_code} - {response.text}")

    def fetch_bulk_availability(self, source: SOURCE, 
                                origin_region: REGION, 
                                destination_region: REGION, 
                                start_date: str = None, 
                                end_date: str = None, 
                                deepness: int = 1) -> list:
        """
        Fetch bulk flight availability data across regions and sources.
        
        Retrieves large volumes of flight availability data filtered by airline
        source, cabin classes, date range, and geographical regions. This method
        is optimized for processing multiple flights across broad criteria.
        
        Args:
            source (SOURCE): Airline source enum (e.g., SOURCE.SMILES, SOURCE.AZUL)
            cabins (list): List of cabin class codes (e.g., ['Y', 'W'])
            start_date (str): Search start date in YYYY-MM-DD format (optional)
            end_date (str): Search end date in YYYY-MM-DD format (optional)
            origin_region (REGION): Origin region enum (e.g., REGION.SOUTH_AMERICA)
            destination_region (REGION): Destination region enum (e.g., REGION.EUROPE)
            deepness (int): Pagination depth for results (default: 1)
            
        Returns:
            list: list containing bulk availability data from API response,
                or empty list if request fails or parameters are invalid
                
        Note:
            - Returns empty list instead of raising exceptions for missing params
            - Logs request parameters for debugging
            - Handles API errors gracefully with empty dict return
            - Designed for high-volume data processing
            - Uses enum values for consistent parameter formatting
        """
        state.logger.info(f"Fetching bulk availability for source: {source.value}, "
                          f"origin_region: {origin_region.value}, destination_region: {destination_region.value}, "
                          f"start_date: {start_date}, end_date: {end_date}, deepness: {deepness}")
        if not all([source, origin_region, destination_region]):
            return []  # Return empty list if any parameter is missing
        params = {
            "source": source.value,
            "origin_region": origin_region.value,
            "destination_region": destination_region.value,
            "take": 1000
        }

        if start_date is not None and start_date != "":
            params["start_date"] = start_date
        if end_date is not None and end_date != "":
            params["end_date"] = end_date       

            
        state.logger.info(f"Fetching bulk availability with params: {params}")

        # Initialize response variables
        response = None
        responseJson = None
        all_data = []
        seen_ids = set()  # Track IDs to avoid duplicates

        for i in range(1, deepness + 1):
            # Call the api
            response = requests.get(self.bulk_availability_url, headers=self.headers, params=params)

            if response.status_code == 200:
                responseJson = response.json()
                current_data = responseJson.get("data", [])
                
                # Deduplicate by ID as recommended by API documentation
                new_data = []
                for item in current_data:
                    item_id = item.get("ID")
                    if item_id and item_id not in seen_ids:
                        seen_ids.add(item_id)
                        new_data.append(item)
                
                all_data.extend(new_data)
                
                state.logger.info(f"Bulk availability fetched successfully for source: {source.value}. Found {len(current_data)} results, {len(new_data)} unique.")

                # Check if there are more results to fetch
                hasMore = responseJson.get("hasMore", False)
                cursor = responseJson.get("cursor", None)
                
                if hasMore and cursor:
                    # Update cursor for next request
                    params["cursor"] = cursor
                    # Update skip to the total number of results we've processed
                    params["skip"] = len(all_data)
                    state.logger.info(f"Continuing to fetch more results with cursor: {cursor} and skip: {params['skip']}")
                else:
                    # No more data to fetch
                    break
            else:
                state.logger.error(f"Failed to fetch bulk availability: {response.status_code} - {response.text}")
                break

        
        if response and response.status_code == 200 and all_data:
            state.logger.info(f"Bulk availability fetched successfully with {len(all_data)} unique results.")
            return all_data
        # If no data was fetched, log the error and return empty list
        else:
            state.logger.error(f"Failed to fetch bulk availability: {response.status_code} - {response.text}")
            return []  # Return empty list if the request fails

    def fetch_availability(self, trip_id) -> dict:
        """
        Fetch detailed availability information for a specific trip.
        
        Retrieves comprehensive flight details for a specific trip ID,
        including segments, pricing, availability, and booking information.
        This method is used to get complete trip details after initial
        search or bulk availability queries.
        
        Args:
            trip_id (str): Unique identifier for the specific trip
            
        Returns:
            dict: Complete trip availability data including segments,
                pricing, and booking details
            
        Note:
            - Provides detailed trip information beyond basic availability
            - Used for final trip processing and booking link generation
            - Includes all flight segments and connection details
            - Returns raw JSON response for maximum flexibility
            - Logs errors with full response details for debugging
            - Handles API errors gracefully by returning None
        """
        
        res = requests.get(f"{self.availability_url}{trip_id}", headers=self.headers)
        
        if res.status_code != 200:
            state.logger.error(f"Failed to fetch outbound availability: {res.status_code} - {res.text}")
            return None

        return res.json() 


# Create a singleton instance for use throughout the application
seats_aero_handler = SeatsAeroHandler()