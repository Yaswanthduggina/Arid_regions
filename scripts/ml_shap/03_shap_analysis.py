"""
Script 03 — SHAP Analysis (TreeSHAP)
For each city: global summary, dependence plots,
monthly SHAP heatmap, seasonal SHAP boxplots.

NOTE: SHAP computed on a stratified random sample of 20k rows
(standard practice — sufficient for robust interpretation).
Full SHAP values saved per city for supplementary tables.
"""
import pandas as pd
import numpy as np
import os
import joblib
import shap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# ─── Config ───────────────────────────────────────────────────────────
CITIES    = ["barmer", "bikaner", "jaisalmer", "jodhpur"]
IN_DIR    = os.path.join("results", "ml_input")
MDL_DIR   = os.path.join("results", "models")
SHAP_DIR  = os.path.join("results", "shap")
os.makedirs(SHAP_DIR, exist_ok=True)

FEATURES  = ["T", "RH", "WS", "Rs", "P"]
FEAT_LABELS = {
    "T":  "Temperature (°C)",
    "RH": "Rel. Humidity (%)",
    "WS": "Wind Speed (m/s)",
    "Rs": "Solar Radiation\n(MJ/m²/hr)",
    "P":  "Pressure (kPa)",
}
SEASON_ORDER  = ["Summer", "Monsoon", "Post-Monsoon", "Winter"]
SEASON_COLORS = {
    "Summer":       "#e74c3c",
    "Monsoon":      "#2980b9",
    "Post-Monsoon": "#27ae60",
    "Winter":       "#8e44ad",
}
MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun",
               "Jul","Aug","Sep","Oct","Nov","Dec"]
SHAP_SAMPLE = 20_000   # rows used for SHAP computation
RANDOM_SEED = 42

def assign_season(month):
    if month in [4, 5, 6]:   return "Summer"
    elif month in [7, 8, 9]: return "Monsoon"
    elif month in [10, 11]:  return "Post-Monsoon"
    else:                    return "Winter"

plt.rcParams.update({
    "figure.dpi":       150,
    "font.family":      "DejaVu Sans",
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "axes.labelsize":   11,
    "xtick.labelsize":  9,
    "ytick.labelsize":  9,
})

all_city_importance = {}

# ══════════════════════════════════════════════════════════════════════
for city in CITIES:
    print(f"\n── SHAP: {city.upper()} ──", flush=True)

    src = os.path.join(IN_DIR, f"{city}_ml_ready.csv")
    mdl = os.path.join(MDL_DIR, f"{city}_xgb_model.joblib")
    if not os.path.exists(src) or not os.path.exists(mdl):
        print(f"   [SKIP] Missing data or model for {city}")
        continue

    df    = pd.read_csv(src, parse_dates=["datetime"])
    model = joblib.load(mdl)

    # ── Stratified sample by month for representativeness ─────────────
    if len(df) > SHAP_SAMPLE:
        sample_idx = df.groupby("month", group_keys=False).apply(
            lambda g: g.sample(
                n=max(1, int(SHAP_SAMPLE * len(g) / len(df))),
                random_state=RANDOM_SEED
            ),
            include_groups=False
        ).index
        df_sample = df.loc[sample_idx].sort_index()
    else:
        df_sample = df

    X_sample = df_sample[FEATURES]
    print(f"   Computing TreeSHAP on {len(df_sample):,} samples …", flush=True)

    # ── TreeSHAP ──────────────────────────────────────────────────────
    explainer   = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)   # (n_sample, 5)
    shap_df     = pd.DataFrame(shap_values, columns=FEATURES,
                               index=df_sample.index)
    shap_df["month"]  = df_sample["month"].values
    shap_df["season"] = df_sample["month"].apply(assign_season).values

    all_city_importance[city] = np.abs(shap_values).mean(axis=0)
    print(f"   SHAP done. Dominant feature: "
          f"{FEATURES[np.abs(shap_values).mean(axis=0).argmax()]}", flush=True)

    # ══════════════════════════════════════════════════════════════════
    # PLOT 1 — Global SHAP Summary (beeswarm)
    # ══════════════════════════════════════════════════════════════════
    shap.summary_plot(
        shap_values, X_sample,
        feature_names=[FEAT_LABELS[f] for f in FEATURES],
        show=False, plot_size=(8, 5)
    )
    fig = plt.gcf()
    fig.axes[0].set_title(f"SHAP Feature Importance — {city.capitalize()}",
                          fontsize=13, pad=10)
    plt.tight_layout()
    fig.savefig(os.path.join(SHAP_DIR, f"{city}_shap_summary.png"), bbox_inches="tight")
    plt.close(fig)
    print(f"   ✔ Summary plot saved", flush=True)

    # ══════════════════════════════════════════════════════════════════
    # PLOT 2 — SHAP Dependence Plots (5 features, 2×3 grid)
    # ══════════════════════════════════════════════════════════════════
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes_flat = axes.flatten()
    for i, feat in enumerate(FEATURES):
        ax = axes_flat[i]
        sc = ax.scatter(
            X_sample[feat], shap_df[feat],
            c=X_sample[feat], cmap="plasma",
            alpha=0.25, s=3, rasterized=True
        )
        ax.axhline(0, color="grey", linewidth=0.8, linestyle="--")
        ax.set_xlabel(FEAT_LABELS[feat].replace("\n", " "), fontsize=9)
        ax.set_ylabel("SHAP value (mm/hr)", fontsize=8)
        ax.set_title(feat, fontsize=10)
        plt.colorbar(sc, ax=ax, shrink=0.7, pad=0.02)
    axes_flat[-1].set_visible(False)
    fig.suptitle(f"SHAP Dependence Plots — {city.capitalize()}", fontsize=13, y=1.01)
    plt.tight_layout()
    fig.savefig(os.path.join(SHAP_DIR, f"{city}_shap_dependence.png"), bbox_inches="tight")
    plt.close(fig)
    print(f"   ✔ Dependence plots saved", flush=True)

    # ══════════════════════════════════════════════════════════════════
    # PLOT 3 — Monthly Mean |SHAP| Heatmap
    # ══════════════════════════════════════════════════════════════════
    monthly_shap = (
        shap_df.groupby("month")[FEATURES]
        .apply(lambda x: x.abs().mean())
    )
    monthly_shap.index = MONTH_NAMES

    fig, ax = plt.subplots(figsize=(11, 4))
    sns.heatmap(
        monthly_shap.T,
        ax=ax,
        cmap="YlOrRd",
        annot=True, fmt=".3f",
        linewidths=0.4,
        cbar_kws={"label": "Mean |SHAP| (mm/hr)"},
        yticklabels=[FEAT_LABELS[f].replace("\n", " ") for f in FEATURES],
    )
    ax.set_title(f"Monthly Mean |SHAP| Values — {city.capitalize()}", fontsize=13)
    ax.set_xlabel("Month"); ax.set_ylabel("Feature")
    plt.tight_layout()
    fig.savefig(os.path.join(SHAP_DIR, f"{city}_monthly_shap_heatmap.png"), bbox_inches="tight")
    plt.close(fig)
    print(f"   ✔ Monthly SHAP heatmap saved", flush=True)

    # ══════════════════════════════════════════════════════════════════
    # PLOT 4 — Seasonal SHAP Boxplots
    # ══════════════════════════════════════════════════════════════════
    fig, axes = plt.subplots(1, 5, figsize=(16, 5), sharey=False)
    for i, feat in enumerate(FEATURES):
        ax = axes[i]
        data_by_season = [
            shap_df.loc[shap_df["season"] == s, feat].values
            for s in SEASON_ORDER
        ]
        bp = ax.boxplot(
            data_by_season,
            patch_artist=True,
            medianprops=dict(color="black", linewidth=1.5),
            whiskerprops=dict(linewidth=0.8),
            flierprops=dict(marker=".", markersize=1, alpha=0.2),
        )
        for patch, s in zip(bp["boxes"], SEASON_ORDER):
            patch.set_facecolor(SEASON_COLORS[s])
            patch.set_alpha(0.75)
        ax.axhline(0, color="grey", linewidth=0.8, linestyle="--")
        ax.set_xticks(range(1, 5))
        ax.set_xticklabels(["Sum", "Mon", "Post", "Win"], fontsize=8)
        ax.set_title(feat, fontsize=10, fontweight="bold")
        if i == 0:
            ax.set_ylabel("SHAP value (mm/hr)", fontsize=9)
    fig.suptitle(f"Seasonal SHAP Distribution — {city.capitalize()}",
                 fontsize=13, y=1.02)
    plt.tight_layout()
    fig.savefig(os.path.join(SHAP_DIR, f"{city}_seasonal_shap.png"), bbox_inches="tight")
    plt.close(fig)
    print(f"   ✔ Seasonal SHAP boxplots saved", flush=True)

    # Save SHAP csv for supplementary tables
    shap_df.to_csv(os.path.join(SHAP_DIR, f"{city}_shap_values.csv"))

# ─── Cross-city importance table ──────────────────────────────────────
if all_city_importance:
    imp_df = pd.DataFrame(all_city_importance, index=FEATURES).T
    imp_df.index.name = "city"
    imp_df.to_csv(os.path.join(SHAP_DIR, "cross_city_mean_shap.csv"))
    print(f"\n── Cross-city Mean |SHAP| ──")
    print(imp_df.round(4).to_string())

print(f"\n✅ SHAP analysis complete → results/shap/")
