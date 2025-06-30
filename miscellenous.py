from enum import Enum , auto
from dataclasses import dataclass

class Unit(Enum):
    """Measurement units for all calculations.
    
    Values:
        CM: Centimeters
        M: Meters
        FT: Feet
    """
    CM = "cm"
    M = "m"
    FT = "ft"


# --------------------------
# Data Classes
# --------------------------
@dataclass
class SheetSize:
    """Represents the size of a single iron sheet.
    
    Attributes:
        length (float): Length of the sheet in cm
        width (float): Width of the sheet in cm
    
    Methods:
        area: Calculates the area of the sheet in cm²
    """
    length: float
    width: float

    def area(self) -> float:
        """Calculate the area of the sheet.
        
        Returns:
            float: Area in cm² (length × width)
        """
        return self.length * self.width

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
    if unit == Unit.M:
        return area_cm2 / CM_TO_M_SQUARED
    elif unit == Unit.FT:
        return area_cm2 / CM_TO_FT_SQUARED
    return area_cm2

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