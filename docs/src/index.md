# Source Code Documentation

Technical documentation for all components of the flightAlertsSystem flight alert system. This section provides comprehensive API references, implementation details, and integration guides for developers.

---

## 📁 Core System Components

### **🎯 Main Application**
- [**main.py**](main.md) - Application entry point and system initialization
- [**alerts_runner.py**](alerts_runner.md) - Core flight alert processing pipeline
- [**config.py**](config.md) - Configuration management and environment validation
- [**global_state.py**](global_state.md) - Centralized state tracking and logging

---

## 📁 Module Categories

### **🌐 [Services](services/index.md)**
External API integrations and data sources
- [Gmail](services/gmail.md) - Email delivery service
- [Google Sheets](services/google_sheets.md) - Data storage and management
- [OpenAI](services/openAI.md) - WhatsApp post generation
- [Seats.aero](services/seats_aero.md) - Flight data retrieval
- [Unsplash](services/unsplash.md) - Travel image fetching
- [WhatsApp](services/whatsapp.md) - Future messaging integration

### **🏗️ [Data Types](data_types/index.md)**
Core data structures and type definitions
- [Enums](data_types/enums.md) - System enumerations (regions, sources, cabins)
- [Images](data_types/images.md) - Image data structures
- [PDF Types](data_types/pdf_types.md) - PDF generation data types
- [Summary Objects](data_types/summary_objs.md) - Flight summary data structures

### **🧠 [Business Logic](logic/index.md)**
Core processing and filtering algorithms
- [Filter](logic/filter.md) - Flight filtering and ranking algorithms
- [PDF Generator](logic/pdf_generator.md) - Report generation engine
- [Trip Builder](logic/trip_builder.md) - Flight trip construction and formatting

### **💰 [Currency Handling](currencies/index.md)**
Financial calculations and currency conversion
- [Cash](currencies/cash.md) - Currency conversion and cash handling
- [Mileage](currencies/mileage.md) - Airline mileage program integration

---

## 🏛️ Architecture Overview

The system follows a modular architecture with clear separation of concerns:

```
📂 flightAlertsSystem/
├── 🎯 main.py                 # Entry point & initialization
├── 🔄 alerts_runner.py        # Main processing pipeline
├── ⚙️ config.py               # Configuration management
├── 📊 global_state.py         # State tracking & logging
├── 🌐 services/               # External integrations
├── 🏗️ data_types/             # Data structures
├── 🧠 logic/                  # Business logic
└── 💰 currencies/             # Financial utilities
```

---

## 🔗 Key Design Patterns

### **Singleton Pattern**
Most services use singleton instances for application-wide access:
```python
from services.seats_aero import handler as seats_handler
from services.openAI import handler as openai_handler
```

### **Deferred Initialization**
Services follow a two-step initialization pattern:
```python
handler = ServiceHandler()  # Create instance
handler.load(api_key)       # Initialize with credentials
```

### **Global State Management**
Centralized logging and state tracking:
```python
from global_state import state
state.logger.info("Operation completed")
state.update_flag('operationCompleted')
```

---

## 📋 Integration Patterns

### **Service Integration**
- **Configuration-driven**: All services use centralized config management
- **Logging integration**: Unified logging through global state
- **Error handling**: Consistent exception patterns across services

### **Data Flow**
1. **Data Collection** → Services fetch from external APIs
2. **Processing** → Logic modules filter and transform data
3. **Content Creation** → Generate marketing materials and reports
4. **Distribution** → Deliver via email and store in sheets

### **Error Recovery**
- **Graceful degradation**: System continues with reduced functionality
- **Comprehensive logging**: All operations logged for debugging
- **State persistence**: System state saved for recovery and analysis

---

## 🛠️ Development Guidelines

### **Adding New Services**
1. Inherit common patterns (singleton, deferred initialization)
2. Integrate with global state for logging
3. Follow consistent error handling patterns
4. Document with comprehensive examples

### **Modifying Existing Components**
1. Update both code and documentation
2. Maintain backward compatibility where possible
3. Test integration points thoroughly
4. Update relevant index files

### **Testing and Debugging**
1. Use global state logs for runtime debugging
2. Check saved state files in `logs/` directory
3. Monitor API rate limits and quotas
4. Validate configuration before deployment

---

*This documentation is automatically maintained and reflects the current system architecture as of July 28, 2025.*
