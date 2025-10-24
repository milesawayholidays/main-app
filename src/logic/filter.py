"""
Flight filtering logic and algorithms.

This module contains the core flight filtering functionality for the flight alert system.
It processes bulk flight availability data from multiple sources, calculates costs using
mileage values and exchange rates, filters for valid round trips, and identifies the
cheapest options by cabin class and city pairings.

The main class Flight_Filter handles:
- Processing raw flight data from multiple airline sources
- Converting costs using mileage values and currency exchange
- Filtering valid round trips based on date constraints
- Finding the cheapest flight options by cabin class
- Grouping results by city pairings for easy comparison
"""

import pandas as pd
from geopy.distance import great_circle
from random import shuffle

from time import sleep

try:
    # Try relative imports first (when imported as part of src package)
    from ..global_state import state
    from ..config import config
    from ..currencies.mileage import handler as mileage_handler
    from ..currencies.cash import handler as cash_handler
    from ..data_types.enums import CABIN, SOURCE
    from ..data_types.summary_objs import summary_trip, summary_round_trip
except ImportError:
    # Fall back to absolute imports (when run directly or in tests)
    from global_state import state
    from config import config
    from currencies.mileage import handler as mileage_handler
    from currencies.cash import handler as cash_handler
    from data_types.enums import CABIN, SOURCE
    from data_types.summary_objs import summary_trip, summary_round_trip

class Flight_Filter:
    """
    Main class for filtering and processing flight availability data.
    
    This class provides methods to process bulk flight availability data from
    multiple airline sources, filter for valid round trips, calculate costs,
    and identify the cheapest options by cabin class and city pairings.
    """
    
    def __init__(self):
        """Initialize the Flight_Filter instance."""
        pass

    def getTopNTripsFromMultipleSources(self,
                                        bulk_availability_by_source: dict[CABIN, list],
                                        cabins: list[CABIN] = None,
                                        n: int = 1,
                                        filter: dict = None) -> dict[CABIN, list[summary_round_trip]]:
        """ 
        Get the top N cheapest trips from multiple airline sources.
        This method processes flight availability data from multiple sources,
        combines the results, and returns the cheapest options by cabin class.
        """

        state.logger.info("Starting to filter top N trips from multiple sources")
        if not bulk_availability_by_source:
            state.logger.warning("No bulk availability data provided.")
            return None
        trips_by_cabin: dict[CABIN, list[summary_round_trip]] = dict()
        for source, bulk_availability in bulk_availability_by_source.items():
            state.logger.info(f"Processing bulk availability for source: {source.name} with length: {len(bulk_availability)}")
            if not bulk_availability:
                state.logger.warning(f"No data found for source: {source}")
                continue

            tripsByCabin = self.process_bulk_availability_object_for_single_trips(
                bulk_availability=bulk_availability,
                source=source,
                include_cabins=cabins if cabins else [cabin for cabin in CABIN],
                filter=filter
            )

            if not tripsByCabin:
                state.logger.warning(f"No trips found for source: {source}")
                continue

            for cabin, trips in tripsByCabin.items():
                if cabin not in trips_by_cabin:
                    trips_by_cabin[cabin] = []
                trips_by_cabin[cabin].extend(trips)

        if not trips_by_cabin or len(trips_by_cabin) == 0 or all(
            len(cabin_data) == 0
            for cabin_data in trips_by_cabin.values()
        ):
            state.logger.warning("No trips found in bulk availability data.")
            return None
        
        state.logger.info("Successfully fetched bulk availability data from multiple sources.")

        state.logger.info("Finding cheapest trips by cabin class")
        topNTripsByCabin = self.find_cheapest_for_single_trips(trips_by_cabin, n=n)

        state.logger.info("Successfully found cheapest cities by cabin.")
        return topNTripsByCabin

    def get_best_round_trips_from_multiple_sources(self,
                                        bulk_availability_by_source: dict[CABIN, list], 
                                        cabins: list[CABIN] = None,
                                        min_return_days: int = None, 
                                        max_return_days: int = None,
                                        n: int = 1, filter: dict = None) -> dict[CABIN, dict[tuple[str, str], list[summary_round_trip]]]:
        """
        Get the top N cheapest trips from multiple airline sources.
        
        This method processes flight availability data from multiple sources,
        combines the results, and returns the cheapest options by cabin class.
        
        Args:
            bulk_availability_by_source (dict[SOURCE, list]): Dictionary mapping
                airline sources to their bulk availability data
            cabins (list[CABIN], optional): List of cabin classes to include
            min_return_days (int, optional): Minimum days between outbound and return
            max_return_days (int, optional): Maximum days between outbound and return
            n (int, optional): Number of top results to return per cabin. Defaults to 1.
            filter (dict, optional): Filter criteria. Supported keys:
                - "origin_country": Only include trips originating from this country (e.g., "BR")
                - "destination_country": Only include trips going to this country (e.g., "US")
                - "origin_cities": List of specific origin cities to include (e.g., ["São Paulo", "Rio de Janeiro"])
                - "destination_cities": List of specific destination cities to include
                - "max_cost": Maximum total cost per flight
                - "min_distance": Minimum distance in kilometers
                - "max_distance": Maximum distance in kilometers
                - "exclude_origin_cities": List of origin cities to exclude
                - "exclude_destination_cities": List of destination cities to exclude
                
        Returns:
            summary_round_trip_list_by_cabin: Dictionary mapping cabin classes
                to lists of the cheapest round trips grouped by city pairings
                
        Raises:
            ValueError: If no bulk availability data is provided or no trips are found
            
        Example:
            # Filter for trips originating only from Brazil, going to US, under $2000
            filter_criteria = {
                "origin_country": "BR",
                "destination_country": "US", 
                "max_cost": 2000,
                "exclude_destination_cities": ["New York"]
            }
            trips = flight_filter.getTopNTripsFromMultipleSources(
                bulk_data, 
                cabins=[CABIN.Y, CABIN.W], 
                n=5,
                filter=filter_criteria
            )
        """
        state.logger.info("Starting to filter top N trips from multiple sources")
        if not bulk_availability_by_source:
            state.logger.warning("No bulk availability data provided.")
            raise ValueError("No bulk availability data provided.")

        trips_by_cabin: dict[CABIN, dict[tuple[str, str], list[summary_round_trip]]] = dict()
        for source, bulk_availability in bulk_availability_by_source.items():
            state.logger.info(f"Processing bulk availability for source: {source.name} with length: {len(bulk_availability)}")
            if not bulk_availability:
                state.logger.warning(f"No data found for source: {source}")
                continue


            tripsByCabin = self.process_bulk_availability_object_for_round_trips(
                bulk_availability=bulk_availability,
                source=source,
                min_return_days=min_return_days,
                max_return_days=max_return_days,
                include_cabins= cabins if cabins else [cabin for cabin in CABIN],
                filter=filter
            )

            if not tripsByCabin:
                state.logger.warning(f"No trips found for source: {source}")
                continue

            for cabin, round_trips_by_city_pairings in tripsByCabin.items():
                if cabin not in trips_by_cabin:
                    trips_by_cabin[cabin] = dict()
                
                for city_pairings, round_trips_list in round_trips_by_city_pairings.items():
                    if city_pairings not in trips_by_cabin[cabin]:
                        trips_by_cabin[cabin][city_pairings] = []

                    trips_by_cabin[cabin][city_pairings].extend(round_trips_list)

        if not trips_by_cabin or len(trips_by_cabin) == 0 or all(
            len(cabin_data.values()) == 0
            for cabin_data in trips_by_cabin.values()
        ):
            state.logger.warning("No trips found in bulk availability data.")
            return None
        
        state.logger.info("Successfully fetched bulk availability data from multiple sources.")

        state.logger.info("Finding cheapest trips by cabin class")
        topNTripsByCabin = self.find_cheapest_for_round_trips(trips_by_cabin, n=n)

        if not topNTripsByCabin or len(trips_by_cabin) == 0 or all(
            len(cabin_data.values()) == 0
            for cabin_data in trips_by_cabin.values()
        ):
            state.logger.warning("No valid trips found.")
            return None

        state.logger.info("Successfully found cheapest cities by cabin.")
        return topNTripsByCabin
            
    
    def __calc_cost(self, df: pd.DataFrame, cabin: str, mileage_value: int) -> pd.Series:
        """
        Calculate the total cost for flights in a given cabin class.
        
        This private method calculates the total cost by converting mileage
        costs to monetary values and adding taxes.
        
        Args:
            df (pd.DataFrame): DataFrame containing flight data
            cabin (CABIN): Cabin class enum value
            mileage_value (int): Mileage point value for cost conversion
            
        Returns:
            pd.Series: Series containing calculated total costs
        """
        cost = df[f"{cabin}MileageCostRaw"] * mileage_value // 1000
        return cost + df[f"TotalTaxes_Standard"]

    @staticmethod
    def __calc_distance(coord1, coord2):
        return great_circle(coord1, coord2).km

    def __filter_trip(self, outbound_row: pd.Series, filters: dict, return_row: pd.Series = None) -> bool: #TODO: FIX THIS FUNCTION TO BE ABLE TO RECEIVE BOTH SINGLE AND ROUND TRIPS
        """
        Apply filters to a complete round trip.
        
        This method checks if a round trip meets the filter criteria by examining
        both the outbound and return flight details. It's designed to be called
        after the round trip pairing is complete.
        
        Args:
            round_trip (summary_round_trip): The complete round trip object
            outbound_row (pd.Series): DataFrame row for the outbound flight
            return_row (pd.Series): DataFrame row for the return flight
            filters (dict): Dictionary of filter criteria
            
        Returns:
            bool: True if the round trip passes all filters, False otherwise
        """
        # Apply origin country filter (check outbound flight origin)
        if "origin_country" in filters:
            outbound_country = outbound_row.get("origin_country", "Unknown")
            if outbound_country != filters["origin_country"]:
                return False
        
        # Apply destination country filter (check outbound flight destination)
        if "destination_country" in filters:
            destination_country = outbound_row.get("destination_country", "Unknown")
            if destination_country != filters["destination_country"]:
                return False
        
        # Apply origin cities filter
        if "origin_cities" in filters:
            origin_city = outbound_row.get("origin_city", "Unknown")
            if origin_city not in filters["origin_cities"]:
                return False
        
        # Apply destination cities filter
        if "destination_cities" in filters:
            destination_city = outbound_row.get("destination_city", "Unknown")
            if destination_city not in filters["destination_cities"]:
                return False
        
        # Apply maximum cost filter (total round trip cost)
        if "max_cost" in filters:
            total_cost = outbound_row.get("totalCost", 0) + (return_row.get("totalCost", 0) if return_row is not None else 0)
            if total_cost > filters["max_cost"]:
                return False
        
        # Apply distance filters
        if "min_distance" in filters and outbound_row.get("distance", 0) < filters["min_distance"]:
            return False
        if "max_distance" in filters and outbound_row.get("distance", 0) > filters["max_distance"]:
            return False
        
        # Apply exclusion filters
        if "exclude_origin_cities" in filters:
            origin_city = outbound_row.get("origin_city", "Unknown")
            if origin_city in filters["exclude_origin_cities"]:
                return False
        
        if "exclude_destination_cities" in filters:
            destination_city = outbound_row.get("destination_city", "Unknown")
            if destination_city in filters["exclude_destination_cities"]:
                return False
        
        return True
    
    def __proccess_BulkAvailability(
            self: list,
            bulk_availability: list,
    ) -> pd.DataFrame:
        """
        Process bulk flight availability data into a DataFrame.
        
        This private method normalizes the raw flight availability data into a
        pandas DataFrame for further processing and filtering.
        
        Args:
            bulk_availability (list): Raw flight availability data
            
        Returns:
            pd.DataFrame: Processed DataFrame containing flight details
            
        Raises:
            ValueError: If no bulk availability data is provided
        """
        if not bulk_availability:
            state.logger.warning("No bulk availability data provided.")
            return None
        
        state.logger.info("Processing bulk availability data into DataFrame")
        df = pd.json_normalize(bulk_availability)
        
        if df.empty:
            state.logger.warning("No data found in bulk availability.")
            return None
        
        # Debug: Log the columns available in the DataFrame
        # state.logger.info(f"Available columns in bulk availability DataFrame: {df.columns.tolist()}")

        # Debug: Log the first few rows to understand the structure
        if not df.empty:
            state.logger.info(f"First row of bulk availability data: {df.iloc[0].to_dict()}")
        
        # Assuming the DataFrame has columns for origin and destination airports
        # Map the airport codes to city names using config.CITY_IATA
        df["origin_city"] = df["Route.OriginAirport"].map(config.IATA_CITY)
        df["destination_city"] = df["Route.DestinationAirport"].map(config.IATA_CITY)
        # Drop rows where origin or destination city is not found
        df.dropna(subset=["origin_city", "destination_city"], inplace=True)

        # Map the origin country too
        df["origin_country"] = df["Route.OriginAirport"].map(config.IATA_COUNTRY)
        df["destination_country"] = df["Route.DestinationAirport"].map(config.IATA_COUNTRY)

        # Drop rows where origin or destination country is not found
        df.dropna(subset=["origin_country", "destination_country"], inplace=True)

        state.logger.info("Finished mapping additional data to DataFrame.")

        df["Distance"] = df.apply(
            lambda row: flight_Filter.__calc_distance(
                (config.IATA_LATITUDE.get(row["Route.OriginAirport"]), config.IATA_LONGITUDE.get(row["Route.OriginAirport"])),
                (config.IATA_LATITUDE.get(row["Route.DestinationAirport"]), config.IATA_LONGITUDE.get(row["Route.DestinationAirport"]))
            ) if config.IATA_LATITUDE.get(row["Route.OriginAirport"]) and config.IATA_LONGITUDE.get(row["Route.OriginAirport"]) and config.IATA_LATITUDE.get(row["Route.DestinationAirport"]) and config.IATA_LONGITUDE.get(row["Route.DestinationAirport"]) else None,
            axis=1
        )
        state.logger.info("Calculated distances for all flights.")

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        state.logger.info("Finished processing bulk availability data into DataFrame.")


        return df

    def __proccessCabinDf(
            self,
            flights_df: pd.DataFrame,
            mileage_value: int,
            cabin: CABIN,
    ) -> pd.DataFrame:
        """
        Process the DataFrame for a specific cabin class.
        
        This private method filters the DataFrame to include only flights in the specified cabin class,
        calculates costs, and prepares the DataFrame for further processing.
        
        Args:
            flights_df (pd.DataFrame): DataFrame containing flight data
            cabin (CABIN): Cabin class enum value
            
        Returns:
            pd.DataFrame: Processed DataFrame for the specified cabin class
        """
        cabin_df = flights_df[flights_df[f"{cabin.name}Available"] == True].copy()
        cabin_df = cabin_df[cabin_df[f"{cabin.name}RemainingSeats"] > 0]

        if cabin_df.empty:
            state.logger.warning(f"No flights found for cabin: {cabin.name}")
            return pd.DataFrame()

        cabin_df["TotalTaxes_Standard"] = cabin_df.apply(
                lambda row: cash_handler.convert_to_system_base(
                    int(row[f"{cabin.name}TotalTaxes"]), 
                    row["TaxesCurrency"]
                ), 
                axis=1
            )
        
        cabin_df["TotalCost"] = self.__calc_cost(cabin_df, cabin.name, mileage_value)
        
        return cabin_df


    def process_bulk_availability_object_for_single_trips(
            self,
            bulk_availability: list,
            source: SOURCE,
            include_cabins: list[CABIN] = [cabin for cabin in CABIN],
            filter: dict = None
    ) -> dict[CABIN, list[summary_trip]] | None:
        """
        Process bulk flight availability data to create single trip options.
        
        This private method processes raw flight availability data, calculates costs,
        applies filters, and creates single trip options grouped by cabin class and city pairings.
        
        Args:
            bulk_availability (list): Raw flight availability data
            source (str): Source identifier for mileage value lookup
            min_return_days (int, optional): Minimum days between outbound and return
            max_return_days (int, optional): Maximum days between outbound and return
            include_cabins (set[CABIN], optional): Set of cabin classes to include.
                Defaults to all available cabin classes.
            filter (dict, optional): Filter criteria. Supported keys:
                - "origin_country": Only include trips originating from this country (e.g., "BR")
                - "destination_country": Only include trips going to this country (e.g., "US")
                - "origin_cities": List of specific origin cities to include
                - "destination_cities": List of specific destination cities to include
                - "max_cost": Maximum total cost per flight
                - "min_distance": Minimum distance in kilometers
                - "max_distance": Maximum distance in kilometers
                - "exclude_origin_cities": List of origin cities to exclude
                - "exclude_destination_cities": List of destination cities to exclude
                
        Returns:
            summary_round_trip_list_by_cabin: Dictionary mapping cabin classes
                to dictionaries of city pairings and their single trip lists
                
        Note:
            - Converts all costs to system base currency using exchange rates
        """
        if not bulk_availability or len(bulk_availability) == 0:
            state.logger.warning("No bulk availability data provided.")
            return None

        state.logger.info(f"Starting to process bulk availability data for single trips") 
        # Assuming bulk_availability is a dictionary with a "data" key containing the relevant data
        bulk_df = self.__proccess_BulkAvailability(bulk_availability)
        if bulk_df.empty:
            state.logger.warning("No data found in bulk availability.")
            return None
        
        mileage_value = mileage_handler.get_mileage_value(source.value)

        trips_by_city_by_cabin: dict[CABIN, dict[str, summary_trip]] = dict()
        state.logger.info(f"Starting to process each cabin class in bulk availability data for cabins: {include_cabins}")
        for cabin in include_cabins:
            state.logger.info(f"Processing cabin class: {cabin.name}")
            cabin_df = self.__proccessCabinDf(
                flights_df=bulk_df,
                mileage_value=mileage_value,
                cabin=cabin
            )

            if cabin_df.empty:
                state.logger.warning(f"No data found for cabin: {cabin.name}.")
                continue

            if cabin not in trips_by_city_by_cabin:
                trips_by_city_by_cabin[cabin] = {}

            for _, row in cabin_df.iterrows():
                # Apply filters to the complete trip
                if filter and not self.__filter_trip(row, filter):
                    continue

                trip = summary_trip(
                    ID=row["ID"],
                    origin_city=row["origin_city"],
                    destination_city=row["destination_city"],
                    totalCost=row["TotalCost"],
                    distance=row["Distance"],
                )

                if (trip.origin_city, trip.destination_city) not in trips_by_city_by_cabin[cabin]:
                    trips_by_city_by_cabin[cabin][(trip.origin_city, trip.destination_city)] = {}

                if trips_by_city_by_cabin[cabin][(trip.origin_city, trip.destination_city)] and trip.totalCost >= trips_by_city_by_cabin[cabin][(trip.origin_city, trip.destination_city)].totalCost:
                    continue

                trips_by_city_by_cabin[cabin][(trip.origin_city, trip.destination_city)] = trip

        trips_by_cabin: dict[CABIN, list[summary_trip]] = dict()
        for cabin, city_trips in trips_by_city_by_cabin.items():
            trips_by_cabin[cabin] = list(city_trips.values())
        return trips_by_cabin

    def process_bulk_availability_object_for_round_trips(
            self, 
            bulk_availability: list, 
            source: SOURCE, min_return_days: int = None, 
            max_return_days: int = None, 
            include_cabins: list[CABIN] = [cabin for cabin in CABIN],
            filter: dict = None
    ) -> dict[CABIN, dict[tuple[str, str], list[summary_round_trip]]] | None:
        """
        Process bulk flight availability data to create round trip combinations.
        
        This private method is the core processing function that:
        - Normalizes raw flight availability data into a DataFrame
        - Maps airport codes to city names
        - Calculates costs using mileage values and exchange rates
        - Groups flights by cabin class and city pairings
        - Creates valid round trip combinations based on date constraints
        - Filters out insufficient or invalid trip options
        
        Args:
            bulk_availability (list): Raw flight availability data
            source (str): Source identifier for mileage value lookup
            min_return_days (int, optional): Minimum days between outbound and return
            max_return_days (int, optional): Maximum days between outbound and return
            include_cabins (set[CABIN], optional): Set of cabin classes to include.
                Defaults to all available cabin classes.
            filter (dict, optional): Filter criteria. Supported keys:
                - "origin_country": Only include trips originating from this country (e.g., "BR")
                - "destination_country": Only include trips going to this country (e.g., "US")
                - "origin_cities": List of specific origin cities to include
                - "destination_cities": List of specific destination cities to include
                - "max_cost": Maximum total cost per flight
                - "min_distance": Minimum distance in kilometers
                - "max_distance": Maximum distance in kilometers
                - "exclude_origin_cities": List of origin cities to exclude
                - "exclude_destination_cities": List of destination cities to exclude
                
        Returns:
            summary_round_trip_list_by_cabin: Dictionary mapping cabin classes
                to dictionaries of city pairings and their round trip lists
                
        Note:
            - Only considers round trips with 5+ valid combinations
            - Filters trips based on min_return_days and max_return_days
            - Converts all costs to system base currency using exchange rates
        """
        if not bulk_availability or len(bulk_availability) == 0:
            state.logger.warning("No bulk availability data provided.")
            return None

        state.logger.info(f"Starting to process bulk availability data") 
        # Assuming bulk_availability is a dictionary with a "data" key containing the relevant data
        bulk_df = self.__proccess_BulkAvailability(bulk_availability)
        if bulk_df.empty:
            state.logger.warning("No data found in bulk availability.")
            return None

        mileage_value = mileage_handler.get_mileage_value(source.value)

        trips_by_cabin: dict[CABIN, dict[tuple[str, str], list[summary_round_trip]]] = dict()
        state.logger.info(f"Starting to process each cabin class in bulk availability data for cabins: {include_cabins}")
        for cabin in include_cabins:
            state.logger.info(f"Processing cabin class: {cabin.name}")
            cabin_df = self.__proccessCabinDf(
                flights_df=bulk_df,
                mileage_value=mileage_value,
                cabin=cabin
            )
            if cabin_df.empty:
                state.logger.warning(f"No data found for cabin: {cabin.name}.")
                continue


            round_trips_by_city: dict[tuple[str, str], list[summary_round_trip]] = dict()
            grouped_cabin = cabin_df.groupby(["origin_city", "destination_city"])
            if grouped_cabin.size == 0:
                state.logger.warning(f"No grouped data found for cabin {cabin.name}.")
                continue
            
            state.logger.info(f"Found {len(grouped_cabin)} groups for cabin {cabin.name}.")
            has_trips = False
            for (origin, destination), group in grouped_cabin:

                state.logger.info(f"Processing trips from {origin} to {destination} for cabin {cabin.name}.")
                if group.empty:
                    state.logger.warning(f"No data found for cabin {cabin.name} from {origin} to {destination}.")
                    continue

                reverse_cabin_group: pd.DataFrame = cabin_df[
                    (cabin_df["origin_city"] == destination) &
                    (cabin_df["destination_city"] == origin)
                ]

                state.logger.info(f"Found {len(reverse_cabin_group)} reverse trips for cabin {cabin.name} from {destination} to {origin}.")

                round_trips_list: list[summary_round_trip] = []
                for _, outbound in group.iterrows():
                    for _, return_ in reverse_cabin_group.iterrows():
                        if return_["Date"] <= outbound["Date"]:
                            continue

                        if min_return_days and max_return_days:
                            interval = (return_["Date"] - outbound["Date"]).days
                            if interval < min_return_days or interval > max_return_days:
                                continue

                        # Apply filters to the complete round trip
                        if filter and not self.__filter_trip(outbound, filter, return_row=return_):
                            continue
                        
                        # Create the round trip object first
                        outbound_trip = summary_trip(
                            ID=outbound["ID"],
                            origin_city=outbound["origin_city"],
                            destination_city=outbound["destination_city"],
                            totalCost=outbound["TotalCost"],
                            distance=outbound["Distance"]
                        )
                        return_trip = summary_trip(
                            ID=return_["ID"],
                            origin_city=return_["origin_city"],
                            destination_city=return_["destination_city"],
                            totalCost=return_["TotalCost"],
                            distance=return_["Distance"]
                        )
                        round_trip = summary_round_trip(
                            outbound=outbound_trip,
                            return_=return_trip,
                        )
                        
                       
                        
                        state.logger.info(f"Adding valid round trip from {origin} to {destination} for cabin {cabin.name}.")
                        round_trips_list.append(round_trip)
                if not round_trips_list or len(round_trips_list) < 1:
                    state.logger.warning(f"No valid round trips found for cabin {cabin.name} from {origin} to {destination}.")
                    continue

                state.logger.info(f"Found {len(round_trips_list)} round trips for cabin {cabin.name} from {origin} to {destination}.")
                round_trips_by_city[(origin, destination)] = round_trips_list

            if not round_trips_by_city or len(round_trips_by_city) == 0:
                state.logger.warning(f"No round trips found for cabin {cabin.name}.")
                continue
            
            has_trips = True
            trips_by_cabin[cabin] = round_trips_by_city
            state.logger.info(f"Found {len(round_trips_by_city)} round trips for cabin {cabin.name}.")

        if not trips_by_cabin or has_trips is False:
            state.logger.warning("No trips found in bulk availability data.")
            return None
        
        state.logger.info("Successfully processed bulk availability for round trips.")
        return trips_by_cabin
    
    def __score(self, *trips: summary_trip) -> float:
        """
        Calculate a score for one or more trips based on cost and distance.
        
        This method computes a score by dividing the total cost of all round trips
        by the total distance traveled, providing a cost-efficiency metric.
        
        Args:
            *round_trips: Variable number of round trip objects
                
        Returns:
            float: Average score for all round trips, or infinity if total distance is zero
            
        Raises:
            ValueError: If no round trips are provided or if any round trip is invalid
        """
        if not trips:
            raise ValueError("At least one round trip must be provided")
        
        total_cost = 0
        total_distance = 0
        
        for trip in trips:
            if not trip or not trip.distance or not trip.totalCost:
                raise ValueError("Invalid trip data")

            total_cost += trip.totalCost
            total_distance += trip.distance

        return total_cost / (total_distance * 0.7) if total_distance > 0 else float('inf')


    def find_cheapest_for_single_trips(self, trip_list_by_cabin: dict[CABIN, list[summary_trip]], n: int = 1) -> dict[CABIN, list[summary_trip]]:
        """
        Find the N cheapest city pairings for each cabin class.
        
        This private method processes grouped trip data to identify
        the cheapest flight options. The algorithm:
        1. For each cabin class:
            - Sorts trips by total cost
            - Takes the top N cheapest trips
        2. Returns a dictionary mapping cabin classes to lists of the N cheapest trips
        Args:
            trip_list_by_cabin (summary_trip_list_by_cabin):
                Dictionary mapping cabin classes to lists of trips  
        Returns:
            summary_trip_list_by_cabin: Dictionary mapping cabin classes to lists of the N cheapest trips
        """
        if not trip_list_by_cabin or len(trip_list_by_cabin) == 0:
            state.logger.warning("No trips found in bulk availability data.")
            return None

        cheapest_trips_by_cabin: dict[CABIN, list[summary_trip]] = dict()
     
        for cabin, trips in trip_list_by_cabin.items():
            if not trips:
                state.logger.warning(f"No trips found for cabin {cabin.name}.")
                continue

            # Sort the trips by total cost
            sorted_trips = sorted(trips, key=lambda x: self.__score(x))

            # Take the top N cheapest trips
            cheapest_trips = sorted_trips[:n]

            if not cheapest_trips:
                state.logger.warning(f"No valid cheapest trips found for cabin {cabin}.")
                continue

            cheapest_trips_by_cabin[cabin] = cheapest_trips

        return cheapest_trips_by_cabin


    def find_cheapest_for_round_trips(self, round_trip_list_by_cabin: dict[CABIN, dict[tuple[str, str], list[summary_round_trip]]], n: int = 1) -> dict[CABIN, dict[tuple[str, str], list[summary_round_trip]]]:
        """
        Find the N cheapest city pairings for each cabin class.
        
        This private method processes grouped round trip data to identify
        the cheapest flight options. The algorithm:
        1. For each cabin class and city pairing:
           - Sorts round trips by total cost (outbound + return)
           - Takes the top 5 cheapest trips per city pairing
        2. Sorts city pairings by the cost of their 5th cheapest trip
        3. Returns the top N cheapest city pairings per cabin class
        
        Args:
            round_trip_list_by_cabin (summary_round_trip_list_by_cabin):
                Dictionary mapping cabin classes to city pairings and their trip lists
                
        Returns:
            dict: Dictionary mapping cabin classes to lists of the N cheapest
                city pairings with their associated round trips
                
        Note:
            - Requires at least 5 valid round trips per city pairing
            - Uses n to determine how many city pairings to return
            - Sorts by the 5th element cost to ensure consistent quality across options
        """
        if not round_trip_list_by_cabin or len(round_trip_list_by_cabin) == 0:
            return None
        
        cheapest_cities_by_cabin: dict[CABIN, list[summary_round_trip]] = dict()

        for cabin, round_trip_by_city_pairings in round_trip_list_by_cabin.items():
            if not round_trip_by_city_pairings:
                state.logger.warning(f"No trips found for cabin {cabin.name}.")
                continue

            sorted_cities: dict[tuple[str, str], list[summary_round_trip]] = dict()

            for city_pairings, round_trips_list in round_trip_by_city_pairings.items():
                if not round_trips_list:
                    state.logger.warning(f"No round trips found for cabin {cabin.name} at city pairings {city_pairings}.")
                    continue
                    
                # Sort the round trips by the total cost of the outbound and return trips
                round_trips_list.sort(key=lambda trip: trip.outbound.totalCost + trip.return_.totalCost)
                
                # Append the top 5 cheapest round trips to the cheapest_cities list
                sorted_cities[city_pairings] = round_trips_list[:5]

            if not sorted_cities or len(sorted_cities) == 0:
                state.logger.warning(f"No valid cheapest cities found for cabin {cabin}.")
                continue

            # Flatten to list of (city_pairing, round_trips_list, 5th_trip_cost) for sorting
            flattened_cities = []
            for city_pairing, round_trips_list in sorted_cities.items():
                first_trip_cost = round_trips_list[0].outbound.totalCost + round_trips_list[0].return_.totalCost

                # Keep only trips that are within 10% of the cheapest trip
                filtered_trips = [
                    trip for trip in round_trips_list
                    if (trip.outbound.totalCost + trip.return_.totalCost) / first_trip_cost <= 1.1
                ]
                
                # Ensure we have at least some trips after filtering
                if len(filtered_trips) < 1:
                    state.logger.warning(f"No valid round trips found after filtering for city pairings {city_pairing}.")
                    continue
                
                # Use the filtered list
                round_trips_list = filtered_trips
                average_score = self.__score(*[trip.outbound for trip in round_trips_list], *[trip.return_ for trip in round_trips_list]) / len(round_trips_list)
                flattened_cities.append((city_pairing, round_trips_list, average_score))

            flattened_cities.sort(key=lambda x: (x[2]))
            flattened_cities = flattened_cities[:n] # Take only n candidates
            shuffle(flattened_cities) # Shuffle the final candidates

            # Convert back to dict format
            final_cheapest_cities = {city_pairing: round_trips_list for city_pairing, round_trips_list, _, in flattened_cities}

            cheapest_cities_by_cabin[cabin] = final_cheapest_cities

        if not cheapest_cities_by_cabin:
            state.logger.warning("No cheapest cities found for any cabin class.")
            return {}

        return cheapest_cities_by_cabin
             
# Create a singleton instance for use throughout the application
flight_Filter = Flight_Filter()