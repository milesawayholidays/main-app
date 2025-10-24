from dataclasses import dataclass

from logic.trip_builder import TripOption, RoundTrip, Route
  

@dataclass
class FlightOptions:
  single_trips: list[TripOption]
  round_trips: list[RoundTrip]
  round_options: list[Route]