import usaddress
from typing import Optional, Tuple

def extract_city_and_state(address: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract city and state from an address string using the usaddress library.
    
    Args:
        address (str): Full address string (e.g., "7375 Rollingdell Dr, Cupertino, CA")
        
    Returns:
        Tuple[Optional[str], Optional[str]]: Tuple of (city, state) or (None, None) if parsing fails
    """
    try:
        # Parse address into components
        tagged_address, address_type = usaddress.tag(address)
        
        # Extract city (try multiple possible fields)
        city = None
        for field in ['PlaceName', 'City', 'Municipality', 'Town']:
            if tagged_address.get(field):
                city = tagged_address[field]
                break
        
        # Extract state (try multiple possible fields)
        state = None
        for field in ['StateName', 'State']:
            if tagged_address.get(field):
                state = tagged_address[field]
                break
        
        return city, state
        
    except (usaddress.RepeatedLabelError, usaddress.NotATaggerError) as e:
        print(f"Error parsing address: {str(e)}")
        return None, None 