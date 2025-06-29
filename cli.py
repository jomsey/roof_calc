import logging
import argparse
import sys
import json

from logger import setup_logging
from roof import RoofFactory, RoofType, Unit, SheetSize
from roof import convert_area, area_unit_str
from defaults import (
    OVERHANG,
    SHEET_WIDTH,
    SHEET_LENGTH,
    WASTE_PERCENTAGE,
    PURLIN_SPACING,
    HEIGHT_RATIO,
    SIDE_EXTENTION
)


def main():
    """Main entry point for the command line interface."""
    setup_logging()

    parser = argparse.ArgumentParser(
        description="""Roof Material Calculator - Estimate construction materials for various roof types.
Supported roof types:
- HIP: Four sloping sides meeting at ridge
- GABLE: Two sloping sides with triangular gable ends
- FLAT: Single slope roof (typically 1-5° slope)""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="""Examples:
  Basic gable roof: %(prog)s GABLE 1000 500
  Metric units: %(prog)s HIP 15 10 --unit m
  Custom sheet size: %(prog)s FLAT 800 600 --sheet_length 300 --sheet_width 120"""
    )

    parser.add_argument("roof_type", choices=[rt.name for rt in RoofType], help="Type of roof (HIP, GABLE, FLAT)")
    parser.add_argument("length", type=float, help="Building length (in specified unit)")
    parser.add_argument("width", type=float, help="Building width (in specified unit)")

    parser.add_argument("--unit", choices=[u.value for u in Unit], default="cm", help="Measurement unit")
    parser.add_argument("--sheet_length", type=float, default=SHEET_LENGTH, help="Sheet length (cm)")
    parser.add_argument("--sheet_width", type=float, default=SHEET_WIDTH, help="Sheet width (cm)")
    parser.add_argument("--purlin_spacing", type=float, default=PURLIN_SPACING, help="Spacing between purlins (cm)")
    parser.add_argument("--truss_spacing", type=float, default=60, help="Spacing between trusses (cm)")
    parser.add_argument("--waste_percent", type=float, default=WASTE_PERCENTAGE, help="Fractional waste (e.g., 0.1 for 10%)")
    parser.add_argument("--roof_overhang", type=float, default=60, help="Overhang at each roof edge (cm)")
    parser.add_argument("--height_ratio", type=float, default=HEIGHT_RATIO, help="Height ratio for sloped roofs")
    parser.add_argument("--side_extension_length", type=float, default=SIDE_EXTENTION, help="Gable roof side extension (cm)")
    parser.add_argument("--flat_roof_rise", type=float, help="Flat roof vertical rise (cm)")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    parser.add_argument("--version", action="version", version="RoofCalc 1.0")

    args = parser.parse_args()

    # Validate positive dimensions
    for name in [
        "length", "width", "sheet_length", "sheet_width", "purlin_spacing",
        "truss_spacing", "roof_overhang", "height_ratio", "side_extension_length"
    ]:
        value = getattr(args, name)
        if value <= 0:
            print(f"Error: {name.replace('_', ' ')} must be positive.", file=sys.stderr)
            sys.exit(1)

    if args.waste_percent < 0:
        print("Error: waste_percent must not be negative.", file=sys.stderr)
        sys.exit(1)

    if args.flat_roof_rise is not None and args.flat_roof_rise <= 0:
        print("Error: flat_roof_rise must be positive if specified.", file=sys.stderr)
        sys.exit(1)

    roof_type = RoofType[args.roof_type]
    unit = Unit(args.unit)

    extra_args = {
        "roof_overhang": args.roof_overhang,
        "height_ratio": args.height_ratio,
        "side_extension_length": args.side_extension_length,
        "flat_roof_rise": args.flat_roof_rise
    }

    sheet_size = SheetSize(args.sheet_length, args.sheet_width)

    try:
        roof = RoofFactory.create_roof(
            roof_type,
            args.length,
            args.width,
            unit=unit,
            **extra_args
        )
        #result = roof.calculate_materials(sheet_size=sheet_size,purlin_spacing=args.purlin_spacing,truss_spacing=args.truss_spacing,waste_percent=args.waste_percent )

        logging.info(f"Calculation successful for roof: {args.roof_type}")

    except Exception as e:
        print(f"Calculation error: {e}", file=sys.stderr)
        logging.error("Calculation error", exc_info=True)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n--- Roof Calculation Summary ({roof_type.name}) ---")
        #for key, value in result.items():
            #if "area" in key.lower():
                #converted = convert_area(value, unit)
                #print(f"{key}: {converted:.2f} {area_unit_str(unit)}")
            #else:
                #print(f"{key}: {value}")

if __name__ == "__main__":
    main()
