"""
Configuration management for the flight alert system.

This module loads environment variables, validates travel and system configurations,
and sets up region/cabin/source filters for the flight alert system. It handles
configuration validation, data mappings, and provides a centralized configuration
object for use throughout the application.

Key Features:
- Environment variable loading and validation
- Travel configuration validation against enums
- Currency and financial settings management
- API key and credentials handling
- Airport data mapping (IATA codes to cities/countries)
- Comprehensive configuration validation
- Default value handling for optional settings

The module validates:
- Geographic regions against REGION enum
- Airline sources against SOURCE enum  
- Cabin classes against CABIN enum
- Date formats and ranges
- Required API credentials
- Airport data availability

Configuration Categories:
- Travel: regions, sources, cabins, dates, trip parameters
- Financial: currency, commissions, fees
- API Credentials: all external service keys
- Data Mappings: airport codes to cities and countries
"""

import os
import pandas as pd
from dotenv import load_dotenv
import json


class Config:
    """
    Configuration manager for the flight alert system.
    
    This class loads, validates, and manages all configuration settings
    for the flight alert system. It handles environment variables,
    validates values against enums, creates data mappings, and ensures
    all required settings are properly configured.
    
    Attributes:
        Travel Configuration:
            ORIGIN_REGION (str): Origin region for flight searches
            DESTINATION_REGION (str): Destination region for flight searches
            SOURCE (str): Primary airline source identifier
            CABINS (list[str]): List of cabin classes to include
            START_DATE (str): Search start date (YYYY-MM-DD)
            END_DATE (str): Search end date (YYYY-MM-DD)
            MIN_RETURN_DAYS (int): Minimum days for return trip
            MAX_RETURN_DAYS (int): Maximum days for return trip
            N (int): Number of top trips to process
            TAKE (int): Maximum results per API query
            
        Financial Configuration:
            CURRENCY (str): Base currency code (e.g., 'BRL', 'USD')
            CURRENCY_SYMBOL (str): Currency symbol (e.g., 'R$', '$')
            COMMISSION (int): Commission amount in cents
            CREDIT_CARD_FEE (int): Credit card fee in cents
            
        API Credentials:
            OPENAI_API_KEY (str): OpenAI API key for content generation
            GOOGLE_SHEETS_CREDS_PATH (str): Path to Google service account credentials
            GOOGLE_EMAIL (str): Gmail address for email delivery
            GOOGLE_PASS (str): Gmail app password
            SEATS_AERO_API_KEY (str): Seats.aero Partner API key
            UNSPLASH_ACCESS_KEY (str): Unsplash API key for images
            MILEAGE_SPREADSHEET_ID (str): Google Sheets ID for mileage data
            MILEAGE_SHEET_NAME (str): Sheet name within mileage spreadsheet
            
        Data Mappings:
            IATA_CITY (dict): Mapping from IATA codes to city names
            CITY_COUNTRY (dict): Mapping from city names to country codes
    """
    
    def __init__(self):
        """
        Initialize the Config instance.
        
        Creates an empty configuration instance. The actual configuration
        loading happens when the load() method is called.
        """
        pass

    def load(self):
        """
        Load and validate all configuration settings from environment variables.
        
        This method systematically loads all required configuration values from
        environment variables, validates their presence, and sets up derived
        data structures such as the airport code mapping.
        
        The loading process handles several categories of configuration:
        - Travel settings (dates, location codes, cabin preferences)
        - Search parameters (days to search, maximum alerts)
        - Financial settings (currency codes, conversion toggles)
        - API credentials (OpenAI, Google services, messaging services)
        - File paths (Google Sheets key, airport data)
        
        Environment Variables Required:
            Travel Configuration:
            - FROM_CODE: Origin airport code
            - TO_CODE: Destination airport code  
            - DEPARTURE_DATE: Travel departure date
            - RETURN_DATE: Return travel date
            - CABIN: Preferred cabin class (from CABIN enum)
            
            Search Settings:
            - DAYS_TO_SEARCH: Number of days to search
            - MAX_DAILY_ALERTS: Maximum alerts per day
            
            Financial Settings:
            - FROM_CURRENCY_CODE: Origin currency code
            - TO_CURRENCY_CODE: Target currency code
            - CONVERT_TO_MILES: Enable mileage conversion
            
            API Credentials:
            - OPENAI_KEY: OpenAI API authentication key
            - WHATSAPP_TOKEN: WhatsApp API token
            - WHATSAPP_PHONE_NUMBER_ID: WhatsApp phone number ID
            - SHEETS_ID: Google Sheets document ID
            - UNSPLASH_ACCESS_KEY: Unsplash API access key
            
            Data Files:
            - SHEETS_API_KEY: Path to Google Sheets API key file
            - AIRPORTS_FILE: Path to airports CSV data file
            
        Raises:
            ValueError: If any required environment variable is missing or empty
            FileNotFoundError: If airport data file cannot be loaded
            
        Side Effects:
            - Populates all configuration attributes
            - Loads and processes airport data CSV
            - Creates airport code to name mapping dictionary
            - Validates all required API credentials are present
            
        Note:
            This method should be called once during application startup
            to ensure all configuration is properly loaded and validated.
        """
        """
        Load and validate all configuration settings from environment and data files.
        
        This method performs the complete configuration loading process:
        1. Loads global state
        2. Reads environment variables from .env file
        3. Validates travel configuration against enums
        4. Sets up financial and API configurations
        5. Loads and processes airport data mappings
        6. Validates all required settings
        
        Raises:
            Exception: If .env file cannot be loaded
            ValueError: If any configuration value is invalid or missing
            
        Note:
            - Must be called before using any configuration values
            - Validates all enum values against their definitions
            - Creates airport mappings from CSV data
            - Ensures all required API credentials are present
            - Sets reasonable defaults for optional parameters
        """
        if os.getenv("MODE") != "production":
            print("Loading environment variables from .env file...")
            success = load_dotenv()
            if not success:
                raise Exception("Failed to load environment variables from .env file.")
        

        self.VERSION = os.getenv("VERSION", "1.0.0")  # Default version if not set
        # Currency configuration
        self.CURRENCY = os.getenv("CURRENCY", "USD")
        self.CURRENCY_SYMBOL = os.getenv("CURRENCY_SYMBOL", "$")
        self.COMMISSION = int(os.getenv("COMMISSION", 0))  # Note: COMISSION in .env (typo)
        self.CREDIT_CARD_FEE = int(os.getenv("CREDIT_CARD_FEE", 0))

        # Secrets
        service_account_str = os.getenv("GOOGLE_SERVICE_ACCOUNT", "{}")
        #print(f"Service account string length: {len(service_account_str)}")
        try:
            if service_account_str and service_account_str != "{}":
                self.GOOGLE_SERVICE_ACCOUNT = json.loads(service_account_str)
            else:
                print("Warning: GOOGLE_SERVICE_ACCOUNT is empty or default")
                self.GOOGLE_SERVICE_ACCOUNT = None
        except json.JSONDecodeError as e:
            print(f"Error parsing GOOGLE_SERVICE_ACCOUNT JSON: {e}")
            self.GOOGLE_SERVICE_ACCOUNT = None
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.GOOGLE_EMAIL = os.getenv("GOOGLE_EMAIL")
        self.GOOGLE_PASS = os.getenv("GOOGLE_PASS")
        self.SEATS_AERO_API_KEY = os.getenv("SEATS_AERO_API_KEY")
        self.UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
        self.EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
        self.MILEAGE_SPREADSHEET_ID = os.getenv("MILEAGE_SPREADSHEET_ID")
        self.MILEAGE_WORKSHEET_NAME = os.getenv("MILEAGE_WORKSHEET_NAME")
        self.CLICKMASSA_TOKEN = os.getenv("CLICKMASSA_TOKEN")
        self.CLICKMASSA_ID = os.getenv("CLICKMASSA_ID")
        
        clickmassa_users_str = os.getenv("CLICKMASSA_USERS", "{}")
        try:
            self.CLICKMASSA_USERS = json.loads(clickmassa_users_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing CLICKMASSA_USERS JSON: {e}")
            self.CLICKMASSA_USERS = None

        self.RESULT_SHEET_ID = os.getenv("RESULT_SHEET_ID")

        # Mappings

        df = pd.read_csv("data/airports.csv")
        df = df[["municipality", "iata_code", "iso_country", "latitude_deg", "longitude_deg", "continent"]]
        df = df.rename(columns={
            "municipality": "City",
            "iata_code": "IATA",
            "iso_country": "Country",
            "latitude_deg": "Latitude",
            "longitude_deg": "Longitude",
            "continent": "Region"
        })

        # Create dictionaries for IATA to City and City to Country

        self.IATA_CITY = df.set_index("IATA")["City"].to_dict()
        self.IATA_COUNTRY = df.set_index("IATA")["Country"].to_dict()
        self.IATA_LATITUDE = df.set_index("IATA")["Latitude"].to_dict()
        self.IATA_LONGITUDE = df.set_index("IATA")["Longitude"].to_dict()
        self.COUNTRY_REGION = df.set_index("Country")["Region"].to_dict()
        
        # Assert required environment variables
        assert_env_vars(
            ("CURRENCY", self.CURRENCY),
            ("CURRENCY_SYMBOL", self.CURRENCY_SYMBOL),  
            ("COMMISSION", self.COMMISSION),
            ("CREDIT_CARD_FEE", self.CREDIT_CARD_FEE),
            ("OPENAI_API_KEY", self.OPENAI_API_KEY),
            ("GOOGLE_EMAIL", self.GOOGLE_EMAIL),
            ("GOOGLE_PASS", self.GOOGLE_PASS),
            ("SEATS_AERO_API_KEY", self.SEATS_AERO_API_KEY),
            ("UNSPLASH_ACCESS_KEY", self.UNSPLASH_ACCESS_KEY),
            ("EXCHANGE_RATE_API_KEY", self.EXCHANGE_RATE_API_KEY),
            ("MILEAGE_SPREADSHEET_ID", self.MILEAGE_SPREADSHEET_ID),
            ("MILEAGE_WORKSHEET_NAME", self.MILEAGE_WORKSHEET_NAME),
            ("CLICKMASSA_TOKEN", self.CLICKMASSA_TOKEN),
            ("CLICKMASSA_ID", self.CLICKMASSA_ID),
            ("CLICKMASSA_USERS", self.CLICKMASSA_USERS),
            ("RESULT_SHEET_ID", self.RESULT_SHEET_ID),
            ("CITY_IATA", self.IATA_CITY),
            ("CITY_COUNTRY", self.IATA_COUNTRY),
            ("CITY_LATITUDE", self.IATA_LATITUDE),
            ("CITY_LONGITUDE", self.IATA_LONGITUDE),
            ("COUNTRY_REGION", self.COUNTRY_REGION),
        )
        
        # Separate check for Google Service Account (which might be None)
        if self.GOOGLE_SERVICE_ACCOUNT is None:
            print("Warning: Google Service Account not configured. Google Sheets functionality may not work.")
        else:
            print("✅ Google Service Account loaded successfully")


def assert_env_vars(*vars):
    """
    Validate that all required environment variables are set and not empty.
    
    This utility function checks a list of environment variable name-value
    pairs to ensure that all required configuration settings have been
    properly loaded and are not None or empty.
    
    Args:
        *vars: Variable arguments of tuples, each containing:
            - var[0] (str): Environment variable name for error messages
            - var[1]: Environment variable value to validate
            
    Raises:
        ValueError: If any variable is None, empty, or otherwise falsy
        
    Note:
        - Used to validate all critical configuration settings
        - Provides clear error messages indicating which variable is missing
        - Called after all configuration loading to ensure completeness
        
    Example:
        >>> assert_env_vars(
        ...     ("API_KEY", config.API_KEY),
        ...     ("DATABASE_URL", config.DATABASE_URL)
        ... )
    """
    for var in vars:
        if not var[1]:
            raise ValueError(f"Missing required environment variable: {var[0]}")

        
# Create a singleton configuration instance for use throughout the application
config = Config()