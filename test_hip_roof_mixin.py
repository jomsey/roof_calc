import unittest
import math
from mixin import HipRoofMixin

class DummyRoof(HipRoofMixin):
    """Dummy class to test the mixin with custom attributes."""
    pass

class TestHipRoofMixin(unittest.TestCase):
    def setUp(self):
        self.roof = DummyRoof()
        self.roof.roof_half_span = 300  # cm
        self.roof.roof_overhang = 50    # cm
        self.roof.roof_height = 200     # cm

    def test_corner_tiebeam_length(self):
        expected = math.hypot(300, 300)
        self.assertAlmostEqual(self.roof.corner_tiebeam_length, expected)

    def test_hip_rafter_overhang(self):
        expected = math.hypot(50,50)
        self.assertAlmostEqual(self.roof.hip_rafter_overhang, expected)

    def test_hip_rafter_length(self):
        tiebeam = math.hypot(300, 300)
        expected = math.hypot(tiebeam, 200) + 50
        self.assertAlmostEqual(self.roof.hip_rafter_length, expected)

    def test_triangular_facial_area(self):
        base = 2 * (300 + 50)
        expected = base * 200
        self.assertAlmostEqual(self.roof.triangular_facial_area, expected)

    def test_missing_attribute_raises_error(self):
        del self.roof.roof_height
        with self.assertRaises(AttributeError) as context:
            _ = self.roof.triangular_facial_area
        self.assertIn("Missing required attribute: 'roof_height'", str(context.exception))


if __name__ == '__main__':
    unittest.main()
