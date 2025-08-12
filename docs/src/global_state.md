# `global_state.py`

This module defines and manages the application's global state across its various stages. It provides flags for progress tracking and a centralized logger for consistent logging throughout the system.

---

## 🧠 Class: `GLOBAL_STATE`

Maintains a shared state object that tracks initialization and execution phases of the application.

### Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| `timestamp` | `str` | Time of state initialization (formatted as `YYYYMMDD_HHMM`). |
| `configInitialized` | `bool` | Whether the config has been successfully loaded. |
| `spreadSheetModInitialized` | `bool` | Whether Google Sheets module has been initialized. |
| `mileageModInitialized` | `bool` | Whether mileage values were successfully loaded. |
| `flightsRetrieved` | `bool` | Whether flight data was fetched. |
| `flightsAnalysed` | `bool` | Whether flight analysis was completed. |
| `availabilityObjectsRetrieved` | `bool` | Whether availability objects have been retrieved. |
| `tripsFormatted` | `bool` | Whether trip formatting has been completed. |
| `email_sent` | `bool` | Whether the admin notification email was sent. |
| `sheets_sent` | `bool` | Whether the top trips were written to Google Sheets. |
| `whatsapp_msg_generated` | `bool` | Whether WhatsApp message content has been generated. |
| `pdf_generated` | `bool` | Whether PDF generation completed successfully. |
| `logger` | `logging.Logger` | Configured logger for use throughout the system. |

---

## 🧰 Methods

### `load()`
Initializes or resets all progress flags and sets the logger.

### `setup_logger() → logging.Logger`
Configures and returns a logger instance named `"global_state"` with stream output and timestamp formatting.

### `reset()`
Re-runs the constructor to reinitialize all state and flags.

---

## 🪪 Singleton Instance

```python
state = GLOBAL_STATE()
