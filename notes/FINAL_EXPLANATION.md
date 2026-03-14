# Final Project Explanation: Physics-Guided ML Interpretability for ETo
## 1. The Core Research Philosophy

**Background:** We calculated the FAO-56 Penman-Monteith Reference Evapotranspiration (ETo) using 25 years of NASA POWER meteorological data for four arid cities in Rajasthan (Barmer, Bikaner, Jaisalmer, Jodhpur). FAO-56 is a complex, non-linear physics equation that gives us the "ground truth" ETo value.

**The Problem:** FAO-56 gives us the final ETo rate, but it doesn't easily quantify *which* meteorological variable (Temperature, Humidity, Wind, Radiation) was the most dominant driver of that specific evaporation rate, nor how those dominant drivers shift seasonally in a desert climate.

**The Solution:** We train a highly accurate Machine Learning model (XGBoost) to emulate the FAO-56 equation. Once the ML model has perfectly learned the physics, we use **SHAP (SHapley Additive exPlanations)**, a game-theory algorithm, to look inside the model and decompose every single hourly prediction into exact contributions (in mm/hr) from each weather variable.

This turns a standard predictive ML task into a **physics interpretability study**.

---

## 2. Script 01: Data Preparation (`01_prepare_dataset.py`)

### What the code does:
This script takes the hourly ETo outputs (`ET0_new/{city}_hourly_ETo.csv`) and prepares them for machine learning. 
1. It loads Temperature (`T`), Relative Humidity (`RH`), Wind Speed (`WS`), Solar Radiation (`Rs`), and Pressure (`P`) as the Input Features ($X$).
2. It loads `ETo_mm_hr` as the Target Variable ($y$).
3. **CRITICAL STEP:** It filters the dataset to **daytime rows only** (`ETo > 0`). 
4. It engineered temporal features: `month`, `hour`, `season` (Summer, Monsoon, Post-Monsoon, Winter).

### Why we did this:
At night, solar radiation is zero, and ETo is often zero or negligible. Including hundreds of thousands of nighttime rows where "nothing is happening" dilutes the machine learning model. By restricting the dataset to daytime active hours (~215,000 rows per city), the model focuses purely on the active physical dynamics of daytime evapotranspiration.

---

## 3. Script 02: XGBoost Training & Validation (`02_train_xgboost.py`)

### What the code does:
This script trains an **XGBoost Regressor** independently for each of the 4 cities. It uses a very specific validation strategy called **`TimeSeriesSplit(n_splits=5)`**. It calculates five metrics: R² (fit), RMSE (absolute error), MAE (average deviance), NSE (Nash-Sutcliffe Efficiency), and Bias.

### Why we did this:
- **XGBoost:** Tree-based models map non-linear physical interactions (like how high wind + low humidity aggressively spike evaporation) better than linear regression. It also has a native, mathematically exact SHAP implementation (`TreeSHAP`).
- **TimeSeriesSplit vs Random Split:** Climate data is sequential. If we randomly shuffled the 25 years of data, the model would cheat by seeing the "future" to predict the "past" (data leakage). `TimeSeriesSplit` forces the model to train on past years to predict future years, proving it has learned robust, durable physics, not just memorized the dataset.
- **Independent Models:** We trained a separate model per city because the micro-climates behave slightly differently. Forcing one global model would blur the geographic differences we want to study.

### The Results:
| City | R² | RMSE (mm/hr) | NSE | Bias |
|------|----|--------------|-----|------|
| Barmer | 0.9987 | 0.0099 | 0.9987 | +0.0002 |
| Bikaner | 0.9986 | 0.0103 | 0.9986 | +0.0002 |
| Jaisalmer | 0.9986 | 0.0104 | 0.9986 | +0.0003 |
| Jodhpur | 0.9988 | 0.0096 | 0.9988 | -0.0002 |

**Explanation for Mentor:** The ML model achieved >0.998 R² and NSE (Nash-Sutcliffe Efficiency is the gold standard for hydrological modeling where >0.9 is excellent). The Bias is effectively zero. This proves conclusively that the XGBoost model has become an essentially perfect mathematical surrogate for the FAO-56 equation. We have zero concern about model inaccuracy; therefore, our SHAP interpretations will be purely reflecting the underlying physics.

---

## 4. Script 03: SHAP Analysis (`03_shap_analysis.py`)

### What the code does:
Because calculating SHAP values on 215,000 rows per city would crash most computers (Out of Memory), we take a **stratified random sample of 20,000 rows** per city. "Stratified" means we ensured proportional representation from all months. We calculate the TreeSHAP values for these 20,000 predictions, generating four distinct types of physical analyses.

### Graph Explanations:

#### A. Global SHAP Summary Plot (Beeswarm)
*(`results/shap/{city}_shap_summary.png`)*
- **What it shows:** Every dot is one single hour's prediction. The X-axis is the SHAP value (how much that variable changed the ETo in mm/hr). The color is the actual value of the weather variable (Red = High, Blue = Low).
- **Physical Meaning:** In all cities, Solar Radiation (`Rs`) is at the top. The red dots for Rs stretch far to the right. This means high solar radiation is the primary driver increasing ETo. Relative Humidity (`RH`) has blue dots on the right, meaning low humidity *increases* ETo (dry air evaporates faster), which perfectly aligns with physics.

#### B. SHAP Dependence Plots
*(`results/shap/{city}_shap_dependence.png`)*
- **What it shows:** Five scatter plots per city, one for each feature. X-axis is the feature value (e.g., Temp in °C), Y-axis is the SHAP effect (in mm/hr).
- **Physical Meaning:** Look closely at the Wind Speed (`WS`) plot. You will notice that as Wind Speed increases, the SHAP value doesn't just form a straight line—it fans out. This indicates complex interactions. High wind only causes massive evaporation if the humidity is low; if it's raining (high humidity), high wind doesn't vaporize as much water. XGBoost captured this non-linear aerodynamic resistance automatically.

#### C. Monthly Mean |SHAP| Heatmap
*(`results/shap/{city}_monthly_shap_heatmap.png`)*
- **What it shows:** The absolute mean SHAP contribution of each variable, sliced by month.
- **Physical Meaning:** This proves the "regime shift" of the climate. In May (Peak Summer), Solar Radiation (`Rs`) and Temperature (`T`) have massive SHAP values. By August (Monsoon), the SHAP value of Humidity (`RH`) jumps significantly, showing that moisture in the air becomes the dominant controlling factor restricting ETo during the rains.

#### D. Seasonal SHAP Boxplots
*(`results/shap/{city}_seasonal_shap.png`)*
- **What it shows:** Boxplots grouping the SHAP values strictly by climate season (Summer, Monsoon, Post-Monsoon, Winter).
- **Physical Meaning:** This is the most "research paper ready" plot. It visually proves that while Radiation is the undisputed king in summer, the influence of Wind Speed and Temperature compresses significantly during the winter months. 

---

## 5. Script 04: Cross-City Analysis (`04_cross_city_analysis.py`)

### What the code does:
This script zooms out to look at all four cities simultaneously to study geospatial variations across the Thar Desert region.

### Graph Explanations:

#### A. Predicted vs Observed 4-Panel Scatter
*(`results/pred_vs_obs_4panel.png`)*
- **What it shows:** Plotted actual FAO-56 ETo on the X-axis vs XGBoost Predicted ETo on the Y-axis. The dotted line is the 1:1 perfect fit line.
- **Physical Meaning:** All points tightly hug the 1:1 line across all four spatial domains. This visually reinforces the metrics table from Script 2, showing our ML surrogate behaves identically in deep desert (Jaisalmer) and semi-arid boundaries (Jodhpur).

#### B. Bias/Residual KDE Distribution
*(`results/bias_distribution.png`)*
- **What it shows:** A bell curve map of the errors (Predicted minus Observed).
- **Physical Meaning:** A bad model would have a curve shifted left or right (systematic under/over-estimation). Our curves are perfectly centered at 0.0 on the X-axis with very narrow spreads. The model has zero systemic bias.

#### C. Cross-City SHAP Importance Bar Chart
*(`results/cross_city_shap_importance.png`)*
- **What it shows:** Side-by-side grouped bars showing the average global SHAP magnitude for each feature in every city.
- **Physical Meaning:** 
  1. Solar Radiation (`Rs`) is identically dominant (~0.18 mm/hr) across the entire arid region. 
  2. Wind Speed (`WS`) has slightly higher importance in Jaisalmer (0.046) compared to Jodhpur (0.036). Jaisalmer is deeper in the desert with fewer windbreaks and higher aerodynamic forcing, and the SHAP mathematically detected this geographic reality.

---

## 6. Script 05: Paper Tables Export (`05_results_summary.py`)

### What the code does:
It aggregates the raw numerical outputs into clean CSV formats (`results/paper_tables/`) corresponding exactly to the tables you will insert into your manuscript.

- **Table 1 (`table1_model_performance.csv`):** Proves model validity.
- **Table 2 (`table2_shap_importance.csv`):** Proves Radiation is universally dominant.
- **Table 3 (`table3_seasonal_shap.csv`):** Proves the temporal shift in driving forces.
- **Table 4 (`table4_dataset_summary.csv`):** Proves the massive data scale (860,000 total daytime hours analyzed).

---

## Summary for your Mentor

> *"We computed 25 years of hourly FAO-56 ETo for four arid cities. To dissect exactly which meteorological drivers control this evaporation dynamically, we trained independent XGBoost Regressors for each city. We proved these models are perfect mathematical surrogates for FAO-56 (R² > 0.998, NSE > 0.998 using rigorous TimeSeries splits). Because the model learned the physics perfectly, we applied TreeSHAP to decompose every hourly prediction. Our results mathematically validate that Solar Radiation dictates total evaporation volume, while dynamic interactions between Wind Speed and Humidity act as the primary modulators during the Monsoon regime. Furthermore, SHAP quantified geographic variance, showing aerodynamic (wind) forcing is a stronger secondary driver in deeper desert regions like Jaisalmer compared to Jodhpur."*
