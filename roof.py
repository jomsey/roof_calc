import math
import logging
from enum import Enum, auto
from dataclasses import dataclass, asdict
from typing import  Dict, Any,List,Optional
from abc import ABC, abstractmethod

#local modules
import defaults
from exceptions import InvalidDimensionsError ,InvalidSheetSizeError
from mixin import HipRoofMixin
from validators import validate_positive,validate_sheet_size,validate_unit,validate_pitch_degrees
from miscellenous import SheetSize,PitchRatio ,Unit,RoofType
from utils import convert_to_cm,unit_str,area_unit_str,convert_area,convert_from_cm
from  sub_roof import HipSubRoof,GableSubRoof


class Roof(ABC):
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
        roof_pitch_deg: Optional[float] = None,
        pitch_ratio: Optional[PitchRatio] = None,
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
        self.building_length = convert_to_cm(building_length,unit)
        self.building_width = convert_to_cm(building_width,unit)
        self.sub_roofs_attached = sub_roofs_attached if sub_roofs_attached is not None else []
        self.roof_pitch_deg = roof_pitch_deg 
        self.pitch_ratio = pitch_ratio
        self._length = self.building_length
        self._width = self.building_width
        if roof_pitch_deg:
            validate_pitch_degrees(roof_pitch_deg)
        if sub_roofs_attached:
            for sr in sub_roofs_attached:
                sr.parent = self
                sr.unit = self.unit
        logging.info(f"{self.__class__.__name__} initialized: {self}")

    
    def __roof_slope_height(self) -> float:
        """Calculate the slope height of the roof 
        Note: Not used for FlatRoof
        Returns:
            float: Diagonal height in centimeters
        Raises:
            NotImplementedError: When called on FlatRoof
        """
        if isinstance(self, FlatRoof):
            msg = "FlatRoof is not meant to use slope height."
            logging.error(msg)
            raise NotImplementedError(msg)

        slope_height = math.hypot(self.roof_height, self.roof_half_span) + self.roof_overhang
        logging.info(f"Diagonal height calculated: {slope_height:.2f} cm")
        return slope_height
     
    def _get_roof_slope_height(self) -> float:
        """Protected accessor for diagonal height calculation."""
        return self.__roof_slope_height()
    
    @property
    def slope_height(self) -> float:
        """Protected accessor for diagonal height calculation."""
        return self.__roof_slope_height()
        
    def sheet_covers_count(self,sheet_cover:"SheetCover",waste_percent: float = defaults.WASTE_PERCENTAGE)->int:
        sheet_area =sheet_cover.sheet_area()
        roof_area = (self.roof_area() if len(self.sub_roofs_attached) == 0 else self.collective_roof_area())* (1 + waste_percent)
        sheets_count = math.ceil(roof_area / sheet_area)
        logging.info(f"Iron sheet count with {waste_percent*100:.0f}% waste: {sheets_count}")
        return sheets_count
     
    @abstractmethod    
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

    @property    
    def roof_pitch_angle_degrees(self) -> float:
        if self.pitch_ratio:
            return self.pitch_ratio.degree
        if self.roof_pitch_deg:
            return self.roof_pitch_deg
 
        return math.degrees(math.atan(self.roof_height/ self.roof_half_span))
        
    @property    
    def roof_pitch_ratio(self) -> float:
        if self.pitch_ratio:
            return self.pitch_ratio 
        return  math.tan(math.radians(self.roof_pitch_angle_degrees))    
        
    def collective_roof_area(self) -> float:
        """Calculate the collective surface area of the entire roof
        Returns:
            float: Total roof area in
        """    
        main_area = self.roof_area()
        sub_areas = sum(sr.roof_area() for sr in self.sub_roofs_attached)
        total = main_area + sub_areas
        logging.info(f"{self.__class__.__name__} collective roof area: {total:.2f} {area_unit_str(self.unit)}")
        return total
        
    @property
    def _ridge_length(self):
        if isinstance(self,GableRoof):
            return self.building_length + 2*self.side_extension_length
            
        if isinstance(self,HipRoof):
            return self.building_length - self.building_width
        if isinstance(self,FlatRoof):
            return 0 
            
    def _to_dict(self) -> dict:
        return {
            "name": self.__class__.__name__,
            "length": self.building_length,
            "width": self.building_width,
            "roof_pitch_deg": self.roof_pitch_angle_degrees,
            "unit": unit_str(self.unit),
            "sub_roofs_attached":[sr.to_dict() for sr in self.sub_roofs_attached] if self.sub_roofs_attached else None,
            "roof_overhang":self.roof_overhang,
            "roof_area": self.collective_roof_area() if self.sub_roofs_attached else self.roof_area(),
            "pitch_ratio":self.roof_pitch_ratio,
            "roof_height":self.roof_height,
        }
        
    def __str__(self) -> str:
        """Return a human-readable string representation of the roof."""
        return (
            f"{self.__class__.__name__}("
            f"length={self.building_length}{unit_str(self.unit)}, "
            f"width={self.building_width}{unit_str(self.unit)})"
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
        roof_pitch_deg: Optional[float] = None,
        pitch_ratio: Optional[PitchRatio] = None,
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
        super().__init__(building_length, building_width, sub_roofs_attached,roof_pitch_deg,pitch_ratio, unit)
        validate_positive(roof_overhang, "roof_overhang")
        validate_positive(height_ratio, "height_ratio")
        self._roof_overhang = convert_to_cm(roof_overhang,unit)
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
        
    
    def to_dict(self):
        return {
            **self._to_dict(),
            "hip_rafter_length":self.hip_rafter_length,
            "corner_tiebeam_length":self.corner_tiebeam_length,
            "triangular_facial_area":self.triangular_facial_area
        }
    
class GableRoof(Roof):
    """A gable roof implementation (two sloping sides with gable ends)."""
    def __init__(
        self,
        building_length: float,
        building_width: float,
        sub_roofs_attached: Optional[List["SubRoof"]] = None,
        roof_pitch_deg: Optional[float] = None,
        pitch_ratio: Optional[PitchRatio] = None,
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
        super().__init__(building_length, building_width, sub_roofs_attached, roof_pitch_deg=roof_pitch_deg,pitch_ratio=pitch_ratio,unit=unit)
        self.side_extension_length = convert_to_cm(side_extension_length,unit)
        self._height_ratio = height_ratio
        self._roof_overhang = convert_to_cm(roof_overhang,unit)
        
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
        
    def to_dict(self):
        return{
            **self._to_dict(),
            "height_ratio":self.height_ratio,
            "side_extension_length":self.side_extension_length,
        }
      

class FlatRoof(Roof):
    """A flat roof implementation (single slope for drainage)."""
    def __init__(
        self,
        building_length: float,
        building_width: float,
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
        super().__init__(building_length, building_width,sub_roofs_attached=None,unit= unit)
        self.flat_roof_rise = convert_to_cm(flat_roof_rise,unit)
        self._roof_overhang = convert_to_cm(roof_overhang,unit)
        logging.info(
            f"FlatRoof: raise={flat_roof_rise}{unit_str(unit)}, "
            f"overhang={roof_overhang}{unit_str(unit)}"
        )
        
    @property
    def roof_height(self):
        return self.flat_roof_rise

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
        logging.info(f"FlatRoof total area: {area:.2f} {area_unit_str(self.unit)}")
        return area
  
    def to_dict(self):
        return{
            **self._to_dict(),
            "roof_height":self.flat_roof_rise,
        }
    
        

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
