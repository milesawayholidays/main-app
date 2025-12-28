"""
Flight filtering logic and algorithms.

This module contains the FlightSearchProcessor class, which provides methods to filter
and process flight availability data from multiple airline sources. It includes
functionality to filter for valid round trips, calculate costs, and identify the
cheapest options by cabin class and city pairings.
Classes:
    FlightSearchProcessor: Main class for filtering and processing flight availability data.    
Methods:
    find_top_oneway_trips: Get the best one-way trips from bulk flight
    find_top_round_trips: Get the best round trips from bulk flight
    __normalise_results: Convert FlightSearchResult data to a pandas DataFrame and map additional information.
    __enrich_dataframe: Expand trip data in the DataFrame to include necessary columns for processing.
    __prepare_cabin_data: Filter the DataFrame for flights available in a specific cabin class and calculate total costs.
    __pair_round_trips: Merge outbound and return flight DataFrames to form round trips.
    __apply_ranking: Sort the DataFrame by specified columns and select the top N entries.
    __calculate_total_cost: Calculate the total cost for flights in a given cabin class.
    __haversine: Calculate the Haversine distance between two geographic points.
    __calculate_score: Calculate a score for one or more trips based on cost and distance.
    __query_results: Apply filters to a complete round trip.
"""

import pandas as pd
import numpy as np

from global_state import state
from config import config
from currencies.mileage import handler as mileage_handler
from currencies.cash import handler as cash_handler

from data_types.enums import CABIN
from data_types.Flight import FlightQuery, RawFlightResult, FilteredFlightList
from data_types.cities import AIRPORT_TIER, TIER_BONUS


class FlightSearchProcessor:
    """
    Main class for filtering and processing flight availability data.
    
    This class provides methods to process bulk flight availability data from
    multiple airline sources, filter for valid round trips, calculate costs,
    and identify the cheapest options by cabin class and city pairings.
    """
    
    
    OUT_SUFFIX = "_out"
    RET_SUFFIX = "_ret"

    ONEWAY_CITY_PAIR_PARAM = [f"origin_city", f"destination_city"]
    ROUND_CITY_PAIR_PARAM = [f"origin_city{OUT_SUFFIX}", f"destination_city{OUT_SUFFIX}"]
    CUTOFF_THRESHOLD = 1.10  # 10% above the minimum price in the city pair
    PACKAGE_SIZE = 5         # Number of options to return per city pair

    WEIGHT_COST = 1.0
    WEIGHT_DISTANCE = 0.01
    WEIGHT_TIER = 3.0

    @classmethod
    def find_top_oneway_trips(
            cls,
            flight_search_results: list[RawFlightResult],
            query: FlightQuery,
            n: int = 1) -> FilteredFlightList:
        """ 
        Get the best one-way trips from bulk flight availability data.
        This method processes flight availability data, applies filters,
        and returns the cheapest options by cabin class.
        Args:
            flight_search_results (list[RawFlightResult]): List of flight availability data
            query (FlightQuery): Filter criteria for trips.
            n (int, optional): Number of top trips to return. Defaults to 1.
        Returns:
            FilteredFlightList: List of the best one-way flight options
        """
        
        state.logger.info(f"Starting to filter top {n} one-way trips of length: {len(flight_search_results)}")
        if not flight_search_results:
            state.logger.warning("No bulk availability data provided.")
            raise ValueError("No bulk availability data provided.")
        
        unproccessed_flights_df:pd.DataFrame = cls.__normalise_results(flight_search_results)
        unproccessed_flights_df:pd.DataFrame = cls.__enrich_dataframe(unproccessed_flights_df)


        cabins: list[CABIN] = query.get("cabins", [cabin for cabin in CABIN])
        valid_columns = [f"{c.name}_available" for c in cabins]

        mask = False
        for col in valid_columns:
            mask = mask | (unproccessed_flights_df[col] > 0)

        unproccessed_flights_df = unproccessed_flights_df[mask]

        if unproccessed_flights_df.empty:
            state.logger.warning("No data found for the specified cabins.")
            raise ValueError("No data found for the specified cabins.")
        
        flights_df: pd.DataFrame
        for cabin in cabins:
            state.logger.info(f"Processing cabin class: {cabin.name}")
            cabin_df: pd.DataFrame = cls.__prepare_cabin_data(
                flights_df=unproccessed_flights_df,
                cabin=cabin.name
            )
            if cabin_df.empty:
                state.logger.warning(f"No data found for cabin: {cabin.name}.")
                continue
            state.logger.info(f"Left with {len(cabin_df)} records after preparing cabin data.")

            if query.get("extra_filters", False):
                cabin_df = cls.__query_results(cabin_df, query)  
            state.logger.info(f"Left with {len(cabin_df)} records after applying extra filters.")

            topN: pd.DataFrame = cls.__apply_ranking(
                df=cabin_df,
                query=query,
                n=n
            )
            state.logger.info(f"Found {len(topN)} top trips")

            flights_df = pd.concat([flights_df, topN], ignore_index=True) if 'flights_df' in locals() else topN
        
        state.logger.info(f"Total top trips found: {len(flights_df)}")
        flights = FilteredFlightList().append_from_dataframe(flights_df)
        if not flights or len(flights) == 0:
            state.logger.warning("No trips found after processing bulk availability data.")
            raise ValueError("No trips found after processing bulk availability data.")
        
        state.logger.info(f"Found {len(flights)} cheapest flights")
        return flights
        
    @classmethod
    def find_top_round_trips(
            cls,
            search_results: list[RawFlightResult],
            query: FlightQuery,
            n: int = 1) -> FilteredFlightList:
        """
        Get the best round trips from bulk flight availability data.
        This method processes flight availability data, applies filters,
        and returns the cheapest options by cabin class.
        Args:
            search_results (list[RawFlightResult]): List of flight availability data
            n (int, optional): Number of top trips to return. Defaults to 1.
            query (FlightQuery, optional): Filter criteria for trips. Defaults to None.
        Returns:
            FilteredFlightList: List of the best round trip flight options
        """
        state.logger.info(f"Starting to filter top {n} round trips of length: {len(search_results)}")
        if not search_results:
            state.logger.warning("No bulk availability data provided.")
            raise ValueError("No bulk availability data provided.")

        unproccessed_trips_df:pd.DataFrame = cls.__normalise_results(search_results)
        unproccessed_trips_df:pd.DataFrame = cls.__enrich_dataframe(unproccessed_trips_df)

        cabins: list[CABIN] = query.get("cabins", [cabin for cabin in CABIN])
        unproccessed_trips_df = unproccessed_trips_df[unproccessed_trips_df["cabin"].isin([cabin.value for cabin in cabins])]
        if unproccessed_trips_df.empty:
            state.logger.warning("No data found for the specified cabins.")
            raise ValueError("No data found for the specified cabins.")
        
        trips_df: pd.DataFrame
        for cabin in cabins:
            state.logger.info(f"Processing cabin class: {cabin.name}")
            cabin_df: pd.DataFrame = cls.__prepare_cabin_data(
                flights_df=unproccessed_trips_df,
                cabin=cabin.name
            )
            if cabin_df.empty:
                state.logger.warning(f"No data found for cabin: {cabin.name}.")
                continue
            state.logger.info(f"Left with {len(cabin_df)} records after preparing cabin data.")

            merged_df: pd.DataFrame = cls.__pair_round_trips(cabin_df)

            merged_df = merged_df[
            merged_df["date_ret"] > merged_df["date_out"]
            ]
            state.logger.info(f"Left with {len(merged_df)} records after pairing round trips.")

            if query.min_return_days and query.max_return_days:
                intervals = (merged_df["date_ret"] - merged_df["date_out"]).dt.days
                merged_df = merged_df[
                    (intervals >= query.min_return_days) &
                    (intervals <= query.max_return_days)
                ]

            if query.get("extra_filters", False):
                merged_df = cls.__query_results(merged_df, query, suffix=cls.OUT_SUFFIX)   
            state.logger.info(f"Left with {len(merged_df)} records after applying extra filters.")   

            topN: pd.DataFrame = cls.__apply_ranking(
                df=merged_df,
                query=query,
                n=n,
                out_suffix=cls.OUT_SUFFIX,
                ret_suffix=cls.RET_SUFFIX
            )
            state.logger.info(f"Found {len(topN)} top trips")

            trips_df = pd.concat([trips_df, topN], ignore_index=True) if 'trips_df' in locals() else topN
             
        state.logger.info(f"Total top trips found: {len(trips_df)}")
        trips = FilteredFlightList().append_from_dataframe(trips_df, out_suffix=cls.OUT_SUFFIX, ret_suffix=cls.RET_SUFFIX)

        if not trips or len(trips) == 0:
            state.logger.warning("No trips found after processing bulk availability data.")
            raise ValueError("No trips found after processing bulk availability data.")
        

        state.logger.info(f"Found {len(trips)} cheapest round trips")
        return trips        


    ###----------------###
    ###----------------###
    ### HELPER METHODS ###
    ###----------------###
    ###----------------###

    
    #--------------------------------------#
    #--------------------------------------#
    #--------------------------------------#
    #---- DataFrame Processing Methods ----#
    #--------------------------------------#
    #--------------------------------------#
    #--------------------------------------#

    @classmethod
    def __normalise_results(
        cls,
        data: list[RawFlightResult],
    ) -> pd.DataFrame:
        """
        Convert RawFlightResult data to a pandas DataFrame and map additional information.

        Args:
            data (list[RawFlightResult]): List of flight search result objects   
        Returns:
            pd.DataFrame: DataFrame containing flight availability data
        """
        if not data:
            state.logger.error("No data provided to vectorise.")
            raise ValueError("No data provided to vectorise.")
        
        state.logger.info("Processing bulk availability data into DataFrame")
        df = pd.DataFrame([d.to_dict() for d in data])
        
        if df.empty:
            state.logger.error("No data found in bulk availability.")
            raise ValueError("No data found in bulk availability.")
        
        state.logger.info(f"Successfully processed bulk availability data into DataFrame with length: {len(df)}")
        return df
    
    @classmethod
    def __enrich_dataframe(
        cls,
        df: pd.DataFrame, 
    ) -> pd.DataFrame:
        """
        Expand trip data in the DataFrame to include necessary columns for processing.
        The necessary columns include:
        - origin_city
        - destination_city
        - origin_country
        - destination_country
        - Distance
        - MileageValue
        - Date
        - updated_at

        Args:
            df (pd.DataFrame): DataFrame containing flight data
        Returns:
            pd.DataFrame: Expanded DataFrame with additional columns
        """
        # Map the airport codes to city names using config.CITY_IATA
        df["origin_city"] = df["origin_airport"].map(config.IATA_CITY)
        df["destination_city"] = df["destination_airport"].map(config.IATA_CITY)
        # Drop rows where origin or destination city is not found
        df.dropna(subset=["origin_city", "destination_city"], inplace=True)

        # Map the origin country too
        df["origin_country"] = df["origin_airport"].map(config.IATA_COUNTRY)
        df["destination_country"] = df["destination_airport"].map(config.IATA_COUNTRY)
        # Drop rows where origin or destination country is not found
        df.dropna(subset=["origin_country", "destination_country"], inplace=True)

    
        df["origin_lat"] = df["origin_airport"].map(config.IATA_LATITUDE)
        df["origin_lon"] = df["origin_airport"].map(config.IATA_LONGITUDE)
        df["destination_lat"] = df["destination_airport"].map(config.IATA_LATITUDE)
        df["destination_lon"] = df["destination_airport"].map(config.IATA_LONGITUDE)

        df["distance"] = cls.__haversine(
            df["origin_lat"], df["origin_lon"],
            df["destination_lat"], df["destination_lon"]
        )

        df.dropna(subset=["distance"], inplace=True)

        df["mileage_value"] = mileage_handler.get_mileage_value_vectorised(
            df["source"].values
        )

        df.dropna(subset=["mileage_value"], inplace=True)

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        
        df["updated_at"] = pd.to_datetime(df["updated_at"], errors="coerce")

        #df = df[df["updated_at"] >= pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=1)]

        state.logger.info(f"Successfully expanded trip data with necessary columns for processing. DataFrame length: {len(df)}")

        return df

    @classmethod
    def __prepare_cabin_data(
        cls,
        flights_df: pd.DataFrame,
        cabin: str) -> pd.DataFrame:
        """
        Filter the DataFrame for flights available in a specific cabin key and calculate total costs.
        
        Args:
            flights_df (pd.DataFrame): DataFrame containing flight data
            cabin (str): Cabin key as a string
            
        Returns:
            pd.DataFrame: Processed DataFrame for the specified cabin key
        """
        cabin_df = flights_df[flights_df[f"{cabin}_available"] == True].copy()
        cabin_df = cabin_df[cabin_df[f"{cabin}_remaining_seats"] > 0]

        cabin_df["cabin"] = CABIN[cabin].value


        if cabin_df.empty:
            state.logger.warning(f"No flights found for cabin: {cabin}")
            return pd.DataFrame()
        
        cabin_df[f"{cabin}_taxes"] = (
            cabin_df[f"{cabin}_taxes"]
            .fillna(0)
            .replace("", 0)
            )   

        cabin_df[f"{cabin}_taxes_standard"] = cash_handler.convert_to_system_base_vectorised(
            cabin_df[f"{cabin}_taxes"].astype(int).values,
            cabin_df["taxes_currency"].values
        )
        
        cabin_df["total_cost"] = cls.__calculate_total_cost(cabin_df, cabin)
        
        return cabin_df

    @classmethod
    def __pair_round_trips(
        cls,
        df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge outbound and return flight DataFrames to form round trips.
        
        Args:
            outbound_df (pd.DataFrame): DataFrame containing outbound flight data
            return_df (pd.DataFrame): DataFrame containing return flight data
        Returns:
            pd.DataFrame: Merged DataFrame containing round trip data
        """
        outbound_df = df.add_suffix(cls.OUT_SUFFIX)
        return_df = (
            df
            .rename(columns={
                "origin_city": "destination_city",
                "destination_city": "origin_city",
            })
            .add_suffix(cls.RET_SUFFIX)
            )   
        
        merged_df = outbound_df.merge(
            return_df,
            left_on=[f"origin_city{cls.OUT_SUFFIX}", f"destination_city{cls.OUT_SUFFIX}"],
            right_on=[f"destination_city{cls.RET_SUFFIX}", f"origin_city{cls.RET_SUFFIX}"],
            how='inner'
        )
            
        merged_df = merged_df[
            merged_df[f"date{cls.RET_SUFFIX}"] > merged_df[f"date{cls.OUT_SUFFIX}"]
        ]

        return merged_df
    
    @classmethod
    def __apply_ranking(
        cls,
        df: pd.DataFrame,
        query: FlightQuery, 
        n: int,
        out_suffix: str = "",
        ret_suffix: str = "",
        ) -> pd.DataFrame:
        """
        Sort the DataFrame by specified columns and select the top N entries.
        
        Args:
            df (pd.DataFrame): DataFrame containing flight data
            n (int): Number of top entries to select
        Returns:
            pd.DataFrame: Sorted DataFrame with top N entries
        """

        if out_suffix != "" and ret_suffix != "":
            df["total_cost"] = df[f"total_cost{out_suffix}"] + df[f"total_cost{ret_suffix}"]
            df["distance"] = df[f"distance{out_suffix}"]

        if query.get("max_cost", None) is not None:
            df = df[
                (df["total_cost"] <= query["max_cost"])
            ]

        df = cls.__calculate_score(df, out_suffix)
        
        group_by_factor = cls.ONEWAY_CITY_PAIR_PARAM if out_suffix == "" and ret_suffix == "" else cls.ROUND_CITY_PAIR_PARAM

        df["min_price_in_pair"] = (
        df.groupby(group_by_factor)["total_cost"]
            .transform("min"))

        df["cutoff_price"] = df["min_price_in_pair"] * cls.CUTOFF_THRESHOLD
        df = df[df["total_cost"] <= df["cutoff_price"]] 
        
        top5 = (
            df
            .sort_values(["score", f"date{out_suffix}", f"date{ret_suffix}"], ascending=[True, True, True])
            .groupby(group_by_factor)
            .head(cls.PACKAGE_SIZE)
        )

        # region pairing
        top5["region_pair"] = list(zip(top5[f"origin_region{out_suffix}"], top5[f"destination_region{out_suffix}"]))


        top5 = top5.sort_values(["region_pair", "score"], ascending=[True, True])

        # GLOBAL limit
        global_limit = n * cls.PACKAGE_SIZE

        topN = top5.head(global_limit).copy()

        cols_to_drop = [
            "min_price_in_pair",
            "cutoff_price",
            "region_pair",
        ]

        topN = topN.drop(columns=[c for c in cols_to_drop if c in topN.columns])

        return topN
    
    #-----------------------------#
    #-----------------------------#
    #-----------------------------#
    #---- Calculation Methods ----#
    #-----------------------------#
    #-----------------------------#
    #-----------------------------#


    @classmethod
    def __calculate_total_cost(cls, df: pd.DataFrame, cabin: str) -> pd.Series:
        """
        Calculate the total cost for flights in a given cabin class.
        
        This private method calculates the total cost by converting mileage
        costs to monetary values and adding taxes.
        
        Args:
            df (pd.DataFrame): DataFrame containing flight data
            cabin (CABIN): Cabin class enum value            
        Returns:
            pd.Series: Series containing calculated total costs
        """
        cost = df[f"{cabin}_mileage"] * df["mileage_value"] // 1000
        return cost + df[f"{cabin}_taxes_standard"]

    @classmethod
    def __haversine(cls, lat1, lon1, lat2, lon2):
        R = 6371

        lat1 = np.radians(lat1)
        lon1 = np.radians(lon1)
        lat2 = np.radians(lat2)
        lon2 = np.radians(lon2)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
        c = 2 * np.arcsin(np.sqrt(a))

        return R * c
    
    @classmethod
    def __calculate_score(cls, df: pd.DataFrame, suffix: str = "") -> pd.DataFrame:
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

            df["score"] = (
                df["total_cost"] * cls.WEIGHT_COST + 
                df["distance"] * cls.WEIGHT_DISTANCE
            )

            DEFAULT_TIER = max(TIER_BONUS.keys())
            df["origin_tier"] = df[f"origin_airport{suffix}"].map(AIRPORT_TIER).fillna(DEFAULT_TIER)
            df["destination_tier"] = df[f"destination_airport{suffix}"].map(AIRPORT_TIER).fillna(DEFAULT_TIER)
            
            
            df["score"] += (df["origin_tier"] + df["destination_tier"]).map(TIER_BONUS).astype(float) * cls.WEIGHT_TIER

            df.drop(columns=["origin_tier", "destination_tier"], inplace=True)

            return df
    
    @staticmethod
    def __query_results(df: pd.DataFrame, query: FlightQuery, suffix: str = "") -> pd.DataFrame:
        """
        Apply filters to a complete round trip.
        
        This method checks if a round trip meets the filter criteria by examining
        both the outbound and return flight details. It's designed to be called
        after the round trip pairing is complete.
        
        Args:
            df (pd.DataFrame): DataFrame containing round trip data
            filter (FlightFilter): Filter criteria for trips
            out_suffix (str, optional): Suffix for outbound flight columns. Defaults to "".
        Returns:
            pd.DataFrame: Filtered DataFrame containing only trips that meet the criteria
        Note:
            This method can handle both one-way and round trips by adjusting the suffixes
            - Use empty suffix for one-way trips
            - Use OUT_SUFFIX suffix for round trips, as both outbound and return flights are merged within the same DataFrame
        """

        q = pd.Series([True] * len(df))

        if query.origin_airports:
            q &= df[f"origin_airport{suffix}"].isin(query.origin_airports)
        
        if query.destination_airports:
            q &= df[f"destination_airport{suffix}"].isin(query.destination_airports)

        if query.origin_cities:
            q &= df[f"origin_city{suffix}"].isin(query.origin_cities)
        
        if query.destination_cities:
            q &= df[f"destination_city{suffix}"].isin(query.destination_cities)

        if query.origin_countries:
            q &= df[f"origin_country{suffix}"].isin(query.origin_countries)
        
        if query.destination_countries:
            q &= df[f"destination_country{suffix}"].isin(query.destination_countries) 
        
        if "min_distance" in query:
            q &= df.get(f"distance{suffix}", 0) >= query["min_distance"]
        
        if "max_distance" in query:
            q &= df.get(f"distance{suffix}", 0) <= query["max_distance"]
        
        return df[q]
             
# Create a singleton instance for use throughout the application
flight_processor = FlightSearchProcessor()   