# FlightAlertsGroup

**Intelligent Flight Alert System** - An advanced, automated solution for discovering, analyzing, and distributing premium flight deals and award availability across multiple airlines and routes.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/Documentation-Available-brightgreen.svg)](docs/index.md)

---

## 🚀 **Overview**

FlightAlertsGroup is a comprehensive flight monitoring and alert system that automatically:

- **🔍 Monitors** flight prices and award availability across multiple airlines
- **📊 Analyzes** pricing trends and identifies exceptional deals
- **🎯 Filters** results based on user preferences and travel requirements  
- **📧 Delivers** personalized flight reports via email with PDF attachments
- **📈 Tracks** market trends and provides intelligent recommendations
- **🌍 Supports** multi-currency pricing and global route networks
- **🌐 Provides** RESTful API endpoints for programmatic access

### **Key Features**

✅ **Multi-Source Integration** - Seats.aero, airline APIs, and market data  
✅ **RESTful API** - FastAPI-based web service with comprehensive endpoints  
✅ **Intelligent Filtering** - Advanced algorithms for personalized results  
✅ **Visual Reports** - Professional PDF reports with charts and destination images  
✅ **Real-time Notifications** - Instant alerts for exceptional deals  
✅ **Currency Conversion** - Multi-currency support with real-time exchange rates  
✅ **Award Flight Analysis** - Mileage program optimization and points valuation  
✅ **Docker Support** - Containerized deployment for easy scaling  
✅ **Automated Scheduling** - Configurable monitoring schedules and alerts  

---

## 📁 **Project Architecture**

```plaintext
FlightAlertsGroup/
├── 📄 README.md                    # Project overview and setup guide
├── ⚙️ requirements.txt             # Python dependencies
├── 🔧 makefile                     # Build and automation commands
├── � Dockerfile                   # Container deployment configuration
├── �🔐 .env                         # Environment configuration
├── 🗃️ data/                        # Reference data and airport information
├── 📁 credentials/                 # Service account credentials
├── 📝 logs/                        # Execution logs and state tracking
├── 📄 pdfs/                        # Generated PDF reports
├── 📚 docs/                        # Comprehensive documentation
│   ├── 📖 index.md                 # Documentation overview
│   ├── 🛠️ installation.md          # Setup and installation guide
│   ├── 📋 usage.md                 # User guide and examples
│   └── 💻 src/                     # Technical documentation
└── 🐍 src/                         # Source code
    ├── 🎯 main.py                  # Standalone application entry point
    ├── 🌐 app.py                   # FastAPI web application
    ├── 🔄 alerts_runner.py         # Core processing pipeline
    ├── ⚙️ config.py                # Configuration management
    ├── 📊 global_state.py          # Centralized state tracking
    ├── 🔗 api/                     # REST API endpoints
    │   └── 🛣️ routes.py            # API route definitions
    ├── 🌐 services/                # External API integrations
    │   ├── 🛫 seats_aero.py        # Flight data retrieval
    │   ├── 📧 gmail.py             # Email delivery service
    │   ├── 📊 google_sheets.py     # Data storage and tracking
    │   ├── 🤖 openAI.py            # AI-powered content generation
    │   ├── 🖼️ unsplash.py          # Travel imagery integration
    │   └── 💬 whatsapp.py          # Messaging platform integration
    ├── 🏗️ data_types/              # Core data structures
    │   ├── 🏷️ enums.py             # System enumerations
    │   ├── 🖼️ images.py            # Image data handling
    │   ├── 📄 pdf_types.py         # PDF document structures
    │   └── 📊 summary_objs.py      # Flight summary objects
    ├── 🧠 logic/                   # Business logic and algorithms
    │   ├── 🔍 filter.py            # Advanced filtering engine
    │   ├── ✈️ trip_builder.py      # Intelligent trip planning
    │   └── 📄 pdf_generator.py     # Report generation engine
    └── 💰 currencies/              # Financial calculations
        ├── 💵 cash.py              # Currency conversion and pricing
        └── ✈️ mileage.py           # Airline mileage program integration
```

---

## 🛠️ **Quick Start**

### **1. Clone and Setup**

```bash
# Clone the repository
git clone https://github.com/yourusername/FlightAlertsGroup.git
cd FlightAlertsGroup

# Complete setup (creates virtual environment, installs dependencies, downloads data)
make local-setup
```

### **2. Configuration**

Create your `.env` file with the required configuration:

```env
# Currency and Pricing
CURRENCY=BRL
CURRENCY_SYMBOL=R$
COMMISSION=500
CREDIT_CARD_FEE=500

# API Keys
OPENAI_API_KEY=your_openai_api_key
SEATS_AERO_API_KEY=your_seats_aero_key
EXCHANGE_RATE_API_KEY=your_exchange_api_key
UNSPLASH_ACCESS_KEY=your_unsplash_key

# Google Services
GOOGLE_SERVICE_ACCOUNT={"type":"service_account","project_id":"your_project",...}
GOOGLE_EMAIL=your_email@gmail.com
GOOGLE_PASS=your_app_password
MILEAGE_SPREADSHEET_ID=your_spreadsheet_id
MILEAGE_WORKSHEET_NAME=mileage
RESULT_SHEET_ID=your_result_sheet_id
```

### **3. Run the System**

#### **Running the Application**
```bash
# Run with complete setup (recommended for first run)
make run

# Run without setup (if already configured)
make run-a
```

#### **Docker Deployment**
```bash
# Build and run with Docker
make docker-image
make run-docker

# Stop Docker container
make stop-docker
```

---

## Render Deployment (Single Service)

This repo is set up to deploy as **one Render web service**:

- FastAPI serves the API under `/api/*`
- The built React frontend is served at `/` (SPA fallback enabled)

### Backend routes

- `GET /api/health`
- `GET /api/flights/oneway`
- `GET /api/flights/roundtrip`

### Local development

Run the backend (FastAPI):

```bash
./venv/bin/python -m uvicorn src.app:APP --reload --port 4000
```

Run the frontend (React):

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api/*` to `http://localhost:4000`.

### Render setup

- Use the blueprint in `render.yaml` (recommended).
- Set your environment variables in Render (same keys as your `.env`).
- Render will provide `PORT`; the container listens on it automatically.

---

## 🌐 **API Endpoints**

The system now provides RESTful API endpoints for programmatic access:

### **Flight Search Endpoints**

#### **Region to Region Search**
```http
GET /from-region-to-region?origin=South America&destination=North America&start_date=2025-08-15&end_date=2025-12-15&cabins=Economy&cabins=Business&min_return_days=5&max_return_days=30&n=3&deepness=2
```

**Parameters:**
- `origin` (string): Origin region name (South America, North America, Europe, Asia, Oceania, Africa)
- `destination` (string): Destination region name
- `start_date` (string): Start date in YYYY-MM-DD format (optional)
- `end_date` (string): End date in YYYY-MM-DD format (optional)
- `cabins` (array): Cabin classes (Economy/Y, Business/J, First/F) - can specify multiple
- `min_return_days` (int): Minimum return days (default: 1)
- `max_return_days` (int): Maximum return days (default: 60)
- `n` (int): Number of results (default: 1)
- `deepness` (int): Search depth (default: 1)

#### **Country to World Search**
```http
GET /from-country-to-world?country=BR&source=azul&start_date=2025-08-15&cabins=Economy&n=5
```

**Parameters:**
- `country` (string): Country code for origin
- `source` (string): Airline source (optional)
- Other parameters same as region search

### **API Response Format**
```json
{
  "statusCode": 200,
  "message": "Alerts runner executed successfully."
}
```

### **Error Responses**
```json
{
  "statusCode": 400,
  "message": "Origin and destination must be specified."
}
```

### **Interactive API Documentation**
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 📊 **System Outputs**

### **Automated Reports**
- 📄 **PDF Flight Reports** - Professional reports with top flight deals, visual charts, and destination imagery
- 📊 **Google Sheets Integration** - Real-time data storage with historical tracking and trend analysis  
- 📧 **Email Notifications** - Personalized alerts with PDF attachments and booking recommendations
- 💬 **WhatsApp Messages** - Instant notifications for time-sensitive deals (optional)

### **Data Analytics**
- 📈 **Price Trend Analysis** - Historical pricing data and market intelligence
- 🎯 **Deal Scoring** - Intelligent ranking of flight opportunities based on user preferences
- 💰 **Currency Analysis** - Multi-currency pricing with real-time conversion rates
- ✈️ **Award Flight Valuation** - Mileage program optimization and points-per-cent analysis

---

## 🏗️ **Core Components**

### **🌐 RESTful API Integration**
- **FastAPI Framework**: Modern, fast web framework with automatic API documentation
- **Flexible Parameters**: Support for region-based and country-based flight searches
- **Real-time Processing**: API endpoints trigger the same powerful flight analysis pipeline
- **Standardized Responses**: Consistent JSON responses with proper HTTP status codes

### **🌍 Multi-Source Data Integration**
- **Seats.aero API**: Real-time flight availability and pricing data
- **Currency APIs**: Live exchange rates for accurate international pricing
- **Unsplash Integration**: Professional destination imagery for visual reports
- **Google Services**: Sheets for data storage, Gmail for notifications

### **📊 Advanced Analytics Engine**
- **Price Tracking**: Historical data analysis and trend identification  
- **Route Optimization**: Intelligent routing suggestions with connection analysis
- **Seasonal Patterns**: Best booking time recommendations based on historical data
- **Award Availability**: Real-time monitoring of mileage program seat releases

---

## 📚 **Documentation**

For comprehensive documentation, visit the [**docs**](docs/index.md) directory:

- 📖 [**Overview**](docs/index.md) - System overview and quick start guide
- 🛠️ [**Installation**](docs/installation.md) - Detailed setup and configuration instructions  
- 📋 [**Usage Guide**](docs/usage.md) - User manual with examples and best practices
- 💻 [**Technical Docs**](docs/src/index.md) - API references and development guides

### **Component Documentation**
- 🌐 [**Services**](docs/src/services/index.md) - External API integrations and configurations
- 🏗️ [**Data Types**](docs/src/data_types/index.md) - Core data structures and enumerations
- 🧠 [**Business Logic**](docs/src/logic/index.md) - Filtering, trip building, and report generation
- 💰 [**Currency Systems**](docs/src/currencies/index.md) - Cash and mileage program handling

---

## � **Advanced Usage**

### **Automated Scheduling**

```bash
# Set up cron job for daily monitoring
crontab -e

# Add daily execution at 6 AM
0 6 * * * cd /path/to/FlightAlertsGroup && make run-a

# Weekly comprehensive reports on Sundays at 8 AM  
0 8 * * 0 cd /path/to/FlightAlertsGroup && make run
```

### **API Integration**

```python
# Example API usage with requests
import requests

# Region to region search
response = requests.get('http://localhost:8000/from-region-to-region', params={
    'origin': 'SA',
    'destination': 'NA', 
    'start_date': '2025-08-15',
    'end_date': '2025-12-15',
    'cabins': ['Y', 'J'],
    'min_return_days': 5,
    'max_return_days': 30,
    'n': 3
})

result = response.json()
print(f"Status: {result['statusCode']}")
print(f"Message: {result['message']}")
```

```bash
# Using curl
curl -X GET "http://localhost:8000/from-region-to-region?origin=SA&destination=NA&cabins=Y&n=3" \
     -H "Content-Type: application/json"
```

### **Programmatic Access to Flight Data**

```python
# Direct access to flight processing pipeline
from src.alerts_runner import GET_from_region_to_region
from src.data_types.enums import CABIN

# Process flights programmatically
response = GET_from_region_to_region(
    origin="SA",
    destination="NA", 
    start_date="2025-08-15",
    end_date="2025-12-15",
    cabins=[CABIN.Y, CABIN.J],
    min_return_days=5,
    max_return_days=30,
    n=3,
    deepness=2
)
```

---

## 🔧 **Development & Deployment**

### **Development Environment**

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests (if available)
make test

# Start development server
uvicorn src.app:APP --reload --host 0.0.0.0 --port 8000

# Run standalone application
make run-a
```

### **Production Deployment**

#### **Docker Deployment**
```bash
# Build Docker image
docker build -t flight-alerts-group .

# Run container with API server
docker run -d --env-file .env -p 8000:8000 flight-alerts-group

# Run container in standalone mode
docker run -d --env-file .env flight-alerts-group python3 src/main.py
```

#### **Cloud Deployment**
```bash
# Deploy to cloud platforms (Heroku, Railway, Render, etc.)
# Set environment variables from .env file
# Deploy with Dockerfile for containerized deployment

# For scheduled execution, use cron jobs or cloud schedulers
# API endpoint: https://your-app.com/from-region-to-region
```

#### **Environment Variables for Production**
```env
# Add to your cloud platform's environment variables
PORT=8000
PYTHONPATH=/app/src
# ... all other variables from .env file
```

---

## 🔍 **Monitoring & Analytics**

### **System Health**
- **📊 Real-time Metrics**: API response times, success rates, error tracking
- **📝 Comprehensive Logging**: Detailed execution logs with state persistence
- **🚨 Alert System**: Email notifications for system errors and exceptional deals
- **💾 State Recovery**: Automatic recovery from failures with saved execution state

### **Business Intelligence**
- **📈 Market Trends**: Price movement analysis and seasonal pattern detection
- **🎯 User Insights**: Preference learning and personalization improvements
- **💰 ROI Tracking**: Savings achieved through automated deal discovery
- **📊 Performance Metrics**: System efficiency and user satisfaction analytics

---

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### **Development Workflow**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## 📄 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **Seats.aero** - Premium flight data API
- **OpenAI** - AI-powered content generation
- **Google Cloud Services** - Gmail and Sheets integration
- **Unsplash** - High-quality travel imagery
- **Python Community** - Amazing open-source libraries

---

## 📞 **Support**

- 📧 **Email**: support@flightalertsgroup.com
- 📚 **Documentation**: [docs/index.md](docs/index.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/FlightAlertsGroup/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/FlightAlertsGroup/discussions)

---

*Built with ❤️ for travelers who value both exceptional deals and their time.*

