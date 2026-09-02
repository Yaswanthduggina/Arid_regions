# Quick Reference Card: ETo Project

## Project Snapshot
**Title:** Physics-Guided ML Interpretability for ETo in Arid Rajasthan
**Data Source:** NASA POWER (2001-2025) → Switching to IMD
**Cities:** Barmer, Bikaner, Jaisalmer, Jodhpur
**Output:** Hourly ETo + SHAP-based driver analysis

---

## NASA Data Used (5 Parameters)

| # | Parameter | NASA Code | Units | Height |
|---|-----------|-----------|-------|--------|
| 1 | Temperature | T2M | °C | 2m |
| 2 | Relative Humidity | RH2M | % | 2m |
| 3 | Wind Speed | WS2M | m/s | 2m |
| 4 | Solar Radiation | ALLSKY_SFC_SW_DWN | MJ/m²/hr | Surface |
| 5 | Pressure | PS | kPa | Surface |

**Resolution:** Hourly
**Period:** 2001-2025 (25 years)

---

## IMD Data Request (Same Specs)

**Required Parameters:**
1. Temperature (°C) at 2m
2. Relative Humidity (%) at 2m
3. Wind Speed (m/s) at 2m
4. Solar Radiation (MJ/m²/hr) at surface
5. Pressure (kPa) at surface

**Critical Requirements:**
- ⚠️ **Hourly resolution** (daily insufficient)
- ⚠️ Same 4 cities
- ⚠️ Same time period (2001-2025)
- ⚠️ Station metadata (lat/lon/elevation)

---

## Key Results Achieved

**ML Model Performance:**
- R² > 0.998 (near-perfect fit)
- NSE > 0.998 (hydrological gold standard)
- Bias ≈ 0 (no systematic error)

**SHAP Findings:**
- Solar Radiation = #1 driver (~0.18 mm/hr contribution)
- Low humidity increases ETo
- Wind importance varies geographically
- Summer = radiation-dominated
- Monsoon = humidity-modulated

---

## File Locations

**Data:**
- `data/raw/{city}_data/` - Original data
- `data/processed/` - Cleaned merged data
- `ET0_new/` - ETo results

**Scripts:**
- `scripts/downloading_data/` - Download scripts
- `scripts/claculation_ETo/` - ETo calculation
- `scripts/ml_shap/` - ML & SHAP analysis

**Documentation:**
- `notes/IMD_DATA_REQUEST.md` - Detailed IMD request
- `notes/PROJECT_REFRESH_SUMMARY.md` - Full project summary
- `notes/FINAL_EXPLANATION.md` - Complete research explanation

---

## Workflow Summary

```
NASA Data → Clean → ETo (FAO-56) → ML (XGBoost) → SHAP Analysis
     ↓
IMD Data → Clean → ETo (FAO-56) → ML (XGBoost) → SHAP Analysis
     ↓
Compare Results
```

---

## Talking Points

**To Mentor:**
- "Completed 25-year hourly ETo calculation for 4 Rajasthan cities using NASA data"
- "Achieved R² > 0.998 with XGBoost, proving perfect physics learning"
- "Used SHAP to quantify solar radiation as primary evaporation driver"
- "Now requesting IMD data to validate with ground observations"

**To IMD:**
- "Need hourly meteorological data for research"
- "5 parameters: T, RH, WS, Radiation, Pressure"
- "4 cities: Barmer, Bikaner, Jaisalmer, Jodhpur"
- "Period: 2001-2025"
- "Purpose: FAO-56 ETo calculation for water resource research"

---

## Critical Reminders

⚠️ **Hourly data is essential** - daily data won't work for SHAP analysis
⚠️ **All 5 parameters required** - FAO-56 equation needs all of them
⚠️ **Station metadata needed** - elevation and measurement heights
⚠️ **Quality flags** - ask about missing data and validation

---

## Next Steps

1. Customize `notes/IMD_DATA_REQUEST.md` with your contact details
2. Submit request to IMD with institutional authorization
3. Plan data format conversion when IMD data arrives
4. Replicate entire pipeline with IMD data
5. Compare NASA vs IMD results

---

## Contact Template

**For IMD Request:**
- Name: [Your Name]
- Institution: [Your Institution]
- Email: [Your Email]
- Research: ETo calculation for arid Rajasthan
- Data: Hourly meteorological (2001-2025)
- Cities: Barmer, Bikaner, Jaisalmer, Jodhpur
- Purpose: Academic research with proper acknowledgment
