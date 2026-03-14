# Sensitivity Analysis of ETo Predictors (XGBoost)

## Background
To understand the robustness and physical validity of the XGBoost machine learning model predicting Evapotranspiration (ETo), a Local Sensitivity Analysis was performed. This determines how fluctuations in each meteorological input variable individually impact the final ETo prediction for each of the four study locations in Rajasthan.

## Methodology
The sensitivity analysis systematically perturbs a single feature while holding all other variables at their historically observed values.
- **Base State**: Features ($T, RH, WS, Rs, P$) fed into the model to predict a Baseline ETo.
- **Perturbations ($\Delta x$)**: $\{-20\%, -10\%, -5\%, 0\%, +5\%, +10\%, +20\%\}$
- **Evaluation**: For each perturbation step on a feature $X$, the modified dataset is evaluated by the model. The output change is calculated as:
  $$ \Delta ETo (\%) = \frac{ETo_{perturbed} - ETo_{baseline}}{ETo_{baseline}} \times 100 $$

This procedure maps how the machine learning model responds globally to simulated environmental changes. 

## Importance for Physical Validity
Unlike linear models with static coefficients, XGBoost captures complex, non-linear interactions (e.g., high temperature combined with low humidity and high wind exacerbates ETo).
The sensitivity analysis proves that the "black-box" model has successfully learned the correct thermodynamic relationships dictated by the FAO-56 Penman-Monteith equation:
1. **Solar Radiation (Rs)**: Should exhibit a strong, direct positive correlation with ETo.
2. **Temperature (T)**: Should exhibit a moderate to strong positive correlation.
3. **Relative Humidity (RH)**: Should exhibit an inverse (negative) relationship; as humidity increases, the demand for atmospheric evaporation decreases.
4. **Wind Speed (WS)**: Should exhibit a positive correlation (removes saturated air allowing continuous evaporation).
5. **Atmospheric Pressure (P)**: Should exert minimal influence on the final result.

The results, documented numerically in `results/sensitivity/sensitivity_results.csv` and visually in the `results/sensitivity/{city}_sensitivity_curve.png` plots, demonstrate these relationships. For instance, the upward slope of the $Rs$ (orange) line and the downward slope of the $RH$ (blue) line visually confirm the model's physical accuracy without the need to calculate SHAP feature attributions on a per-sample basis. This method helps quickly communicate the driving parameters to researchers in a highly interpretable format.





The Baseline_ETo (which is 0.2852 mm/hr for Barmer in your example) is the average predicted Evapotranspiration for the original, unmodified historical data.

Here is exactly where it comes from and how it is calculated in the 

08_sensitivity_analysis.py
 script:

1. Where it comes from
In the script, right before we start changing variables by -20% or +10%, we do this:

Load the Original Data: We load the entire dataset for Barmer exactly as it was measured originally (the unaltered Temperature, Humidity, Wind Speed, Solar Radiation, and Pressure).
Make Predictions: We pass this unaltered data into your trained XGBoost model and ask it to predict the Evapotranspiration (ETo) for every single hour in the dataset.
Calculate the Average: We take the average (mean) of all those thousands of hourly ETo predictions.
For Barmer, the average ETo prediction of the original data is 0.2852 mm/hr. This becomes our "Baseline".

2. Why we need it
To measure "Sensitivity" (how much a variable affects the output), we need a starting point to compare against.

In your table:

Baseline_ETo (0.2852): What the model predicts normally.
New_ETo (0.3034): What the model predicts when we artificially force the Temperature (T) to be 10.0% hotter.
Change_% (6.38%): Because 0.3034 is roughly 6.38% larger than the baseline 0.2852, we conclude that a 10% rise in temperature causes a 6.38% rise in ETo.
If we didn't calculate the Baseline_ETo from the original data first, we wouldn't have any number to compare the "New_ETo" against to find the percentage change! You can confidently explain in your paper that the baseline represents the historical mean prediction of the model before any artificial perturbations were introduced.