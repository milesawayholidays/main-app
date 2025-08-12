# Project Index

## Overview

This index provides an organized list of all major files and modules in the project, along with a brief description of their purpose. It is meant to serve as a reference for developers navigating the codebase.

---

## Index

### [Documentation](../docs/)

* **[`docs/installation.md`](./installation.md)**
  Step-by-step installation guide for setting up the flight alerts system from GitHub.

* **[`docs/usage.md`](./usage.md)**
  Full usage instructions for setting up and running the alert system.

* **[`docs/*.md`](../docs/)**
  Module-level documentation (one per major Python file).

---

### [Core Modules](../src/)

* **[`main.py`](./src/main.md)**
  Entry point of the application. Loads config, calls the runner, and handles top-level error reporting.

* **[`alerts_runner.py`](./src/alerts_runner.md)**
  Core logic pipeline for fetching, filtering, formatting, generating, and sending flight alert data.

* **[`config.py`](./src/config.md)**
  Loads environment variables, validates travel and system configurations, sets up region/cabin/source filters.

* **[`global_state.py`](./src/global_state.md)**
  Manages shared application state and logger instance throughout the pipeline.

---

### [Data Types](../src/data_types/)

* **[`data_types/enums.py`](./src/data_types/enums.md)**
  Enumerations for `SOURCE`, `REGION`, and `CABIN`.

* **[`data_types/images.py`](./src/data_types/images.md)**
  `Image` dataclass representing an image fetched from Unsplash.

* **[`data_types/pdf_types.py`](./src/data_types/pdf_types.md)**
  `PDF_OBJ` dataclass used to pass PDF metadata and binary data.

* **[`data_types/summary_objs.py`](./src/data_types/summary_objs.md)**
  Structures for summary trips and round-trip groupings used in flight filtering.

---

### [Services](../src/services/)

* **[`services/gmail.py`](./src/services/gmail.md)**
  Sends emails with or without PDF attachments to the configured recipient.

* **[`services/google_sheets.py`](./src/services/google_sheets.md)**
  Handles interaction with Google Sheets API for storing top-N trip data.

* **[`services/openAI.py`](./src/services/openAI.md)**
  Generates WhatsApp travel alert posts via OpenAI API.

* **[`services/seats_aero.py`](./src/services/seats_aero.md)**
  Handles flight data retrieval and processing from Seats.aero API.

* **[`services/unsplash.py`](./src/services/unsplash.md)**
  Fetches a travel-related image using Unsplash API for each alert.

* **[`services/whatsapp.py`](./src/services/whatsapp.md)**
  WhatsApp integration service (currently a placeholder for future implementation).

---

### [Currency and Mileage](../src/currencies/)

* **[`currencies/cash.py`](./src/currencies/cash.md)**
  Fetches exchange rates and converts currency amounts using `ExchangeRate-API`.

* **[`currencies/mileage.py`](./src/currencies/mileage.md)**
  Reads mileage point values from a spreadsheet to calculate flight costs.

---

### [Logic](../src/logic/)

* **[`logic/filter.py`](./src/logic/filter.md)**
  Flight filtering logic and algorithms.

* **[`logic/pdf_generator.py`](./src/logic/pdf_generator.md)**
  PDF generation functionality for flight alerts and reports.

* **[`logic/trip_builder.py`](./src/logic/trip_builder.md)**
  Core business logic for building and processing trip data structures.

---

### [Data](../data/)

* **[`data/airports.csv`](../data/airports.csv)**
  Source for mapping airport IATA codes to cities and countries.
  
  *Note: This file may not be available in the repository. Please refer to the [installation guide](./installation.md) for instructions on obtaining the required data files.*

---

## Suggested Next Steps

* [ ] Add README.md at root with project description and quickstart.
* [ ] Include a `tests/` directory with test cases.
* [ ] Write docstrings for public classes/methods where missing.

---

This index will be maintained alongside the rest of the documentation. If you'd like it in another format (PDF, HTML), just ask.
