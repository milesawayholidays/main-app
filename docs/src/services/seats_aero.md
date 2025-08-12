# [`seats_aero.py`](../../src/services/seats_aero.py)

This module provides comprehensive integration with the Seats.aero Partner API for flight data retrieval and processing. It handles authentication, cached searches, bulk availability queries, and individual trip lookups with robust error handling and caching capabilities.

---

## 📄 Overview

The `SeatsAeroHandler` class manages all interactions with the Seats.aero Partner API, providing access to comprehensive flight availability data from multiple airline sources. It follows the application's deferred initialization pattern and includes comprehensive logging and error handling.

Key capabilities:
- **Partner API Authentication**: Secure API key-based authentication with validation
- **Cached Search Queries**: Access to pre-indexed flight data for fast lookups
- **Bulk Availability Retrieval**: Large-scale data fetching across regions and sources
- **Individual Trip Details**: Detailed availability for specific flight combinations
- **Multi-Source Support**: Access to data from multiple airline partners
- **Error Resilience**: Comprehensive error handling with detailed logging

The service integrates with multiple API endpoints:
- **Cached Search**: Pre-indexed flight searches with filtering
- **Bulk Availability**: Region and source-based bulk data retrieval  
- **Trip Availability**: Individual flight combination details

---

## 📦 Classes

### `SeatsAeroHandler`

Main handler class for Seats.aero API operations and flight data management.

#### Initialization (`__init__(self)`)

Creates an uninitialized handler with API endpoints configured but no authentication.

- **Behavior:**
  - Sets up API endpoint URLs for all service types
  - Configures JSON accept headers for consistent response format
  - No authentication until `load()` is called

#### Methods

##### `load(self, api_key: str) -> None`

Initializes the handler with Partner API authentication and validates connectivity.

- **Parameters:**
  - `api_key` (`str`): Seats.aero Partner API key for authentication

- **Behavior:**
  - Adds Partner-Authorization header with provided API key
  - Performs authentication test with GRU→CDG sample query
  - Validates API response to ensure proper authentication
  - Logs successful initialization or authentication failures

- **Raises:**
  - `ValueError`: If API authentication fails or returns non-200 status

- **Note:**
  - Must be called before any other API methods
  - Performs immediate connectivity test for early error detection

##### `fetch_cached_search(self, origin_airport: str, destination_airport: str, start_date: str, end_date: str, take: int, order_by: str) -> list`

Retrieves cached flight search results with filtering and pagination.

- **Parameters:**
  - `origin_airport` (`str`): IATA code of origin airport (e.g., "GRU")
  - `destination_airport` (`str`): IATA code of destination airport (e.g., "CDG")
  - `start_date` (`str`): Search start date in YYYY-MM-DD format
  - `end_date` (`str`): Search end date in YYYY-MM-DD format
  - `take` (`int`): Maximum number of results to return
  - `order_by` (`str`): Sorting criteria for results

- **Returns:**
  - `list`: Cached search results, empty list if no results found

- **Behavior:**
  - Queries pre-indexed flight data for faster response times
  - Applies date range and airport filtering
  - Handles pagination with configurable result limits
  - Returns empty list on API errors (non-blocking)

- **Error Handling:**
  - Logs API errors but doesn't raise exceptions
  - Returns empty list for graceful degradation
  - Comprehensive error logging for debugging

##### `fetch_bulk_availability(self, source: str, cabins: list, start_date: str, end_date: str, origin_region: REGION, destination_region: REGION, take: int) -> dict`

Fetches large-scale availability data across regions and sources.

- **Parameters:**
  - `source` (`str`): Airline source identifier (from SOURCE enum values)
  - `cabins` (`list`): List of cabin class objects to include in search
  - `start_date` (`str`): Search start date (YYYY-MM-DD)
  - `end_date` (`str`): Search end date (YYYY-MM-DD)
  - `origin_region` (`REGION`): Geographic origin region enum
  - `destination_region` (`REGION`): Geographic destination region enum
  - `take` (`int`): Maximum number of results to retrieve

- **Returns:**
  - `dict`: Bulk availability data organized by routes and dates

- **Behavior:**
  - Constructs POST request with comprehensive search parameters
  - Handles cabin class enumeration and formatting
  - Processes large-scale availability datasets
  - Returns structured data for downstream processing

- **Raises:**
  - `ValueError`: If API request fails or returns error status
  - Comprehensive error logging with status codes and response details

- **Request Format:**
  ```json
  {
    "source": "airline_code",
    "cabins": ["Y", "W", "J"],
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "origin_region": "SA",
    "destination_region": "EU",
    "take": 1000
  }
  ```

##### `fetch_availability(self, trip_id: str) -> dict`

Retrieves detailed availability information for a specific trip.

- **Parameters:**
  - `trip_id` (`str`): Unique identifier for the trip/flight combination

- **Returns:**
  - `dict`: Detailed trip availability data including pricing, schedules, and booking information

- **Behavior:**
  - Queries specific trip endpoint with trip identifier
  - Returns comprehensive trip details for booking processing
  - Includes pricing, schedule, and availability information

- **Raises:**
  - `ValueError`: If trip ID is invalid or API request fails
  - Detailed error logging with response information

---

## 🏗️ Singleton Pattern

The module creates a singleton instance for application-wide use:

```python
handler = SeatsAeroHandler()
```

This instance should be loaded once during application startup using `handler.load(api_key)`.

---

## 🧠 Error Handling

- **Authentication Validation**: Tests API connectivity during initialization with sample query
- **API Status Monitoring**: Checks HTTP status codes and logs detailed error information
- **Graceful Degradation**: Cached search returns empty lists instead of raising exceptions
- **Comprehensive Logging**: All API interactions logged with status codes and response details
- **Error Propagation**: Critical errors (bulk availability, trip details) raise exceptions with context

---

## 💡 Usage Examples

### Basic Handler Initialization

```python
from services.seats_aero import handler as seats_handler

# Initialize the handler (typically done during app startup)
seats_handler.load(api_key="your_seats_aero_partner_api_key")
```

### Cached Search Queries

```python
# Search for cached flight data
results = seats_handler.fetch_cached_search(
    origin_airport="GRU",
    destination_airport="CDG", 
    start_date="2025-08-01",
    end_date="2025-08-31",
    take=50,
    order_by="price_asc"
)

print(f"Found {len(results)} cached results")
```

### Bulk Availability Retrieval

```python
from data_types.enums import REGION, SOURCE, CABIN

# Fetch bulk availability data
bulk_data = seats_handler.fetch_bulk_availability(
    source=SOURCE.AZUL.value,
    cabins=[CABIN.Y, CABIN.W],
    start_date="2025-08-01", 
    end_date="2025-08-31",
    origin_region=REGION.SA,
    destination_region=REGION.EU,
    take=1000
)

print(f"Retrieved bulk data: {len(bulk_data)} routes")
```

### Individual Trip Details

```python
# Get detailed trip information
trip_details = seats_handler.fetch_availability("trip_12345_abcdef")

print(f"Trip price: {trip_details.get('price')}")
print(f"Available seats: {trip_details.get('available_seats')}")
```

### Integration with Flight Processing Pipeline

```python
# Typical usage in alerts_runner.py
def fetch_flight_data_for_region(origin_region, dest_region):
    """Fetch flight data for processing pipeline"""
    all_data = {}
    
    # Fetch from each configured source
    for source in [SOURCE.AZUL, SOURCE.GOL, SOURCE.LATAM]:
        try:
            source_data = seats_handler.fetch_bulk_availability(
                source=source.value,
                cabins=config.CABINS,
                start_date=config.START_DATE,
                end_date=config.END_DATE,
                origin_region=origin_region,
                destination_region=dest_region,
                take=config.TAKE
            )
            all_data[source.value] = source_data
            state.logger.info(f"Fetched data from {source.value}")
            
        except ValueError as e:
            state.logger.error(f"Failed to fetch from {source.value}: {e}")
            continue
            
    return all_data
```

---

## 🌐 API Integration Details

**Seats.aero Partner API Endpoints:**

1. **Cached Search**: `https://seats.aero/partnerapi/search`
   - Method: GET
   - Purpose: Pre-indexed flight searches
   - Response: List of cached flight options

2. **Bulk Availability**: `https://seats.aero/partnerapi/availability`
   - Method: POST
   - Purpose: Large-scale availability queries
   - Response: Comprehensive availability datasets

3. **Trip Details**: `https://seats.aero/partnerapi/trips/{trip_id}`
   - Method: GET
   - Purpose: Detailed trip information
   - Response: Complete trip details with pricing

**Authentication:**
- Header: `Partner-Authorization: {api_key}`
- Content-Type: `application/json`
- Accept: `application/json`

**Rate Limiting:**
- Enforced by Seats.aero API
- No client-side throttling implemented
- Error responses include rate limit information

---

## 🔐 Authentication

**Partner API Requirements:**
- Valid Seats.aero Partner API account
- Active API key with appropriate permissions
- Access to partner-level data feeds

**Authentication Process:**
1. API key provided during `load()` method
2. Authentication header added to all requests
3. Immediate connectivity test with sample query
4. Validation of response format and access level

---

## 🔗 Dependencies

- [`requests`](https://docs.python-requests.org/): HTTP client for API communication
- [`config`](../config.md): Configuration management (imported but not used for API key)
- [`global_state`](../global_state.md): Centralized logging and state management
- [`REGION, SOURCE`](../data_types/enums.md): Enum types for API parameter validation

---

## ⚠️ Notes

- **Deferred Loading**: Handler requires explicit `load()` call with API key
- **Partner API Only**: Requires partner-level access to Seats.aero services
- **No Client-Side Caching**: All data is fetched fresh from API (server-side caching only)
- **Error Recovery**: Cached searches fail gracefully, bulk operations raise exceptions
- **Regional Filtering**: Supports geographic region filtering for targeted searches
- **Multi-Source Support**: Can fetch data from multiple airline sources simultaneously
- **JSON Only**: All API interactions use JSON format for requests and responses
