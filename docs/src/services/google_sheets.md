# [`google_sheets.py`](../../src/services/google_sheets.py)

This module provides a comprehensive Google Sheets integration service for storing flight alert data. It features a hierarchical class structure with `WorkSheet`, `SpreadSheet`, and `GoogleSheetsHandler` classes to manage all aspects of Google Sheets operations via the Google Sheets API using service account credentials.

---

## 📄 Overview

The module implements a three-tier architecture:
- **`WorkSheet`**: Wrapper for individual worksheet operations (reading/writing data, managing headers)
- **`SpreadSheet`**: Wrapper for spreadsheet-level operations (managing worksheets)  
- **`GoogleSheetsHandler`**: Main handler for authentication and high-level operations

The system uses a singleton pattern with a global `handler` instance for application-wide access. It supports creating spreadsheets, managing worksheets, and writing structured flight data with standardized headers.

---

## 📦 Classes

### `WorkSheet`

Wrapper class for gspread Worksheet operations, providing methods to manage individual worksheets.

#### Initialization (`__init__(worksheet: gspread.Worksheet, headers: list[str] = None)`)

- **Parameters:**
  - `worksheet` (`gspread.Worksheet`): The gspread Worksheet instance to wrap
  - `headers` (`list[str]`, optional): Headers to set in the first row
- **Behavior:** Automatically sets headers in the first row if provided

#### Methods

##### `update_headers(headers: list[str]) -> WorkSheet`
Updates the worksheet headers and returns self for method chaining.

##### `get_all_values() -> list[list[str]]`
Retrieves all worksheet values excluding the header row, with unformatted values.

##### `add_row(row: list[str]) -> None`
Appends a single row to the worksheet.

##### `add_rows(rows: list[list[str]]) -> None`
Efficiently appends multiple rows to the worksheet.

### `SpreadSheet`

Wrapper class for gspread Spreadsheet operations, managing worksheet creation and retrieval.

#### Initialization (`__init__(spreadsheet: gspread.Spreadsheet, spreadsheet_name: str)`)

- **Parameters:**
  - `spreadsheet` (`gspread.Spreadsheet`): The gspread Spreadsheet instance
  - `spreadsheet_name` (`str`): Name of the spreadsheet

#### Methods

##### `get_worksheet(worksheet_name: str) -> WorkSheet`
Retrieves an existing worksheet by name, wrapped in a WorkSheet instance.

##### `create_worksheet(worksheet_name: str, rows_n: int, cols_n: int, headers: list[str]) -> WorkSheet`
Creates a new worksheet with specified dimensions and headers.

### `GoogleSheetsHandler`

Main handler class managing Google Sheets authentication and high-level operations.

#### Initialization (`__init__()`)

Creates an uninitialized handler instance. Call `load()` to initialize.

#### Methods

##### `load() -> None`

Initializes the Google Sheets handler with service account authentication.

- **Behavior:**
  - Loads credentials from `./sheets_api_key.json` (hardcoded path)
  - Creates authorized gspread client
  - Validates authentication and authorization
- **Raises:** `ValueError` if credentials cannot be loaded or client authorization fails

##### `get_sheet(spreadsheet_id: str) -> SpreadSheet`

Retrieves an existing Google Spreadsheet by ID.

- **Parameters:**
  - `spreadsheet_id` (`str`): Unique ID of the Google Spreadsheet
- **Returns:** `SpreadSheet` wrapper for the requested spreadsheet
- **Raises:** `gspread.SpreadsheetNotFound` if spreadsheet doesn't exist

##### `create_sheet(spreadsheet_name: str) -> str`

Creates a new Google Spreadsheet.

- **Parameters:**
  - `spreadsheet_name` (`str`): Title for the new spreadsheet
- **Returns:** `str` - The spreadsheet ID of the created spreadsheet
- **Behavior:** Logs creation success/failure

---

## 📊 Standard Headers

The module defines standard headers for flight data export:

```python
HEADERS = [
    "Outbound ID", "Return ID", "Origin Airport", "Destination Airport", 
    "Outbound Departure", "Outbound Arrival", "Return Departure", "Return Arrival",
    "Outbound Mileage Cost", "Outbound Taxes", "Outbound Normal Taxes",
    "Outbound Total Cost", "Outbound Normal Total Cost",
    "Return Mileage Cost", "Return Taxes", "Return Normal Taxes",
    "Return Total Cost", "Return Normal Total Cost",
    "Normal Selling Price", "Outbound Booking Links", "Return Booking Links"
]
```

---

## 🏗️ Singleton Pattern

The module creates a singleton instance for application-wide use:

```python
handler = GoogleSheetsHandler()
```

This instance should be loaded once during application startup and used throughout the system.

---

## 🧠 Error Handling

- Validates credential file path and logs errors before raising exceptions
- Checks credential loading and gspread client authorization
- Wraps all Google Sheets API operations in try-except blocks
- Provides detailed error logging for debugging
- Uses fallback error handling for critical operations

---

## 🔐 Authentication

**Current Implementation:**
- Uses hardcoded path `./sheets_api_key.json` for service account credentials
- Requires Google Sheets API scope: `https://www.googleapis.com/auth/spreadsheets`
- Service account must have appropriate permissions for target spreadsheets

**Required Setup:**
- Google service account JSON credentials file in project root
- Service account must have Google Sheets API enabled
- Appropriate sharing permissions for target spreadsheets

---

## 🔗 Dependencies

- [`config`](../config.md): Configuration management (imported but path currently hardcoded)
- [`global_state`](../global_state.md): Centralized logging and state management
- [`gspread`](https://gspread.readthedocs.io/en/latest/): Python client library for Google Sheets API
- [`google.oauth2.service_account`](https://googleapis.dev/python/google-auth/latest/reference/google.oauth2.service_account.html): OAuth2 service account credential handling

---

## 💡 Usage Examples

### Basic Usage

```python
from services.google_sheets import handler as sheets_handler

# Initialize the handler
sheets_handler.load()

# Create a new spreadsheet
spreadsheet = sheets_handler.create_sheet("Flight Data 2025")
print(f"Created spreadsheet with ID: {spreadsheet}")

# Get existing spreadsheet (using the returned ID)
spreadsheet_obj = sheets_handler.get_sheet(spreadsheet)

# Get the default worksheet (usually "Sheet1") or create a new one
try:
    worksheet = spreadsheet_obj.get_worksheet("Sheet1")
except:
    # If default sheet doesn't exist, create one
    worksheet = spreadsheet_obj.create_worksheet("Data", 100, 10, 
                                                 ["Column1", "Column2", "Column3"])

# Add data
worksheet.add_row(["Flight1", "Flight2", "NYC", "LAX"])
```

### Working with Flight Data (Method Chaining)

```python
# Create worksheet with headers and add data in one flow
headers = ["Outbound ID", "Return ID", "Origin Airport", "Destination Airport"]

# Method chaining approach
flight_data = [
    ["FL001", "FL002", "JFK", "LAX"],
    ["FL003", "FL004", "BOS", "SFO"]
]

worksheet = (spreadsheet_obj
             .create_worksheet("Flights_2025", 1000, len(headers), headers)
             .add_rows(flight_data))

# Alternative: Step-by-step approach
worksheet = spreadsheet_obj.create_worksheet("Flights_2025", 1000, len(headers), headers)
worksheet.add_rows(flight_data)
```

### Reading Data from Existing Sheets

```python
# Read mileage data (like in the currencies/mileage.py usage)
mileage_data = (sheets_handler
                .get_sheet(config.MILEAGE_SPREADSHEET_ID)
                .get_worksheet(config.MILEAGE_WORKSHEET_NAME)
                .get_all_values())

# Process the data (excluding headers)
mileage_dict = {}
for row in mileage_data:
    if len(row) >= 2:  # Ensure row has at least 2 columns
        program = row[0]
        miles = int(row[1])
        mileage_dict[program] = miles
```

---
