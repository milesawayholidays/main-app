# [`summary_objs.py`](../../src/data_types/summary_objs.py)

This module defines lightweight summary representations of trips and round trips. These objects are used when full flight data isn't required—e.g., for sorting, filtering, or presenting top-N flight options.

## Classes

### `summary_trip`
Represents a simplified version of a single trip (either outbound or return).

#### Fields:
- `ID: str`  
  A unique identifier for the trip, typically used to fetch full availability details.
  
- `city: str`  
  The name of the city of departure or arrival.

- `totalCost: int`  
  The total cost of the trip in the system's base currency (e.g., BRL or USD).

---

### `summary_round_trip`
Represents a simplified round-trip flight, combining an outbound and a return `summary_trip`.

#### Fields:
- `outbound: summary_trip`  
  The outbound leg of the round trip.

- `return_: summary_trip`  
  The return leg of the round trip.

---

## Type Aliases

### `summary_round_trip_list`
```python
list[summary_round_trip]
```
A list of round-trip summary objects.


### summary_round_trip_list_by_city_pairing
```python 
dict[dict[(str, str), summary_round_trip_list]]
```
A dictionary grouping round-trip lists by city pairings. The key is a tuple (origin_city, destination_city).

### summary_round_trip_list_by_cabin
```python
#CABIN defined in data_types/enums.md
dict[CABIN, summary_round_trip_list_by_city_pairing]
```
A dictionary grouping round-trip lists by city pairings. The key is a tuple (origin_city, destination_city).

