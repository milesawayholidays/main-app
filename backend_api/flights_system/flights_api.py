from fastapi import APIRouter, Query

from src.data_types.Flight import FlightQuery
from src.orchestrator import find_trips

flights_router = APIRouter()

@flights_router.get("/oneway")
def get_oneway_flights(
    origin_regions: list[str] | None = None,
    destination_regions: list[str] | None = None,
    origin_countries: list[str] | None = None,
    destination_countries: list[str] | None = None,
    origin_cities: list[str] | None = None,
    destination_cities: list[str] | None = None,
    origin_airports: list[str] | None = None,
    destination_airports: list[str] | None = None,
    sources: list[str] | None = None,
    cabins: list[str] | None = None,
    min_cost: float | None = None,
    max_cost: float | None = None,
    min_remaining_seats: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    n: int = Query(1, ge=1, le=8),
    deepness: int = Query(1, ge=1, le=3)):
    """Retrieve one-way flights based on various filters."""
    query = FlightQuery()
    query.build_query(
        origin_regions=origin_regions,
        destination_regions=destination_regions,
        origin_countries=origin_countries,
        destination_countries=destination_countries,
        origin_cities=origin_cities,
        destination_cities=destination_cities,
        origin_airports=origin_airports,
        destination_airports=destination_airports,
        sources=sources,
        cabins=cabins,
        min_cost=min_cost,  
        max_cost=max_cost,
        min_remaining_seats=min_remaining_seats)
    
    return find_trips(
        query=query,
        start_date=start_date,
        end_date=end_date,
        n=n,
        deepness=deepness,
        oneway=True)

@flights_router.get("/roundtrip")
def get_roundtrip_flights(
    origin_regions: list[str] | None = None,
    destination_regions: list[str] | None = None,
    origin_countries: list[str] | None = None,
    destination_countries: list[str] | None = None,
    origin_cities: list[str] | None = None,
    destination_cities: list[str] | None = None,
    origin_airports: list[str] | None = None,
    destination_airports: list[str] | None = None,
    sources: list[str] | None = None,
    cabins: list[str] | None = None,
    min_cost: float | None = None,
    max_cost: float | None = None,
    min_return_days: int | None = None,
    max_return_days: int | None = None,
    min_remaining_seats: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    n: int = Query(1, ge=1, le=8),
    deepness: int = Query(1, ge=1, le=3)):
    """Retrieve round-trip flights based on various filters."""
    query = FlightQuery()
    query.build_query(
        origin_regions=origin_regions,
        destination_regions=destination_regions,
        origin_countries=origin_countries,
        destination_countries=destination_countries,
        origin_cities=origin_cities,
        destination_cities=destination_cities,
        origin_airports=origin_airports,
        destination_airports=destination_airports,
        sources=sources,
        cabins=cabins,
        min_cost=min_cost,
        max_cost=max_cost,
        min_return_days=min_return_days,
        max_return_days=max_return_days,
        min_remaining_seats=min_remaining_seats)
    
    return find_trips(
        query=query,
        start_date=start_date,
        end_date=end_date,
        n=n,
        deepness=deepness,
        oneway=False)


from backend_api.flights_system.testing.flight_testing import flight_testing_router

flights_router.include_router(flight_testing_router, prefix="/testing")