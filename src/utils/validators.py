"""Input validators."""
import re
from typing import Optional


def validate_product_name(name: str) -> tuple[bool, Optional[str]]:
    """
    Validate product name.
    
    Args:
        name: Product name
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Product name is required"
    
    if len(name) < 3:
        return False, "Product name must be at least 3 characters"
    
    if len(name) > 200:
        return False, "Product name must be less than 200 characters"
    
    return True, None


def validate_hsn_code(hsn_code: str) -> tuple[bool, Optional[str]]:
    """
    Validate HSN code.
    
    Args:
        hsn_code: HSN code
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not hsn_code or not hsn_code.strip():
        return False, "HSN code is required"
    
    # Remove spaces and dashes
    clean_hsn = hsn_code.replace(' ', '').replace('-', '')
    
    if not re.match(r'^\d{4,8}$', clean_hsn):
        return False, "HSN code must be 4-8 digits"
    
    return True, None


def validate_quantity(quantity: float) -> tuple[bool, Optional[str]]:
    """
    Validate quantity.
    
    Args:
        quantity: Quantity
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if quantity is None:
        return False, "Quantity is required"
    
    if quantity <= 0:
        return False, "Quantity must be greater than 0"
    
    if quantity > 1000000:
        return False, "Quantity must be less than 1,000,000"
    
    return True, None


def validate_uom(uom: str) -> tuple[bool, Optional[str]]:
    """
    Validate unit of measurement.
    
    Args:
        uom: Unit of measurement
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_uoms = ['kg', 'g', 'litre', 'ml', 'pieces', 'box', 'carton', 'pack']
    
    if not uom or not uom.strip():
        return False, "Unit of measurement is required"
    
    if uom.lower() not in valid_uoms:
        return False, f"Invalid unit. Must be one of: {', '.join(valid_uoms)}"
    
    return True, None
