from fastapi import APIRouter

from src.data_types.Flight import FlightQuery
from src.orchestrator import generate_raw_cache, find_trips_from_cache

flight_testing_router = APIRouter()

@flight_testing_router.get("/generate-cache")
def generate_cache_handler(
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
    start_date: str = None,
    end_date: str = None,
    deepness: int = 1
):
    
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
    
    return generate_raw_cache(
        query=query,
        deepness=deepness,
        start_date=start_date,
        end_date=end_date
    )


@flight_testing_router.get("/process-cache")
def process_cache_handler(
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
    n: int = 1,
    oneway: bool = True
):
    
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
        min_remaining_seats=min_remaining_seats
        )
    
    return find_trips_from_cache(
        query=query,
        n=n,
        oneway=oneway,
    )
    