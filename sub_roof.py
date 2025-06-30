import math
import logging
from dataclasses import dataclass, field
from typing import List, Optional
from validators import validate_positive,validate_pitch_degrees
from miscellenous import Unit
from mixin import HipRoofMixin
from pprint import pprint as print

@dataclass
class SubRoof:
    name: str
    section_length: float  # along main roof
    width: float           # depth of sub-roof out from main
    roof_pitch_deg: float  # pitch in degrees
    unit: Unit = Unit.CM
    on_extreme_end: bool = False  # gable or hip end
    sub_roofs_attached: List["SubRoof"] = field(default_factory=list)

    def __post_init__(self):
        validate_positive(self.section_length, "section_length")
        validate_positive(self.width, "width")
        self.roof_half_span = self.section_length * .5
        validate_pitch_degrees(self.roof_pitch_deg)

    @property
    def pitch_rise_run(self) -> float:
        """Return the roof rise-to-run ratio based on pitch in degrees."""
        return math.tan(math.radians(self.roof_pitch_deg))

    @property
    def slope_height(self) -> float:
        """Return the slant height of the roof section using pitch."""
        rise = self.pitch_rise_run * self.roof_half_span
        hypotenuse = math.hypot(rise, self.width / 2)
        return hypotenuse
        
    @property     
    def roof_height(self):
        return 200
        
    @property     
    def roof_overhang(self):
        return 60
        
    def roof_area(self) -> float:
        """Calculate the total sloped area of this sub-roof and its children."""
        main_area = 2 * self.slope_height * self.section_length
        sub_areas = sum(sr.roof_area() for sr in self.sub_roofs_attached)
        total = main_area + sub_areas
        logging.info(f"{self.name} roof area: {total:.2f} cm²")
        return total

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "section_length": self.section_length,
            "width": self.width,
            "roof_pitch_deg": self.roof_pitch_deg,
            "on_extreme_end": self.on_extreme_end,
            "unit": self.unit.value,
            "sub_roofs_attached": [sr.to_dict() for sr in self.sub_roofs_attached],
        }

    def __str__(self) -> str:
        return f"{self.name}: {self.section_length}x{self.width} pitch= {self.roof_pitch_deg}°"
     
        
class HipSubRoof(SubRoof,HipRoofMixin):
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "section_length": self.section_length,
            "width": self.width,
            "roof_pitch_deg": self.roof_pitch_deg,
            "on_extreme_end": self.on_extreme_end,
            "unit": self.unit.value,
            "hip_rafter_length":self.hip_rafter_length,
            "corner_tiebeam_length":self.corner_tiebeam_length,
            "triangular_facial_area":self.triangular_facial_area,
            "facial_base_length":self.facial_base_length,
            "sub_roofs_attached": [sr.to_dict() for sr in self.sub_roofs_attached],
        }

class GableSubRoof(SubRoof):
    pass       




