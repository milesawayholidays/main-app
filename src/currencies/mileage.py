'''
Mileage class for managing mileage values.
This class fetches mileage values from a Google Sheet specified in the configuration.
It provides methods to access mileage values by program name.
It includes error handling for fetching values and accessing specific mileage programs.
It is part of a larger system that manages flight alerts and related services.
'''
from ..global_state import state

from ..data_types.enums import SOURCE

from ..services.google_sheets import handler as sheets_handler

class Mileage:
    def __init__(self):
        self.mileage_values: dict[SOURCE, int] = dict()

    def load(self, mileage_spreadsheet_id: str, mileage_worksheet_name: str):
        """
        Initialize the Mileage handler to fetch and manage mileage values.
        This class retrieves mileage values from a Google Sheet specified in the
        configuration. It provides methods to access mileage values by program name.
        The mileage values are stored in a dictionary for quick access. 
        Attributes:
            mileage_values (dict): Dictionary mapping mileage program names to their values
        """

        if(mileage_spreadsheet_id == "test"):
            self.mileage_values = {
                "azul": 1400,
                "smiles": 1500,
                "qantas": 3000
            }
            return

        rows = (sheets_handler
                .get_sheet(mileage_spreadsheet_id)
                .get_worksheet(mileage_worksheet_name)
                .get_all_values())
        
        if not rows:
                raise Exception("No mileage values found in the sheet.")
        
        for row in rows:
            program = row[0]
            mileage = int(row[1])
            self.mileage_values[program] = mileage
            
        state.logger.info(f"Mileage handler initialized and mileage values fetched with length: {len(self.mileage_values)}")


    def get_mileage_value(self, program: str) -> int:
        """
        Retrieve the mileage value for a specific program.
        Args:
            program (str): Name of the mileage program
        Returns:
            int: Mileage value for the specified program
        Raises:
            ValueError: If the program is not found in the mileage values
        """
        if program in self.mileage_values:
            return self.mileage_values[program]
        else:
            state.logger.warning(f"Mileage value for program '{program}' not found.")
            raise ValueError(f"Mileage value for program '{program}' not found.")
        
    
handler = Mileage()
