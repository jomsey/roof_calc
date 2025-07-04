import math
import logging
from enum import Enum, auto
from dataclasses import dataclass, asdict
from typing import  Dict, Any,List,Optional
#local modules
import defaults
from exceptions import InvalidDimensionsError ,InvalidSheetSizeError
from mixin import HipRoofMixin
from validators import validate_positive,validate_sheet_size,validate_unit
from miscellenous import SheetSize, Unit ,area_unit_str,convert_area
from  sub_roof import HipSubRoof,GableSubRoof

# Constants
CM_TO_M_SQUARED = 10000
CM_TO_FT_SQUARED = 929.0304
CM_TO_M = 100
CM_TO_F = 30.48

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
    
# --------------------------
# Main Roof Classes
# --------------------------

class Roof:
    """Base class for all roof types providing common functionality.
    
    Attributes:
        building_length (float): Length of the building in specified units
        building_width (float): Width of the building in specified units
        unit (Unit): Measurement unit (cm, m, ft)
    
    Methods:
        purlin_line_count: Calculate number of purlin lines needed
        trusses_count: Calculate number of trusses needed
        iron_sheets_count: Calculate iron sheets required
        ridge_cover_count: Calculate ridge covers needed
        roof_area: Calculate roof surface area (abstract)
    """
    
    def __init__(
        self,
        building_length: float,
        building_width: float,
        sub_roofs_attached: Optional[List["SubRoof"]] = None,
        unit: "Unit" = Unit.CM,
    ) -> None:
        """Initialize a roof with basic dimensions.
        Args:
            building_length: Length of the building (must be positive)
            building_width: Width of the building (must be positive)
            unit: Measurement unit (default: centimeters)
        Raises:
            InvalidDimensionsError: If length or width are not positive
        """
        validate_positive(building_length, "building_length")
        validate_positive(building_width, "building_width")
        validate_unit(unit)
        self.unit = unit
        self.building_length = self._convert_to_cm(building_length)
        self.building_width = self._convert_to_cm(building_width)
        self.sub_roofs_attached = sub_roofs_attached if sub_roofs_attached is not None else []
        
        logging.info(f"{self.__class__.__name__} initialized: {self}")

    def _convert_to_cm(self, value: float) -> float:
        """Convert a measurement to centimeters based on the current unit.
        Args:
            value: Measurement in the current unit
            
        Returns:
            float: Value converted to centimeters
        """
        if self.unit == Unit.M:
            return value * CM_TO_M
        elif self.unit == Unit.FT:
            return value * CM_TO_F
        return value
        
    def __roof_slope_height(self) -> float:
        """Calculate the slope height of the roof 
        Note: Not used for FlatRoof
        Returns:
            float: Diagonal height in centimeters
        Raises:
            NotImplementedError: When called on FlatRoof
        """
        if type(self) is FlatRoof:
            msg = "FlatRoof is not meant to use slope height."
            logging.error(msg)
            raise NotImplementedError(msg)

        slope_height = math.hypot(self.roof_height, self.roof_half_span) + self.roof_overhang
        logging.info(f"Diagonal height calculated: {slope_height:.2f} cm")
        return slope_height
     
    def _get_roof_slope_height(self) -> float:
        """Protected accessor for diagonal height calculation."""
        return self.__roof_slope_height()
    
    def purlin_lines_count(self, purlin_spacing: float) -> int:
        """Calculate number of purlin lines based on spacing.
        Args:
            purlin_spacing: Distance between purlin lines in cm (must be positive)
        Returns:
            int: Number of purlin lines needed
        Raises:
            InvalidDimensionsError: If spacing is not positive
        """
        validate_positive(purlin_spacing, "purlin_spacing")
        count = math.ceil(self._get_roof_slope_height() / purlin_spacing)
        logging.info(f"purlin lines: {count}")
        return count
        

    def main_trusses_count(self, truss_spacing: float) -> int:
        """Calculate number of trusses based on spacing.
        Args:
            truss_spacing: Distance between trusses in cm (must be positive)
        Returns:
            int: Number of trusses needed
        Raises:
            InvalidDimensionsError: If spacing is not positive
        """
        validate_positive(truss_spacing, "truss_spacing")
        count = math.floor(self.building_length / truss_spacing) + 1
        logging.info(f"Truss count: {count}")
        return count

    def iron_sheets_count(self, sheet_size: "SheetSize", waste_percent: float = defaults.WASTE_PERCENTAGE) -> int:
        """Calculate number of iron sheets needed, including waste allowance.
        Args:
            sheet_size: Dimensions of the iron sheets
            waste_percent: Additional material percentage for waste/cutting (default: 0.1 = 10%)
            
        Returns:
            int: Number of sheets needed (rounded up)
        Raises:
            InvalidSheetSizeError: If sheet dimensions are invalid
            ValueError: If waste percentage is negative
        """
        validate_sheet_size(sheet_size)
        validate_positive(waste_percent)
        sheet_area = sheet_size.area()
        
        total_area = (self.roof_area() if len(self.sub_roofs_attached) == 0 else self.collective_roof_area())* (1 + waste_percent)
        count = math.ceil(total_area / sheet_area)
        logging.info(f"Iron sheet count with {waste_percent*100:.0f}% waste: {count}")
        return count

    def ridge_cover_count(self, cover_length: float = defaults.RIDGE_LENGTH) -> int:
        """Calculate number of ridge covers needed.
        Args:""'
            cover_length: Length of each ridge cover piece in cm (default: 180)
        Returns:
            int: Number of ridge covers needed (0 for flat roofs)
        Raises:
            InvalidDimensionsError: If cover length is not positive
        """
        validate_positive(cover_length, "cover_length")
        
        if isinstance(self, FlatRoof):
            logging.info("FlatRoof does not require ridge covers.")
            return 0
        

    def roof_area(self) -> float:
        """Calculate the total surface area of the main roof.
        Note: This is an abstract method that must be implemented by subclasses.
        Returns:
            float: Total roof area in cm²
        Raises:
            NotImplementedError: If called directly on Roof base class
        """
        raise NotImplementedError("Subclasses must implement roof_area()")
        
        
    @property
    def roof_half_span(self) -> float:
        return 0.5 * self.building_width

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the roof properties to a dictionary.
        Returns:
            Dictionary containing roof type, dimensions, and unit
        """
        return {
            "type": self.__class__.__name__,
            "length": self.building_length,
            "width": self.building_width,
            "unit": self.unit.value,
        }
        
    def collective_roof_area(self) -> float:
        """Calculate the collective surface area of the entire roof
        Returns:
            float: Total roof area in
        """    
        main_area = self.roof_area()
        sub_areas = sum(sr.roof_area() for sr in self.sub_roofs_attached)
        total = main_area + sub_areas
        logging.info(f"{self.__class__.__name__} collective roof area: {total:.2f} cm²")
        return total
        
    def __str__(self) -> str:
        """Return a human-readable string representation of the roof."""
        return (
            f"{self.__class__.__name__}("
            f"length={self.building_length}{self.unit.value}, "
            f"width={self.building_width}{self.unit.value})"
        )


class HipRoof(Roof, HipRoofMixin):
    """A hip roof implementation (four sloping sides).
    Additional Attributes:
        roof_overhang (float): Overhang distance beyond walls
        height_ratio (float): Ratio of width to roof height (default 3:1)
    The hip roof has four sloping sides that meet at the top, forming a ridge.
    """
    def __init__(
        self,
        building_length: float,
        building_width: float,
        sub_roofs_attached: Optional[List["SubRoof"]] = None,
        roof_overhang: float = defaults.OVERHANG,
        height_ratio: float = defaults.HEIGHT_RATIO,
        unit: "Unit" = Unit.CM,
    ) -> None:
        """Initialize a hip roof.
        Args:
            building_length: Length of the building
            building_width: Width of the building
            roof_overhang: Overhang distance beyond walls in specified units (default: 60)
            height_ratio: Ratio of width to roof height (default: 3)
            unit: Measurement unit (default: centimeters)
        Raises:
            InvalidDimensionsError: If any dimension is not positive
        """
        super().__init__(building_length, building_width, sub_roofs_attached, unit)
        validate_positive(roof_overhang, "roof_overhang")
        validate_positive(height_ratio, "height_ratio")
        self._roof_overhang = self._convert_to_cm(roof_overhang)
        self._height_ratio = height_ratio
        logging.info(f"HipRoof: height={self.roof_height:.2f}{unit.value},overhang={roof_overhang}{unit.value}"
        )

    @property
    def roof_overhang(self) -> float:
        """Get the roof overhang distance.
        Returns:
            float: Overhang in centimeters
        """
        return self._roof_overhang
        
    @property
    def roof_height(self) -> float:
        """Calculate the vertical height of the roof.
        Returns:
            float: Roof height in centimeters
        """
        return self.building_width / self._height_ratio
        
    def ridge_cover_count(self, cover_length: float = defaults.RIDGE_LENGTH):
        raise NotImplementedError("ridge_cover_count not yet implemented for HipRoof.")

        
    def roof_area(self) -> float:
        logging.info("Calculating roof area for HipRoof...")
        hip_rafter_length = self.hip_rafter_length
        slope_height = self._get_roof_slope_height()
        # The length of the central ridge of the hip roof.
        ridge_length = self.building_length - self.building_width
        #length of the bottom facia from one corner to the other
        facial_length = self.building_width + 2*self.roof_overhang
        #length of the sides triangular face base
        face_triangle_base_length = self.building_width + self.roof_overhang
        # Area of the two trapezoidal faces
        trapezoids_area = (ridge_length + facial_length) * slope_height
        # Area of the two triangular faces
        triangular_faces_area = (face_triangle_base_length * slope_height) * 2
        total_area = trapezoids_area + triangular_faces_area
        logging.info(f"HipRoof total area: {total_area:.2f} cm²")
        return total_area 
        
    def main_trusses_count(self, truss_spacing: float) -> int:
        """Calculate number of trusses based on spacing.
        Args:
            truss_spacing: Distance between trusses in cm (must be positive)
        Returns:
            int: Number of trusses needed
        Raises:
            InvalidDimensionsError: If spacing is not positive
        """
        validate_positive(truss_spacing, "truss_spacing")
        span_length = self.building_length - self.building_width
        count = math.floor(span_length / truss_spacing) + 1
        logging.info(f"Hip Roof Truss count: {count}")
        return count

class GableRoof(Roof):
    """A gable roof implementation (two sloping sides with gable ends)."""
    def __init__(
        self,
        building_length: float,
        building_width: float,
        sub_roofs_attached: Optional[List["SubRoof"]] = None,
        side_extension_length: float = defaults.SIDE_EXTENTION,
        height_ratio: float = defaults.HEIGHT_RATIO,
        roof_overhang: float = defaults.OVERHANG,
        unit: "Unit" = Unit.CM,
    ) -> None:
        """Initialize a gable roof.
        Args:
            building_length: Length of the building
            building_width: Width of the building
            side_extension_length: Extension beyond gable ends in specified units (default: 30)
            height_ratio: Ratio of width to roof height (default: 3)
            roof_overhang: Overhang distance beyond walls in specified units (default: 60)
            unit: Measurement unit (default: centimeters)
        Raises:
            InvalidDimensionsError: If any dimension is not positive
        """
        validate_positive(side_extension_length, "side_extension_length")
        validate_positive(height_ratio, "height_ratio")
        validate_positive(roof_overhang, "roof_overhang")
        super().__init__(building_length, building_width, sub_roofs_attached, unit)
        self.side_extension_length = self._convert_to_cm(side_extension_length)
        self._height_ratio = height_ratio
        self._roof_overhang = self._convert_to_cm(roof_overhang)
        
        logging.info(
            f"GableRoof: height={self.roof_height:.2f}{unit.value}, "
            f"overhang={roof_overhang}{unit.value}"
        )

    @property
    def roof_height(self) -> float:
        """Calculate the vertical height of the roof.
        Returns:
            float: Roof height in centimeters
        """
        return self.building_width / self._height_ratio

    @property
    def roof_overhang(self) -> float:
        """Get the roof overhang distance.
        Returns:
            float: Overhang in centimeters
        """
        return self._roof_overhang
        
    def ridge_cover_count(self, cover_length: float = defaults.RIDGE_LENGTH) -> int:
        """Calculate number of ridge covers needed.
        Args:""'
            cover_length: Length of each ridge cover piece in cm (default: 180)
        Returns:
            int: Number of ridge covers needed (0 for flat roofs)
        Raises:
            InvalidDimensionsError: If cover length is not positive
        """
        validate_positive(cover_length, "cover_length")
        ridge_length = self.building_length + (2 * self.side_extension_length)
        count = math.ceil(ridge_length / cover_length)
        logging.info(f"Main Gable Ridge cover count: {count}")
        return count    
  
    def roof_area(self) -> float:
        """Calculate the total surface area of the gable roof.
        Returns:
            float: Total roof area in cm²
        """
        logging.info("Calculating roof area for GableRoof...")
        roof_length = self.building_length + (self.side_extension_length * 2)
        roof_width = self._get_roof_slope_height()
        area = 2 * (roof_length * roof_width)
        logging.info(f"GableRoof total area: {area:.2f} cm²")
        return area


class FlatRoof(Roof):
    """A flat roof implementation (single slope for drainage)."""
    def __init__(
        self,
        building_length: float,
        building_width: float,
        sub_roofs_attached: Optional[List["SubRoof"]] = None,
        flat_roof_rise: float = 10,
        roof_overhang: float = defaults.OVERHANG,
        unit: "Unit" = Unit.CM,
    ) -> None:
        """Initialize a flat roof.
        Args:
            building_length: Length of the building
            building_width: Width of the building
            flat_roof_rise: Vertical rise for drainage in specified units
            roof_overhang: Overhang distance beyond walls in specified units (default: 60)
            unit: Measurement unit (default: centimeters)
        Raises:
            InvalidDimensionsError: If any dimension is not positive
        """

        validate_positive(flat_roof_rise, "flat_roof_rise")
        validate_positive(roof_overhang, "roof_overhang")
        super().__init__(building_length, building_width, sub_roofs_attached, unit)
        self.flat_roof_rise = self._convert_to_cm(flat_roof_rise)
        self._roof_overhang = self._convert_to_cm(roof_overhang)
        
        logging.info(
            f"FlatRoof: raise={flat_roof_rise}{unit.value}, "
            f"overhang={roof_overhang}{unit.value}"
        )

    @property
    def roof_overhang(self) -> float:
        """Get the roof overhang distance.
        Returns:
            float: Overhang in centimeters
        """
        return self._roof_overhang
        
    @property
    def slope_length(self):
        return math.hypot(self.building_width  , self.flat_roof_rise) + self.roof_overhang
       
    def roof_area(self) -> float:
        """Calculate the total surface area of the flat roof.
        Returns:
            float: Total roof area in cm²
        """
        logging.info("Calculating roof area for FlatRoof...")
        area = self.slope_length * self.building_length
        logging.info(f"FlatRoof total area: {area:.2f} cm²")
        return area


# --------------------------
# Factory and Setup
# --------------------------
class RoofFactory:
    """Factory class for creating roof instances of different types."""
    @staticmethod
    def create_roof(
        roof_type: RoofType,
        building_length: float,
        building_width: float,
        unit: "Unit" = Unit.CM,
        **kwargs,
    ) -> Roof:
        """Create a roof instance of the specified type.
        Args:
            roof_type: Type of roof to create (HIP, GABLE, FLAT)
            building_length: Length of the building
            building_width: Width of the building
            unit: Measurement unit
            **kwargs: Additional parameters specific to each roof type
        Returns:
            Roof: Instance of the requested roof type
        Raises:
            ValueError: If roof_type is invalid
            
        Note:
            For HipRoof: accepts 'roof_overhang' and 'height_ratio'
            For GableRoof: accepts 'side_extension_length', 'roof_overhang', and 'height_ratio'
            For FlatRoof: accepts 'flat_roof_rise' and 'roof_overhang'
        """
        if roof_type == RoofType.HIP:
            allowed = ["roof_overhang", "height_ratio", "sub_roofs_attached"]
            filtered = {k: v for k, v in kwargs.items() if k in allowed}
            return HipRoof(building_length, building_width, unit=unit, **filtered)
        elif roof_type == RoofType.GABLE:
            allowed = ["side_extension_length", "roof_overhang", "height_ratio", "sub_roofs_attached"]
            filtered = {k: v for k, v in kwargs.items() if k in allowed}
            return GableRoof(building_length, building_width, unit=unit, **filtered)
        elif roof_type == RoofType.FLAT:
            allowed = ["flat_roof_rise", "roof_overhang", "sub_roofs_attached"]
            filtered = {k: v for k, v in kwargs.items() if k in allowed}
            return FlatRoof(building_length, building_width, unit=unit, **filtered)
        raise ValueError("Invalid roof type")
        
    