"""
Script 05 — Results Summary
Consolidates all result CSVs into clean, paper-ready formatted tables
and saves to results/paper_tables/.
"""
import pandas as pd
import numpy as np
import os

OUT_DIR = os.path.join("results", "paper_tables")
os.makedirs(OUT_DIR, exist_ok=True)

CITIES = ["barmer", "bikaner", "jaisalmer", "jodhpur"]

# ─── Table 1: Model Performance Metrics ───────────────────────────────
metrics_path = os.path.join("results", "metrics_all_cities.csv")
if os.path.exists(metrics_path):
    metrics = pd.read_csv(metrics_path)
    metrics.columns = [c.strip() for c in metrics.columns]
    # Rename columns for paper
    metrics_paper = metrics.rename(columns={"city": "City"})
    metrics_paper["City"] = metrics_paper["City"].str.capitalize()
    metrics_paper.to_csv(os.path.join(OUT_DIR, "table1_model_performance.csv"), index=False)
    print("Table 1 — Model Performance Metrics")
    print(metrics_paper.to_string(index=False))
    print()

# ─── Table 2: Cross-City SHAP Feature Importance ──────────────────────
shap_path = os.path.join("results", "shap", "cross_city_mean_shap.csv")
if os.path.exists(shap_path):
    shap_imp = pd.read_csv(shap_path, index_col="city")
    shap_imp.index = shap_imp.index.str.capitalize()
    shap_imp.index.name = "City"
    shap_imp = shap_imp.round(4)
    shap_imp.columns = ["Temp (T)", "Humidity (RH)", "Wind (WS)", "Radiation (Rs)", "Pressure (P)"]

    # Add dominant feature column
    shap_imp["Dominant Feature"] = shap_imp.iloc[:, :5].idxmax(axis=1)
    shap_imp.to_csv(os.path.join(OUT_DIR, "table2_shap_importance.csv"))
    print("Table 2 — Cross-City SHAP Feature Importance")
    print(shap_imp.to_string())
    print()

# ─── Table 3: Seasonal SHAP Summary (per city) ────────────────────────
SEASON_ORDER = ["Summer", "Monsoon", "Post-Monsoon", "Winter"]
FEATURES     = ["T", "RH", "WS", "Rs", "P"]
seasonal_rows = []

for city in CITIES:
    shap_csv = os.path.join("results", "shap", f"{city}_shap_values.csv")
    if not os.path.exists(shap_csv):
        continue
    shap_df = pd.read_csv(shap_csv)
    if "season" not in shap_df.columns:
        continue
    for season in SEASON_ORDER:
        sub = shap_df[shap_df["season"] == season][FEATURES]
        mean_abs = sub.abs().mean()
        dominant = mean_abs.idxmax()
        row = {"City": city.capitalize(), "Season": season,
               "Dominant": dominant, "Dom_SHAP": round(mean_abs[dominant], 4)}
        for f in FEATURES:
            row[f"SHAP_{f}"] = round(mean_abs.get(f, np.nan), 4)
        seasonal_rows.append(row)

if seasonal_rows:
    seasonal_df = pd.DataFrame(seasonal_rows)
    seasonal_df.to_csv(os.path.join(OUT_DIR, "table3_seasonal_shap.csv"), index=False)
    print("Table 3 — Seasonal SHAP Summary")
    print(seasonal_df.to_string(index=False))
    print()

# ─── Table 4: Dataset Summary ──────────────────────────────────────────
ds_path = os.path.join("results", "ml_input", "dataset_summary.csv")
if os.path.exists(ds_path):
    ds = pd.read_csv(ds_path)
    ds["city"] = ds["city"].str.capitalize()
    ds.rename(columns={"city": "City", "n_rows": "N (daytime hours)",
                        "eto_mean_mm_hr": "ETo Mean (mm/hr)",
                        "eto_max_mm_hr":  "ETo Max (mm/hr)"}, inplace=True)
    ds.to_csv(os.path.join(OUT_DIR, "table4_dataset_summary.csv"), index=False)
    print("Table 4 — Dataset Summary")
    print(ds.to_string(index=False))

print(f"\n✅ All paper tables saved → {OUT_DIR}")
