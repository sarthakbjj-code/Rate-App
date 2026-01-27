"""Utility functions for the application."""
import re
from typing import Optional, Tuple


def validate_hsn_code(hsn_code: str) -> bool:
    """
    Validate HSN code format (4-8 digits).
    
    Args:
        hsn_code: HSN code to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not hsn_code:
        return False
    
    # Remove any spaces or dashes
    hsn_code = hsn_code.replace(' ', '').replace('-', '')
    
    # Check if it's 4-8 digits
    if re.match(r'^\d{4,8}$', hsn_code):
        return True
    
    return False


def normalize_price(price: float, quantity: float, unit: str, target_unit: str = None) -> Optional[float]:
    """
    Normalize price to standard unit.
    
    Examples:
        - 500g @ ₹150 → ₹300/kg
        - 2 litre @ ₹200 → ₹100/litre
        - Pack of 6 @ ₹120 → ₹20/piece
        
    Args:
        price: Current price
        quantity: Current quantity
        unit: Current unit (e.g., 'g', 'kg', 'ml', 'litre')
        target_unit: Target unit for normalization (optional)
        
    Returns:
        Normalized price or None if conversion not possible
    """
    if not price or not quantity or quantity == 0:
        return None
    
    unit = unit.lower().strip()
    
    # Weight conversions to kg
    weight_to_kg = {
        'g': 0.001,
        'gram': 0.001,
        'grams': 0.001,
        'kg': 1.0,
        'kilogram': 1.0,
        'kilograms': 1.0,
    }
    
    # Volume conversions to litre
    volume_to_litre = {
        'ml': 0.001,
        'millilitre': 0.001,
        'millilitres': 0.001,
        'l': 1.0,
        'litre': 1.0,
        'litres': 1.0,
        'liter': 1.0,
        'liters': 1.0,
    }
    
    # Try weight conversion
    if unit in weight_to_kg:
        normalized_quantity = quantity * weight_to_kg[unit]  # Convert to kg
        return price / normalized_quantity
    
    # Try volume conversion
    if unit in volume_to_litre:
        normalized_quantity = quantity * volume_to_litre[unit]  # Convert to litre
        return price / normalized_quantity
    
    # For pieces, box, carton, etc., price per unit
    if unit in ['piece', 'pieces', 'pc', 'pcs', 'unit', 'units', 'box', 'carton', 'pack']:
        return price / quantity
    
    # If no conversion possible, return price per given unit
    return price / quantity


def extract_quantity_from_text(text: str) -> Tuple[Optional[float], Optional[str]]:
    """
    Extract quantity and unit from product text.
    
    Examples:
        "Ashirvaad Atta 5kg" → (5.0, 'kg')
        "Fortune Oil 1 Litre" → (1.0, 'litre')
        "Maggi 12 Pack" → (12.0, 'pack')
        
    Args:
        text: Product text
        
    Returns:
        Tuple of (quantity, unit) or (None, None)
    """
    if not text:
        return None, None
    
    text = text.lower()
    
    # Pattern: number followed by unit
    patterns = [
        r'(\d+(?:\.\d+)?)\s*(kg|kilogram|kilograms)',
        r'(\d+(?:\.\d+)?)\s*(g|gram|grams)',
        r'(\d+(?:\.\d+)?)\s*(l|litre|litres|liter|liters)',
        r'(\d+(?:\.\d+)?)\s*(ml|millilitre|millilitres|milliliter|milliliters)',
        r'(\d+(?:\.\d+)?)\s*(piece|pieces|pc|pcs)',
        r'(\d+(?:\.\d+)?)\s*(pack|box|carton)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            quantity = float(match.group(1))
            unit = match.group(2)
            return quantity, unit
    
    return None, None


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent SQL injection and XSS.
    
    Args:
        text: Input text
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove any potentially harmful characters
    text = re.sub(r'[<>\"\'%;()&+]', '', text)
    
    # Limit length
    text = text[:200]
    
    return text.strip()


def format_currency(amount: float) -> str:
    """
    Format amount as Indian currency.
    
    Args:
        amount: Amount to format
        
    Returns:
        Formatted string (e.g., "₹295.50")
    """
    if amount is None:
        return "N/A"
    
    return f"₹{amount:,.2f}"


def calculate_savings_percentage(current_price: float, target_price: float) -> float:
    """
    Calculate savings percentage.
    
    Args:
        current_price: Current price
        target_price: Target price
        
    Returns:
        Savings percentage
    """
    if not current_price or current_price == 0:
        return 0.0
    
    return ((current_price - target_price) / current_price) * 100
