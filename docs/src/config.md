# `config.py`

This module centralizes all configuration and environment variable handling for the application. It loads environment variables, validates them, parses configuration data, and prepares mapping dictionaries from the airport dataset.

---

## ⚙️ Class: `Config`

Handles all environment setup and validation.

### Method: `load()`

Initializes the system by:

- Loading `.env` variables using `dotenv`.
- Validating required fields.
- Parsing string-based settings (e.g. cabin classes, dates).
- Reading and processing airport data (`airports.csv`) into mapping dictionaries.

### Key Attributes

| Attribute | Description |
|----------|-------------|
| `ORIGIN_REGION`, `DESTINATION_REGION` | Geographic regions defined in [`REGION`](./data_types/enums.md#region). |
| `SOURCE` | Default data provider for flight info (from [`SOURCE`](./data_types/enums.md#source)). |
| `CABINS` | List of cabin classes to search (`"Y"` for economy, `"W"` for business). |
| `START_DATE`, `END_DATE` | Date range for outbound flights. |
| `MIN_RETURN_DAYS`, `MAX_RETURN_DAYS` | Bounds for return flight intervals. |
| `N`, `TAKE` | Control number of trips to analyze and fetch limits. |
| `CURRENCY`, `CURRENCY_SYMBOL` | Target system currency (e.g. `USD`, `$`). |
| `COMMISSION`, `CREDIT_CARD_FEE` | Multipliers (in basis points) for pricing. |
| `OPENAI_API_KEY`, `UNSPLASH_ACCESS_KEY` | External service credentials. |
| `GOOGLE_EMAIL`, `GOOGLE_PASS` | Email sender credentials. |
| `MILEAGE_SPREADSHEET_ID`, `MILEAGE_SHEET_NAME` | Google Sheets identifiers for mileage lookups. |
| `SEATS_AERO_API_KEY` | Key for querying Seats.aero flight data. |

---

## 🗺 Mappings

### Airport Data (`../data/airports.csv`)
Loaded and parsed into:

- `IATA_CITY`: Maps IATA code ➝ city name.
- `CITY_COUNTRY`: Maps city name ➝ country code.

---

## ✅ Function: `assert_env_vars(...)`

Utility function that checks all required environment variables were properly loaded. Raises a `ValueError` if any required value is missing or falsy.

---

## 🌐 Dependencies

- [`data_types.enums`](./data_types/enums.md): for validating region, cabin, and source values.
- `pandas`: for loading and transforming airport mappings.
- `dotenv`: for loading local environment configuration.
- [`global_state`](../global_state.md): Logging system.
