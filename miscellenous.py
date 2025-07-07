import math
from enum import Enum , auto
from dataclasses import dataclass


# --------------------------
# Enums 
# --------------------------
class RoofType(Enum):
    """Types of roof supported.
    Values:
        HIP: Hip roof (four sloping sides)
        GABLE: Gable roof (two sloping sides with gable ends)
        FLAT: Flat roof (single slope for drainage)
    """
    HIP = auto()
    GABLE = auto()
    FLAT = auto()
 
    
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
    

        
@dataclass
class SheetOverup:
    left_right_overup: float
    top_bottom_overup: float


@dataclass(frozen=True)
class PitchRatio:
    rise: float
    run: float = 12.0  # Default run is 12, common in roof construction

    @property
    def degrees(self) -> float:
        """Convert pitch ratio to pitch in degrees."""
        return math.degrees(math.atan(self.rise / self.run))

    def __str__(self):
        return f"{self.rise}:{self.run}"

    def to_tuple(self):
        return (self.rise, self.run)
