from data_types.enums import REGION, CABIN

from global_state import state

def convert_region_to_enum(region: str) -> REGION:
    """
    Convert a region string to a REGION enum.
    
    Args:
        region (str): The region string to convert.
    
    Returns:
        REGION: The corresponding REGION enum.
    
    Raises:
        ValueError: If the region string is invalid.
    """
    try:
        return REGION(region)
    except ValueError as e:
        raise ValueError(f"Invalid region provided: {e}")
    
def convert_cabins_list_to_enum(cabins: list[str]) -> list[CABIN]:
    """
    Convert a list of cabin strings to a list of CABIN enums.
    
    Args:
        cabins (list[str]): List of cabin class strings to convert.
    
    Returns:
        list[CABIN]: List of corresponding CABIN enums.
    
    Raises:
        ValueError: If any cabin string is invalid.
    """
    try:
        return [CABIN(cabin) for cabin in cabins] if cabins else []
    except ValueError as e:
        raise ValueError(f"Invalid cabin class provided: {e}")
    

def convert_cabins_str_to_enum(cabins: str) -> list[CABIN]:
    """
    Attempt to convert a list of cabin strings to CABIN enums.
    
    Args:
        cabins (list[str]): List of cabin class strings to convert.
    
    Returns:
        list[CABIN]: List of corresponding CABIN enums, or empty list if input is None.
    """
    cabinAsCABIN: list[CABIN] = []
    if cabins:
        state.logger.info(f"Converting cabins '{cabins}' to CABIN enum")
        cabinsList = cabins.split(",") if isinstance(cabins, str) else cabins
        cabinAsCABIN = convert_cabins_list_to_enum(cabinsList)
        
    return cabinAsCABIN