"""
Google Sheets integration service for storing flight alert data.

This module handles interaction with Google Sheets API for storing and managing
flight alert data. It provides functionality to create spreadsheets, write
round trip data, and manage worksheet operations for flight alert reporting
and data persistence.

Key Features:
- Google Sheets API authentication and authorization
- Automatic spreadsheet and worksheet creation
- Flight data formatting and export
- Header management and data organization
- Error handling and logging for all operations

The module integrates with:
- Google Sheets API v4 via gspread library
- Service account authentication
- Global state for logging and status tracking
- Trip builder objects for data formatting

Data Structure:
- Creates separate spreadsheets for each city pairing and date
- Organizes data with standardized headers
- Includes selling price summaries
- Supports multiple round trip options per sheet
"""

import gspread
from google.oauth2.service_account import Credentials

try:
    from ..global_state import state
except ImportError:
    from global_state import state

# Standard headers for flight data export
HEADERS = [
    "Outbound ID", "Return ID", "Origin Airport", "Destination Airport", 
    "Outbound Departure", "Outbound Arrival", "Return Departure", "Return Arrival",
    "Outbound Mileage Cost", "Outbound Taxes", "Outbound Normal Taxes",
    "Outbound Total Cost", "Outbound Normal Total Cost",
    "Return Mileage Cost", "Return Taxes", "Return Normal Taxes",
    "Return Total Cost", "Return Normal Total Cost",
    "Normal Selling Price", "Outbound Booking Links", "Return Booking Links"
]

class WorkSheet:
    """
    Wrapper class for gspread Worksheet operations.
    This class provides methods to manage a specific worksheet within a Google Spreadsheet,
    including adding rows, updating headers, and handling data operations.
    Attributes:
        worksheet (gspread.Worksheet): The gspread Worksheet instance
    """

    def __init__(self, worksheet: gspread.Worksheet, headers: list[str] = None):
        """
        Initialize a WorkSheet object with the given gspread Worksheet.
        
        Args:
            worksheet (gspread.Worksheet): The gspread Worksheet instance
            
        Note:
            - Used to manage operations on a specific worksheet
            - Requires Google Sheets client to be initialized first
        """
        self.worksheet = worksheet
        if headers:
            self.update_headers(headers)
        

    def update_headers(self, headers: list[str]) -> "WorkSheet":
        """
        Update the headers of the worksheet.
        
        Args:
            headers (list[str]): List of header names to set in the first row

        Returns:
            WorkSheet: The updated WorkSheet instance

        Note:
            - Automatically updates the first row with new headers
            - Useful for initializing or resetting worksheet structure
        """        
        self.worksheet.batch_update([{
                'range': '1:1',
                'values': [headers]
            }])
        return self

    def get_all_values(self) -> list[list[str]]:
        """
        Retrieve all values from the worksheet.
        
        Returns:
            list[list[str]]: A list of lists containing all cell values in the worksheet
            
        Note:
            - Useful for reading existing data in the worksheet
            - Returns empty list if no data is present
        """
        #should ignore the first row
        return self.worksheet.get_all_values(value_render_option='UNFORMATTED_VALUE')[1:]

    def add_row(self, row: list[str]) -> None:
        """
        Add a new row of data to the worksheet.
        
        Args:
            row (list[str]): List of values to add as a new row
            
        Note:
            - Automatically appends the row to the next available position
            - Assumes headers are already set in the first row
        """
        self.worksheet.append_row(row, value_input_option='USER_ENTERED')

    def add_rows(self, rows: list[list[str]]) -> "WorkSheet":
        """
        Add multiple rows of data to the worksheet.
        
        Args:
            rows (list[list[str]]): List of rows to add
            
        Note:
            - Efficiently appends all rows in a single operation
            - Assumes headers are already set in the first row
        """
        self.worksheet.append_rows(rows, value_input_option='USER_ENTERED')
        return self

class SpreadSheet:
    """
    Wrapper class for gspread Spreadsheet operations.
    This class provides methods to manage a Google Spreadsheet, including
    creating worksheets, retrieving existing ones, and handling data operations.
    Attributes:
        spreadsheet_id (str): Unique ID of the Google Spreadsheet
        spreadsheet_name (str): Name of the Google Spreadsheet
        client (gspread.Client): Authorized gspread client instance
    """
    def __init__(self, spreadsheet: gspread.Spreadsheet, spreadsheet_name: str):
        """
        Initialize a SpreadSheet object with the given spreadsheet ID.
        
        Args:
            spreadsheet (gspread.Spreadsheet): The gspread Spreadsheet instance
            spreadsheet_name (str): Name of the Google Spreadsheet
            
        Note:
            - Used to manage operations on a specific spreadsheet
            - Requires Google Sheets client to be initialized first
        """
        self.spreadsheet = spreadsheet
        self.spreadsheet_name = spreadsheet_name

    def get_worksheet(self, worksheet_name: str) -> WorkSheet:
        """
        Retrieve a worksheet by name from the spreadsheet.
        
        Args:
            worksheet_name (str): Name of the worksheet to retrieve
            
        Returns:
            gspread.Worksheet: The requested worksheet object
            
        Raises:
            gspread.WorksheetNotFound: If the specified worksheet does not exist
        """
        return WorkSheet(self.spreadsheet.worksheet(worksheet_name))

    def create_worksheet(self, worksheet_name: str, rows_n: int, cols_n: int, headers: list[str]) -> WorkSheet:
        """
        Create a new worksheet in the spreadsheet with the specified name.
        
        Args:
            worksheet_name (str): Name for the new worksheet
            
        Returns:
            gspread.Worksheet: The newly created worksheet object
            
        Raises:
            Exception: Re-raises any Google Sheets API errors that occur
                during worksheet creation
                
        Note:
            - Automatically adds the new worksheet to the spreadsheet
            - Logs creation success for tracking
        """
        return WorkSheet(worksheet=self.spreadsheet.add_worksheet(title=worksheet_name, rows=rows_n, cols=cols_n), headers=headers)

class GoogleSheetsHandler:
    """
    Handler class for Google Sheets operations related to flight alert data.
    
    This class manages all interactions with Google Sheets API, including
    authentication, spreadsheet creation, data writing, and worksheet management.
    It's designed specifically for storing flight alert data with standardized
    formatting and error handling.
    
    Attributes:
        client (gspread.Client): Authorized Google Sheets client instance
        
    Note:
        - Requires valid Google service account credentials
        - Sets global state flag when successfully initialized
        - All operations include comprehensive logging
    """
    
    def __init__(self):
        pass
  
    def load(self, google_service_account) -> None: 
        """
        Initialize the Google Sheets handler with service account authentication.
        
        Sets up Google Sheets API client using service account credentials
        from the configured path. Validates credentials and authorization
        before marking the handler as ready for use.


        Args:
            google_service_account (dict): Google service account credentials
                as a dictionary containing the necessary authentication details
        
        Raises:
            ValueError: If credentials path is not configured, credentials
                cannot be loaded, or client authorization fails
                
        Note:
            - Uses spreadsheets scope for read/write access
            - Sets global state flag on successful initialization
            - Logs all initialization steps for debugging
        """
            
        try:
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            state.logger.info("Loading credentials from service account...")
            credentials = Credentials.from_service_account_info(google_service_account, scopes=scopes)

            if not credentials:
                state.logger.error("Failed to load credentials from the provided info.")
                raise ValueError("Failed to load credentials from the provided info.")

            state.logger.info("Authorizing Google Sheets client...")
            self.client = gspread.authorize(credentials)
            
            if not self.client:
                state.logger.error("Failed to authorize Google Sheets client with the provided credentials.")
                raise ValueError("Failed to authorize Google Sheets client with the provided credentials.")

            user_email = credentials.service_account_email
            state.logger.info(f"Google Sheets handler loaded successfully with user_email: {user_email}!")

        except Exception as e:
            state.logger.error(f"Error during Google Sheets initialization: {str(e)}")
            raise 

    def get_sheet(self, spreadsheet_id: str) -> SpreadSheet:
        """
        Retrieve a Google Spreadsheet by its unique ID.
        
        Args:
            spreadsheet_id (str): Unique ID of the Google Spreadsheet
            
        Returns:
            SpreadSheet: The requested spreadsheet object
            
        Raises:
            gspread.SpreadsheetNotFound: If the specified spreadsheet does not exist
        """
        spreadsheet = self.client.open_by_key(spreadsheet_id)
        return SpreadSheet(spreadsheet, spreadsheet.title)
    

    


# Create a singleton instance for use throughout the application    
handler = GoogleSheetsHandler()


# Legacy code kept for reference - original implementation methods
# TODO: Remove after confirming new implementation works correctly    
''' def write_top15_to_sheet(self, sheet_name: str, spreadsheet_id: str, roundTrips: list[RoundTrip]) -> None :
    if not roundTrips:
        state.logger.error("No data to write to the sheet.")
        raise ValueError("No data to write to the sheet.")
    try: 
      sheet = self.client.open_by_key(spreadsheet_id)
      try:
        worksheet = sheet.worksheet(sheet_name)
      except gspread.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=sheet_name, rows=ROWS_N, cols=COLS_N)
      worksheet.clear()

      worksheet.update("1:1", HEADERS)

      rows = []
      for trip in roundTrips:
        row = trip.make_row()
        rows.append(row)

      worksheet.update(f"A2:R{len(rows)+1}", rows)

      state.logger.info(f"Top 15 data written to sheet '{sheet_name}' in spreadsheet '{spreadsheet_id}'")
      state.logger.info("Data written successfully to the Google Sheet.")
    except Exception as e:
      state.logger.error(f"Failed to write data to Google Sheet: {e}")
      raise e
      
    return 
  
  def readSheet(self, spreadsheet_id: str, sheet_name: str) -> list[list[str]]:
    try:
      sheet = self.client.open_by_key(spreadsheet_id)
      worksheet = sheet.worksheet(sheet_name)
      data = worksheet.get_all_values()
      state.logger.info(f"Data read from sheet '{sheet_name}' in spreadsheet '{spreadsheet_id}'")
      return data
    except Exception as e:
      state.logger.error(f"Failed to read data from Google Sheet: {e}")
      raise e
    
  def getRowByColumnValue(self, spreadsheet_id: str, sheet_name: str, column: int, value: str) -> list[str]:
    try:
      sheet = self.client.open_by_key(spreadsheet_id)
      worksheet = sheet.worksheet(sheet_name)
      cell = worksheet.find(value, in_column=column)
      if cell:
        row_data = worksheet.row_values(cell.row)
        state.logger.info(f"Row found for value '{value}' in column {column} of sheet '{sheet_name}'")
        return row_data
      else:
        state.logger.warning(f"No row found for value '{value}' in column {column} of sheet '{sheet_name}'")
        return []
    except Exception as e:
      state.logger.error(f"Failed to find row by column value in Google Sheet: {e}")
      raise e
  
handler = GoogleSheetsHandler()
'''