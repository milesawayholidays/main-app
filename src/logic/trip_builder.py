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

from config import config
from global_state import state
from currencies.cash import handler as cash_handler
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
    
    def __init__(self, availabilityId: str, originAirport: str, destinationAirport: str, departure: str, arrival: str, booking_links: list[str], source: str, mileageCost: int, taxes_currency: str, taxes_currency_symbol: str, taxes: float, cabin: str, remaining_seats: int = 0):
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
        self.availability_Id = availabilityId
        self.origin_airport = originAirport
        self.destination_airport = destinationAirport
        self.departure = departure
        self.arrival = arrival
        self.booking_links = booking_links
        self.source = source
        self.mileage_cost = mileageCost
        self.taxes_currency = taxes_currency
        self.taxes_currency_symbol = taxes_currency_symbol
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

        normal_currency = config.CURRENCY
        normal_currency_symbol = config.CURRENCY_SYMBOL

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

    def to_row(self) -> list:
        return [
            self.availability_Id,
            self.origin_airport,
            self.destination_airport,
            self.departure.format("%Y-%m-%d %H:%M"),
            self.arrival.format("%Y-%m-%d %H:%M"),
            self.mileage_cost_to_str(),
            self.taxes_to_str(),
            self.normal_taxes_to_str(),
            self.total_cost_to_str(),
            self.normal_total_cost_to_str(),
            self.selling_price,
            self.normal_selling_price,
            "; ".join(self.booking_links)
        ]
    

def cents_to_str(cents: int, currency_symbol: str, currency_title: str) -> str:
    """
    Convert cents to a formatted currency string.
    
    This utility function converts integer cent values to properly formatted
    currency strings with symbol and currency code.
    
    Args:
        cents (int): Amount in cents
        currency_symbol (str): Currency symbol (e.g., '$', 'R$')
        currency_title (str): Currency code (e.g., 'USD', 'BRL')
        
    Returns:
        str: Formatted currency string (e.g., "$ 123.45 (USD)")
        
    Raises:
        ValueError: If currency_symbol or currency_title is not provided
    """
    if not currency_symbol or not currency_title:
        state.logger.error("CURRENCY_SYMBOL or CURRENCY_TITLE environment variable is not set.")
        raise ValueError("CURRENCY_SYMBOL or CURRENCY_TITLE environment variable is not set.")
    return f"{currency_symbol} {cents // 100}.{cents % 100:02d} ({currency_title})"

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
            originAirport=trip.origin_airport,
            destinationAirport=trip.destination_airport,
            departure=trip.departure,
            arrival=trip.arrival,
            booking_links=trip.booking_links,
            source=trip.source,
            mileageCost=trip.mileage_cost,
            taxes_currency=trip.taxes_currency,
            taxes_currency_symbol=trip.taxes_currency_symbol,
            taxes=trip.taxes,
            cabin=trip.cabin,
            remaining_seats=trip.remaining_seats)
        self.whatsapp_post = openAI_handler.generateWhatsAppPost(
            origin=self.origin_airport,
            destination=self.destination_airport,
            departure_dates=[self.departure],
            return_dates=[],
            cabin=self.cabin,
            selling_price=self.selling_price
        )
        self.images = fetch_image(f"{config.IATA_CITY.get(self.origin_airport, 'Unknown')} Landscape Tourism Beautiful")
        self.pdf = None
        self.release_date = release_date

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
    
    def __init__(self, outbound: Trip, return_: Trip):
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
        self.selling_price = outbound.selling_price + return_.selling_price
        self.normal_selling_price = outbound.normal_selling_price + return_.normal_selling_price

    def to_row(self) -> list:
        """
        Create a row of data for spreadsheet export.
        
        Generates a comprehensive list of all round trip details formatted
        for export to Google Sheets or other tabular formats.
        
        Returns:
            list: List containing all trip details in order:
                - Outbound/Return IDs, airports, dates, times
                - Mileage costs, taxes (original and converted)
                - Total costs (original and converted)
                - Selling price and booking links
        """
        normal_selling_price = cents_to_str(self.normal_selling_price, self.outbound.normal_currency_symbol, self.outbound.normal_currency)
        return [
            self.outbound.availability_Id, #Outbound id
            self.return_.availability_Id, #Return id
            self.outbound.origin_airport, #Origin airport
            self.return_.origin_airport, #Destination airport
            self.outbound.departure, #Outbound departure
            self.outbound.arrival, #Outbound arrival
            self.return_.departure, #Return departure
            self.return_.arrival, #Return arrival
            self.outbound.mileage_cost_to_str(), #Outbound mileage cost
            self.outbound.taxes_to_str(), #Outbound taxes
            self.outbound.normal_taxes_to_str(), #Outbound normal taxes
            self.outbound.total_cost_to_str(), #Outbound total cost
            self.outbound.normal_total_cost_to_str(), #Outbound normal total cost
            self.return_.mileage_cost_to_str(), #Return mileage cost
            self.return_.taxes_to_str(), #Return taxes
            self.return_.normal_taxes_to_str(), #Return normal taxes
            self.return_.total_cost_to_str(), #Return total cost
            self.return_.normal_total_cost_to_str(), #Return normal total cost
            normal_selling_price, #Normal selling price
            "; ".join(l for l in self.outbound.booking_links),
            "; ".join(l for l in self.return_.booking_links),
        ]
    
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
        return cents_to_str(self.normal_selling_price, self.outbound.normal_currency_symbol, self.outbound.normal_currency)

class RoundTripOptions:
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
    
    def __init__(self, roundTrips: list[RoundTrip], origin_city: str, destination_city: str, origin_country: str, destination_country: str, cabin: str, release_date: str):
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
        self.roundTrips = roundTrips
        self.origin_city = origin_city
        self.destination_city = destination_city
        self.origin_country = origin_country
        self.destination_country = destination_country
        self.departure_dates = sorted(set(trip.outbound.departure for trip in roundTrips))
        self.return_dates = sorted(set(trip.return_.departure for trip in roundTrips))
        self.selling_price = getHighestSellingPrice(roundTrips)
        self.cabin = cabin
        self.source = roundTrips[0].outbound.source if roundTrips else "Unknown"
        self.release_date = release_date
        self.whatsapp_post = openAI_handler.generateWhatsAppPost(
            origin=f"{origin_city}({origin_country})",
            destination=f"{destination_city}({destination_country})",
            departure_dates=self.departure_dates,
            return_dates=self.return_dates,
            cabin=cabin,
            selling_price=self.selling_price
        )
        self.images = fetch_image(f"{destination_city} Landscape Tourism Beautiful")

    def set_release_date(self, release_date: str):
        """
        Set the release date for the round trip options.
        
        Args:
            release_date (str): Date string in 'YYYY-MM-DD' format
            
        Note:
            - This method allows updating the release date after initialization
        """
        self.release_date = release_date
    def delete_images(self):
        """
        Delete temporary files associated with this round trip option.
        
        This method is used to clean up any temporary files created during
        the processing of round trip options, such as images or PDFs.
        """
        for image in self.images:
            if image and image.filePath and os.path.exists(image.filePath):
                os.remove(image.filePath)


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
        if trip.normal_selling_price > highest_selling_price:
            highest_selling_price = trip.normal_selling_price
            normal_highest_selling_price_str = trip.normal_selling_price_to_str()

    return normal_highest_selling_price_str


def format_availability_object(availabilityObject: dict) -> Trip:
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
    if not availabilityObject or len(availabilityObject) == 0:
        state.logger.error("Availability object is empty.")
        return None
    
    '''
    print(f"availability obj columns: {availabilityObject.keys()}")
    print(f"availability obj data[0] columns: {availabilityObject['data'][0].keys()}")
    print(f"booking links: {availabilityObject['booking_links']}")
    '''

    booking_links_as_str_list = []
    if "booking_links" in availabilityObject:
        booking_links_as_str_list = [f"{link['label']}: {link['link']}" for link in availabilityObject["booking_links"]]    


    return Trip(
        availabilityId=availabilityObject["data"][0]["AvailabilityID"],
        originAirport=availabilityObject["data"][0]["AvailabilitySegments"][0]["OriginAirport"],
        destinationAirport=availabilityObject["data"][0]["AvailabilitySegments"][len(availabilityObject["data"][0]["AvailabilitySegments"]) - 1]["DestinationAirport"],
        departure=availabilityObject["data"][0]["AvailabilitySegments"][0]["DepartsAt"],
        arrival=availabilityObject["data"][0]["AvailabilitySegments"][len(availabilityObject["data"][0]["AvailabilitySegments"]) - 1]["ArrivesAt"],
        booking_links=booking_links_as_str_list,
        source=availabilityObject["data"][0]["AvailabilitySegments"][0]["Source"],
        mileageCost=availabilityObject["data"][0]["MileageCost"],
        taxes_currency=availabilityObject["data"][0]["TaxesCurrency"],
        taxes_currency_symbol=availabilityObject["data"][0]["TaxesCurrencySymbol"],
        taxes=availabilityObject["data"][0]["TotalTaxes"],
        cabin=availabilityObject["data"][0]["Cabin"],
        remaining_seats=availabilityObject["data"][0]["RemainingSeats"] if "RemainingSeats" in availabilityObject["data"][0] else 0
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