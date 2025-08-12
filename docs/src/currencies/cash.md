# [`cash.py`](../../src/currencies/cash.py)

This module provides utilities to manage currency values and conversions using the [ExchangeRate API](https://www.exchangerate-api.com/). It converts prices to a target currency in cents, caches conversion rates for performance, and follows the application's deferred initialization pattern.

---

## 📄 Overview

The `CashHandler` class manages currency conversion operations with intelligent caching to minimize API calls. It follows the same initialization pattern as other handlers in the system - creating an empty instance that requires `load()` to be called explicitly.

The handler converts all monetary amounts to cents (integer representation) for precise calculations and maintains a cache of exchange rates to improve performance and reduce API usage.andler.py`](../../src/currencies/cash.py)

This module provides utilities to manage currency values and conversions using the [ExchangeRate API](https://www.exchangerate-api.com/). It converts prices to a target currency in cents and caches conversion rates for performance.

---

## 🔧 Environment Variables

- `EXCHANGE_RATE_API_KEY` – Your API key for the ExchangeRate API. Required at module load time.
- `TARGET_CURRENCY` – The system’s base currency. All conversion targets will be based on this.

---

## 📦 Classes

### `CashHandler`

Handles conversion of cash amounts across currencies with intelligent rate caching.

#### Initialization (`__init__(self)`)

Creates an uninitialized CashHandler instance with an empty rate cache. No configuration is loaded until `load()` is called.

- **Behavior:** Initializes empty cache dictionary for storing exchange rates

#### Methods

##### `load(self, target_currency: str, api_key: str) -> None`

Initializes the handler with target currency and optional API key.

- **Parameters:**
  - `target_currency` (`str`): The system's base currency (converted to uppercase)
  - `api_key` (`str`): ExchangeRate API key for rate fetching
- **Behavior:**
  - Validates target currency is provided and not empty
  - Stores target currency in uppercase format
  - Stores API key for exchange rate fetching
  - Logs successful initialization with target currency
- **Raises:**
  - `ValueError`: If target_currency is not provided or empty

##### `normal_to_cents(self, amount: float) -> int`

Converts a float monetary amount to integer cents representation.

- **Parameters:**
  - `amount` (`float`): The monetary amount to convert
- **Returns:** 
  - `int`: The amount in cents (multiplied by 100)
- **Behavior:**
  - Validates amount is not negative
  - Converts to cents by multiplying by 100 and casting to int
- **Raises:**
  - `ValueError`: If amount is negative

##### `get_rate(self, base_currency: str) -> int`

Retrieves exchange rate from base currency to target currency, with caching.

- **Parameters:**
  - `base_currency` (`str`): Currency to convert from
- **Returns:**
  - `int`: Exchange rate in cents
- **Behavior:**
  - Checks cache first to avoid redundant API calls
  - Fetches rate from API if not cached
  - Converts rate to cents and stores in cache
  - Returns cached or fetched rate in cents

##### `fetch_rate(self, base_currency: str) -> float`

Fetches current exchange rate directly from ExchangeRate API.

- **Parameters:**
  - `base_currency` (`str`): Currency to convert from
- **Returns:**
  - `float`: Raw exchange rate from API
- **Behavior:**
  - Makes HTTP request to ExchangeRate API
  - Validates response status and data structure
  - Caches successful rate for future use
  - Provides detailed error logging
- **Raises:**
  - `ValueError`: If conversion rate not found in API response
  - `Exception`: If API request fails with status code and response details

##### `convert_to_system_base(self, amount_in_cents: int, base_currency: str) -> int`

Converts monetary amount from base currency to system target currency.

- **Parameters:**
  - `amount_in_cents` (`int`): Amount in cents to convert
  - `base_currency` (`str`): Source currency for the amount
- **Returns:**
  - `int`: Converted amount in cents in target currency
- **Behavior:**
  - Returns original amount if base currency equals target currency
  - Retrieves exchange rate using `get_rate()`
  - Performs conversion calculation with integer division
  - Logs errors for missing exchange rates
- **Raises:**
  - `ValueError`: If exchange rate cannot be found for the currency pair

---

## 🏗️ Singleton Pattern

The module creates a singleton instance for application-wide use:

```python
handler = CashHandler()
```

This instance should be loaded once during application startup using `handler.load(target_currency, api_key)`.

---

## 🧠 Error Handling

- **Input Validation**: Raises `ValueError` for empty target currency or negative amounts
- **API Failures**: Raises `Exception` with detailed HTTP status and response information
- **Missing Data**: Raises `ValueError` when conversion rates cannot be found in API responses
- **Comprehensive Logging**: Uses global state logger for all error conditions and successful operations
- **Cache Management**: Handles cache misses gracefully by fetching fresh rates from API

---

## 💡 Usage Examples

### Basic Usage

```python
from currencies.cash import handler as cash_handler

# Initialize the handler (typically done during app startup)
cash_handler.load(target_currency="BRL", api_key="your_api_key_here")

# Convert amounts to cents
amount_in_cents = cash_handler.normal_to_cents(29.99)  # Returns 2999

# Get exchange rate for currency conversion
usd_to_brl_rate = cash_handler.get_rate("USD")  # Returns rate in cents

# Convert amounts between currencies
usd_amount_cents = 5000  # $50.00 in cents
brl_amount_cents = cash_handler.convert_to_system_base(usd_amount_cents, "USD")
```

### Integration with Flight Processing

```python
# Typical usage in flight price calculations
def convert_flight_price(price_cents: int, source_currency: str) -> int:
    """Convert flight price to system base currency"""
    try:
        return cash_handler.convert_to_system_base(price_cents, source_currency)
    except ValueError as e:
        state.logger.error(f"Currency conversion failed: {e}")
        return price_cents  # Fallback to original amount
```

### Handling API Limitations

```python
# Example with error handling for rate fetching
def safe_currency_conversion(amount: float, from_currency: str) -> int:
    try:
        amount_cents = cash_handler.normal_to_cents(amount)
        return cash_handler.convert_to_system_base(amount_cents, from_currency)
    except ValueError as e:
        state.logger.warning(f"Invalid amount or currency: {e}")
        return 0
    except Exception as e:
        state.logger.error(f"Exchange rate API error: {e}")
        # Could implement fallback logic here
        raise
```

---

## 🌐 API Integration

**ExchangeRate API Details:**
- **Endpoint**: `https://v6.exchangerate-api.com/v6/{api_key}/pair/{from}/{to}`
- **Response Format**: JSON with `conversion_rate` field
- **Caching**: Rates are cached in memory to minimize API calls
- **Error Handling**: HTTP status codes and response validation

**Required Setup:**
- Valid ExchangeRate API key (optional parameter, can be passed during `load()`)
- Internet connectivity for rate fetching
- Proper error handling for API failures

---

## 📌 Global Objects

### `handler: CashHandler`

A singleton instance used throughout the system for currency operations.

**Usage Pattern:**
1. Import: `from currencies.cash import handler as cash_handler`
2. Initialize: `cash_handler.load(target_currency="BRL", api_key="key")` (during app startup)
3. Use: `cash_handler.convert_to_system_base(amount, currency)`

---

## 🔗 Dependencies

- [`requests`](https://docs.python-requests.org/): For HTTP calls to the ExchangeRate API
- [`global_state`](../global_state.md): Centralized logging and system state management

---

## ⚠️ Notes

- **Deferred Loading**: Handler requires explicit `load()` call with target currency
- **Integer Precision**: All monetary calculations use integer cents to avoid floating-point precision issues
- **Cache Persistence**: Rate cache is in-memory only and resets on application restart
- **Currency Validation**: No validation of currency codes - relies on ExchangeRate API for validation
