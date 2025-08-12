# Services Documentation

External API integrations and service components for the flightAlertsSystem flight alert system. This section covers all external service integrations including authentication, data retrieval, content generation, and communication services.

---

## 📧 **Communication Services**

### [**Gmail Service**](gmail.md)
Email delivery service for flight alert reports and administrative notifications.
- **Type**: Function-based service  
- **Purpose**: Secure SMTP email delivery with PDF attachments
- **Key Features**: Gmail integration, PDF attachments, self-sending capability
- **Authentication**: Google App Password required

### [**WhatsApp Service**](whatsapp.md) 🚧
Future WhatsApp messaging integration for automated alert distribution.
- **Type**: Placeholder (future development)
- **Purpose**: Direct WhatsApp group message delivery
- **Current Status**: Content generation handled by OpenAI service
- **Planned Features**: Automated distribution, group management, analytics

---

## 🤖 **AI and Content Services**

### [**OpenAI Service**](openAI.md)
AI-powered WhatsApp post generation for marketing flight deals.
- **Type**: Class-based service with deferred initialization
- **Purpose**: Generate compelling Portuguese marketing content
- **Key Features**: GPT-4o integration, marketing optimization, accessibility focus
- **Authentication**: OpenAI API key required

### [**Unsplash Service**](unsplash.md)
Travel image fetching service for visual marketing content.
- **Type**: Function-based service
- **Purpose**: High-quality destination imagery for marketing materials
- **Key Features**: Travel-focused search, multiple image retrieval, BytesIO processing
- **Authentication**: Unsplash Access Key required

---

## 📊 **Data Services**

### [**Google Sheets Service**](google_sheets.md)
Comprehensive data storage and management service.
- **Type**: Hierarchical class structure (WorkSheet → SpreadSheet → GoogleSheetsHandler)
- **Purpose**: Flight data storage, tracking, and analysis
- **Key Features**: Automated spreadsheet creation, data export, worksheet management
- **Authentication**: Google Service Account credentials required

### [**Seats.aero Service**](seats_aero.md)
Primary flight data retrieval service from airline partner APIs.
- **Type**: Class-based service with deferred initialization
- **Purpose**: Comprehensive flight availability data access
- **Key Features**: Cached searches, bulk availability, individual trip details
- **Authentication**: Seats.aero Partner API key required

---

## 🏗️ **Service Architecture**

### **Common Patterns**

#### **Initialization Patterns**
```python
# Class-based services (deferred initialization)
handler = ServiceHandler()
handler.load(api_key)

# Function-based services (direct usage)
from services.service_name import function_name
result = function_name(parameters)
```

#### **Singleton Usage**
```python
# Import singleton instances
from services.seats_aero import handler as seats_handler
from services.openAI import handler as openai_handler
from services.google_sheets import handler as sheets_handler
```

#### **Error Handling**
All services integrate with the global state logging system:
```python
from global_state import state
state.logger.info("Operation successful")
state.logger.error("Operation failed")
```

---

## 🔑 **Authentication Requirements**

| Service | Authentication Type | Configuration | Purpose |
|---------|-------------------|---------------|---------|
| **Gmail** | Google App Password | `GOOGLE_EMAIL`, `GOOGLE_PASS` | Email delivery |
| **Google Sheets** | Service Account | `sheets_api_key.json` | Data storage |
| **OpenAI** | API Key | Passed to `load()` method | Content generation |
| **Seats.aero** | Partner API Key | Passed to `load()` method | Flight data |
| **Unsplash** | Access Key | `UNSPLASH_ACCESS_KEY` | Image fetching |
| **WhatsApp** | TBD | Future implementation | Message delivery |

---

## 🔄 **Service Integration Flow**

### **Data Collection Pipeline**
1. **[Seats.aero](seats_aero.md)** → Fetch flight availability data
2. **[Logic Modules](../logic/index.md)** → Process and filter data
3. **[Content Generation](#ai-and-content-services)** → Create marketing materials

### **Content Creation Pipeline**
1. **[OpenAI](openAI.md)** → Generate WhatsApp marketing posts
2. **[Unsplash](unsplash.md)** → Fetch destination images
3. **[PDF Generator](../logic/pdf_generator.md)** → Create formatted reports

### **Distribution Pipeline**
1. **[Google Sheets](google_sheets.md)** → Store data for tracking
2. **[Gmail](gmail.md)** → Email PDF reports to administrators
3. **[WhatsApp](whatsapp.md)** → Future automated message delivery

---

## 📋 **Service Status**

| Service | Status | Implementation | Documentation |
|---------|--------|----------------|---------------|
| **Gmail** | ✅ Active | Function-based | Complete |
| **Google Sheets** | ✅ Active | Class hierarchy | Complete |
| **OpenAI** | ✅ Active | Class-based | Complete |
| **Seats.aero** | ✅ Active | Class-based | Complete |
| **Unsplash** | ✅ Active | Function-based | Complete |
| **WhatsApp** | 🚧 Planned | Placeholder | Roadmap only |

---

## 🛠️ **Development Guidelines**

### **Adding New Services**
1. **Choose Pattern**: Class-based (complex) vs Function-based (simple)
2. **Follow Patterns**: Use deferred initialization for class-based services
3. **Integration**: Include global state logging and error handling
4. **Documentation**: Create comprehensive documentation with examples
5. **Update Index**: Add service to this index file

### **Service Dependencies**
- **Global State**: All services should integrate with centralized logging
- **Configuration**: Use config module for environment variables
- **Error Handling**: Follow consistent exception patterns
- **Testing**: Include authentication validation and error scenarios

### **API Integration Best Practices**
- **Rate Limiting**: Respect external API limits and implement caching where appropriate
- **Error Recovery**: Handle network failures and API errors gracefully
- **Security**: Store credentials securely and validate authentication
- **Logging**: Log all external API interactions for debugging and monitoring

---

*Service documentation updated: July 28, 2025*
