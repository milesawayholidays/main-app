# API Documentation

The FlightAlertsGroup system provides RESTful API endpoints for programmatic access to flight search and alert functionality.

## Base URL
```
http://milesawayholidays.com/api/ if deployed

or 

http://localhost:[PORT]/api/ if running locally
```

## Authentication
Currently, the API does not require authentication. Consider implementing authentication for production use.

## Endpoints

### Flight Search

#### Region to Region Search
Search for flights between geographical regions.

**Endpoint:** `GET api/from-region-to-region`

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| origin   | string | Yes | - | Origin region name (South America, North America, Europe, Asia, Oceania, Africa) |
| destination | string | Yes | - | Destination region name |
| start_date | string | No | - | Start date in YYYY-MM-DD format |
| end_date | string | No | - | End date in YYYY-MM-DD format |
| cabins | array[string] | No | - | economy, premium, business, first |
| min_return_days | integer | No | 1 | Minimum return days |
| max_return_days | integer | No | 60 | Maximum return days |
| n | integer | No | 1 | Number of results |
| deepness | integer | No | 1 | Search depth |

**Example Request:**
```http
GET api/from-region-to-region?origin=South America&destination=North America&start_date=2025-08-15&cabins=economy&cabins=business&n=3
```

**Example Response:**
```json
{
  "statusCode": 200,
  "message": "Alerts runner executed successfully."
}
```

#### Country to World Search
Search for flights from a specific country to worldwide destinations.

**Endpoint:** `GET api/from-country-to-world`

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| country | string | Yes | - | Country code for origin |
| source | string | No | - | Airline source filter |
| start_date | string | No | - | Start date in YYYY-MM-DD format |
| end_date | string | No | - | End date in YYYY-MM-DD format |
| cabins | array[string] | No | - | economy, premium, business, first |
| min_return_days | integer | No | 1 | Minimum return days |
| max_return_days | integer | No | 60 | Maximum return days |
| n | integer | No | 1 | Number of results |
| deepness | integer | No | 1 | Search depth |

**Example Request:**
```http
GET api/from-country-to-world?country=BR&source=azul&cabins=premium&n=5
```

## Error Responses

### 400 Bad Request
```json
{
  "statusCode": 400,
  "message": "Origin and destination must be specified."
}
```

### 500 Internal Server Error
```json
{
  "statusCode": 500,
  "message": "Error description here"
}
```

## Region Names (for API parameters)
- `South America`
- `North America` 
- `Europe`
- `Asia`
- `Oceania`
- `Africa`

## Region Codes (enum values)
- `SA` - South America
- `NA` - North America
- `EU` - Europe
- `AS` - Asia
- `OC` - Oceania
- `AF` - Africa

## Cabin Classes
- `economy` - Economy class
- `premium` - Economy class
- `business` - Business class  
- `first` - First class

## Usage Examples

### Python with requests
```python
import requests

# Region to region search
response = requests.get('http://localhost:8000/api/from-region-to-region', params={
    'origin': 'South America',
    'destination': 'North America',
    'start_date': '2025-08-15',
    'cabins': ['economy', 'business'],  
    'n': 3
})

print(response.json())
```

### cURL
```bash
curl -X GET "http://localhost:8000/api/from-region-to-region?origin=South%20America&destination=North%20America&cabins=economy&n=3" \
     -H "Content-Type: application/json"
```

### JavaScript/Fetch
```javascript
const response = await fetch('/from-region-to-region?origin=South%20America&destination=North%20America&cabins=economy&n=3');
const data = await response.json();
console.log(data);
```

## Interactive Documentation
When the server is running, you can access interactive API documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Rate Limiting
Currently, no rate limiting is implemented. Consider adding rate limiting for production deployment.

## Production Considerations
- Implement authentication/authorization
- Add rate limiting
- Enable CORS for web applications
- Use HTTPS in production
- Monitor API usage and performance
