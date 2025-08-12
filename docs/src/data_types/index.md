# Data Types Documentation

Core data structures, type definitions, and enumerations used throughout the flightAlertsSystem flight alert system. This section provides comprehensive documentation for all data types that define the system's data model and processing structures.

---

## 🏷️ **System Enumerations**

### [**Enums**](enums.md)
Core system enumerations defining valid values for key system parameters.
- **REGION**: Geographic regions for flight searches (SA, NA, EU, AS, AF, OC)
- **SOURCE**: Airline data sources and partners (AZUL, GOL, LATAM, etc.)
- **CABIN**: Flight cabin classes (Y=Economy, W=Premium Economy, J=Business, F=First)
- **Usage**: Configuration validation, API parameter formatting, data filtering

---

## 🖼️ **Media and Content Types**

### [**Images**](images.md)
Image data structures for marketing content and visual materials.
- **Image Class**: Container for image URLs and binary data
- **BytesIO Integration**: In-memory image processing for PDF embedding
- **Usage**: Unsplash integration, PDF generation, marketing content

### [**PDF Types**](pdf_types.md)
Data structures for PDF report generation and document handling.
- **PDF_OBJ Class**: Container for PDF binary data and metadata
- **Email Integration**: Structured for Gmail attachment processing
- **Usage**: Report generation, email delivery, file management

---

## 📊 **Flight Data Structures**

### [**Summary Objects**](summary_objs.md)
High-level data structures for flight summary and reporting.
- **Flight Summary Types**: Aggregated flight information containers
- **Report Structures**: Data organization for dashboard and reporting
- **Usage**: Data aggregation, report generation, system monitoring

---

## 🏗️ **Data Type Architecture**

### **Type Hierarchy**
```
📂 data_types/
├── 🏷️ enums.py          # System enumerations
├── 🖼️ images.py         # Image data structures
├── 📄 pdf_types.py      # PDF document types
└── 📊 summary_objs.py   # Summary and reporting types
```

### **Common Patterns**

#### **Enum Usage**
```python
from data_types.enums import REGION, SOURCE, CABIN

# Configuration validation
if origin_region in REGION:
    process_region(origin_region)

# API parameter formatting
source_value = SOURCE.AZUL.value  # Returns "azul"
```

#### **Object Instantiation**
```python
from data_types.images import Image
from data_types.pdf_types import PDF_OBJ

# Create image object
image = Image(url="https://example.com/image.jpg", buffer=image_data)

# Create PDF object
pdf = PDF_OBJ(title="flight_report.pdf", bin=pdf_binary_data)
```

---

## 🔗 **Integration Points**

### **Configuration System**
Data types integrate with the configuration system for validation:
- **[Config Module](../config.md)** uses enums for parameter validation
- **Environment validation** ensures values match enum definitions
- **Error handling** provides clear feedback for invalid configurations

### **Service Integration**
Services use data types for structured data handling:
- **[Unsplash Service](../services/unsplash.md)** returns Image objects
- **[Gmail Service](../services/gmail.md)** accepts PDF_OBJ attachments
- **[PDF Generator](../logic/pdf_generator.md)** creates PDF_OBJ instances

### **Business Logic**
Logic modules rely on data types for processing:
- **[Filter Module](../logic/filter.md)** uses enums for categorization
- **[Trip Builder](../logic/trip_builder.md)** creates summary objects
- **Data aggregation** uses summary types for reporting

---

## 📋 **Data Type Specifications**

| Type Category | Purpose | Key Features | Integration |
|---------------|---------|--------------|-------------|
| **Enums** | System constants | Validation, API formatting | Config, Services |
| **Images** | Visual content | BytesIO buffers, URL handling | Unsplash, PDF gen |
| **PDF Types** | Document handling | Binary data, metadata | Gmail, Reports |
| **Summary Objects** | Data aggregation | Flight summaries, reporting | Logic, Analytics |

---

## 🛠️ **Development Guidelines**

### **Adding New Data Types**
1. **Define Structure**: Create clear class definitions with type hints
2. **Document Fields**: Provide comprehensive field documentation
3. **Integration Points**: Consider how other modules will use the type
4. **Validation**: Include input validation where appropriate
5. **Update Index**: Add new types to this index file

### **Type Design Principles**
- **Immutability**: Prefer immutable data structures where possible
- **Type Safety**: Use type hints and validation for better IDE support
- **Serialization**: Consider JSON serialization needs for API integration
- **Memory Efficiency**: Optimize for memory usage in data-intensive operations

### **Enum Guidelines**
- **Descriptive Names**: Use clear, descriptive enum names
- **Value Consistency**: Ensure enum values match external API expectations
- **Backward Compatibility**: Consider impact when modifying existing enums
- **Documentation**: Document the meaning and usage of each enum value

---

## 🔍 **Usage Examples**

### **Enum Validation**
```python
from data_types.enums import REGION, SOURCE, CABIN

def validate_flight_config(origin_region: str, source: str, cabin: str):
    """Validate flight configuration against enums"""
    
    # Validate region
    if not any(region.value == origin_region for region in REGION):
        raise ValueError(f"Invalid region: {origin_region}")
    
    # Validate source
    if not any(src.value == source for src in SOURCE):
        raise ValueError(f"Invalid source: {source}")
    
    # Validate cabin
    if not any(cb.value == cabin for cb in CABIN):
        raise ValueError(f"Invalid cabin: {cabin}")
```

### **Image Processing**
```python
from data_types.images import Image
from io import BytesIO

def process_marketing_images(image_urls: list[str]) -> list[Image]:
    """Process marketing images from URLs"""
    images = []
    
    for url in image_urls:
        # Download image data
        image_data = download_image(url)
        buffer = BytesIO(image_data)
        
        # Create Image object
        image = Image(url=url, buffer=buffer)
        images.append(image)
    
    return images
```

### **PDF Document Handling**
```python
from data_types.pdf_types import PDF_OBJ

def create_flight_report(flight_data: dict) -> PDF_OBJ:
    """Generate flight report PDF"""
    
    # Generate PDF content
    pdf_content = generate_pdf_from_data(flight_data)
    
    # Create PDF object
    report = PDF_OBJ(
        title=f"flight_report_{flight_data['date']}.pdf",
        bin=pdf_content
    )
    
    return report
```

---

*Data types documentation updated: July 28, 2025*
