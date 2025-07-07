from miscellenous import Unit

# --------------------------
# Output Conversion Helpers
# --------------------------
def convert_area(area_cm2: float, unit: "Unit") -> float:
    """Convert area from cm² to the specified unit.
    
    Args:
        area_cm2: Area in square centimeters
        unit: Target unit for conversion
        
    Returns:
        float: Area in the requested unit
    """
    #Conversion Constants
    CM_TO_M_SQUARED = 10000
    CM_TO_FT_SQUARED = 929.0304
    
    if unit == Unit.M:
        return area_cm2 / CM_TO_M_SQUARED
    elif unit == Unit.FT:
        return area_cm2 / CM_TO_FT_SQUARED
    return area_cm2
    
def convert_from_cm(value: float, unit: "Unit") -> float:
    """Convert area from cm² to the specified unit.
    
    Args:
        area_cm2: Area in square centimeters
        unit: Target unit for conversion
        
    Returns:
        float: Area in the requested unit
    """
    #Conversion Constants
    CM_TO_M = 100
    CM_TO_F = 30.48
    
    if unit == Unit.M:
            return value / CM_TO_M
    elif unit == Unit.FT:
            return value / CM_TO_F
    return value    
    
def area_unit_str(unit: "Unit") -> str:
    """Get the string representation of an area unit.
    
    Args:
        unit: The unit to convert
        
    Returns:
        str: Unit string with squared symbol (cm², m², ft²)
    """
    if unit == Unit.M:
        return "m²"
    elif unit == Unit.FT:
        return "ft²"
    return "cm²"
    
def unit_str(unit: "Unit") -> str:
    """Get the string representation of a unit.
    Args:
        unit: The unit to convert
    """
    if unit == Unit.M:
        return "m"
    elif unit == Unit.FT:
        return "ft"
    return "cm"
    
def convert_to_cm(value: float,unit) -> float:
        """Convert a measurement to centimeters based on the current unit.
        Args:
            value: Measurement in the current unit
        Returns:
            float: Value converted to centimeters
        """
        
        #Conversion Constants
        CM_TO_M = 100
        CM_TO_F = 30.48
        
        if unit == Unit.M:
            return value * CM_TO_M
        elif unit == Unit.FT:
            return value * CM_TO_F
        return value    