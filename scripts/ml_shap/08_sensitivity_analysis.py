"""
Script 08 — Sensitivity Analysis
Perturbs each feature by a percentage to observe the resulting percentage change in ETo predictions.
Outputs results to results/sensitivity/.
"""
import pandas as pd
import numpy as np
import os
import joblib
import matplotlib.pyplot as plt

# ─── Config ───────────────────────────────────────────────────────────
CITIES = ["barmer", "bikaner", "jaisalmer", "jodhpur"]
IN_DIR = os.path.join("results_1", "ml_input")
MDL_DIR = os.path.join("results_1", "models")
OUT_DIR = os.path.join("results_1", "sensitivity")
os.makedirs(OUT_DIR, exist_ok=True)

FEATURES = ["T", "RH", "WS", "Rs", "P"]
TARGET = "ETo_mm_hr"
PERTURBATIONS = [-0.20, -0.10, -0.05, 0.0, 0.05, 0.10, 0.20]

# Feature colors for plotting
COLORS = {
    "T": "#d62728",    # Red
    "RH": "#1f77b4",   # Blue
    "WS": "#9467bd",   # Purple
    "Rs": "#ff7f0e",   # Orange
    "P": "#7f7f7f"     # Grey
}

all_results = []

for city in CITIES:
    src = os.path.join(IN_DIR, f"{city}_ml_ready.csv")
    mdl_path = os.path.join(MDL_DIR, f"{city}_xgb_model.joblib")
    
    if not os.path.exists(src) or not os.path.exists(mdl_path):
        print(f"[SKIP] {city}: Missing data or model.")
        continue

    # Load data and model
    df = pd.read_csv(src)
    X_base = df[FEATURES].copy()
    model = joblib.load(mdl_path)

    # Baseline prediction
    y_base = model.predict(X_base)
    base_eto_mean = np.mean(y_base)
    print(f"\n── {city.upper()} ── Base ETo: {base_eto_mean:.4f} mm/hr")

    city_results = []

    for feature in FEATURES:
        for p in PERTURBATIONS:
            if p == 0.0:
                # No perturbation, zero change
                city_results.append({
                    "City": city,
                    "Feature": feature,
                    "Perturbation_%": 0,
                    "Baseline_ETo": base_eto_mean,
                    "New_ETo": base_eto_mean,
                    "Change_%": 0.0
                })
                continue

            # Copy base data and perturb the target feature
            X_pert = X_base.copy()
            # Apply percentage multiplier: (1 + P)
            X_pert[feature] = X_pert[feature] * (1.0 + p)

            # Predict new ETo
            y_pert = model.predict(X_pert)
            new_eto_mean = np.mean(y_pert)

            # Calculate % change in ETo output
            change_pct = ((new_eto_mean - base_eto_mean) / base_eto_mean) * 100

            city_results.append({
                "City": city,
                "Feature": feature,
                "Perturbation_%": p * 100,
                "Baseline_ETo": round(base_eto_mean, 4),
                "New_ETo": round(new_eto_mean, 4),
                "Change_%": round(change_pct, 4)
            })

    df_res = pd.DataFrame(city_results)
    all_results.append(df_res)
    
    # ── Plotting ──────────────────────────────────────────────────────
    plt.figure(figsize=(10, 6))
    
    for feature in FEATURES:
        # Filter data for this feature
        f_data = df_res[df_res["Feature"] == feature]
        plt.plot(
            f_data["Perturbation_%"], 
            f_data["Change_%"], 
            marker='o', 
            linewidth=2, 
            label=feature, 
            color=COLORS.get(feature, 'black')
        )

    plt.axhline(0, color='black', linestyle='--', alpha=0.5)
    plt.axvline(0, color='black', linestyle='--', alpha=0.5)
    
    plt.title(f"Sensitivity Analysis - {city.capitalize()}", fontsize=16)
    plt.xlabel("Input Perturbation (%)", fontsize=14)
    plt.ylabel("Output ETo Change (%)", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend(title="Feature", fontsize=12, title_fontsize=12)
    plt.tight_layout()
    
    plot_path = os.path.join(OUT_DIR, f"{city}_sensitivity_curve.png")
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"   ✔ Plot saved → {plot_path}")

# Combine results and save
if all_results:
    final_df = pd.concat(all_results, ignore_index=True)
    summary_path = os.path.join(OUT_DIR, "sensitivity_results.csv")
    final_df.to_csv(summary_path, index=False)
    print(f"\n✅ Numerical results saved → {summary_path}")
