# [`mileage.py`](../../src/currencies/mileage.py)

This module handles mileage redemption values for various airline loyalty programs by loading data from a Google Sheet. It provides a simple interface to access mileage conversion rates for different airline sources.

---

## 📄 Overview

The `Mileage` class loads a mapping of airline program names (based on SOURCE enum values) to their respective mileage redemption rates. These values are retrieved from a Google Sheet specified in the configuration and used throughout the system for currency conversion calculations.

The module follows the application's pattern of deferred initialization - the class is instantiated but requires `load()` to be called explicitly to fetch data from Google Sheets.

---

## 📦 Classes

### `Mileage`

Manages mileage redemption rates for different airline loyalty programs.

#### Initialization (`__init__(self)`)

Creates an uninitialized Mileage instance. No data is loaded until `load()` is called.

#### Methods

##### `load(self) -> None`

Initializes the mileage handler by fetching data from the configured Google Sheet.

- **Behavior:**
  - Retrieves data from spreadsheet using `config.MILEAGE_SPREADSHEET_ID` and `config.MILEAGE_WORKSHEET_NAME`
  - Uses method chaining with the Google Sheets handler for clean data access
  - Populates `self.mileage_values` dictionary with program → mileage mappings
  - Validates that data exists and raises exception if sheet is empty
  - Logs successful initialization with data count

- **Data Structure:**
  - `mileage_values`: `dict[SOURCE, int]` - Maps airline source enums to mileage values
  
- **Raises:**
  - `Exception`: If no mileage values are found in the sheet

##### `get_mileage_value(self, program: str) -> int`

Retrieves the mileage redemption rate for a specific airline program.

- **Parameters:**
  - `program` (`str`): Name of the airline loyalty program
- **Returns:** 
  - `int`: Mileage value for the specified program
- **Behavior:**
  - Looks up program in the loaded mileage values dictionary
  - Logs warning if program is not found
- **Raises:**
  - `ValueError`: If the program is not found in the loaded mileage values

---

## 🏗️ Singleton Pattern

The module creates a singleton instance for application-wide use:

```python
handler = Mileage()
```

This instance should be loaded once during application startup using `handler.load()`.

---

## 🧠 Error Handling

- **Empty Sheet Validation**: Raises exception if no data is found in the configured Google Sheet
- **Program Lookup**: Logs warnings and raises `ValueError` for unknown airline programs  
- **Graceful Degradation**: Provides clear error messages for debugging missing mileage data
- **Integration**: Uses global state logger for consistent error reporting throughout the system

---

## 💡 Usage Examples

### Basic Usage

```python
from currencies.mileage import handler as mileage_handler

# Initialize the handler (typically done during app startup)
mileage_handler.load()

# Get mileage value for a specific airline program
try:
    azul_mileage = mileage_handler.get_mileage_value("azul")
    print(f"Azul mileage rate: {azul_mileage}")
except ValueError as e:
    print(f"Program not found: {e}")
```

### Integration with Flight Processing

```python
# Typical usage in flight cost calculations
def calculate_mileage_cost(flight_cost: int, airline_program: str) -> int:
    try:
        mileage_rate = mileage_handler.get_mileage_value(airline_program)
        return flight_cost * mileage_rate
    except ValueError:
        # Fallback to default calculation if program not found
        return flight_cost
```

---

## � Data Format

The Google Sheet should be structured as follows:

| source      | value (cents) |
|-------------|---------------|
| azul        | 125           |
| gol         | 150           |
| latam       | 200           |

- **Column 1**: Airline program name (should match SOURCE enum values)
- **Column 2**: Integer mileage redemption rate in cents
- **Headers**: Not required (skipped by `get_all_values()`)

---

## 🔗 Global Objects

### `handler: Mileage`

A singleton instance used throughout the system for mileage calculations.

**Usage Pattern:**
1. Import: `from currencies.mileage import handler as mileage_handler`
2. Initialize: `mileage_handler.load()` (during app startup)
3. Use: `mileage_handler.get_mileage_value(program_name)`

---

## 🔗 Dependencies

- [`sheets_handler`](../services/google_sheets.md): For Google Sheets integration using the new hierarchical API
- [`SOURCE`](../data_types/enums.md): Enum defining valid airline source identifiers  
- [`config`](../config.md): Configuration variables for spreadsheet ID and worksheet name
- [`global_state`](../global_state.md): Centralized logging and state management

---

## ⚠️ Notes

- **Type Safety**: Uses `dict[SOURCE, int]` typing for better IDE support and validation
- **Method Chaining**: Leverages the new Google Sheets handler's fluent interface for cleaner code
- **Error Resilience**: Validates data existence before processing to prevent runtime issues
