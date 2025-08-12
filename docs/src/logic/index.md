# Logic Documentation

Core business logic modules for the flightAlertsSystem flight alert system. This section covers the essential processing logic that transforms raw flight data into actionable insights and user-friendly reports.

---

## 🔍 **Data Processing**

### [**Filter**](filter.md)
Advanced flight data filtering and search criteria application.
- **FilterEngine Class**: Core filtering logic for flight data
- **Multi-Criteria Filtering**: Price, time, route, and preference-based filters
- **Dynamic Filtering**: Real-time filter application and adjustment
- **Usage**: Flight search refinement, alert customization, data reduction

### [**Trip Builder**](trip_builder.md)
Intelligent trip construction and itinerary optimization.
- **TripBuilder Class**: Core trip planning and optimization logic
- **Multi-Segment Trips**: Complex itinerary building with connections
- **Route Optimization**: Best route selection based on multiple criteria
- **Usage**: Itinerary planning, route comparison, travel optimization

---

## 📄 **Report Generation**

### [**PDF Generator**](pdf_generator.md)
Comprehensive PDF report generation for flight alerts and summaries.
- **PDFGenerator Class**: Main PDF creation and formatting engine
- **Template System**: Flexible report templates for different use cases
- **Visual Integration**: Charts, maps, and images in PDF reports
- **Usage**: Alert reports, trip summaries, marketing materials

---

## 🏗️ **Logic Architecture**

### **Module Structure**
```
📂 logic/
├── 🔍 filter.py          # Flight data filtering
├── ✈️ trip_builder.py    # Trip planning and optimization
└── 📄 pdf_generator.py   # PDF report generation
```

### **Processing Pipeline**
```
Raw Flight Data → Filter → Trip Builder → PDF Generator → User Reports
      ↓              ↓           ↓              ↓
   External APIs → Filtering → Optimization → Formatting → Delivery
```

### **Handler Pattern**
All logic modules follow consistent patterns:
- **Deferred Initialization**: Configuration loaded when needed
- **State Management**: Integration with global state system
- **Error Recovery**: Comprehensive exception handling
- **Performance Optimization**: Efficient processing algorithms

---

## 🎯 **Filtering System**

### **Filter Categories**

#### **Price Filters**
- **Budget Range**: Min/max price constraints
- **Currency Conversion**: Multi-currency price comparison
- **Award Pricing**: Mileage program cost filtering
- **Dynamic Pricing**: Real-time price change tracking

#### **Time Filters**
- **Departure Windows**: Preferred departure time ranges
- **Duration Limits**: Maximum flight duration constraints
- **Connection Limits**: Maximum layover time restrictions
- **Schedule Preferences**: Morning/afternoon/evening preferences

#### **Route Filters**
- **Airport Preferences**: Preferred departure/arrival airports
- **Airline Preferences**: Preferred/excluded airline carriers
- **Aircraft Type**: Equipment preferences and restrictions
- **Alliance Preferences**: Star Alliance, OneWorld, SkyTeam focus

#### **Quality Filters**
- **Cabin Class**: Economy, premium economy, business, first
- **Seat Selection**: Available seat preferences
- **Service Quality**: Airline rating and service quality metrics
- **Amenity Preferences**: Wi-Fi, meals, entertainment systems

---

## ✈️ **Trip Building Logic**

### **Optimization Algorithms**

#### **Route Optimization**
```python
from logic.trip_builder import TripBuilder

# Initialize trip builder
builder = TripBuilder()
builder.load()

# Build optimized trip
trip = builder.build_optimal_trip(
    origin="GRU",
    destination="LAX",
    dates=["2025-08-15", "2025-08-22"],
    preferences={
        "max_connections": 1,
        "preferred_airlines": ["LATAM", "American"],
        "cabin_class": "business"
    }
)
```

#### **Multi-City Trips**
- **Complex Itineraries**: Support for multi-destination trips
- **Open-Jaw Routing**: Different departure/return airports
- **Stopover Optimization**: Strategic layover utilization
- **Cost Minimization**: Best price across multiple segments

#### **Connection Analysis**
- **Minimum Connection Time**: Airport-specific MCT compliance
- **Immigration Requirements**: International connection considerations
- **Terminal Changes**: Inter-terminal transfer time calculation
- **Baggage Handling**: Through-checking availability analysis

---

## 📊 **PDF Report Generation**

### **Report Types**

#### **Flight Alert Reports**
```python
from logic.pdf_generator import PDFGenerator

# Initialize PDF generator
pdf_gen = PDFGenerator()
pdf_gen.load()

# Generate flight alert report
report = pdf_gen.generate_alert_report(
    flights=flight_data,
    user_preferences=user_config,
    include_charts=True,
    include_maps=True
)
```

#### **Trip Summary Reports**
- **Comprehensive Itineraries**: Complete trip planning documents
- **Visual Timeline**: Graphical trip timeline with connections
- **Cost Breakdown**: Detailed pricing analysis and comparisons
- **Booking Information**: Direct links and booking instructions

#### **Market Analysis Reports**
- **Price Trend Analysis**: Historical pricing data visualization
- **Route Comparison**: Multiple route option analysis
- **Seasonal Patterns**: Best booking time recommendations
- **Award Availability**: Mileage program opportunity analysis

### **Visual Elements**
- **Charts and Graphs**: Price trends, route maps, timeline visualizations
- **Marketing Images**: Destination photos from Unsplash integration
- **Branding Elements**: Consistent visual identity and formatting
- **Interactive Elements**: QR codes for booking links and mobile access

---

## 🔗 **Integration Points**

### **Service Integration**
Logic modules integrate with external services:
- **[Seats.aero Service](../services/seats_aero.md)** provides raw flight data for processing
- **[Google Sheets Service](../services/google_sheets.md)** stores filtering preferences and trip data
- **[Unsplash Service](../services/unsplash.md)** provides destination images for PDF reports
- **[OpenAI Service](../services/openai.md)** generates intelligent trip recommendations

### **Data Type Integration**
Logic modules use structured data types:
- **[Enums](../data_types/enums.md)** for filtering parameters and trip preferences
- **[Summary Objects](../data_types/summary_objs.md)** for trip data organization
- **[PDF Types](../data_types/pdf_types.md)** for report generation and delivery
- **[Images](../data_types/images.md)** for visual content in PDF reports

### **Currency Integration**
Logic modules incorporate pricing analysis:
- **[Cash Module](../currencies/cash.md)** for multi-currency price filtering and reporting
- **[Mileage Module](../currencies/mileage.md)** for award flight analysis and optimization

---

## 📋 **Logic Processing Matrix**

| Module | Input | Processing | Output | Performance |
|--------|-------|------------|--------|-------------|
| **Filter** | Raw flight data | Multi-criteria filtering | Filtered results | Sub-second response |
| **Trip Builder** | Flight options | Route optimization | Optimized itineraries | < 5 second processing |
| **PDF Generator** | Trip data | Report formatting | PDF documents | < 10 second generation |

---

## 🛠️ **Development Guidelines**

### **Filter Development**
1. **Criteria Definition**: Clearly define filter parameters and logic
2. **Performance Optimization**: Efficient filtering algorithms for large datasets
3. **User Interface**: Intuitive filter configuration and management
4. **Validation**: Input validation and error handling
5. **Testing**: Comprehensive filter accuracy testing

### **Trip Building Algorithms**
1. **Optimization Strategy**: Balance price, convenience, and user preferences
2. **Constraint Handling**: Manage complex routing constraints and requirements
3. **Scalability**: Handle large route networks and connection possibilities
4. **Real-time Processing**: Quick response times for interactive trip building
5. **Fallback Options**: Alternative suggestions when optimal routes unavailable

### **PDF Generation Best Practices**
1. **Template Design**: Flexible, maintainable report templates
2. **Performance**: Efficient rendering for large reports with many images
3. **Mobile Compatibility**: Responsive design for mobile viewing
4. **Accessibility**: Screen reader compatibility and clear visual hierarchy
5. **Branding Consistency**: Maintain visual identity across all report types

---

## 🔍 **Usage Examples**

### **Advanced Filtering**
```python
from logic.filter import FilterEngine

# Initialize filter engine
filter_engine = FilterEngine()
filter_engine.load()

# Apply complex filters
filtered_flights = filter_engine.apply_filters(
    flights=raw_flight_data,
    filters={
        "price_range": {"min": 300, "max": 800, "currency": "USD"},
        "departure_window": {"start": "06:00", "end": "10:00"},
        "max_connections": 1,
        "preferred_airlines": ["LATAM", "GOL"],
        "cabin_class": "economy",
        "max_duration": 12  # hours
    }
)

# Get filter statistics
stats = filter_engine.get_filter_stats(filtered_flights)
print(f"Filtered {len(filtered_flights)} flights from {stats.total_input}")
```

### **Intelligent Trip Building**
```python
from logic.trip_builder import TripBuilder

# Initialize trip builder
trip_builder = TripBuilder()
trip_builder.load()

# Build complex multi-city trip
trip = trip_builder.build_multi_city_trip(
    itinerary=[
        {"city": "São Paulo", "dates": ["2025-08-01", "2025-08-05"]},
        {"city": "Buenos Aires", "dates": ["2025-08-05", "2025-08-10"]},
        {"city": "Santiago", "dates": ["2025-08-10", "2025-08-15"]},
        {"city": "São Paulo", "dates": ["2025-08-15"]}
    ],
    preferences={
        "budget": 2000,
        "currency": "USD",
        "cabin_class": "business",
        "airline_alliance": "oneworld"
    }
)

# Analyze trip options
analysis = trip_builder.analyze_trip_options(trip)
best_option = analysis.recommend_best_option()
```

### **Comprehensive PDF Report**
```python
from logic.pdf_generator import PDFGenerator

# Initialize PDF generator
pdf_gen = PDFGenerator()
pdf_gen.load()

# Generate comprehensive trip report
report = pdf_gen.generate_comprehensive_report(
    trip_data=optimized_trip,
    user_preferences=user_config,
    options={
        "include_price_trends": True,
        "include_destination_images": True,
        "include_weather_forecast": True,
        "include_booking_links": True,
        "include_travel_tips": True,
        "template": "premium"
    }
)

# Customize report branding
branded_report = pdf_gen.apply_branding(
    report=report,
    branding={
        "logo": company_logo,
        "colors": brand_colors,
        "fonts": brand_fonts,
        "footer_text": "Powered by flightAlertsSystem"
    }
)
```

---

## 📈 **Performance Analytics**

### **Processing Metrics**
- **Filter Performance**: Average filtering time per 1000 flights
- **Trip Building Speed**: Optimization time for different complexity levels
- **PDF Generation Time**: Report creation time by template and content
- **Memory Usage**: Resource consumption during processing operations

### **Quality Metrics**
- **Filter Accuracy**: Precision and recall of filtering operations
- **Trip Optimization Quality**: Cost savings and convenience improvements
- **Report Completeness**: Information coverage and visual quality scores
- **User Satisfaction**: Feedback on generated reports and trip suggestions

---

*Logic documentation updated: July 28, 2025*
