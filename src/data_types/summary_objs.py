"""
Summary data structures for flight filtering and grouping.

This module defines lightweight data structures used to represent
trip summaries and round-trip groupings during the flight filtering
process. These objects contain essential information needed for
filtering and organizing flight data before full trip processing.
"""

from dataclasses import dataclass

@dataclass
class summary_trip:
    """
    Represents a summary of a single flight trip.
    
    This lightweight structure contains the essential information
    needed for filtering and comparison during the initial trip
    processing stages.
    
    Attributes:
        ID (str): Unique identifier for the trip
        city (str): Destination city name
        totalCost (int): Total cost of the trip in cents
        distance (int): Distance of the trip in kilometers
    """
    ID: str
    city: str
    totalCost: int
    distance: int

@dataclass
class summary_round_trip:
    """
    Represents a complete round-trip consisting of outbound and return flights.
    
    This structure pairs two summary_trip objects to represent
    a complete round-trip journey for filtering and comparison.
    
    Attributes:
        outbound (summary_trip): The outbound flight trip
        return_ (summary_trip): The return flight trip (note: 'return_' to avoid Python keyword)
        distance (int): Total distance of the round trip in kilometers
    """
    outbound: summary_trip
    return_: summary_trip

@dataclass
class summary_round_trip_with_city(summary_round_trip):
    """
    Represents a round trip with additional city information.
    
    This structure extends summary_round_trip to include the origin and
    destination cities for better context in filtering and grouping.
    
    Attributes:
        outbound (summary_trip): The outbound flight trip
        return_ (summary_trip): The return flight trip
        origin_city (str): The origin city of the round trip
        destination_city (str): The destination city of the round trip
    """
    origin_city: str
    destination_city: str
