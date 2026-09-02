# IMD Data Request for ETo Calculation Project

## Project Overview

**Research Title:** Physics-Guided ML Interpretability for Reference Evapotranspiration (ETo) in Arid Rajasthan

**Study Area:** Four cities in the Thar Desert region of Rajasthan:
- **Barmer** (25.75°N, 71.38°E, Elevation: 227m)
- **Bikaner** (28.02°N, 73.31°E, Elevation: 234m)
- **Jaisalmer** (26.91°N, 70.91°E, Elevation: 225m)
- **Jodhpur** (26.24°N, 73.02°E, Elevation: 231m)

**Study Period:** 25 years (2001–2025)

**Research Objective:** 
To calculate FAO-56 Penman-Monteith Reference Evapotranspiration (ETo) and use Machine Learning (XGBoost) with SHAP (SHapley Additive exPlanations) to quantify which meteorological variables dominantly control evaporation dynamics in arid climates, and how these drivers shift seasonally.

---

## Data Previously Used (NASA POWER)

The following meteorological parameters were obtained from NASA POWER API at **hourly temporal resolution**:

| Parameter | NASA Code | Description | Units | Purpose in ETo Calculation |
|-----------|-----------|-------------|-------|----------------------------|
| Air Temperature | T2M | Mean temperature at 2 meters above surface | °C | Primary driver of vapor pressure deficit |
| Relative Humidity | RH2M | Relative humidity at 2 meters | % | Controls actual vapor pressure and aerodynamic resistance |
| Wind Speed | WS2M | Wind speed at 2 meters | m/s | Aerodynamic term in Penman-Monteith equation |
| Solar Radiation | ALLSKY_SFC_SW_DWN | Surface shortwave downward radiation (all-sky conditions) | MJ/m²/hr | Radiative energy available for evaporation |
| Surface Pressure | PS | Surface atmospheric pressure | kPa | Psychrometric constant and vapor pressure calculations |

**Temporal Resolution:** Hourly (critical for capturing diurnal evaporation patterns)
**Spatial Resolution:** Point data at specific coordinates for each city

---

## IMD Data Request Specification

### Required Meteorological Parameters

To replicate the NASA-based analysis with IMD data, we request the following parameters at **hourly resolution**:

#### 1. Air Temperature
- **Parameter Name:** Dry bulb temperature
- **Measurement Height:** 2 meters above ground
- **Units:** °C (Celsius)
- **Required:** Mean hourly temperature
- **Alternative:** If hourly mean is unavailable, please provide hourly observations that can be averaged

#### 2. Relative Humidity
- **Parameter Name:** Relative humidity
- **Measurement Height:** 2 meters above ground
- **Units:** % (percentage)
- **Required:** Mean hourly relative humidity
- **Alternative:** If RH is unavailable, we can calculate from dew point temperature if provided

#### 3. Wind Speed
- **Parameter Name:** Wind speed
- **Measurement Height:** 2 meters above ground
- **Units:** m/s (meters per second)
- **Required:** Mean hourly wind speed
- **Note:** If measured at different height (e.g., 10m), please provide the measurement height so we can apply logarithmic wind profile adjustment to 2m

#### 4. Solar Radiation
- **Parameter Name:** Global solar radiation / Shortwave radiation
- **Measurement:** Surface downward solar radiation
- **Units:** MJ/m²/hr (Megajoules per square meter per hour) OR W/m² (Watts per square meter)
  - If provided in W/m², we can convert to MJ/m²/hr (1 W/m² = 0.0036 MJ/m²/hr)
- **Required:** Hourly solar radiation values
- **Alternative:** If solar radiation measurements are unavailable, sunshine duration hours can be used to estimate solar radiation using Angstrom-Prescott equation

#### 5. Atmospheric Pressure
- **Parameter Name:** Surface atmospheric pressure / Station pressure
- **Units:** kPa (kilopascals) OR hPa/mbar (can be converted)
- **Required:** Mean hourly pressure
- **Alternative:** If pressure measurements are unavailable, we can estimate from elevation using standard atmosphere equations (less accurate but acceptable)

---

### Temporal Requirements

- **Time Period:** January 1, 2001 to December 31, 2025 (25 years)
- **Temporal Resolution:** **Hourly data is critical**
  - Daily data is insufficient for our analysis because:
    - We need to capture diurnal patterns in evaporation
    - Night-time vs day-time physics differ significantly
    - SHAP analysis requires hourly granularity to understand temporal dynamics
    - Our ML model was trained on ~215,000 hourly data points per city

### Spatial Requirements

- **Station Locations:** For each of the four cities (Barmer, Bikaner, Jaisalmer, Jodhpur), please provide data from the nearest IMD meteorological station
- **Station Metadata:** Please include:
  - Station name and code
  - Exact latitude and longitude
  - Elevation above mean sea level (meters)
  - Measurement heights for all instruments
  - Distance from city center (if station is not within city limits)

---

### Data Format Preferences

**Preferred Format:** CSV files with the following structure:

```
datetime,T,RH,WS,Rs,P
2001-01-01 00:00,15.2,65,2.1,0,101.3
2001-01-01 01:00,14.8,67,1.9,0,101.2
...
```

**Alternative Formats:** 
- NetCDF files
- JSON format
- Excel files

**Required Columns:**
- `datetime`: ISO format (YYYY-MM-DD HH:MM) in IST (Indian Standard Time)
- `T`: Temperature (°C)
- `RH`: Relative Humidity (%)
- `WS`: Wind Speed (m/s at 2m)
- `Rs`: Solar Radiation (MJ/m²/hr)
- `P`: Pressure (kPa)

---

### Quality Control Requirements

Please provide information on:
- **Data completeness:** Percentage of missing data for each parameter
- **Quality flags:** Any quality control flags or data validation indicators
- **Missing data handling:** How missing values are represented (e.g., -999, NaN, NULL)
- **Instrument calibration:** Any known calibration issues or changes during the 25-year period
- **Station relocation:** If any station was relocated during the study period

---

## Why This Data is Required

### Scientific Justification

1. **FAO-56 Penman-Monteith Equation:** This is the internationally standard method for calculating reference evapotranspiration, recommended by FAO (Food and Agriculture Organization). It requires all five meteorological parameters listed above.

2. **Physics-Guided Machine Learning:** We trained XGBoost models to emulate the FAO-56 equation and achieved R² > 0.998, proving the ML models perfectly learned the physics. We now use SHAP to decompose each prediction into contributions from each variable.

3. **Hourly Resolution Criticality:**
   - ETo varies significantly between day and night
   - Solar radiation is zero at night but dominant during day
   - Wind and humidity effects differ diurnally
   - Our analysis filters to daytime hours only (ETo > 0) to focus on active evaporation dynamics
   - Seasonal regime shifts (summer vs monsoon) can only be captured with hourly data

4. **Research Outputs:** This analysis will produce:
   - Quantified rankings of meteorological drivers by season
   - Geographic comparison of evaporation controls across the Thar Desert
   - SHAP-based equations showing exact contribution of each variable
   - Insights for water resource management in arid Rajasthan

---

## Comparison: NASA vs IMD Data

| Aspect | NASA POWER (Used Previously) | IMD (Requested) |
|--------|----------------------------|-----------------|
| Data Source | Satellite-derived reanalysis | Ground-based observations |
| Spatial Resolution | 0.5° × 0.5° grid (~50km) | Point measurements at stations |
| Temporal Resolution | Hourly | Hourly (requested) |
| Accuracy | Good for regional trends | Higher accuracy at local scale |
| Advantages | Global coverage, consistent methodology | Actual ground measurements, local accuracy |
| Limitations | May miss local microclimate effects | Station availability, potential gaps |

**Why Switch to IMD:**
- Ground observations are more accurate for local-scale studies
- IMD data is the official meteorological record for India
- Better validation for local agricultural and water resource applications
- Mentor's requirement for using authentic Indian meteorological data

---

## Additional Information for IMD

### Contact Information
- **Researcher:** [Your Name]
- **Institution:** [Your Institution]
- **Email:** [Your Email]
- **Phone:** [Your Phone]
- **Research Purpose:** Academic research on evapotranspiration dynamics in arid Rajasthan

### Data Usage Agreement
- This data will be used solely for academic research purposes
- Proper acknowledgment to IMD will be provided in all publications
- Data will not be shared with third parties without IMD permission
- Research findings may be shared with IMD upon request

### Timeline
- **Data Required By:** [Specify your deadline]
- **Research Completion Expected:** [Specify expected completion]

---

## Summary for Quick Reference

**Cities:** Barmer, Bikaner, Jaisalmer, Jodhpur (Rajasthan)

**Period:** 2001–2025 (25 years)

**Resolution:** Hourly

**Parameters Required:**
1. Temperature (°C) at 2m
2. Relative Humidity (%) at 2m
3. Wind Speed (m/s) at 2m
4. Solar Radiation (MJ/m²/hr) at surface
5. Pressure (kPa) at surface

**Purpose:** FAO-56 ETo calculation + ML interpretability analysis

**Contact:** [Your contact details]

---

## Appendix: FAO-56 Equation Reference

For IMD's reference, the FAO-56 hourly Penman-Monteith equation we will implement is:

```
ETo = [0.408 × Δ × (Rn - G) + γ × (37/(T+273)) × u2 × (es - ea)] / [Δ + γ × (1 + 0.24 × u2)]
```

Where:
- **ETo**: Reference evapotranspiration (mm/hr)
- **Δ**: Slope of saturation vapor pressure curve (kPa/°C)
- **Rn**: Net radiation (MJ/m²/hr) = Rns - Rnl
- **G**: Soil heat flux (MJ/m²/hr)
- **γ**: Psychrometric constant (kPa/°C)
- **T**: Air temperature (°C)
- **u2**: Wind speed at 2m (m/s)
- **es**: Saturation vapor pressure (kPa)
- **ea**: Actual vapor pressure (kPa)

All parameters listed in this request are essential for this calculation.
