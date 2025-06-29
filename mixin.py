import math

class HipRoofMixin:
    def _get_attr(self, attr_name: str):
        if not hasattr(self, attr_name):
            raise AttributeError(f"Missing required attribute: '{attr_name}' in {self.__class__.__name__}")
        return getattr(self, attr_name)

    @property
    def corner_tiebeam_length(self) -> float:
        half_span = self._get_attr('roof_half_span')
        return math.hypot(half_span, half_span)

    @property
    def hip_rafter_overhang(self) -> float:
        overhang = self._get_attr('roof_overhang')
        return math.hypot(overhang, overhang)

    @property
    def hip_rafter_length(self) -> float:
        tiebeam = self.corner_tiebeam_length
        height = self._get_attr('roof_height')
        overhang = self._get_attr('roof_overhang')
        return math.hypot(tiebeam, height) + overhang

    @property
    def triangular_facial_area(self) -> float:
        base = self.facial_base_length
        height = self._get_attr('roof_height')
        return base * height

    @property
    def facial_base_length(self) -> float:
        half_span = self._get_attr('roof_half_span')
        overhang = self._get_attr('roof_overhang')
        return 2 * (half_span + overhang)
