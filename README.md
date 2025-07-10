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

---


