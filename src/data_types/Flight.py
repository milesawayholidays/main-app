import pandas as pd
from dataclasses import dataclass, asdict

from src.config import config

from .enums import REGION, CABIN, SOURCE, PROVIDER

from src.logic.trip_builder import TripOption, RoundTrip, Route


### FLIGHT SEARCH RESULT DATA TYPES ###

@dataclass
class Availability:
    ID: str
    origin_airport: str
    destination_airport: str
    source: str
    date: str
    y_available: bool
    w_available: bool
    j_available: bool
    f_available: bool
    y_mileage: int
    w_mileage: int
    j_mileage: int
    f_mileage: int
    taxes_currency: str
    y_taxes: float
    w_taxes: float
    j_taxes: float
    f_taxes: float
    y_remaining_seats: int
    w_remaining_seats: int
    j_remaining_seats: int
    f_remaining_seats: int
    created_at: str
    updated_at: str
    provider: PROVIDER
    
class RawFlightResult(Availability):
    origin_region: str
    destination_region: str

    def __init__(self, origin_region: str, destination_region: str, availability: Availability):
        self.origin_region = origin_region
        self.destination_region = destination_region
        super().__init__(**asdict(availability))

    @classmethod
    def from_list(cls, origin_region: str, destination_region: str, availability_list: list[Availability]):
        FlightSearchResults: list[RawFlightResult] = []
        for availability in availability_list:
            FlightSearchResults.append(cls(origin_region, destination_region, availability))
        return FlightSearchResults
    
    def to_dict(self):
        return {
            "ID": self.ID,
            "origin_airport": self.origin_airport,
            "destination_airport": self.destination_airport,
            "origin_region": self.origin_region,
            "destination_region": self.destination_region,
            "source": self.source,
            "date": self.date,
            "y_available": self.y_available,
            "w_available": self.w_available,
            "j_available": self.j_available,
            "f_available": self.f_available,
            "y_mileage": self.y_mileage,
            "w_mileage": self.w_mileage,
            "j_mileage": self.j_mileage,
            "f_mileage": self.f_mileage,
            "taxes_currency": self.taxes_currency,
            "y_taxes": self.y_taxes,
            "w_taxes": self.w_taxes,
            "j_taxes": self.j_taxes,
            "f_taxes": self.f_taxes,
            "y_remaining_seats": self.y_remaining_seats,
            "w_remaining_seats": self.w_remaining_seats,
            "j_remaining_seats": self.j_remaining_seats,
            "f_remaining_seats": self.f_remaining_seats,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "provider": self.provider
        }


### FLIGHT FILTER DATA TYPES ###

ONEWAY_DF_COLUMNS = set([
    "ID",
    "origin_airport",
    "destination_airport",
    "origin_region",
    "destination_region",
    "source",
    "date",
    "cabin",
    "y_available",
    "w_available",
    "j_available",
    "f_available",
    "y_mileage",
    "w_mileage",
    "j_mileage",
    "f_mileage",
    "taxes_currency",
    "y_taxes",
    "w_taxes",
    "j_taxes",  
    "f_taxes",
    "y_remaining_seats",
    "w_remaining_seats",
    "j_remaining_seats",
    "f_remaining_seats",
    "created_at",
    "updated_at",
    "provider",
    "origin_city",
    "destination_city",
    "origin_country",
    "destination_country",
    "origin_lat",
    "origin_lon",
    "destination_lat",
    "destination_lon",
    "distance",
    "mileage_value",
    "y_taxes_standard",
    "w_taxes_standard",
    "j_taxes_standard",  
    "f_taxes_standard",
    "total_cost",
    "score",
])

ROUND_DF_COLUMNS = set([
    "ID_out",
    "ID_ret",
    "origin_city_out",
    "origin_country_out",
    "origin_region_out",
    "destination_city_out",
    "destination_country_out",
    "destination_region_out",
    "origin_city_ret",
    "origin_country_ret",
    "origin_region_ret",
    "destination_city_ret",
    "destination_country_ret",
    "destination_region_ret",
    "cabin_out",
    "cabin_ret",
    "source_out",
    "source_ret",
    "date_out",
    "date_ret",
    "y_available_out",
    "w_available_out",
    "s_available_out",
    "f_available_out",
    "y_available_ret",
    "w_available_ret",
    "s_available_ret",
    "f_available_ret",
    "y_mileage_out",
    "w_mileage_out",
    "s_mileage_out",
    "f_mileage_out",
    "y_mileage_ret",
    "w_mileage_ret",
    "s_mileage_ret",
    "f_mileage_ret",
    "taxes_currency_out",
    "y_taxes_out",
    "w_taxes_out",
    "s_taxes_out",
    "f_taxes_out",
    "taxes_currency_ret",
    "y_taxes_ret",
    "w_taxes_ret",
    "s_taxes_ret",
    "f_taxes_ret",
    "y_remaining_seats_out",
    "w_remaining_seats_out",
    "s_remaining_seats_out",
    "f_remaining_seats_out",
    "y_remaining_seats_ret",
    "w_remaining_seats_ret",
    "s_remaining_seats_ret",
    "f_remaining_seats_ret",
    "created_at_out",
    "updated_at_out",
    "created_at_ret",
    "updated_at_ret",    
    "provider_out",
    "provider_ret",
])

class FlightFilterResult:
    outbound_id: str
    return_id: str | None

    origin_city: str
    origin_country: str
    origin_region: str
    destination_city: str
    destination_country: str
    destination_region: str
    cabin: str
    
    out_provider: PROVIDER
    ret_provider: PROVIDER

class FilteredFlightList(list[FlightFilterResult]):
    
    def append_from_dataframe(self, df: pd.DataFrame, out_suffix: str = "", ret_suffix: str = ""):
        if df is None or df.empty:
            return

        is_round = ret_suffix != ""
        if is_round and (out_suffix == "" or ret_suffix == ""):
            raise ValueError("Both out_suffix and ret_suffix must be provided for round-trip data.")

        # The processing pipeline may add extra computed columns (e.g. total_cost, distance)
        # and may evolve naming. Only require the minimal set needed to build FlightFilterResult.
        required_cols = {
            f"ID{out_suffix}",
            f"origin_city{out_suffix}",
            f"origin_country{out_suffix}",
            f"origin_region{out_suffix}",
            f"destination_city{out_suffix}",
            f"destination_country{out_suffix}",
            f"destination_region{out_suffix}",
            f"cabin{out_suffix}",
            f"provider{out_suffix}",
        }
        if is_round:
            required_cols |= {
                f"ID{ret_suffix}",
                f"provider{ret_suffix}",
            }

        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"DataFrame missing required columns: {sorted(missing)}")

        for _, row in df.iterrows():
            result = FlightFilterResult()
            result.outbound_id = row[f"ID{out_suffix}"]
            result.return_id = row[f"ID{ret_suffix}"] if not ret_suffix == "" else None

            result.origin_city = row[f"origin_city{out_suffix}"]
            result.origin_country = row[f"origin_country{out_suffix}"]
            result.origin_region = row[f"origin_region{out_suffix}"]
            result.destination_city = row[f"destination_city{out_suffix}"]
            result.destination_country = row[f"destination_country{out_suffix}"]
            result.destination_region = row[f"destination_region{out_suffix}"]

            result.cabin = row[f"cabin{out_suffix}"]

            result.out_provider = row[f"provider{out_suffix}"]
            result.ret_provider = row[f"provider{ret_suffix}"] if not ret_suffix == "" else None

            self.append(result)
        
        return self


### FLIGHT FILTER DATA TYPES ###

class FlightQuery:
    origin_regions: list[str] | None
    destination_regions: list[str] | None
    origin_countries: list[str] | None
    destination_countries: list[str] | None
    origin_cities: list[str] | None
    destination_cities: list[str] | None
    origin_airports: list[str] | None
    destination_airports: list[str] | None
    sources: list[str] | None
    cabins: list[str] | None
    min_cost: float | None
    max_cost: float | None
    min_return_days: int | None
    max_return_days: int | None
    min_remaining_seats: int | None

    extra_queries: bool | None

    def __init__(self):
        # Initialize all query fields to None so we can set them atomically
        self.origin_regions = None
        self.destination_regions = None
        self.origin_countries = None
        self.destination_countries = None
        self.origin_cities = None
        self.destination_cities = None
        self.origin_airports = None
        self.destination_airports = None
        self.sources = None
        self.cabins = None
        self.min_cost = None
        self.max_cost = None
        self.min_return_days = None
        self.max_return_days = None
        self.min_remaining_seats = None
        self.extra_queries = None

    def get(self, key: str, default):
        # Return the attribute value, but treat explicit None as "not provided"
        val = getattr(self, key, default)
        return default if val is None else val
    
    def _validate_list(self, values, allowed_getter=None, param_name: str = ""):
        """
        Validate a list of values against an allowed set (from allowed_getter) and
        return the cleaned list or raise ValueError listing invalid entries.

        - If `values` is None, returns None.
        - If `allowed_getter` is provided, it will be called (no args) to obtain
          an iterable of allowed values. If not provided, no validation is done.
        """
        if values is None:
            return None

        # Accept any iterable but convert to list for consistent storage
        incoming = list(values)

        if allowed_getter is None:
            return incoming

        allowed = set(allowed_getter())
        invalid = [v for v in incoming if v not in allowed]
        if invalid:
            raise ValueError(f"Invalid {param_name}: {invalid}")

        return incoming

    
    
    def build_query(self,
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
                    min_remaining_seats: int | None = None):
        # Map incoming parameter names to their values
        inputs = {
            "origin_regions": origin_regions,
            "destination_regions": destination_regions,
            "origin_countries": origin_countries,
            "destination_countries": destination_countries,
            "origin_cities": origin_cities,
            "destination_cities": destination_cities,
            "origin_airports": origin_airports,
            "destination_airports": destination_airports,
            "sources": sources,
            "cabins": cabins,
            "min_cost": min_cost,
            "max_cost": max_cost,
            "min_return_days": min_return_days,
            "max_return_days": max_return_days,
            "min_remaining_seats": min_remaining_seats,
        }

        # Validators for specific fields (callable returning allowed values)
        validators = {
            # Regions are normalized below via REGION.parse to accept both enum codes and names.
            "origin_regions": None,
            "destination_regions": None,
            "origin_countries": lambda: list(config.IATA_COUNTRY.values()),
            "destination_countries": lambda: list(config.IATA_COUNTRY.values()),
            "origin_cities": lambda: list(config.IATA_CITY.values()),
            "destination_cities": lambda: list(config.IATA_CITY.values()),
            "origin_airports": lambda: list(config.IATA_COUNTRY.keys()),
            "destination_airports": lambda: list(config.IATA_COUNTRY.keys()),
            # Sources/cabins are normalized below; accept user-friendly values.
            "sources": None,
            "cabins": None,
            
        }

        for key, val in inputs.items():
            allowed_getter = validators.get(key)
            validated = None
            # Only validate list-like fields; scalars pass through as-is
            if key in ("min_cost", "max_cost", "min_return_days", "max_return_days", "min_remaining_seats"):
                validated = val
            else:
                if key in ("origin_regions", "destination_regions"):
                    if val is None:
                        validated = None
                    else:
                        incoming = list(val)
                        invalid: list[str] = []
                        normalized: list[str] = []
                        for v in incoming:
                            try:
                                normalized.append(REGION.parse(v).value)
                            except Exception:
                                invalid.append(str(v))
                        if invalid:
                            raise ValueError(f"Invalid {key}: {invalid}")
                        validated = normalized
                elif key == "sources":
                    if val is None:
                        validated = None
                    else:
                        allowed = set(SOURCE.get_source_values())
                        incoming = [str(v).strip() for v in list(val) if str(v).strip()]
                        invalid = [v for v in incoming if v not in allowed]
                        if invalid:
                            raise ValueError(f"Invalid {key}: {invalid}")
                        validated = incoming
                elif key == "cabins":
                    if val is None:
                        validated = None
                    else:
                        incoming = [str(v).strip() for v in list(val) if str(v).strip()]
                        allowed_keys = set(CABIN.__members__.keys())
                        allowed_values = set(c.value for c in CABIN)
                        invalid = [v for v in incoming if v not in allowed_keys and v not in allowed_values]
                        if invalid:
                            raise ValueError(f"Invalid {key}: {invalid}")
                        validated = incoming
                else:
                    validated = self._validate_list(val, allowed_getter=allowed_getter, param_name=key)

            setattr(self, key, validated)

        if any(v is not None for v in inputs.values()):
            self.extra_queries = True


@dataclass
class FlightOptions:
  single_trips: list[TripOption]
  round_trips: list[RoundTrip]
  round_options: list[Route]