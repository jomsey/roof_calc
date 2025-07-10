# 🏠 Roof Material Estimator

A modular and extensible tool built in **Python** for estimating roofing materials such as iron sheets, timber (purlins, rafters, tie beams, trusses), nails, and ridge covers. The system supports complex roof configurations including **main roofs**, **sub-roofs**, and **roof intersections**.

Designed for **construction workers**, **engineers**, and **DIY builders**, this tool simplifies roofing estimates for **hip**, **gable**, and **flat roofs**—with support for **sloped calculations**, **valleys**, and **pitch-based design logic**.

---

## 📌 Key Features

✅ **Supports multiple roof types**: HIP, GABLE, FLAT  
✅ **Sub-roof support**: Attach child roofs (e.g., porches, dormers) with independent dimensions and pitch  
✅ **Pitch-based calculations**: Uses trigonometry to compute real lengths and areas  
✅ **Valleys and intersections**: Smart logic for handling overlapping roofs  
✅ **Material estimation**:
- Iron sheets
- Ridge covers
- Nails (kg)
- Purlins, rafters, tie beams, trusses

✅ **Standard unit tests**  
✅ **Command-line interface (CLI)**  
✅ **Easily extensible and testable**  

---

## 🧱 Materials Calculated

| Material       | Description                                |
|----------------|--------------------------------------------|
| Iron Sheets    | Based on sheet size and slope-adjusted area |
| Ridge Covers   | Calculated by number of roof ridges         |
| Nails (kg)     | Estimated from default nail usage per m²    |
| Purlins        | Based on spacing and roof width             |
| Rafters        | Span-based rafter count with spacing logic  |
| Tie Beams      | One per truss span (typical)                |
| Trusses        | Based on roof length and spacing            |

```markdown
# Roof Calculation System 🏠📐

A Python package for professional roof design and material estimation.


## Usage 🚀

### Basic Roof Creation
```python
from roof import RoofFactory, Unit, RoofType

# Create different roof types
gable = RoofFactory.create_roof(
    roof_type=RoofType.GABLE,
    building_length=10,  # meters
    building_width=6,
    unit=Unit.M
)

hip = RoofFactory.create_roof(
    roof_type=RoofType.HIP,
    building_length=12,
    building_width=8
)
```

### Advanced Calculations
```python
# Get roof properties
print(f"Surface area: {gable.roof_area():.2f} m²")
print(f"Pitch angle: {gable.roof_pitch_angle_degrees}°")
print(f"Ridge length: {gable._ridge_length} m")

# Create structural frame
frame = gable.create_frame(
    truss_spacing=0.6,  # 60cm spacing
    purlin_spacing=0.9  # 90cm spacing
)
print(f"Trusses needed: {frame.trusses_count}")
```

### Material Estimation
```python
from roof import SheetCover

# Calculate required materials
sheet = SheetCover(width=1, length=2, unit=Unit.M)
print(f"Sheets needed: {gable.sheet_covers_count(sheet, waste_percent=0.1)}")
```

## API Reference 📚

### Roof Classes
```python
class GableRoof(Roof):
    """Two sloping sides with gable ends"""
    def __init__(self, building_length, building_width, 
                 side_extension_length=0.3, roof_overhang=0.6, ...)

class HipRoof(Roof):
    """Four sloping sides meeting at top"""
    def __init__(self, building_length, building_width,
                 roof_overhang=0.6, height_ratio=3, ...)

class FlatRoof(Roof):
    """Single slope for drainage"""
    def __init__(self, building_length, building_width,
                 flat_roof_rise=0.1, ...)
```

## Examples 🏗️

### Complex Roof with Attachments
```python
main_roof = RoofFactory.create_roof(
    roof_type=RoofType.HIP,
    building_length=15,
    building_width=10,
    unit=Unit.M
)

porch_roof = SubRoof(
    roof_type=RoofType.GABLE,
    building_length=4,
    building_width=3
)

main_roof.sub_roofs_attached = [porch_roof]
print(f"Total area: {main_roof.collective_roof_area():.2f} m²")
```

## Development 🛠️
```bash
# Clone and install
git clone https://github.com/yourrepo/roof-calculator
cd roof-calculator
pip install -e .

# Run tests
unittest tests/

# Run linter
flake8 src/
```

## License 📄
MIT License - See LICENSE file for details
```

