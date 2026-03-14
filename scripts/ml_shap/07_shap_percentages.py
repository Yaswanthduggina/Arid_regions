"""
Script 07 — Generate SHAP Percentage Contributions
Calculates the relative percentage importance of each feature 
per month and season based on mean absolute SHAP values.
"""
import pandas as pd
import numpy as np
import os

# ─── Config ───────────────────────────────────────────────────────────
CITIES    = ["barmer", "bikaner", "jaisalmer", "jodhpur"]
SHAP_DIR  = os.path.join("results_1", "shap")
RES_DIR   = os.path.join("results_1", "shap")

FEATURES  = ["T", "RH", "WS", "Rs", "P"]
MONTH_NAMES = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}
SEASON_ORDER  = ["Summer", "Monsoon", "Post-Monsoon", "Winter"]

all_percentages_df = []
text_report_lines = []
text_report_lines.append("XGBoost SHAP Percentage Contributions")
text_report_lines.append("=====================================")
text_report_lines.append("Formula: Percentage(F) = |SHAP(F)| / sum(|SHAP(all_features)|) * 100\n")

for city in CITIES:
    print(f"\n── Processing Percentages for: {city.upper()} ──")
    shap_path = os.path.join(SHAP_DIR, f"{city}_shap_values.csv")
    
    if not os.path.exists(shap_path):
        print(f"   [SKIP] SHAP values missing for {city}")
        continue
        
    # Read the SHAP values directly. They are in mm/hr unit.
    shap_df = pd.read_csv(shap_path, index_col=0) 
    
    # Calculate Mean Absolute SHAP values (which measures total impact magnitude)
    def calc_abs_mean(x): return x.abs().mean()
    season_abs_means = shap_df.groupby("season")[FEATURES].apply(calc_abs_mean)
    month_abs_means = shap_df.groupby("month")[FEATURES].apply(calc_abs_mean)
    
    text_report_lines.append(f"--- City: {city.upper()} ---")
    
    # Process Seasons
    text_report_lines.append("\n[Seasonal % Contribution]")
    for season in SEASON_ORDER:
        if season not in season_abs_means.index:
            continue
        vals = season_abs_means.loc[season]
        total_shap = vals.sum()
        pcts = (vals / total_shap) * 100
        
        row_dict = {
            "City": city.capitalize(),
            "Period_Type": "Season",
            "Period": season
        }
        for f in FEATURES: row_dict[f"{f}_%"] = pcts[f]
        all_percentages_df.append(row_dict)
        
        eq_str = f"{season:12s} | " + "  ".join([f"{f}: {pcts[f]:5.1f}%" for f in FEATURES])
        text_report_lines.append(eq_str)
        
    # Process Months
    text_report_lines.append("\n[Monthly % Contribution]")
    for m in range(1, 13):
        if m not in month_abs_means.index:
            continue
        vals = month_abs_means.loc[m]
        total_shap = vals.sum()
        pcts = (vals / total_shap) * 100
        month_name = MONTH_NAMES[m]
        
        row_dict = {
            "City": city.capitalize(),
            "Period_Type": "Month",
            "Period": month_name,
        }
        for f in FEATURES: row_dict[f"{f}_%"] = pcts[f]
        all_percentages_df.append(row_dict)
        
        eq_str = f"{month_name:12s} | " + "  ".join([f"{f}: {pcts[f]:5.1f}%" for f in FEATURES])
        text_report_lines.append(eq_str)

    text_report_lines.append("\n")

# Save outputs
df_out = pd.DataFrame(all_percentages_df)
csv_out_path = os.path.join(RES_DIR, "seasonal_monthly_percentages.csv")
df_out.to_csv(csv_out_path, index=False)
print(f"✔ Saved tabular data to {csv_out_path}")

txt_out_path = os.path.join(RES_DIR, "percentage_contributions_report.txt")
with open(txt_out_path, "w") as fh:
    fh.write("\n".join(text_report_lines))
print(f"✔ Saved text report to {txt_out_path}")
print("✅ Done!")
