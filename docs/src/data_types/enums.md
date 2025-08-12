# [`enums.py`](../../src/data_types/enums.py)

This module defines the core enumerations used throughout the project. Enums provide semantic clarity and enforce consistency across the system when handling categorical values related to data sources, geographic regions, and cabin classes.

## Enums

### `SOURCE`
Represents the origin of award flight availability data. This enum is used to distinguish between the different APIs or programs being queried.

- `AZUL`: Data sourced from the Azul airline program.
- `SMILES`: Data sourced from the Smiles loyalty program.
- `QATAR`: Data sourced from the Qatar Airways program.

### `REGION`
Defines high-level geographical regions used for organizing or filtering search results.

- `NORTH_AMERICA`
- `SOUTH_AMERICA`
- `AFRICA`
- `ASIA`
- `EUROPE`
- `OCEANIA`

These values may be used in filters when performing searches across broad destination zones.

### `CABIN`
Enumerates the cabin classes available for flight bookings.

- `ECONOMY ("Y")`: Economy class seating.
- `BUSINESS ("W")`: Business class seating.

Used when filtering, formatting, or displaying flight availability based on service tier.
