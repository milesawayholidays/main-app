"""
Core business logic for building and processing trip data structures.

This module contains the essential classes and functions for handling flight trip data,
including individual trips, round trips, and trip options. It manages cost calculations,
currency conversions, price formatting, and integrates with external services for
content generation and image fetching.

Key Components:
- Trip: Represents individual flight segments with cost calculations
- RoundTrip: Combines outbound and return trips with pricing logic
- RoundTripOptions: Groups multiple round trips with marketing content
- Utility functions for formatting and data processing

The module handles:
- Mileage cost calculations and currency conversions
- Commission and credit card fee applications
- Price formatting for different currencies
- WhatsApp post generation via OpenAI
- Travel image fetching from Unsplash
- Data formatting for spreadsheet export
"""
import os
from datetime import datetime

from config import config
from global_state import state
from currencies.cash import handler as cash_handler, cents_to_str
from currencies.mileage import handler as mileage_handler

from services.openAI import handler as openAI_handler
from services.unsplash import fetch_image


class Trip:
    """
    Represents a single flight trip with comprehensive cost calculations.
    
    This class encapsulates all information about a single flight segment,
    including departure/arrival details, pricing calculations with mileage
    values, taxes, commissions, and currency conversions. It automatically
    calculates total costs, selling prices, and provides formatted string
    representations for various price components.
    
    Attributes:
        availability_Id (str): Unique identifier for the flight availability
        origin_airport (str): Origin airport code
        destination_airport (str): Destination airport code
        departure (str): Departure date/time
        arrival (str): Arrival date/time
        booking_links (str): Comma-separated booking URLs
        source (str): Airline source/program
        mileage_cost (int): Cost in mileage points
        taxes_currency (str): Currency code for taxes
        taxes_currency_symbol (str): Currency symbol for taxes
        taxes (float): Tax amount in original currency
        cabin (str): Cabin class code
        total_cost (int): Total cost including mileage value and taxes
        selling_price (int): Final selling price with commissions and fees
        normal_* (various): Converted values in system base currency
    """

    def __init__(self, availabilityId: str, region: str, originAirport: str, destinationAirport: str, departure_date: datetime, 
                 departure_time: datetime, arrival_date: datetime, arrival_time: datetime,
                 booking_links: list[str], source: str, mileageCost: int, taxes_currency: str, taxes_currency_symbol: str,
                 taxes: float, cabin: str, remaining_seats: int = 0):
        """
        Initialize a Trip instance with flight details and automatic cost calculations.
        
        Args:
            availabilityId (str): Unique identifier for the flight availability
            originAirport (str): IATA code for origin airport
            destinationAirport (str): IATA code for destination airport
            departure (str): Departure date and time
            arrival (str): Arrival date and time
            booking_links (str): Booking URLs (comma-separated if multiple)
            source (str): Airline source/loyalty program identifier
            mileageCost (int): Cost in mileage points
            taxes_currency (str): Currency code for taxes (e.g., 'USD', 'BRL')
            taxes_currency_symbol (str): Currency symbol (e.g., '$', 'R$')
            taxes (float): Tax amount in the specified currency
            cabin (str): Cabin class code (e.g., 'Y', 'W')
            remaining_seats (int): Number of remaining seats available (default 0)
            
        Raises:
            ValueError: If the mileage value for the source is invalid or not found
            
        Note:
            - Automatically calculates total cost using mileage values
            - Applies commission and credit card fees from config
            - Converts all monetary values to system base currency
        """
        normal_currency = config.CURRENCY
        normal_currency_symbol = config.CURRENCY_SYMBOL
        self.availability_Id = availabilityId
        self.region = region
        self.origin_airport = originAirport
        self.origin_city = config.IATA_CITY.get(originAirport, "Unknown")
        self.origin_country = config.IATA_COUNTRY.get(originAirport, "Unknown")
        self.destination_airport = destinationAirport
        self.destination_city = config.IATA_CITY.get(destinationAirport, "Unknown")
        self.destination_country = config.IATA_COUNTRY.get(destinationAirport, "Unknown")
        self.departure_date = departure_date
        self.arrival_date = arrival_date
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.booking_links = booking_links
        self.source = source
        self.mileage_cost = mileageCost
        self.taxes_currency = taxes_currency if taxes > 0 else normal_currency
        self.taxes_currency_symbol = taxes_currency_symbol if taxes > 0 else normal_currency_symbol
        self.taxes = taxes
        self.cabin = cabin
        mileage_value = mileage_handler.get_mileage_value(self.source)
        self.remaining_seats = remaining_seats

        if mileage_value is None:
            state.logger.error(f"Invalid mileage value for source: {self.source}")
            raise ValueError(f"Invalid mileage value for source: {self.source}")
        
        self.total_cost = self.mileage_cost * mileage_value // 1000 + self.taxes  
        self.comission = config.COMMISSION
        self.credit_card_fee = config.CREDIT_CARD_FEE
        
        self.selling_price = self.total_cost * (10000 + self.comission + self.credit_card_fee) // 10000
        

        self.normal_currency = normal_currency
        self.normal_currency_symbol = normal_currency_symbol
        self.normal_taxes = cash_handler.convert_to_system_base(self.taxes, self.normal_currency)
        self.normal_total_cost = cash_handler.convert_to_system_base(self.total_cost, self.normal_currency)
        self.normal_selling_price = cash_handler.convert_to_system_base(self.selling_price, self.normal_currency)


    def taxes_to_str(self) -> str:
        """
        Format taxes amount as a currency string in original currency.
        
        Returns:
            str: Formatted tax amount (e.g., "$ 125.50 (USD)")
            
        Raises:
            ValueError: If currency symbol or currency code is not set
        """
        if not self.normal_currency_symbol or not self.normal_currency:
            state.logger.error("NORMAL_TAXES_CURRENCY_SYMBOL or NORMAL_TAXES_CURRENCY environment variable is not set.")
            raise ValueError("TAXES_CURRENCY_SYMBOL or TAXES_CURRENCY environment variable is not set.")
        return cents_to_str(self.taxes, self.taxes_currency_symbol, self.taxes_currency)
    
    def normal_taxes_to_str(self) -> str:
        """
        Format taxes amount as a currency string in system base currency.
        
        Returns:
            str: Formatted tax amount in base currency (e.g., "R$ 625.75 (BRL)")
            
        Raises:
            ValueError: If normal currency symbol or currency code is not set
        """
        if not self.normal_currency_symbol or not self.normal_currency:
            state.logger.error("NORMAL_TAXES_CURRENCY_SYMBOL or NORMAL_TAXES_CURRENCY environment variable is not set.")
            raise ValueError("NORMAL_TAXES_CURRENCY_SYMBOL or NORMAL_TAXES_CURRENCY environment variable is not set.")
        return cents_to_str(self.normal_taxes, self.normal_currency_symbol, self.normal_currency)
    
    def total_cost_to_str(self) -> str:
        """
        Format total cost as a currency string in original currency.
        
        Returns:
            str: Formatted total cost including mileage value and taxes
            
        Raises:
            ValueError: If taxes currency symbol or currency code is not set
        """
        if not self.taxes_currency_symbol or not self.taxes_currency:
            state.logger.error("TAXES_CURRENCY_SYMBOL or TAXES_CURRENCY environment variable is not set.")
            raise ValueError("TAXES_CURRENCY_SYMBOL or TAXES_CURRENCY environment variable is not set.")
        return cents_to_str(self.total_cost, self.taxes_currency_symbol, self.taxes_currency)
    
    def normal_total_cost_to_str(self) -> str:
        """
        Format total cost as a currency string in system base currency.
        
        Returns:
            str: Formatted total cost in base currency
            
        Raises:
            ValueError: If normal currency symbol or currency code is not set
        """
        if not self.normal_currency_symbol or not self.normal_currency:
            state.logger.error("NORMAL_TAXES_CURRENCY_SYMBOL or NORMAL_TAXES_CURRENCY environment variable is not set.")
            raise ValueError("NORMAL_TAXES_CURRENCY_SYMBOL or NORMAL_TAXES_CURRENCY environment variable is not set.")
        return cents_to_str(self.normal_total_cost, self.normal_currency_symbol, self.normal_currency)
    
    def mileage_cost_to_str(self) -> str:
        """
        Format mileage cost as a string with source program.
        
        Returns:
            str: Formatted mileage cost (e.g., "50000 smiles miles")
            
        Raises:
            ValueError: If taxes currency symbol or currency code is not set
        """
        if not self.taxes_currency_symbol or not self.taxes_currency:
            state.logger.error("TAXES_CURRENCY_SYMBOL or TAXES_CURRENCY environment variable is not set.")
            raise ValueError("TAXES_CURRENCY_SYMBOL or TAXES_CURRENCY environment variable is not set.")
        return f"{self.mileage_cost} {self.source} miles"

    def selling_price_to_str(self) -> str:
        """
        Format selling price as a currency string in original currency.

        Returns:
            str: Formatted selling price including mileage value and taxes

        Raises:
            ValueError: If taxes currency symbol or currency code is not set
        """
        if not self.taxes_currency_symbol or not self.taxes_currency:
            state.logger.error("TAXES_CURRENCY_SYMBOL or TAXES_CURRENCY environment variable is not set.")
            raise ValueError("TAXES_CURRENCY_SYMBOL or TAXES_CURRENCY environment variable is not set.")
        return cents_to_str(self.normal_selling_price, self.normal_currency_symbol, self.normal_currency)
    

class TripOption(Trip):
    """
    Represents a flight trip option with additional metadata.
    
    This class extends the Trip class to include additional fields for
    marketing and content generation purposes, such as WhatsApp posts,
    travel images, and PDF reports.
    
    Attributes:
        whatsapp_post (str): Generated WhatsApp marketing post content
        images (list): List of travel images fetched from Unsplash
        pdf (PDF_OBJ): Generated PDF report for the trip option
    """
    
    def __init__(self, release_date: str, trip: Trip):
        super().__init__(
            availabilityId=trip.availability_Id,
            region=trip.region,
            originAirport=trip.origin_airport,
            destinationAirport=trip.destination_airport,
            departure_date=trip.departure_date,
            departure_time=trip.departure_time,
            arrival_date=trip.arrival_date,
            arrival_time=trip.arrival_time,
            booking_links=trip.booking_links,
            source=trip.source,
            mileageCost=trip.mileage_cost,
            taxes_currency=trip.taxes_currency,
            taxes_currency_symbol=trip.taxes_currency_symbol,
            taxes=trip.taxes,
            cabin=trip.cabin,
            remaining_seats=trip.remaining_seats)
        #self.images = fetch_image(f"{config.IATA_CITY.get(self.origin_airport, 'Unknown')} Landscape Tourism Beautiful")
        self.release_date = release_date
        
    def to_row(self, whatsapp_post: bool = False) -> list:
        whatsappPost = ""
        if whatsapp_post:
            whatsappPost = openAI_handler.generateWhatsAppPost(
                origin_city=self.origin_city,
                origin_country=self.origin_country,
                destination_city=self.destination_city,
                destination_country=self.destination_country,
                departure_dates=[self.departure_date],
                return_dates=[],
                cabin=self.cabin,
                miles_cost=self.mileage_cost_to_str(),
                taxes=self.taxes_to_str(),
                source=self.source,
                total_cost=self.total_cost_to_str(),
                selling_price=self.selling_price_to_str(),
                remaining_seats=str(self.remaining_seats),
                booking_link=self.booking_links[0] if self.booking_links else ""
            )
        return [
            self.release_date,
            self.availability_Id,
            self.remaining_seats,
            self.region,
            self.source,
            self.cabin,
            self.origin_airport,
            self.origin_city,
            self.origin_country,
            self.destination_airport,
            self.destination_city,
            self.destination_country,
            str(self.departure_date),
            str(self.departure_time),
            str(self.arrival_date),
            str(self.arrival_time),
            self.mileage_cost,
            self.taxes / 100,
            self.taxes_currency,
            self.normal_taxes / 100,
            self.total_cost / 100,
            self.normal_total_cost / 100,
            self.selling_price / 100,
            "; ".join(self.booking_links),
            whatsappPost
        ]

class RoundTrip:
    """
    Represents a complete round trip consisting of outbound and return flights.
    
    This class combines two Trip objects (outbound and return) to create a
    complete round trip booking. It calculates combined pricing and provides
    methods for data export and price formatting.
    
    Attributes:
        outbound (Trip): The outbound flight trip
        return_ (Trip): The return flight trip (underscore to avoid keyword conflict)
        selling_price (int): Combined selling price of both trips
        normal_selling_price (int): Combined selling price in system base currency
    """
    
    def __init__(self, outbound: TripOption, return_: TripOption, OptionID: str):
        """
        Initialize a RoundTrip with outbound and return flights.
        
        Args:
            outbound (Trip): The outbound flight trip
            return_ (Trip): The return flight trip
            
        Note:
            - Automatically calculates combined selling prices
            - Uses underscore for return_ to avoid Python keyword conflict
        """
        self.outbound = outbound
        self.return_ = return_
        self.region = f"{outbound.region}-{return_.region}"
        self.mileage_cost = outbound.mileage_cost + return_.mileage_cost
        self.taxes = outbound.normal_taxes + return_.normal_taxes
        self.total_cost = outbound.normal_total_cost + return_.normal_total_cost
        self.selling_price = outbound.selling_price + return_.selling_price
        self.option_id = OptionID
    
    def normal_selling_price_to_str(self) -> str:
        """
        Format the combined selling price as a currency string in base currency.
        
        Returns:
            str: Formatted selling price for the complete round trip
            
        Raises:
            ValueError: If normal currency symbol or currency code is not set
        """
        if not self.outbound.normal_currency_symbol or not self.outbound.normal_currency:
            state.logger.error("NORMAL_SELLING_PRICE_CURRENCY_SYMBOL or NORMAL_SELLING_PRICE_CURRENCY environment variable is not set.")
            raise ValueError("NORMAL_SELLING_PRICE_CURRENCY_SYMBOL or NORMAL_SELLING_PRICE_CURRENCY environment variable is not set.")
        return cents_to_str(self.selling_price, self.outbound.normal_currency_symbol, self.outbound.normal_currency)

    def to_row(self) -> list:
        return [
            self.outbound.release_date,
            self.option_id,
            self.outbound.availability_Id,
            self.return_.availability_Id,
            self.outbound.source,
            self.mileage_cost,
            cents_to_str(self.taxes, self.outbound.taxes_currency_symbol, self.outbound.taxes_currency),
            cents_to_str(self.total_cost, self.outbound.taxes_currency_symbol, self.outbound.taxes_currency),
            cents_to_str(self.selling_price, self.outbound.taxes_currency_symbol, self.outbound.taxes_currency),
        ]

class Route:
    """
    Represents a collection of round trip options with marketing content.
    
    This class groups multiple round trip options for the same city pairing
    and cabin class, generating associated marketing content including
    WhatsApp posts and travel images. It provides a complete package
    for flight alert distribution.
    
    Attributes:
        roundTrips (list[RoundTrip]): List of available round trip options
        origin_city (str): Origin city name
        destination_city (str): Destination city name
        origin_country (str): Origin country name
        destination_country (str): Destination country name
        departure_dates (list): Sorted unique departure dates
        return_dates (list): Sorted unique return dates
        selling_price (str): Highest selling price formatted as string
        cabin (str): Cabin class code
        source (str): Airline source/program
        release_date (str): Content release date
        whatsapp_post (str): Generated WhatsApp marketing post
        images (list): Travel images fetched from Unsplash
        pdf (PDF_OBJ): Generated PDF report for the round trip options
    """
    
    def __init__(self, ID: str, roundTrips: list[RoundTrip], origin_city: str, destination_city: str, origin_country: str, destination_country: str, cabin: str, release_date: str):
        """
        Initialize RoundTripOptions with trips and generate marketing content.
        
        Args:
            roundTrips (list[RoundTrip]): List of available round trip options
            origin_city (str): Name of the origin city
            destination_city (str): Name of the destination city
            origin_country (str): Name of the origin country
            destination_country (str): Name of the destination country
            cabin (str): Cabin class code (e.g., 'Y', 'W')
            release_date (str): Date for content release
            remaining_seats (int): Number of remaining seats available (default 0)
        Note:
            - Automatically generates WhatsApp post via OpenAI
            - Fetches travel images from Unsplash
            - Calculates departure/return date ranges
            - Determines highest selling price for marketing
        """
        if not roundTrips or len(roundTrips) == 0:
            state.logger.error("RoundTrips list is empty.")
            return {}
        
        self.ID = ID
        self.region = roundTrips[0].region
        self.roundTrips = roundTrips
        self.origin_city = origin_city
        self.destination_city = destination_city
        self.origin_country = origin_country
        self.destination_country = destination_country
        self.departure_dates = sorted(set(trip.outbound.departure_date for trip in roundTrips))
        self.return_dates = sorted(set(trip.return_.departure_date for trip in roundTrips))
        
        self.cabin = cabin
        self.source = roundTrips[0].outbound.source if roundTrips else "Unknown"
        self.release_date = release_date

        sorted(roundTrips, key=lambda x: x.selling_price)
        self.highest_selling_price = roundTrips[-1].selling_price
        self.lowest_selling_price = roundTrips[0].selling_price
        self.average_selling_price = sum(trip.selling_price for trip in roundTrips) // len(roundTrips) if roundTrips else 0

        sorted(roundTrips, key=lambda x: x.outbound.mileage_cost + x.return_.mileage_cost)
        self.highest_mileage_cost = roundTrips[-1].outbound.mileage_cost + roundTrips[-1].return_.mileage_cost
        self.lowest_mileage_cost = roundTrips[0].outbound.mileage_cost + roundTrips[0].return_.mileage_cost
        self.average_mileage_cost = sum(trip.outbound.mileage_cost + trip.return_.mileage_cost for trip in roundTrips) // len(roundTrips) if roundTrips else 0

        sorted(roundTrips, key=lambda x: x.outbound.normal_taxes + x.return_.normal_taxes)
        self.highest_taxes = roundTrips[-1].outbound.normal_taxes + roundTrips[-1].return_.normal_taxes
        self.lowest_taxes = roundTrips[0].outbound.normal_taxes + roundTrips[0].return_.normal_taxes
        self.average_taxes = sum(trip.outbound.normal_taxes + trip.return_.normal_taxes for trip in roundTrips) // len(roundTrips) if roundTrips else 0

        sorted(roundTrips, key=lambda x: x.outbound.normal_total_cost + x.return_.normal_total_cost)
        self.highest_total_cost = roundTrips[-1].outbound.normal_total_cost + roundTrips[-1].return_.normal_total_cost
        self.lowest_total_cost = roundTrips[0].outbound.normal_total_cost + roundTrips[0].return_.normal_total_cost
        self.average_total_cost = sum(trip.outbound.normal_total_cost + trip.return_.normal_total_cost for trip in roundTrips) // len(roundTrips) if roundTrips else 0


        """ self.whatsapp_post = openAI_handler.generateWhatsAppPost(
            origin_city=origin_city,
            origin_country=origin_country,
            destination_city=destination_city,
            destination_country=destination_country,
            departure_dates=self.departure_dates,
            return_dates=self.return_dates,
            cabin=cabin,
            miles_cost=f"{mileage_cost} {roundTrips[0].outbound.source} miles",
            taxes=cents_to_str(taxes, roundTrips[0].outbound.normal_currency_symbol, roundTrips[0].outbound.normal_currency),
            source=self.source,
            selling_price=self.selling_price,
            remaining_seats=str(min(trip.outbound.remaining_seats for trip in roundTrips)) if roundTrips else "0",
            booking_link=roundTrips[0].outbound.booking_links[0] if roundTrips and roundTrips[0].outbound.booking_links else ""
        ) """
        #self.images = fetch_image(f"{destination_city} Landscape Tourism Beautiful")

    def to_row(self) -> list[str]:
        return [
            self.release_date,                              #Release Date
            self.ID,                                        #Option ID
            self.region,                                    #Region
            self.origin_city,                               #Origin City
            self.origin_country,                            #Origin Country
            self.destination_city,                          #Destination City
            self.destination_country,                       #Destination Country
            self.highest_mileage_cost,                      #Highest Mileage Cost
            self.lowest_mileage_cost,                       #Lowest Mileage Cost
            self.average_mileage_cost,                      #Average Mileage Cost
            self.highest_taxes,                             #Highest Taxes
            self.lowest_taxes,                              #Lowest Taxes
            self.average_taxes ,                            #Average Taxes
            self.highest_total_cost,                        #Highest Total Cost
            self.lowest_total_cost,                         #Lowest Total Cost
            self.average_total_cost,                        #Average Total Cost
            self.highest_selling_price,                     #Highest Selling Price
            self.lowest_selling_price,                      #Lowest Selling Price
            self.average_selling_price,                     #Average Selling Price
        ]
        

def getHighestSellingPrice(trips: list[RoundTrip]) -> str:
    """
    Find the highest selling price among a list of round trips.
    
    This function identifies the trip with the highest selling price
    and returns it as a formatted currency string for marketing purposes.
    
    Args:
        trips (list[RoundTrip]): List of round trip objects to evaluate
        
    Returns:
        str: Formatted highest selling price (e.g., "R$ 2,450.00 (BRL)")
        
    Raises:
        ValueError: If the trips list is empty
        
    Note:
        - Uses normal_selling_price (base currency) for comparison
        - Returns formatted string for display purposes
    """
    if not trips or len(trips) == 0:
        state.logger.error("Trips list is empty.")
        raise ValueError("Trips list is empty.")
    
    highest_selling_price = 0
    normal_highest_selling_price_str = ""
    for trip in trips:
        if trip.selling_price > highest_selling_price:
            highest_selling_price = trip.selling_price
            normal_highest_selling_price_str = trip.normal_selling_price_to_str()

    return normal_highest_selling_price_str


def format_availability_object(availabilityObject: dict, region: str) -> Trip:
    """
    Convert raw availability data into a Trip object.
    
    This function transforms raw flight availability data from external APIs
    into a structured Trip object with all necessary fields populated.
    
    Args:
        availabilityObject (dict): Raw availability data containing:
            - AvailabilityId: Unique identifier
            - AvailabilitySegments: List of flight segments
            - MileageCost: Cost in mileage points
            - TaxesCurrency: Currency code for taxes
            - taxesCurrencySymbol: Currency symbol
            - TotalTaxes: Tax amount
            - bookingLinks: List of booking URLs
            - cabin: Cabin class code
            
    Returns:
        Trip: Formatted Trip object ready for processing
        
    Raises:
        ValueError: If availabilityObject is empty or invalid
        
    Note:
        - Extracts origin/destination from first/last segments
        - Combines multiple booking links with commas
        - Uses segment source for airline identification
    """
    if not availabilityObject or len(availabilityObject) == 0 or "data" not in availabilityObject or len(availabilityObject["data"]) == 0:
        state.logger.error("Availability object is empty.")
        return None
    
    '''
    print(f"availability obj columns: {availabilityObject.keys()}")
    print(f"availability obj data[0] columns: {availabilityObject['data'][0].keys()}")
    print(f"booking links: {availabilityObject['booking_links']}")
    '''

    booking_links_as_str_list = []
    if "booking_links" in availabilityObject:
        booking_links_as_str_list = [f"{link['link']}" for link in availabilityObject["booking_links"]]    

    cheapest = min(availabilityObject["data"], 
                   key=lambda x: x["MileageCost"] * mileage_handler.get_mileage_value(x["AvailabilitySegments"][0]["Source"]) // 1000 + x["TotalTaxes"])

    departure = cheapest["AvailabilitySegments"][0]["DepartsAt"]
    arrival = cheapest["AvailabilitySegments"][len(cheapest["AvailabilitySegments"]) - 1]["ArrivesAt"]

    return Trip(
        availabilityId=cheapest["AvailabilityID"],
        region=region,
        originAirport=cheapest["AvailabilitySegments"][0]["OriginAirport"],
        destinationAirport=cheapest["AvailabilitySegments"][len(cheapest["AvailabilitySegments"]) - 1]["DestinationAirport"],
        departure_date= datetime.strptime(departure, "%Y-%m-%dT%H:%M:%SZ").date(),
        departure_time=datetime.strptime(departure, "%Y-%m-%dT%H:%M:%SZ").time(),
        arrival_date=datetime.strptime(arrival, "%Y-%m-%dT%H:%M:%SZ").date(),
        arrival_time=datetime.strptime(arrival, "%Y-%m-%dT%H:%M:%SZ").time(),
        booking_links=booking_links_as_str_list,
        source=cheapest["AvailabilitySegments"][0]["Source"],
        mileageCost=cheapest["MileageCost"],
        taxes_currency=cheapest["TaxesCurrency"],
        taxes_currency_symbol=cheapest["TaxesCurrencySymbol"],
        taxes=cheapest["TotalTaxes"],
        cabin=cheapest["Cabin"],
        remaining_seats=cheapest["RemainingSeats"] if "RemainingSeats" in cheapest else 0
    )


# Legacy code kept for reference - original format_top15 implementation
# TODO: Remove after confirming new implementation works correctly
'''
def format_top15(availabilityObjectPairs) -> list[RoundTrip]:
    if not availabilityObjectPairs or len(availabilityObjectPairs) == 0:
        return []
    
    trips = []

    for item in availabilityObjectPairs:
        trips.append(
            Trip(
                availabilityId=item[0]["AvailabilityId"],
                originAirport=item[0]["AvailabilitySegments"][0]["OriginAirport"],
                destinationAirport=item[0]["AvailabilitySegments"][item[0].len() - 1]["DestinationAirport"],
                date=item[0]["AvailabilitySegments"][0]["DepartsAt"],
                return_date=item[0]["AvailabilitySegments"][item[0].len() - 1]["ReturnDate"],
                booking_links=", ".join(item[0]["bookingLinks"]),
                distance= sum(segment["distance"] for segment in availabilityObjectPairs[0]["AvailabilitySegments"]),
                source=item[0]["AvailabilitySegments"][0]["source"],
                mileageCost=item[0]["MileageCost"],
                taxes_currency=item[0]["TaxesCurrency"],
                taxes_currency_symbol=item[0]["taxesCurrencySymbol"],
                taxes=item[0]["TotalTaxes"],
                cabin=item[0]["cabin"]
            ),
            Trip(
                availabilityId=item[1]["AvailabilityId"],
                originAirport=item[1]["AvailabilitySegments"][0]["OriginAirport"],
                destinationAirport=item[1]["AvailabilitySegments"][item[0].len() - 1]["DestinationAirport"],
                date=item[1]["AvailabilitySegments"][0]["DepartsAt"],
                booking_links=", ".join(item[1]["bookingLinks"]),
                distance= sum(segment["distance"] for segment in availabilityObjectPairs[1]["AvailabilitySegments"]),
                source=item[1]["AvailabilitySegments"][0]["source"],
                mileageCost=item[1]["miles"],
                taxes_currency=item[1]["taxesCurrency"],
                taxes_currency_symbol=item[1]["taxesCurrencySymbol"],
                taxes=item[1]["taxes"],
                total_value=item[1]["total_value"],
                cabin=item[1]["cabin"]
            )
        )

    return [RoundTrip(outbound=trip[0], return_=trip[1]) for trip in trips]
'''