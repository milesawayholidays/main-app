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

import requests

from src.global_state import state

from src.data_types.enums import REGION, SOURCE, CABIN
from src.data_types.Flight import Availability

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

    def fetch_bulk_availability(
        self,
        source: str,
        origin_region: str,
        destination_region: str,
        start_date: str = None,
        end_date: str = None,
        deepness: int = 1,
        cabin: str = None
    ) -> list[Availability]:

        # Safety clamp: deepness controls pagination depth (pages) per region-pair query.
        try:
            deepness = int(deepness)
        except Exception:
            deepness = 1
        deepness = max(1, min(deepness, 3))

        state.logger.info(
            f"Fetching bulk availability for "
            f"{source}/{origin_region} → {destination_region}, deepness={deepness}"
        )

        if not all([source, origin_region, destination_region]):
            return []

        # Build base params
        params = {
            "source": source,
            "origin_region": origin_region,
            "destination_region": destination_region,
            "cabin": cabin if cabin else None,
            "take": 1000,
            "include_filtered": "true"
        }

        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        all_items_raw: list[dict] = []
        cursor = None

        for _ in range(deepness):
            response = requests.get(self.bulk_availability_url, headers=self.headers, params=params)
            if response.status_code != 200:
                state.logger.error(f"Bulk availability failed: {response.status_code} - {response.text}")
                break

            data_json = response.json()
            page_items = data_json.get("data", [])

            all_items_raw.extend(page_items)

            # Pagination
            hasMore = data_json.get("hasMore", False)
            cursor = data_json.get("cursor")
            if not (hasMore and cursor):
                break

            # Update params for next page
            params["cursor"] = cursor
            params["skip"] = len(all_items_raw)

        if not all_items_raw:
            return []

        # Deduplication AFTER all pages
        unique_items = {item["ID"]: item for item in all_items_raw if item.get("ID")}

        # Build Availability objects only once
        results: list[Availability] = []
        for item in unique_items.values():
            route = item.get("Route", {})
            results.append(Availability(
                ID=item.get("ID"),
                origin_airport=route.get("OriginAirport"),
                destination_airport=route.get("DestinationAirport"),
                source=source,
                date=item.get("Date"),
                y_available=item.get("YAvailable"),
                w_available=item.get("WAvailable"),
                j_available=item.get("JAvailable"),
                f_available=item.get("FAvailable"),
                y_mileage=item.get("YMileageCostRaw"),
                w_mileage=item.get("WMileageCostRaw"),
                j_mileage=item.get("JMileageCostRaw"),
                f_mileage=item.get("FMileageCostRaw"),
                taxes_currency=item.get("TaxesCurrency"),
                y_taxes=item.get("YTotalTaxesRaw"),
                w_taxes=item.get("WTotalTaxesRaw"),
                j_taxes=item.get("JTotalTaxesRaw"),
                f_taxes=item.get("FTotalTaxesRaw"),
                y_remaining_seats=item.get("YRemainingSeatsRaw"),
                w_remaining_seats=item.get("WRemainingSeatsRaw"),
                j_remaining_seats=item.get("JRemainingSeatsRaw"),
                f_remaining_seats=item.get("FRemainingSeatsRaw"),
                created_at=item.get("CreatedAt"),
                updated_at=item.get("UpdatedAt"),
                provider="seats.aero"
            ))

        return results


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