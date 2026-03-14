"""
Script 06 — Generate SHAP Additive Equations
Reads SHAP values and XGBoost base values to generate additive equations
for ETo per month and season, providing interpretable physical formulas.
"""
import pandas as pd
import numpy as np
import os
import joblib
import shap

# ─── Config ───────────────────────────────────────────────────────────
CITIES    = ["barmer", "bikaner", "jaisalmer", "jodhpur"]
MDL_DIR   = os.path.join("results_1", "models")
SHAP_DIR  = os.path.join("results_1", "shap")
RES_DIR   = os.path.join("results_1", "shap")
os.makedirs(RES_DIR, exist_ok=True)

FEATURES  = ["T", "RH", "WS", "Rs", "P"]
MONTH_NAMES = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}
SEASON_ORDER  = ["Summer", "Monsoon", "Post-Monsoon", "Winter"]

all_equations_df = []
text_report_lines = []
text_report_lines.append("XGBoost SHAP Additive Contribution Equations")
text_report_lines.append("============================================")
text_report_lines.append("Formula: ETo = Base_Value + SHAP(T) + SHAP(RH) + SHAP(WS) + SHAP(Rs) + SHAP(P)\n")

for city in CITIES:
    print(f"\n── Processing Equations for: {city.upper()} ──")
    
    # Paths
    mdl_path = os.path.join(MDL_DIR, f"{city}_xgb_model.joblib")
    shap_path = os.path.join(SHAP_DIR, f"{city}_shap_values.csv")
    
    if not os.path.exists(mdl_path) or not os.path.exists(shap_path):
        print(f"   [SKIP] Model or SHAP values missing for {city}")
        continue
        
    # Load model to get base value
    model = joblib.load(mdl_path)
    explainer = shap.TreeExplainer(model)
    base_value = explainer.expected_value
    # expected_value can sometimes be a single-element array
    base_value = float(np.atleast_1d(base_value)[0])
    
    # Load SHAP values
    shap_df = pd.read_csv(shap_path, index_col=0) # index is datetime
    
    # Calculate Season Averages
    season_means = shap_df.groupby("season")[FEATURES].mean()
    
    # Calculate Month Averages
    month_means = shap_df.groupby("month")[FEATURES].mean()
    
    text_report_lines.append(f"--- City: {city.upper()} ---")
    
    # Process Seasons
    text_report_lines.append("\n[Seasonal Equations]")
    for season in SEASON_ORDER:
        if season not in season_means.index:
            continue
        vals = season_means.loc[season]
        
        row_dict = {
            "City": city.capitalize(),
            "Period_Type": "Season",
            "Period": season,
            "Base_Value": base_value
        }
        for f in FEATURES: row_dict[f"{f}_SHAP"] = vals[f]
        all_equations_df.append(row_dict)
        
        # Build string equation
        eq_str = f"ETo({season:12s}) = {base_value:6.3f} (Base)"
        for f in FEATURES:
            sign = "+" if vals[f] >= 0 else "-"
            eq_str += f"  {sign} {abs(vals[f]):5.3f} ({f:2s})"
        text_report_lines.append(eq_str)
        
    # Process Months
    text_report_lines.append("\n[Monthly Equations]")
    for m in range(1, 13):
        if m not in month_means.index:
            continue
        vals = month_means.loc[m]
        month_name = MONTH_NAMES[m]
        
        row_dict = {
            "City": city.capitalize(),
            "Period_Type": "Month",
            "Period": month_name,
            "Base_Value": base_value
        }
        for f in FEATURES: row_dict[f"{f}_SHAP"] = vals[f]
        all_equations_df.append(row_dict)
        
        # Build string equation
        eq_str = f"ETo({month_name:12s}) = {base_value:6.3f} (Base)"
        for f in FEATURES:
            sign = "+" if vals[f] >= 0 else "-"
            eq_str += f"  {sign} {abs(vals[f]):5.3f} ({f:2s})"
        text_report_lines.append(eq_str)
        
    text_report_lines.append("\n")

# Save outputs
df_out = pd.DataFrame(all_equations_df)
csv_out_path = os.path.join(RES_DIR, "seasonal_monthly_equations.csv")
df_out.to_csv(csv_out_path, index=False)
print(f"✔ Saved tabular data to {csv_out_path}")

txt_out_path = os.path.join(RES_DIR, "additive_equations_report.txt")
with open(txt_out_path, "w") as fh:
    fh.write("\n".join(text_report_lines))
print(f"✔ Saved text report to {txt_out_path}")
print("✅ Done!")
#Saved tabular data to results_1\shap\seasonal_monthly_percentages.csv
#✔ Saved text report to results_1\shap\percentage_contributions_report.txt