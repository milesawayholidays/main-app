"""
Enumeration definitions for the flight alert system.

This module contains al
class SOURCE(Enum):sed throughout the application
to define valid values for sources, regions, and cabin classes.
"""

from enum import Enum


class SOURCE(Enum):
    """
    Enum for supported airline mileage programs and booking sources.
    
    These represent the different airline loyalty programs or booking
    platforms that the system can fetch flight data from.
    """
    AZUL = "azul"          # Azul Airlines loyalty program
    SMILES = "smiles"      # Smiles (GOL) loyalty program  
    QANTAS = "qantas"        # Qantas Airways loyalty program

    @classmethod
    def get_source_values(cls):
        """
        Get a list of all source values.
        
        Returns:
            List[str]: List of source values
        """
        return ["azul", "smiles", "qantas"]


class REGION(Enum):
    """
    Enum for geographical regions used in flight searches.
    
    These regions are used to define origin and destination areas
    for flight searches and filtering.
    """
    NA = "North America"    # United States, Canada, Mexico
    SA = "South America"    # Brazil, Argentina, Chile, etc.
    AF = "Africa"                  # All African countries
    AS = "Asia"                      # Asian countries including Middle East
    EU = "Europe"                  # European countries
    OC = "Oceania"               # Australia, New Zealand, Pacific islands

    @classmethod
    def from_country(cls, country_code: str, country_region_mapping: dict) -> 'REGION':
        """
        Get REGION enum from country code using the country-region mapping.
        
        Args:
            country_code (str): Country code (e.g., "BR", "US")
            country_region_mapping (dict): Mapping from country to region code
            
        Returns:
            REGION: The corresponding REGION enum value
            
        Raises:
            ValueError: If country is not found or region is invalid
        """
        region_code = country_region_mapping.get(country_code)
        if not region_code:
            raise ValueError(f"Country '{country_code}' not found in configuration.")
        
        # The mapping returns region codes like "NA", "SA" which are enum names
        # We need to get the enum member by name, not by value
        try:
            return getattr(cls, region_code)  # Get enum member by name
        except AttributeError:
            raise ValueError(f"Region code '{region_code}' not found in REGION enum.")
    
    @classmethod
    def from_region_name(cls, region_name: str):
        """
        Get REGION enum from region name string.
        
        Args:
            region_name (str): Region name (e.g., "South America")
            
        Returns:
            REGION: The corresponding REGION enum value
            
        Raises:
            ValueError: If region name is not found
        """
        for region in cls:
            if region.value == region_name:
                return region
        
        raise ValueError(f"Region '{region_name}' not found in REGION enum.")

    @classmethod
    def parse(cls, region: str) -> 'REGION':
        """Parse a region from either enum name (e.g. 'NA') or value (e.g. 'North America').

        Accepts case-insensitive inputs and normalizes common separators.
        """
        if region is None:
            raise ValueError("Region cannot be None")

        raw = str(region).strip()
        if not raw:
            raise ValueError("Region cannot be empty")

        # 1) Exact value match
        try:
            return cls(raw)
        except Exception:
            pass

        # 2) Enum name match (NA, EU, etc.)
        key = raw.strip().upper()
        if key in cls.__members__:
            return cls.__members__[key]

        # 3) Case-insensitive value match (normalize separators)
        normalized = raw.lower().replace("_", " ").replace("-", " ")
        normalized = " ".join(normalized.split())
        for member in cls:
            if member.value.lower() == normalized:
                return member

        raise ValueError(f"Region '{region}' not found in REGION enum")

    @classmethod
    def get_region_values(cls):
        """
        Get a list of all region values.
        
        Returns:
            List[str]: List of region names
        """
        return ["North America", "South America", "Africa", "Asia", "Europe", "Oceania"]
    
    @classmethod
    def get_region_names(cls):
        """
        Get a list of all region enum names.
        
        Returns:
            List[str]: List of region enum names
        """
        return ["NA", "SA", "AF", "AS", "EU", "OC"]
class CABIN(Enum):
    """
    Enum for airline cabin classes.
    
    Uses standard IATA cabin class codes to represent different
    service levels on flights.
    """
    y = "economy"     # Economy/Coach class
    w = "premium"  # Premium Economy class
    j = "business"    # Business class
    f = "first"       # First class

class PROVIDER(str, Enum):
    SEATS_AERO = "seats.aero"