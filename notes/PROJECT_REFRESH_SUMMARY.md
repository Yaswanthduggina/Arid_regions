# Project Refresh Summary: ETo Calculation & ML Interpretability

## Quick Project Overview (2-Month Refresher)

**What You Did:**
You calculated Reference Evapotranspiration (ETo) for 4 cities in Rajasthan using NASA POWER data, then used Machine Learning to understand which weather factors control evaporation.

**Cities Studied:**
- Barmer, Bikaner, Jaisalmer, Jodhpur (all in Thar Desert region)

**Time Period:**
- 25 years: 2001–2025

**Key Achievement:**
- Built XGBoost models that achieved R² > 0.998 (nearly perfect)
- Used SHAP to mathematically prove that Solar Radiation is the #1 driver of evaporation
- Showed how drivers shift from summer (radiation-dominated) to monsoon (humidity-dominated)

---

## Step-by-Step Workflow You Completed

### Phase 1: Data Download (NASA POWER)
You downloaded 5 meteorological parameters at **hourly** resolution:

1. **T2M** - Temperature (°C)
2. **RH2M** - Relative Humidity (%)
3. **WS2M** - Wind Speed (m/s)
4. **ALLSKY_SFC_SW_DWN** - Solar Radiation (MJ/m²/hr)
5. **PS** - Pressure (kPa)

**Scripts:** `scripts/downloading_data/download_*.py`

**Output:** JSON files in `data/raw/{city}_data/`

---

### Phase 2: Data Processing
You merged and cleaned the data:

1. **Merge:** Combined all 5 parameters into single CSV per city
2. **Clean:** Removed fill values (-999), applied scientific range checks

**Scripts:** 
- `scripts/merge_hourly_city_data.py`
- `scripts/clean_hourly_merged.py`

**Output:** `data/processed/{city}_hourly_clean.csv`

---

### Phase 3: ETo Calculation
You calculated hourly ETo using FAO-56 Penman-Monteith equation:

**Script:** `scripts/claculation_ETo/calc_ETo_corrected.py`

**Key Physics:**
- Calculated vapor pressure terms (es, ea, delta, gamma)
- Computed net radiation (Rn = Rns - Rnl)
- Handled day/night differences in soil heat flux (G)
- Applied FAO-56 hourly equation

**Output:** `ET0_new/{city}_hourly_ETo.csv`

**Result:** ~219,000 hourly ETo values per city (25 years × 8760 hours)

---

### Phase 4: Machine Learning Analysis
You built XGBoost models to learn the physics:

**Script:** `scripts/ml_shap/01_prepare_dataset.py`
- Filtered to daytime only (ETo > 0) → ~215,000 rows per city
- Created temporal features (month, hour, season)

**Script:** `scripts/ml_shap/02_train_xgboost.py`
- Trained separate model per city
- Used TimeSeriesSplit (5-fold) to prevent data leakage
- Achieved R² > 0.998, NSE > 0.998, Bias ≈ 0

**Why This Matters:**
- The ML model became a perfect mathematical surrogate for FAO-56
- This means SHAP interpretations reflect actual physics, not model errors

---

### Phase 5: SHAP Interpretability
You used SHAP to decompose predictions:

**Script:** `scripts/ml_shap/03_shap_analysis.py`
- Sampled 20,000 rows per city (stratified by month)
- Calculated TreeSHAP values
- Generated 4 types of plots per city:
  1. Summary plot (global importance)
  2. Dependence plots (feature interactions)
  3. Monthly heatmap (temporal shifts)
  4. Seasonal boxplots (regime changes)

**Key Findings:**
- Solar Radiation (Rs) is universally dominant (~0.18 mm/hr contribution)
- Low humidity increases ETo (dry air evaporates faster)
- Wind speed importance varies geographically (higher in Jaisalmer)
- Summer = radiation-dominated, Monsoon = humidity-modulated

---

### Phase 6: Cross-City Analysis
You compared all 4 cities:

**Script:** `scripts/ml_shap/04_cross_city_analysis.py`
- Predicted vs Observed scatter plots (all hug 1:1 line)
- Bias distribution (centered at 0, narrow spread)
- Cross-city SHAP importance comparison

**Script:** `scripts/ml_shap/05_results_summary.py`
- Exported paper-ready tables for manuscript

---

## Current Status

**Completed:**
- ✅ NASA data download (2001-2025)
- ✅ Data cleaning and processing
- ✅ Hourly ETo calculation (FAO-56)
- ✅ ML model training (XGBoost)
- ✅ SHAP analysis and interpretation
- ✅ Cross-city comparison
- ✅ Results documentation

**New Requirement:**
- 🔄 Mentor wants you to replicate the entire analysis using **IMD data** instead of NASA data

---

## What You Need to Do Now

### Step 1: Request IMD Data
Use the document `notes/IMD_DATA_REQUEST.md` to request:
- Same 5 parameters (T, RH, WS, Rs, P)
- Same time period (2001-2025)
- Same cities (Barmer, Bikaner, Jaisalmer, Jodhpur)
- **Critical:** Hourly resolution (daily is insufficient)

### Step 2: Once IMD Data Arrives
You'll need to:
1. Check data format and convert to match your existing structure
2. Handle any missing data or quality flags
3. Ensure units match NASA data (or convert)
4. Run the same processing pipeline:
   - Merge parameters
   - Clean data
   - Calculate ETo
   - Train ML models
   - Run SHAP analysis

### Step 3: Compare Results
Compare NASA-based vs IMD-based results:
- Are ETo values similar?
- Do ML models perform similarly?
- Do SHAP interpretations match?
- Document any differences (ground observations vs satellite)

---

## Key Files Reference

### Data Files
- `data/raw/{city}_data/` - Original NASA JSON files
- `data/processed/{city}_hourly_clean.csv` - Cleaned merged data
- `ET0_new/{city}_hourly_ETo.csv` - Final ETo calculations

### Analysis Scripts
- `scripts/downloading_data/` - NASA download scripts (reference for IMD format)
- `scripts/claculation_ETo/calc_ETo_corrected.py` - ETo calculation
- `scripts/ml_shap/` - ML and SHAP analysis pipeline

### Documentation
- `notes/PROJECT_OVERVIEW.md` - Detailed workflow
- `notes/FINAL_EXPLANATION.md` - Complete research explanation
- `notes/IMD_DATA_REQUEST.md` - IMD data request (NEW)
- `notes/PROJECT_REFRESH_SUMMARY.md` - This file (NEW)

---

## Important Technical Details

### Why Hourly Data?
- ETo varies dramatically day vs night
- Solar radiation is zero at night
- Wind and humidity effects differ diurnally
- SHAP needs hourly granularity for temporal analysis
- Your ML models were trained on ~215,000 hourly points

### Why 5 Parameters?
All are required for FAO-56 equation:
- **Temperature**: Vapor pressure deficit
- **Humidity**: Actual vapor pressure
- **Wind**: Aerodynamic resistance
- **Radiation**: Energy available for evaporation
- **Pressure**: Psychrometric constant

### Why Separate Models per City?
- Microclimates differ across the Thar Desert
- Jaisalmer (deep desert) vs Jodhpur (semi-arid edge)
- SHAP detected geographic differences in wind importance

---

## Next Actions

1. **Review** `notes/IMD_DATA_REQUEST.md` and customize with your contact details
2. **Send** the request to IMD with proper institutional authorization
3. **Wait** for data delivery (may take time)
4. **Plan** data format conversion (IMD format likely differs from NASA)
5. **Replicate** the entire pipeline with IMD data
6. **Compare** NASA vs IMD results in your analysis

---

## Quick Reference: File Locations

```
c:\Reasearch paper\
├── data/
│   ├── raw/              # NASA JSON files
│   └── processed/        # Cleaned CSV files
├── ET0_new/              # ETo calculation results
├── scripts/
│   ├── downloading_data/ # NASA download scripts
│   ├── claculation_ETo/  # ETo calculation
│   └── ml_shap/          # ML and SHAP analysis
├── notes/
│   ├── PROJECT_OVERVIEW.md
│   ├── FINAL_EXPLANATION.md
│   ├── IMD_DATA_REQUEST.md        # NEW - Use this for IMD
│   └── PROJECT_REFRESH_SUMMARY.md # NEW - This file
└── results/              # SHAP plots and analysis outputs
```

---

## Mentor Talking Points

When discussing with your mentor:

**What You Accomplished:**
- "I calculated 25 years of hourly FAO-56 ETo for 4 Rajasthan cities using NASA data"
- "I trained XGBoost models that achieved R² > 0.998, proving they perfectly learned the physics"
- "I used SHAP to quantify that solar radiation is the primary driver, with wind and humidity as secondary modulators"
- "I showed how these drivers shift seasonally from summer to monsoon"

**Current Task:**
- "I'm now requesting the same meteorological data from IMD to validate and replicate the analysis with ground observations"
- "I need hourly data for the same 5 parameters, same cities, same time period"
- "Once I receive IMD data, I'll run the identical pipeline and compare results"

**Scientific Value:**
- "This will validate whether satellite-derived (NASA) vs ground-based (IMD) data produce consistent ETO estimates"
- "The comparison will be valuable for understanding uncertainties in evapotranspiration modeling"
- "Results will inform water resource management in arid Rajasthan"
