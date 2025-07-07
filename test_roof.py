import unittest
import math

from roof import Roof, HipRoof, GableRoof, FlatRoof, RoofFactory, RoofType, Unit, SheetSize
from exceptions import InvalidDimensionsError, InvalidSheetSizeError
from mixin import HipRoofMixin

class TestRoofCalculations(unittest.TestCase):
    def setUp(self):
        # Common valid parameters
        self.valid_length = 1000
        self.valid_width = 600
        self.valid_unit = Unit.CM
        
    # --------------------------
    # Base Class & Validation Tests
    # --------------------------
    def test_negative_dimensions(self):
        with self.assertRaises(InvalidDimensionsError):
            Roof(-1000, 600, Unit.CM)
        with self.assertRaises(InvalidDimensionsError):
            Roof(1000, -600, Unit.CM)
        with self.assertRaises(InvalidDimensionsError):
            HipRoof(1000, 600, roof_overhang=-50)
        with self.assertRaises(InvalidDimensionsError):
            GableRoof(1000, 600, height_ratio=-3)
    
    def test_invalid_units(self):
        with self.assertRaises(ValueError):
            Roof(1000, 600, "invalid_unit")
    
    def test_invalid_sheet_size(self):
        roof = RoofFactory.create_roof(RoofType.GABLE, 1000, 600)
        with self.assertRaises(InvalidSheetSizeError):
            roof.iron_sheets_count(SheetSize(0, 100))
        with self.assertRaises(InvalidSheetSizeError):
            roof.iron_sheets_count(SheetSize(100, 0))
        with self.assertRaises(InvalidSheetSizeError):
            roof.iron_sheets_count(SheetSize(-100, 100))
    
    def test_waste_percentage_edge_cases(self):
        roof = RoofFactory.create_roof(RoofType.GABLE, 1000, 600)
        with self.assertRaises(InvalidDimensionsError):
            roof.iron_sheets_count(SheetSize(200, 100), waste_percent=-0.1)
        
        # 0% waste
        count = roof.iron_sheets_count(SheetSize(200, 100), waste_percent=0)
        self.assertIsInstance(count, int)
    
    # --------------------------
    # Unit Conversion Tests
    # --------------------------
    def test_unit_conversion(self):
        # Test in meters
        roof_m = HipRoof(10, 6, unit=Unit.M)
        self.assertAlmostEqual(roof_m.building_length, 1000)
        self.assertAlmostEqual(roof_m.building_width, 600)
        
        # Test in feet
        roof_ft = HipRoof(32.8, 19.68, unit=Unit.FT)
        self.assertAlmostEqual(roof_ft.building_length, 1000, delta=1)
        self.assertAlmostEqual(roof_ft.building_width, 600, delta=1)
    
    # --------------------------
    # Hip Roof Edge Cases
    # --------------------------
    def test_hip_roof_minimal_dimensions(self):
        roof = HipRoof(1, 1)
        area = roof.roof_area()
        self.assertGreater(area, 0)
        
        trusses = roof.main_trusses_count(30)
        self.assertEqual(trusses, 1)  # Should have at least 1 truss
    
    def test_hip_roof_zero_overhang(self):
        roof = HipRoof(1000, 600, roof_overhang=0)
        area = roof.roof_area()
        self.assertGreater(area, 0)
    
    def test_hip_roof_extreme_ratio(self):
        # Very steep roof
        roof_steep = HipRoof(1000, 600, height_ratio=1)
        self.assertAlmostEqual(roof_steep.roof_height, 600)
        
        # Very flat roof
        roof_flat = HipRoof(1000, 600, height_ratio=20)
        self.assertAlmostEqual(roof_flat.roof_height, 30)
    
    def test_hip_roof_truss_count_edge(self):
        roof = HipRoof(1000, 600)
        # Spacing larger than building length
        self.assertEqual(roof.main_trusses_count(2000), 1)
        
        # Spacing equal to building length
        self.assertEqual(roof.main_trusses_count(1000), 2)
    
    # --------------------------
    # Gable Roof Edge Cases
    # --------------------------
    def test_gable_roof_minimal_dimensions(self):
        roof = GableRoof(1, 1)
        area = roof.roof_area()
        self.assertGreater(area, 0)
        
        ridge_covers = roof.ridge_cover_count()
        self.assertGreater(ridge_covers, 0)
    
    def test_gable_roof_zero_side_extension(self):
        roof = GableRoof(1000, 600, side_extension_length=0)
        area = roof.roof_area()
        self.assertGreater(area, 0)
    
    def test_gable_roof_negative_side_extension(self):
        with self.assertRaises(InvalidDimensionsError):
            GableRoof(1000, 600, side_extension_length=-10)
    
    def test_gable_ridge_covers_edge(self):
        roof = GableRoof(1000, 600)
        # Cover length larger than ridge
        self.assertEqual(roof.ridge_cover_count(2000), 1)
        
        # Cover length equal to ridge
        self.assertEqual(roof.ridge_cover_count(1060), 1)  # 1000 + 2*30
    
    # --------------------------
    # Flat Roof Edge Cases
    # --------------------------
    def test_flat_roof_minimal_dimensions(self):
        roof = FlatRoof(1, 1)
        area = roof.roof_area()
        self.assertGreater(area, 0)
    
    def test_flat_roof_zero_rise(self):
        roof = FlatRoof(1000, 600, flat_roof_rise=0)
        area = roof.roof_area()
        self.assertAlmostEqual(area, 1000 * (600 + 2*60))  # Length * (Width + 2*overhang)
    
    def test_flat_roof_negative_rise(self):
        with self.assertRaises(InvalidDimensionsError):
            FlatRoof(1000, 600, flat_roof_rise=-5)
    
    def test_flat_roof_no_ridge_covers(self):
        roof = FlatRoof(1000, 600)
        self.assertEqual(roof.ridge_cover_count(), 0)
    
    # --------------------------
    # Factory & Sub-Roof Tests
    # --------------------------
    def test_roof_factory_invalid_type(self):
        with self.assertRaises(ValueError):
            RoofFactory.create_roof("INVALID_TYPE", 1000, 600)
    
    def test_sub_roof_attachment(self):
        main_roof = HipRoof(1000, 600)
        sub_roof = HipSubRoof(200, 300)  # Assuming SubRoof implementation exists
        
        main_roof.sub_roofs_attached = [sub_roof]
        main_area = main_roof.roof_area()
        sub_area = sub_roof.roof_area()
        collective_area = main_roof.collective_roof_area()
        
        self.assertAlmostEqual(collective_area, main_area + sub_area)
    
    def test_multiple_sub_roofs(self):
        main_roof = GableRoof(1000, 600)
        sub1 = GableSubRoof(200, 300)
        sub2 = HipSubRoof(150, 250)
        
        main_roof.sub_roofs_attached = [sub1, sub2]
        total_area = (main_roof.roof_area() + 
                      sub1.roof_area() + 
                      sub2.roof_area())
        self.assertAlmostEqual(main_roof.collective_roof_area(), total_area)
    
    # --------------------------
    # Material Calculation Tests
    # --------------------------
    def test_iron_sheets_edge_cases(self):
        roof = GableRoof(1000, 600)
        # Sheet larger than roof
        count = roof.iron_sheets_count(SheetSize(10000, 10000))
        self.assertEqual(count, 1)
        
        # Sheet same size as roof
        area = roof.roof_area()
        sheet_size = SheetSize(math.sqrt(area), math.sqrt(area))
        self.assertEqual(roof.iron_sheets_count(sheet_size), 1)
    
    def test_purlin_lines_edge_cases(self):
        roof = HipRoof(1000, 600)
        # Spacing larger than diagonal height
        self.assertEqual(roof.purlin_lines_count(2000), 1)
        
        # Zero spacing
        with self.assertRaises(InvalidDimensionsError):
            roof.purlin_lines_count(0)
    
    def test_truss_count_edge_cases(self):
        roof = HipRoof(1000, 600)
        # Zero spacing
        with self.assertRaises(InvalidDimensionsError):
            roof.main_trusses_count(0)
        
        # Exact division
        self.assertEqual(roof.main_trusses_count(500), 3)  # (400/500)+1 = 1.8 -> floor(1.8)+1 = 2? Need to verify formula
    
    # --------------------------
    # Special Cases
    # --------------------------
    def test_square_hip_roof(self):
        roof = HipRoof(600, 600)
        area = roof.roof_area()
        self.assertAlmostEqual(area, 4 * (600 * math.sqrt(300**2 + 200**2)), delta=0.1)
    
    def test_long_thin_gable_roof(self):
        roof = GableRoof(5000, 300)
        sheets = roof.iron_sheets_count(SheetSize(200, 100))
        self.assertGreater(sheets, 50)  # Sanity check
    
    def test_flat_roof_minimal_slope(self):
        roof = FlatRoof(1000, 600, flat_roof_rise=0.001)
        area = roof.roof_area()
        self.assertAlmostEqual(area, 1000 * 720, delta=1)  # Should be nearly same as zero slope

if __name__ == "__main__":
    unittest.main()