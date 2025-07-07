from __future__ import annotations  # For forward references without quotes
import math
import logging
from dataclasses import dataclass, field
from typing import List, Tuple
from miscellenous import Unit, SheetSize, SheetOverup
from utils import convert_to_cm, unit_str
from validators import validate_positive, validate_unit, validate_sheet_size, validate_sheet_overup
from roof import Roof,HipRoof,GableRoof,FlatRoof
from sub_roof import SubRoof,HipSubRoof,GableSubRoof
#from mixin import PurlinMixin,JackRafterMixin


# ---------------------
# ROOF COVER SHEETS
# ---------------------
@dataclass
class SheetCover:
    sheet_size: SheetSize
    cover_overup: SheetOverup

    def __post_init__(self):
        validate_sheet_size(self.sheet_size)
        validate_sheet_overup(self.cover_overup)

    def sheet_area(self) -> float:
        effective_length = self.sheet_size.length - self.cover_overup.left_right_overup
        effective_width = self.sheet_size.width - self.cover_overup.top_bottom_overup
        return effective_length * effective_width

class PurlinMixin:
    @property
    def purlin_lines_count(self) -> int:
        slope_length = self.roof.slope_length if isinstance(self.roof, FlatRoof) else self.roof.slope_height
        return math.ceil(slope_length / self.purlin_spacing)

    @property
    def cumulative_purlins_length(self) -> float | None:
        if self.is_gable and not isinstance(self.roof, FlatRoof):
            extension = self.roof.side_extension_length
            return (self.roof._length + extension) * self.purlin_lines_count * 2
        if isinstance(self.roof, HipRoof):
            total = 0
            for length in self.trapezoid_face_purlins:
                total += 2 * length
            for length in self.triangular_face_purlins:
                total += length
            return round(total, 2)
        if isinstance(self.roof, FlatRoof):
            return self.roof._length * self.purlin_lines_count

    @property
    def triangular_face_purlins(self) -> List[float] | None:
        if self.is_gable:
            return None
        h = self.slope_height
        tr_base = (self.half_span + self.overhang) * 2
        levels = [round(tr_base, 2)]
        current_height = 0
        while current_height + self.purlin_spacing < h:
            current_height += self.purlin_spacing
            purlin_length = tr_base * (1 - current_height / h)
            levels.append(round(purlin_length, 2))
        return levels

    @property
    def trapezoid_face_purlins(self) -> List[float] | None:
        if self.is_gable or isinstance(self.roof, SubRoof):
            return None
        bottom_base = self.roof._length + 2 * self.overhang
        top_base = self.roof._ridge_length
        levels = [round(bottom_base, 2)]
        current_height = 0
        while current_height + self.purlin_spacing < self.slope_height:
            current_height += self.purlin_spacing
            ratio = current_height / self.slope_height
            base_at_height = bottom_base - (bottom_base - top_base) * ratio
            levels.append(round(base_at_height, 2))
        levels.append(round(top_base, 2))
        return levels

    @property
    def parallelogram_face_purlins(self) -> List[float] | None:
        if not isinstance(self.roof, SubRoof):
            return None
        purlin_length = self.roof.width
        levels = [round(purlin_length, 2)]
        current_height = 0
        while current_height + self.purlin_spacing < self.slope_height:
            current_height += self.purlin_spacing
            levels.append(round(purlin_length, 2))
        return levels

class JackRafterMixin:
    @property
    def _jack_runs(self) -> List[float]:
        return [
            n * self.truss_spacing
            for n in range(1, int(self.half_span // self.truss_spacing) + 1)
            if n * self.truss_spacing < self.half_span
        ]

    @property
    def collective_jack_rafter_lengths(self) -> List[float] | None:
        if self.is_gable:
            return None
        return [round(run / math.cos(math.atan(self.pitch)), 2) for run in self._jack_runs]

    @property
    def jack_tiebeams_lengths(self) -> List[float] | None:
        if self.is_gable:
            return None
        return [round(run * math.cos(math.atan(self.pitch)), 2) for run in self._jack_runs]


# ---------------------
# ROOF FRAME
# ---------------------
@dataclass
@dataclass
class RoofFrame(JackRafterMixin, PurlinMixin):
    roof: Roof
    truss_spacing: float
    purlin_spacing: float
    unit: Unit = Unit.CM

    def __post_init__(self):
        validate_positive(self.truss_spacing, "truss_spacing")
        validate_positive(self.purlin_spacing, "purlin_spacing")
        self.purlin_spacing = convert_to_cm(self.purlin_spacing, self.unit)
        self.truss_spacing = convert_to_cm(self.truss_spacing, self.unit)
        self.half_span = self.roof.roof_half_span
        self.overhang = self.roof.roof_overhang
        self.rise = self.roof.roof_height
        self.pitch = self.roof.roof_pitch_ratio
        self.slope_height = self.roof.slope_height
        self.is_gable = isinstance(self.roof, (GableRoof, FlatRoof, GableSubRoof))

    @property
    def main_trusses_count(self) -> int:
        return math.floor(self.roof._length / self.truss_spacing) + 1

    @property
    def hip_rafter_length(self) -> float | None:
        if self.is_gable:
            return None
        hip_rafter_overhang = math.hypot(self.overhang, self.overhang)
        return math.hypot(self.diagonal_hip_tiebeam_length, self.rise) + hip_rafter_overhang

    @property
    def diagonal_hip_tiebeam_length(self) -> float | None:
        if self.is_gable:
            return None
        return math.hypot(self.half_span, self.half_span)

    @property
    def common_tiebeam_length(self) -> float | None:
        return None if self.is_gable else 2 * self.half_span

    @property
    def hip_face_common_tiebeam(self) -> float | None:
        return None if self.is_gable else self.half_span

    def to_dict(self) -> dict:
        return {
            "jack_rafter_lengths": self.collective_jack_rafter_lengths,
            "main_trusses_count": self.main_trusses_count,
            "hip_rafter_length": self.hip_rafter_length,
            "common_tiebeam_length": self.common_tiebeam_length,
            "hip_face_common_tiebeam": self.hip_face_common_tiebeam,
            "jack_tiebeams_lengths": self.jack_tiebeams_lengths,
            "diagonal_hip_tiebeam_length": self.diagonal_hip_tiebeam_length,
            "cumulative_purlins_length": self.cumulative_purlins_length,
            "purlin_lines_count": self.purlin_lines_count,
            "triangular_face_purlins": self.triangular_face_purlins,
            "trapezoid_face_purlins": self.trapezoid_face_purlins,
            "parallelogram_face_purlins": self.parallelogram_face_purlins,
        }

    #     
#         
from pprint import pprint as print    
r=GableRoof(1600,750)
s =HipSubRoof("porch",200,150,parent=r)
f=RoofFrame(s,150,54)
print('')
print(f.to_dict())


# 
# 