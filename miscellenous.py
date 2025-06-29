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

