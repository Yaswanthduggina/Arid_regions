"""
Script 04 — Cross-City Comparison & Bias Analysis
- 4-panel Predicted vs Observed scatter
- Metrics comparison table (all cities)
- Residual/Bias distribution
- Cross-city SHAP importance bar chart
"""
import pandas as pd
import numpy as np
import os
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

# ─── Config ───────────────────────────────────────────────────────────
CITIES    = ["barmer", "bikaner", "jaisalmer", "jodhpur"]
IN_DIR    = os.path.join("results", "ml_input")
MDL_DIR   = os.path.join("results", "models")
SHAP_DIR  = os.path.join("results", "shap")
RES_DIR   = "results"

FEATURES  = ["T", "RH", "WS", "Rs", "P"]
TARGET    = "ETo_mm_hr"
CITY_COLORS = {
    "barmer":    "#e74c3c",
    "bikaner":   "#3498db",
    "jaisalmer": "#f39c12",
    "jodhpur":   "#2ecc71",
}

plt.rcParams.update({
    "figure.dpi": 150,
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

def nse(obs, sim):
    return 1 - np.sum((obs - sim)**2) / np.sum((obs - obs.mean())**2)

# ─── Load predictions for all cities ──────────────────────────────────
city_data = {}
metrics_rows = []

for city in CITIES:
    src = os.path.join(IN_DIR, f"{city}_ml_ready.csv")
    mdl = os.path.join(MDL_DIR, f"{city}_xgb_model.joblib")
    if not os.path.exists(src) or not os.path.exists(mdl):
        print(f"[SKIP] {city}: missing files")
        continue

    df    = pd.read_csv(src, parse_dates=["datetime"])
    model = joblib.load(mdl)
    X     = df[FEATURES].values
    y     = df[TARGET].values
    y_hat = model.predict(X)

    city_data[city] = {"obs": y, "pred": y_hat, "residuals": y_hat - y}
    metrics_rows.append({
        "City":  city.capitalize(),
        "R²":    round(r2_score(y, y_hat), 4),
        "RMSE":  round(np.sqrt(mean_squared_error(y, y_hat)), 4),
        "MAE":   round(mean_absolute_error(y, y_hat), 4),
        "NSE":   round(nse(y, y_hat), 4),
        "Bias":  round(float(np.mean(y_hat - y)), 4),
    })
    print(f"[OK] {city:10s} predictions computed")

# ══════════════════════════════════════════════════════════════════════
# PLOT 1 — 4-Panel Predicted vs Observed Scatter
# ══════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 2, figsize=(11, 10))
axes = axes.flatten()

for i, city in enumerate(CITIES):
    if city not in city_data:
        continue
    ax  = axes[i]
    obs = city_data[city]["obs"]
    pred= city_data[city]["pred"]
    r2  = r2_score(obs, pred)

    # Sample for plotting density (keep max 20k points)
    if len(obs) > 20000:
        idx = np.random.choice(len(obs), 20000, replace=False)
        obs_p, pred_p = obs[idx], pred[idx]
    else:
        obs_p, pred_p = obs, pred

    ax.scatter(obs_p, pred_p, alpha=0.15, s=3,
               color=CITY_COLORS[city], rasterized=True)

    lim = max(obs.max(), pred.max()) * 1.05
    ax.plot([0, lim], [0, lim], "k--", linewidth=1.2, label="1:1 line")
    ax.set_xlim(0, lim); ax.set_ylim(0, lim)
    ax.set_xlabel("FAO-56 ETo (mm/hr)", fontsize=10)
    ax.set_ylabel("XGBoost ETo (mm/hr)", fontsize=10)
    ax.set_title(f"{city.capitalize()}  (R²={r2:.4f})", fontsize=11)
    ax.legend(fontsize=8, loc="upper left")

fig.suptitle("Predicted vs Observed ETo — All Cities", fontsize=14, y=1.01)
plt.tight_layout()
fig.savefig(os.path.join(RES_DIR, "pred_vs_obs_4panel.png"), bbox_inches="tight")
plt.close(fig)
print("✔ Pred vs Obs 4-panel saved")

# ══════════════════════════════════════════════════════════════════════
# PLOT 2 — Residual/Bias Distribution (KDE)
# ══════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))
for city in CITIES:
    if city not in city_data:
        continue
    resid = city_data[city]["residuals"]
    sns.kdeplot(resid, ax=ax, label=city.capitalize(),
                color=CITY_COLORS[city], linewidth=2, fill=True, alpha=0.15)
ax.axvline(0, color="black", linewidth=1.2, linestyle="--")
ax.set_xlabel("Residual: Predicted − Observed ETo (mm/hr)", fontsize=11)
ax.set_ylabel("Density", fontsize=11)
ax.set_title("Bias Distribution Across Cities", fontsize=13)
ax.legend(fontsize=9)
plt.tight_layout()
fig.savefig(os.path.join(RES_DIR, "bias_distribution.png"), bbox_inches="tight")
plt.close(fig)
print("✔ Bias distribution saved")

# ══════════════════════════════════════════════════════════════════════
# PLOT 3 — Cross-City SHAP Importance Bar Chart
# ══════════════════════════════════════════════════════════════════════
shap_imp_path = os.path.join(SHAP_DIR, "cross_city_mean_shap.csv")
if os.path.exists(shap_imp_path):
    shap_imp = pd.read_csv(shap_imp_path, index_col="city")
    FEAT_SHORT = {"T": "Temp", "RH": "Humidity", "WS": "Wind", "Rs": "Radiation", "P": "Pressure"}
    shap_imp.columns = [FEAT_SHORT.get(c, c) for c in shap_imp.columns]

    fig, ax = plt.subplots(figsize=(12, 5))
    x      = np.arange(len(CITIES))
    n_feat = len(shap_imp.columns)
    width  = 0.12
    palette= plt.cm.Set2(np.linspace(0, 1, n_feat))

    for j, (feat, color) in enumerate(zip(shap_imp.columns, palette)):
        vals = [shap_imp.loc[city, feat] if city in shap_imp.index else 0 for city in CITIES]
        ax.bar(x + j * width, vals, width, label=feat, color=color, edgecolor="white")

    ax.set_xticks(x + width * (n_feat - 1) / 2)
    ax.set_xticklabels([c.capitalize() for c in CITIES], fontsize=10)
    ax.set_ylabel("Mean |SHAP| (mm/hr)", fontsize=11)
    ax.set_title("Cross-City Feature Importance via SHAP", fontsize=13)
    # Legend placed outside axes so it never overlaps bars
    ax.legend(title="Feature", fontsize=9,
              loc="upper left", bbox_to_anchor=(1.01, 1), borderaxespad=0)
    plt.tight_layout()
    fig.savefig(os.path.join(RES_DIR, "cross_city_shap_importance.png"), bbox_inches="tight")
    plt.close(fig)
    print("✔ Cross-city SHAP importance chart saved")

# ══════════════════════════════════════════════════════════════════════
# Save metrics comparison table
# ══════════════════════════════════════════════════════════════════════
metrics_df = pd.DataFrame(metrics_rows)
metrics_df.to_csv(os.path.join(RES_DIR, "cross_city_metrics.csv"), index=False)
print("\n── Cross-City Metrics ──")
print(metrics_df.to_string(index=False))
print(f"\n✅ Cross-city analysis complete → results/")
