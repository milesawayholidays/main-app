# [`flight_filter.py`](../../src/logic/filter.py)

This module defines the `Flight_Filter` class responsible for processing flight availability data to generate, group, filter, and rank round-trip options based on cabin class and total cost.

---

## 📄 Overview

The `Flight_Filter` class filters and ranks round-trip flight data fetched from multiple sources, aiming to return the cheapest city pairings per cabin. It supports:
- Extracting valid round trips from raw bulk availability.
- Grouping round trips by origin/destination city and cabin.
- Selecting the top-N cheapest city pairings.
- Merging and comparing multiple data sources.

---

## 📦 Class

### `Flight_Filter`

Provides high-level filtering and cost-optimization logic for flight availability data.

#### Initialization (`__init__`)
- Initializes a basic instance. No parameters required.

#### Methods

##### `getTopNTripsFromMultipleSources(bulk_availability_by_source: dict[SOURCE, dict]) -> summary_round_trip_list_by_cabin`

Processes bulk availability from multiple sources and returns the top-N cheapest city pairings for each cabin.

- **Raises:** `ValueError` if no data is provided or no valid trips are found.

##### `getCheapestNTrips(bulk_availability: dict, source: SOURCE) -> summary_round_trip_list_by_cabin`

Filters a single source’s availability to return the cheapest city pairings by cabin.

- **Raises:** `ValueError` if data is missing or processing fails.

##### `mash_sources_together(left: summary_round_trip_list_by_cabin, right: summary_round_trip_list_by_cabin) -> summary_round_trip_list_by_cabin`

Combines and merges round trip data from two sources, aligning city pairings.

- **Raises:** `ValueError` if input dictionaries are empty or incompatible.

---

## 🔎 Internal Methods

### `__processBulkAvailabilityForRoundTrips(...) -> summary_round_trip_list_by_cabin`

Processes raw availability into structured round-trip groupings by city and cabin.

- Normalizes and filters data.
- Maps airport codes to city names.
- Pairs outbound and return flights within date range.
- Calculates system-standardized total cost (miles + taxes).

### `__calc_cost(df: pd.DataFrame, cabin: CABIN, mileage_value: int) -> pd.Series`

Computes the total cost of a flight using mileage valuation and standardized taxes.

### `__find_cheapest_cities_by_cabin(...) -> summary_round_trip_list_by_cabin`

Sorts round trip groupings by total cost and selects the top-N cheapest city pairings for each cabin.

- Returns a structured dictionary of filtered `summary_round_trip` lists.

---

## 🧠 Error Handling

- Logs warnings and raises exceptions when input is invalid or data is missing.
- Filters out insufficient or malformed trip data (e.g., missing city, not enough trips).
- Defensive against empty datasets or invalid city mappings.

---

## 🔐 Configuration Requirements

- `config.CABINS`: List of cabin classes to include.
- `config.MIN_RETURN_DAYS`, `config.MAX_RETURN_DAYS`: Valid date range for return flights.
- `config.IATA_CITY`: Airport-to-city mapping.
- `config.N`: Number of top cities to retain.
  
---

## 🔗 Dependencies

- [`pandas`](https://pandas.pydata.org/): Used for data processing and filtering.
- [`config`](../config.md): Configuration constants and parameters.
- [`global_state`](../global_state.md): Logging system.
- [`currencies.mileage`](../currencies/mileage.md): Provides mileage valuation.
- [`currencies.cash`](../currencies/cash.md): Currency normalization utilities.
- [`data_types.enums`](../data_types/enums.md): Contains `CABIN` and `SOURCE` enums.
- [`data_types.summary_objs`](../data_types/summary_objs.md): Typed containers for round trip summaries.

---

