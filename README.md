# 🏠 Roof Material Estimator – Python Toolkit

A **professional-grade** yet **user-friendly** Python tool for estimating roofing materials. This package simplifies the work of **builders**, **engineers**, **architects**, and **DIY homeowners** by delivering accurate material quantities for **hip**, **gable**, and **flat** roof structures, including **sub-roofs**, **valleys**, and **roof intersections**.

Designed with flexibility and extensibility in mind, this modular system handles real-world roofing scenarios—from basic sheds to complex multi-section buildings.

---

## 🚩 Key Capabilities

✅ **Multiple Roof Types** – HIP, GABLE, FLAT
✅ **Sub-Roof Support** – For porches, dormers, L/T-extensions
✅ **Pitch-Aware Calculations** – Real lengths, slope adjustments, rise/run logic
✅ **Roof Intersections** – Handles overlap logic, shared ridges, valleys
✅ **Material Estimation**:

* Iron sheets (based on effective area)
* Ridge covers (based on ridges)
* Nails (kg, adjustable usage per m²)
* Timber: purlins, rafters, tie beams, trusses

✅ **Unit Handling** – Supports meters (m), centimeters (cm), millimeters (mm)
✅ **CLI Interface** – For quick command-line estimations
✅ **Extensively Tested** – Includes structured unit tests
✅ **Extensible** – Add your own roof types or framing rules

---

## 📀 Roof Types Supported

| Roof Type | Description                               |
| --------- | ----------------------------------------- |
| Gable     | Two sloped sides with vertical gable ends |
| Hip       | Four sloped sides meeting at the ridge    |
| Flat      | Minimal slope for drainage, low pitch     |

---

## 🩵 Materials Estimated

| Material     | Logic                                               |
| ------------ | --------------------------------------------------- |
| Iron Sheets  | Based on slope-corrected roof area + waste margin   |
| Ridge Covers | Total ridge lines across roof and sub-roofs         |
| Nails (kg)   | Calculated from default usage per square meter      |
| Purlins      | Calculated from width and spacing across trusses    |
| Rafters      | Estimated from span and spacing, adjusted for slope |
| Tie Beams    | One per truss or per major span                     |
| Trusses      | Based on building length and user-defined spacing   |

---

## 🧰 Basic Usage

```python
from roof import RoofFactory, RoofType, Unit

# Create a gable roof
gable = RoofFactory.create_roof(
    roof_type=RoofType.GABLE,
    building_length=10,
    building_width=6,
    unit=Unit.M
)

# Surface area and pitch
print(gable.roof_area())
print(gable.roof_pitch_angle_degrees)

# Structural frame estimation
frame = gable.create_frame(truss_spacing=0.6, purlin_spacing=0.9)
print(frame.trusses_count)
print(frame.purlins_count)
```

---

## 🛆 Material Estimation

```python
from roof import SheetCover

sheet = SheetCover(width=1.0, length=2.0, unit=Unit.M)

# Sheets needed for main gable roof
print(gable.sheet_covers_count(sheet, waste_percent=0.1))

# Ridge covers and nails
print(gable.estimate_ridge_covers())
print(gable.estimate_nails_kg())
```

---

## 🏧 Sub-Roof Attachments & Intersections

```python
from roof import SubRoof, RoofType

main_roof = RoofFactory.create_roof(
    roof_type=RoofType.HIP,
    building_length=15,
    building_width=10,
    unit=Unit.M
)

porch = SubRoof(
    name="Porch",
    roof_type=RoofType.GABLE,
    building_length=4,
    building_width=3,
    pitch_ratio=5,
    section_length=4,
    width=3
)

# Attach and integrate
main_roof.sub_roofs_attached = [porch]
print(main_roof.collective_roof_area())
```

---

## 💻 Command Line Interface (CLI)

```bash
# Estimate materials from terminal
python cli.py --roof_type HIP --length 10 --width 8 --unit m \
  --truss_spacing 0.6 --purlin_spacing 0.9
```

Supports nested sub-roof declarations and custom configurations.

---

## 🧪 Development & Testing

```bash
# Clone repo
git clone https://github.com/yourusername/roof-material-estimator
cd roof-material-estimator

# Install in editable mode
pip install -e .

# Run unit tests
python -m unittest discover -s tests

# Linting
flake8 .
```

---

## 📁 Project Structure

```
roof/
├── roof/                 # Core logic and roof models
│   ├── base.py
│   ├── hip.py
│   ├── gable.py
│   ├── flat.py
│   ├── subroof.py
│   ├── frame.py
│   ├── materials.py
│   └── factory.py
├── mixin/                # Mixins: trusses, rafters, etc.
├── cli.py                # Command line interface
├── tests/                # Unit test suite
├── utils/                # Unit conversion, validation
└── README.md
```

---

## 📚 API Highlights

* `RoofFactory.create_roof(...)`
* `.create_frame(truss_spacing, purlin_spacing)`
* `.roof_area()`
* `.sheet_covers_count(...)`
* `.estimate_ridge_covers()`
* `.collective_roof_area()` for main + sub-roofs
* `.sub_roofs_attached = [...]`

---

## 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.

---

## 🤝 Contributing

Pull requests, ideas, and feedback are welcome. Help improve roof logic, add more region-specific standards, or support new roof designs.

---

## 🌍 Real-World Use Cases

✅ **Local Fundis & Builders** – Estimate iron sheets before buying
✅ **Construction Engineers** – Plan timber & trusses per span
✅ **Architects** – Validate roof spans for aesthetics and coverage
✅ **DIY Homeowners** – Plan extensions like porches or store roofs

---

> **NOTE:** This project is constantly evolving. Valley logic, ridge overlaps, and partial-truss support across intersections are continually improving.
