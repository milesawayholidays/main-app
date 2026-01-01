# API Documentation

This repo exposes a FastAPI app under the `/api` prefix.

## Base URL

- Local backend (recommended): `http://localhost:4000/api`
- Docker / Render (single service): `https://<your-domain>/api`

## Authentication

No authentication is implemented.

## Endpoints

### Health

**Endpoint:** `GET /api/health`

**Response:**
```json
{ "status": "API is running", "version": "..." }
```

### Flights

The flight search endpoints return a wrapper:

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

Notes:
- `single_trips` contains one-way trip rows (and also the outbound/return legs for round trips).
- `round_trips` is the relational pairing between outbound and return.
- `round_options` is the grouped, user-facing round-trip routes (one per city-pair / cabin).

#### One-way

**Endpoint:** `GET /api/flights/oneway`

**Query parameters (all optional unless noted):**

| Parameter | Type | Description |
|---|---:|---|
| origin_regions | list[string] | Regions to include (repeat the param for multiple). Accepts region **codes** (`NA`) and **names** (`North America`). |
| destination_regions | list[string] | Same as `origin_regions`. |
| origin_countries | list[string] | Country names as used by `data/airports.csv` mapping. |
| destination_countries | list[string] | Country names as used by `data/airports.csv` mapping. |
| origin_cities | list[string] | City names as used by `data/airports.csv` mapping. |
| destination_cities | list[string] | City names as used by `data/airports.csv` mapping. |
| origin_airports | list[string] | IATA codes (e.g., `YYZ`). |
| destination_airports | list[string] | IATA codes. |
| sources | list[string] | `azul`, `smiles`, `qantas` |
| cabins | list[string] | Cabin **names** (`economy`, `premium`, `business`, `first`) or cabin **codes** (`y`, `w`, `j`, `f`). |
| min_cost | float | Minimum total cost filter. |
| max_cost | float | Maximum total cost filter. |
| min_remaining_seats | int | Minimum remaining seats filter. |
| start_date | string | `YYYY-MM-DD` |
| end_date | string | `YYYY-MM-DD` |
| n | int | Results per **region-pair per cabin**. Server clamps to `1..8` (default `1`). |
| deepness | int | Seats.aero pagination depth. Server clamps to `1..3` (default `1`). |

**Example (cURL):**

```bash
curl "http://localhost:4000/api/flights/oneway?origin_regions=NA&destination_regions=AS&cabins=business&n=2&deepness=1"
```

#### Round-trip

**Endpoint:** `GET /api/flights/roundtrip`

Same parameters as one-way, plus:

| Parameter | Type | Description |
|---|---:|---|
| min_return_days | int | Minimum trip length in days. |
| max_return_days | int | Maximum trip length in days. |

**Example (cURL):**

```bash
curl "http://localhost:4000/api/flights/roundtrip?origin_regions=EU&destination_regions=NA&cabins=business&min_return_days=5&max_return_days=14&n=1"
```

### WhatsApp Post Generation

**Endpoint:** `POST /api/get-post`

This generates WhatsApp post text from selected rows.

**Request body:**
```json
{
  "rows": [
    {
      "id": "...",
      "origin_city": "...",
      "origin_country": "...",
      "destination_city": "...",
      "destination_country": "...",
      "departure_date": "...",
      "return_date": "...",
      "cabin": "...",
      "program": "...",
      "mileage_cost": "...",
      "taxes": "...",
      "total_cost": "...",
      "remaining_seats": "...",
      "booking_link": "..."
    }
  ]
}
```

**Response:**
```json
{ "status": 200, "data": { "posts": [], "skipped": [] } }
```

## Regions / Sources / Cabins

### Regions
- Names: `North America`, `South America`, `Africa`, `Asia`, `Europe`, `Oceania`
- Codes: `NA`, `SA`, `AF`, `AS`, `EU`, `OC`

`origin_regions` / `destination_regions` accept either form (case-insensitive).

### Sources
- `azul`
- `smiles`
- `qantas`

### Cabins
- Names: `economy`, `premium`, `business`, `first`
- Codes: `y`, `w`, `j`, `f`

## Interactive Documentation

When the backend is running locally you can use:

- Swagger UI: `http://localhost:4000/docs`
- ReDoc: `http://localhost:4000/redoc`

In production (Docker/Render), these are available at:

- Swagger UI: `https://<your-domain>/docs`
- ReDoc: `https://<your-domain>/redoc`
