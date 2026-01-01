# ✈️ Flight Alert System — Usage Guide

This project can be used in three main ways:

- **Dev mode (local)**: run FastAPI + React with hot reload.
- **Docker deployment**: run a single container that serves both the API and the built frontend.
- **Render deployment**: same as Docker (single service).

---

## 🧰 Prerequisites

### ✅ Install Dependencies

Make sure you have **Python 3.11+**.

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

### Standalone (pipeline)

```bash
# First run (creates venv, installs deps, downloads data)
make run

# Run without setup (when already configured)
make run-a
```

### API + React UI (local dev)

The recommended local dev setup is:

```bash
make local-setup
make frontend-install
make dev
```

This runs:

- FastAPI backend on `http://localhost:4000`
- React (Vite) frontend on `http://localhost:5173`

The frontend proxies `/api/*` to the backend.

### Docker

#### Single container (frontend + API)

```bash
make docker-image
make run-docker
```

Defaults:

- Host port `4000` → container port `4000`
- Uses `.env` via `--env-file`
- Uses `--restart unless-stopped`
- Uses `-m 300m --memory-swap 500m`

Stop:

```bash
make stop-docker
```

#### Docker Compose (single service)

```bash
make compose-up
```

Defaults:

- App: `http://localhost:4000`
- API: `http://localhost:4000/api/health`

Stop:

```bash
make compose-down

### Render (deployment)

Render deploys the same single Docker service:

- UI: `https://<your-domain>/`
- API: `https://<your-domain>/api/health`

Use `render.yaml` and set the same environment variables you would put in `.env`.
```

---

## 🌐 Using the API

Once the FastAPI server is running, you can use the RESTful endpoints to trigger flight searches programmatically.

### **API Endpoints**

All API routes are under the `/api` prefix.

#### **One-way flights**

```http
GET /api/flights/oneway?origin_regions=NA&destination_regions=AS&cabins=business&n=2&deepness=1
```

#### **Round-trip flights**

```http
GET /api/flights/roundtrip?origin_regions=EU&destination_regions=NA&cabins=business&min_return_days=5&max_return_days=14&n=1
```

Notes:

- `origin_regions` / `destination_regions` accept region **codes** (`NA`) or region **names** (`North America`), case-insensitive.
- `cabins` accepts cabin **names** (`economy`, `premium`, `business`, `first`) or cabin **codes** (`y`, `w`, `j`, `f`).
- `sources` accepts: `azul`, `smiles`, `qantas`.
- `n` is capped server-side to `1..8`.
- `deepness` is capped server-side to `1..3`.

### **API Usage Examples**

#### **Python with requests**
```python
import requests

# One-way example
response = requests.get('http://localhost:4000/api/flights/oneway', params={
    'origin_regions': ['NA'],
    'destination_regions': ['AS'],
    'cabins': ['business'],
    'n': 2,
    'deepness': 1,
})

result = response.json()
print(result['status'])
print(result['data'].keys())
```

#### **cURL**
```bash
curl "http://localhost:4000/api/flights/roundtrip?origin_regions=EU&destination_regions=NA&cabins=business&min_return_days=5&max_return_days=14&n=1"
```

#### **JavaScript/Fetch**
```javascript
const response = await fetch('/api/flights/oneway?origin_regions=NA&destination_regions=AS&cabins=business&n=2');
const data = await response.json();
console.log(data);
```

### **API Response Format**

```json
{
    "status": 200,
    "data": {
        "single_trips": [],
        "round_trips": [],
        "round_options": []
    }
}
```

For detailed API documentation, visit the [API Documentation](api.md) or use the interactive docs at `http://localhost:4000/docs`.

---

## 📋 What Standalone Mode Does

When you run the pipeline (`make run` / `make run-a`), it:

1. Loads config and global state.
2. Runs the `alerts_runner()` pipeline.
3. Fetches flight availability and ranks it.
4. Calculates costs (exchange rates + markups).
5. Generates outputs (WhatsApp post text, PDFs).
6. Writes results to Google Sheets.
7. Emails the admin with PDFs attached.

---

## 📁 Folder Structure (Simplified)

```
.
├── backend_api/              # FastAPI routers (/api/*)
├── src/                      # Core pipeline + services
├── frontend/                 # React UI (Vite)
├── data/airports.csv         # Airport mapping dataset
├── public/                   # Static assets served by FastAPI
└── docs/                     # Documentation
```

---

## 🥪 Tips for Testing Locally

* Use smaller date ranges and smaller `n` values in your API request / UI to test faster.
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
