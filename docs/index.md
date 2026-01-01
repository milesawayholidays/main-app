# Flight Alert System Documentation

Welcome to the comprehensive documentation for the **flight-alerts-system** project. This system automates discovery and analysis of flight award availability and exposes a small REST API used by the React frontend.

---

## 📚 Documentation Structure

### **📖 User Guides**
- [**Installation Guide**](installation.md) - Complete setup instructions for development and production
- [**Usage Guide**](usage.md) - How to configure and run the flight alert system (standalone and API modes)
- [**API Documentation**](api.md) - RESTful API endpoints and usage examples
- [**Contents Overview**](contents.md) - Detailed system architecture and component overview

### **🔧 Source Code Documentation**
- [**Source Code Documentation**](src/index.md) - Complete technical documentation for all system components

### **🌐 API Documentation**
- **Interactive API Docs** - Available at `http://localhost:4000/docs` when running the backend
- **API Reference** - RESTful endpoints for programmatic access to flight data

---

## 🚀 Quick Start

### **Quick Start**
```bash
# Clone and complete setup
git clone https://github.com/AnnWann/flight-alerts-system.git
cd flight-alerts-system
make local-setup

# Run the application
make dev
```

- Backend: `http://localhost:4000`
- Frontend: `http://localhost:5173`

### **Docker Deployment**
```bash
# Build and run with Docker
make docker-image
make run-docker
```

1. **[Install the System](installation.md)** - Set up dependencies and configuration
2. **[Configure Settings](usage.md)** - Set up API keys and flight search parameters  
3. **[Run the Pipeline](src/main.md)** - Execute the flight alert system
4. **[Explore Components](src/index.md)** - Dive into technical implementation details

---

## 🏗️ System Overview

The system consists of several key components:

- **🔍 Data Collection**: Fetches flight data from multiple airline sources
- **📊 Analysis Engine**: Filters and ranks flight deals using intelligent algorithms
- **🎨 Content Generation**: Creates marketing materials using AI and image services
- **📧 Distribution**: Delivers alerts via email with PDF reports
- **💾 Data Management**: Stores results in Google Sheets for tracking

---

## 🔗 Key Components

| Component | Description | Documentation |
|-----------|-------------|---------------|
| **Main Pipeline** | Core orchestration and execution flow | [main.md](src/main.md) |
| **Configuration** | System settings and environment management | [config.md](src/config.md) |
| **Alert Runner** | Flight data processing and report generation | [alerts_runner.md](src/alerts_runner.md) |
| **Services** | External API integrations and data sources | [services/](src/services/index.md) |
| **Data Types** | Core data structures and enums | [data_types/](src/data_types/index.md) |
| **Business Logic** | Flight filtering and trip building logic | [logic/](src/logic/index.md) |
| **Currency Handling** | Mileage and cash conversion utilities | [currencies/](src/currencies/index.md) |

---

## 📋 Documentation Navigation

Each section contains detailed technical documentation with:
- **API References** - Complete method signatures and parameters
- **Usage Examples** - Practical code examples and integration patterns
- **Error Handling** - Exception types and recovery strategies
- **Configuration** - Setup requirements and environment variables
- **Dependencies** - Required libraries and external services

---

## 🆘 Support

For technical questions and implementation details, refer to:
- **[Installation Issues](installation.md#troubleshooting)** - Common setup problems and solutions
- **[Configuration Problems](src/config.md#error-handling)** - Environment and API key issues
- **[Pipeline Errors](src/alerts_runner.md#error-handling)** - Runtime issues and debugging

---

*Last Updated: July 28, 2025*
