import math
import logging
from dataclasses import dataclass, field
from typing import List, Optional
from validators import validate_positive,validate_pitch_degrees
from miscellenous import Unit
from utils import convert_to_cm,unit_str,area_unit_str,convert_area
from mixin import HipRoofMixin




@dataclass
class SubRoof:
    name: str
    section_length: float  # along main roof
    width: float           # depth of sub-roof out from main
    unit: Unit = Unit.CM
    on_extreme_end: bool = False  # position along the main - either has one or two vallies depending where it is situated
    sub_roofs_attached: List["SubRoof"] = field(default_factory=list)
    parent: Optional["SubRoof"] = field(default=None, repr=False)

    def __post_init__(self):
        self._length = self.width
        validate_positive(self.section_length, "section_length")
        validate_positive(self.width, "width")
        self.section_length = convert_to_cm(self.section_length,self.unit)
        self.width = convert_to_cm(self.width,self.unit)
        self.roof_pitch_ratio = self.pitch_rise_run
        for sr in self.sub_roofs_attached:
            sr.parent = self
            
        if self.parent.__class__.__name__ == "FlatRoof":
            msg = "Sub roofs on flat roof are not supported"
            logging.error(msg)
            raise NotImplementedError(msg)    

    @property
    def roof_half_span(self):
        return 0.5 * self.section_length
        
    @property
    def slope_height(self) -> float:
        """Return the slant height of the roof section using pitch."""
        rise = self.pitch_rise_run * self.roof_half_span
        hypotenuse = math.hypot(rise, self.width / 2)
        return hypotenuse
        
    
    @property
    def pitch_rise_run(self) -> float:
        """Get rise/run ratio based on effective pitch."""
        roof_pitch = self.parent.roof_pitch_angle_degrees
        return math.tan(math.radians(roof_pitch))

    @property
    def roof_height(self) -> float:
        """Calculate vertical roof height using inherited or direct pitch."""
        height = self.pitch_rise_run * self.roof_half_span
        logging.info(f"{self.name} roof height: {height:.2f} cm")
        return height
    
    @property     
    def roof_overhang(self):
        return self.parent.roof_overhang
        
    @property
    def valley_length(self):
        pass
    
    @property
    def collective_ridge_length(self):
        pass
   
    def roof_area(self) -> float:
        """Calculate the total sloped area of this sub-roof and its children."""
        main_area = 2 * self.slope_height * self.section_length
        sub_areas = sum(sr.roof_area() for sr in self.sub_roofs_attached)
        total = main_area + sub_areas
        logging.info(f"{self.name} roof area: {total:.2f} cm²")
        return total

    def _to_dict(self) -> dict:
        return {
            "name": self.name,
            "section_length": self.section_length,
            "width": self.width,
            "roof_pitch_deg": self.parent.roof_pitch_angle_degrees,
            "on_extreme_end": self.on_extreme_end,
            "unit": self.unit.value,
            "sub_roofs_attached": [sr.to_dict() for sr in self.sub_roofs_attached],
            "roof_overhang":self.roof_overhang
        }

    def __str__(self) -> str:
        return f"{self.name}: {self.section_length}x{self.width} pitch= {self.roof_pitch_deg}°"
        
        
     
        
class HipSubRoof(SubRoof,HipRoofMixin):
    def to_dict(self) -> dict:
        return {
            **self._to_dict(),
            "hip_rafter_length":self.hip_rafter_length,
            "corner_tiebeam_length":self.corner_tiebeam_length,
            "triangular_facial_area":self.triangular_facial_area,
        }

@dataclass
class GableSubRoof(SubRoof):
    side_extension_length:float = 30
    
    def to_dict(self) -> dict:
        return {
            **self._to_dict(),
            "side_extension_length":self.side_extension_length
        }
