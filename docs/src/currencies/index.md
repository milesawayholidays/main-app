# Currencies Documentation

Currency conversion and pricing modules for the flightAlertsSystem flight alert system. This section covers both cash-based pricing and mileage program integration for comprehensive flight cost analysis.

---

## 💰 **Cash Currency System**

### [**Cash**](cash.md)
Cash-based pricing and currency conversion functionality.
- **CashHandler Class**: Main interface for cash pricing operations
- **Multi-Currency Support**: Real-time exchange rate integration
- **Price Conversion**: Automatic currency conversion for international flights
- **Usage**: Flight pricing, cost comparison, budget analysis

---

## ✈️ **Mileage Program Integration**

### [**Mileage**](mileage.md)
Airline mileage program integration and points valuation.
- **MileageHandler Class**: Core mileage program management
- **Points Valuation**: Calculate cash equivalent of award flights
- **Program Integration**: Support for major airline loyalty programs
- **Usage**: Award flight search, points optimization, value comparison

---

## 🏗️ **Currency Architecture**

### **Module Structure**
```
📂 currencies/
├── 💰 cash.py          # Cash pricing and conversion
└── ✈️ mileage.py       # Mileage program integration
```

### **Handler Pattern**
Both currency modules follow a consistent handler pattern:
- **Deferred Initialization**: Configuration loaded on first use
- **Singleton Access**: Global instances through handler registry
- **Error Handling**: Comprehensive exception management
- **State Management**: Integration with global state system

---

## 💱 **Exchange Rate Integration**

### **Real-Time Rates**
The cash module integrates with external exchange rate APIs:
```python
from currencies.cash import CashHandler

# Initialize cash handler
cash_handler = CashHandler()
cash_handler.load()

# Convert currency
usd_price = cash_handler.convert(amount=100, from_currency="BRL", to_currency="USD")
```

### **Supported Currencies**
- **BRL**: Brazilian Real (primary currency)
- **USD**: US Dollar (international standard)
- **EUR**: Euro (European flights)
- **GBP**: British Pound (UK flights)
- **Additional**: Extensible for other currencies as needed

---

## 🎯 **Points Valuation System**

### **Award Flight Analysis**
The mileage module provides comprehensive award flight valuation:
```python
from currencies.mileage import MileageHandler

# Initialize mileage handler
mileage_handler = MileageHandler()
mileage_handler.load()

# Calculate points value
cash_equivalent = mileage_handler.calculate_value(
    points_required=50000,
    program="LATAM",
    route="GRU-MIA"
)
```

### **Loyalty Program Support**
- **LATAM Pass**: Primary Brazilian program
- **GOL Smiles**: Alternative Brazilian program
- **Star Alliance**: International program integration
- **OneWorld**: Alliance program support
- **SkyTeam**: Comprehensive alliance coverage

---

## 🔗 **Integration Points**

### **Service Integration**
Currency modules integrate with external services:
- **[Seats.aero Service](../services/seats_aero.md)** uses pricing for flight comparison
- **[Google Sheets Service](../services/google_sheets.md)** stores currency conversion rates
- **[OpenAI Service](../services/openai.md)** incorporates pricing in summaries

### **Logic Integration**
Business logic modules use currency data:
- **[Filter Module](../logic/filter.md)** applies price-based filtering
- **[Trip Builder](../logic/trip_builder.md)** includes cost analysis
- **Price comparison** logic uses both cash and mileage valuations

### **Configuration**
Currency settings managed through configuration:
- **[Config Module](../config.md)** defines default currencies and programs
- **Environment variables** store API keys for exchange rate services
- **User preferences** determine primary currency and program focus

---

## 📊 **Currency Features Matrix**

| Feature | Cash Module | Mileage Module | Implementation |
|---------|-------------|----------------|----------------|
| **Real-time Rates** | ✅ | ✅ | External API integration |
| **Multi-Currency** | ✅ | N/A | Major currencies supported |
| **Program Support** | N/A | ✅ | Major airline programs |
| **Conversion Cache** | ✅ | ✅ | Performance optimization |
| **Historical Data** | ✅ | ⚠️ | Limited historical tracking |
| **Alert Integration** | ✅ | ✅ | Price change notifications |

---

## 🛠️ **Development Guidelines**

### **Adding Currency Support**
1. **Exchange Rate API**: Integrate with reliable exchange rate service
2. **Conversion Logic**: Implement bi-directional conversion methods
3. **Caching Strategy**: Cache rates to minimize API calls
4. **Error Handling**: Handle API failures gracefully
5. **Testing**: Comprehensive unit tests for conversion accuracy

### **Mileage Program Integration**
1. **Program Research**: Understand program rules and restrictions
2. **Valuation Model**: Develop accurate points valuation algorithm
3. **Award Availability**: Consider seat availability in valuations
4. **Seasonal Adjustments**: Account for peak/off-peak pricing
5. **Documentation**: Maintain program-specific documentation

### **Performance Considerations**
- **Rate Caching**: Cache exchange rates to reduce API calls
- **Batch Processing**: Process multiple conversions efficiently
- **Memory Usage**: Optimize for memory efficiency in large datasets
- **API Limits**: Respect rate limits of external services

---

## 🔍 **Usage Examples**

### **Cash Currency Conversion**
```python
from currencies.cash import CashHandler

# Initialize handler
cash = CashHandler()
cash.load()

# Convert flight price from USD to BRL
brl_price = cash.convert(
    amount=299.99,
    from_currency="USD",
    to_currency="BRL"
)

# Format for display
formatted_price = cash.format_currency(brl_price, "BRL")
print(f"Flight price: {formatted_price}")  # Flight price: R$ 1,649.95
```

### **Mileage Value Calculation**
```python
from currencies.mileage import MileageHandler

# Initialize handler
mileage = MileageHandler()
mileage.load()

# Calculate award flight value
award_value = mileage.calculate_award_value(
    origin="GRU",
    destination="MIA",
    points_required=50000,
    program="LATAM_PASS",
    cabin_class="business"
)

# Compare with cash price
cash_equivalent = award_value.cash_equivalent
points_per_cent = award_value.points_per_cent
value_rating = award_value.value_rating  # "excellent", "good", "poor"
```

### **Integrated Price Analysis**
```python
from currencies.cash import CashHandler
from currencies.mileage import MileageHandler

def analyze_flight_pricing(flight_data: dict) -> dict:
    """Comprehensive flight pricing analysis"""
    
    # Initialize handlers
    cash = CashHandler()
    mileage = MileageHandler()
    cash.load()
    mileage.load()
    
    # Get cash prices in multiple currencies
    cash_prices = {
        "USD": flight_data["price_usd"],
        "BRL": cash.convert(flight_data["price_usd"], "USD", "BRL"),
        "EUR": cash.convert(flight_data["price_usd"], "USD", "EUR")
    }
    
    # Get award flight options
    award_options = mileage.get_award_options(
        origin=flight_data["origin"],
        destination=flight_data["destination"],
        date=flight_data["date"]
    )
    
    # Calculate best value option
    best_value = determine_best_value(cash_prices, award_options)
    
    return {
        "cash_prices": cash_prices,
        "award_options": award_options,
        "recommendation": best_value
    }
```

---

## 📈 **Pricing Analytics**

### **Market Analysis**
Currency modules support market analysis features:
- **Price Trend Tracking**: Historical price data analysis
- **Currency Impact**: Exchange rate impact on international flights
- **Award Availability**: Mileage program seat availability tracking
- **Value Alerts**: Notifications for exceptional pricing opportunities

### **Reporting Integration**
Pricing data flows into system reporting:
- **Daily Price Reports**: Automated currency conversion summaries
- **Award Value Reports**: Best mileage redemption opportunities
- **Market Intelligence**: Currency trend impact on flight pricing
- **User Preferences**: Personalized pricing based on user's preferred currency/programs

---

*Currency documentation updated: July 28, 2025*
