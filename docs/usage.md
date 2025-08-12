# ✈️ Flight Alert System — Usage Guide

This project automates the process of identifying and promoting the best round-trip mileage deals. It can be run in two modes: **standalone mode** for automated execution, or **API mode** for programmatic access via RESTful endpoints.

---

## 🧰 Prerequisites

### ✅ Install Dependencies

Make sure you have Python 3.10+ and run the complete setup:

```bash
# Complete setup (virtual environment, dependencies, data)
make local-setup
```

---

## ⚙️ Environment Setup

Create a `.env` file at the project root with the following variables:

```env
### Financial Configuration
CURRENCY=BRL                       # string - 3-letter currency code
CURRENCY_SYMBOL=R$                 # string - currency symbol for display
COMMISSION=500                     # integer - commission in cents
CREDIT_CARD_FEE=500               # integer - credit card fee in cents

### API Keys and Service Configuration
OPENAI_API_KEY=your_openai_key                        # string - OpenAI API key
SEATS_AERO_API_KEY=your_seats_aero_key               # string - Seats.aero API key
EXCHANGE_RATE_API_KEY=your_exchange_rate_api_key     # string - Exchange rate API key
UNSPLASH_ACCESS_KEY=your_unsplash_key                # string - Unsplash API key

### Google Services Configuration
GOOGLE_SERVICE_ACCOUNT={"type":"service_account",...} # string - JSON service account credentials
GOOGLE_EMAIL=your_email@gmail.com                    # string - Gmail address for sending emails
GOOGLE_PASS=your_app_password                        # string - Gmail app password
MILEAGE_SPREADSHEET_ID=your_spreadsheet_id           # string - Google Sheets ID for mileage data
MILEAGE_WORKSHEET_NAME=mileage                        # string - Sheet name within the mileage spreadsheet
RESULT_SHEET_ID=your_result_sheet_id                 # string - Google Sheets ID for storing results
```

**Note:** Travel parameters (origin, destination, dates, etc.) are now configured via API calls rather than environment variables.
```

---

## 🚀 Running the System

### **Running the Application**

The application can run in different modes depending on your configuration. Both commands start the same application:

```bash
# Run with complete setup (recommended for first run)
make run

# Run without setup (if already configured)
make run-a
```

**Note:** The application automatically determines whether to run in standalone mode or start the FastAPI server based on your configuration.

**Access the API:**
- API Base URL: `http://localhost:8000`
- Interactive Documentation: `http://localhost:8000/docs`
- Alternative Documentation: `http://localhost:8000/redoc`

### **Option 3: Docker**
Containerized deployment for easy scaling and deployment.

```bash
# Build Docker image
make docker-image

# Run Docker container
make run-docker

# Stop Docker container
make stop-docker
```

---

## 🌐 Using the API

Once the FastAPI server is running, you can use the RESTful endpoints to trigger flight searches programmatically.

### **API Endpoints**

#### **Region to Region Search**
Search for flights between geographical regions.

```http
GET /from-region-to-region?origin=South America&destination=North America&start_date=2025-08-15&cabins=Economy&n=3
```

**Parameters:**
- `origin` (required): Origin region name (South America, North America, Europe, Asia, Oceania, Africa)
- `destination` (required): Destination region name
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `cabins` (optional): Cabin classes (Economy/Y, Business/J, First/F) - can specify multiple
- `min_return_days` (optional): Minimum return days (default: 1)
- `max_return_days` (optional): Maximum return days (default: 60)
- `n` (optional): Number of results (default: 1)
- `deepness` (optional): Search depth (default: 1)

#### **Country to World Search**
```http
GET /from-country-to-world?country=BR&source=azul&cabins=Economy&n=5
```

### **API Usage Examples**

#### **Python with requests**
```python
import requests

# Region to region search
response = requests.get('http://localhost:8000/from-region-to-region', params={
    'origin': 'South America',
    'destination': 'North America',
    'start_date': '2025-08-15',
    'cabins': ['Economy', 'Business'],  # Can use full names or codes: ['Y', 'J']
    'n': 3
})

result = response.json()
print(f"Status: {result['statusCode']}")
print(f"Message: {result['message']}")
```

#### **cURL**
```bash
curl -X GET "http://localhost:8000/from-region-to-region?origin=South%20America&destination=North%20America&cabins=Economy&n=3" \
     -H "Content-Type: application/json"
```

#### **JavaScript/Fetch**
```javascript
const response = await fetch('/from-region-to-region?origin=South%20America&destination=North%20America&cabins=Economy&n=3');
const data = await response.json();
console.log(data);
```

### **API Response Format**
```json
{
  "statusCode": 200,
  "message": "Alerts runner executed successfully."
}
```

For detailed API documentation, visit the [API Documentation](api.md) or access the interactive docs at `http://localhost:8000/docs` when the server is running.

---

## 📋 Configuration Details

## 🏃 Running the System

Run the main script:

```bash
make run
```

It will:

1. Load config and global state.
2. Trigger the full `alerts_runner()` pipeline.
3. Fetch top N round-trips using external APIs.
4. Calculate total and selling prices with exchange rates and markups.
5. Generate:

   * WhatsApp post text
   * A PDF for each route
6. Write top combos to Google Sheets.
7. Email the admin with all PDFs attached.

---

## 📁 Folder Structure (Simplified)

```
.
├── main.py
├── config.py
├── global_state.py
├── src/
│   ├── currencies/
│   │   ├── cash.py
│   │   └── mileage.py
    ├── logic/
│   │   ├── filter.py
│   │   ├── pdf_generator.py
│   │   └── trip_builder.py
│   ├── data_types/
│   │   ├── enums.py
│   │   ├── images.py
│   │   ├── pdf_types.py
│   │   └── summary_objs.py
│   └── services/
│       ├── gmail.py
│       ├── google_sheets.py
│       ├── openAI.py
│       ├── seats_aero.py
│       ├── unsplash.py
│       └── whatsapp.py
├── alerts_runner.py
├── requirements.txt
├── .env
└── data/
    └── airports.csv
```

---

## 🥪 Tips for Testing Locally

* Set fewer days and smaller `N` in your `.env` to test faster.
* Comment out email sending and Sheets writing to isolate bugs.
* Monitor logs in real time via `state.logger`.

---

## 🛠️ Gotchas

* All monetary values are handled in **cents** to avoid float errors.
* Exchange rates are cached in memory, not persisted.
* If one trip's availability fails, the system raises **upstream** — catch high!
* The PDF creation logic depends on a valid release schedule (date + time of day).
* Always test in staging before production — especially PDF layout and email format.

---

## 🤛 FAQ

**Q: How do I update the mileage values?**
A: Update the linked Google Sheet with the mileage values per program (e.g. Smiles, Azul, etc.)

**Q: Why do I see `Unknown` for some cities?**
A: Check your `airports.csv` file. The mapping may be missing for a given IATA code.

**Q: What timezone is used?**
A: All time-based logic uses the system's local time.

---
