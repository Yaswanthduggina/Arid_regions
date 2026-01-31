import pandas as pd
import os

cities = ["jaisalmer", "bikaner", "jodhpur", "barmer"]

for city in cities:
    print(f"\n🧹 Cleaning {city}")

    path = f"data/processed/{city}_hourly_merged.csv"
    df = pd.read_csv(path, index_col=0, parse_dates=True)

    # Remove NASA fill values
    df.replace([-999, -99], pd.NA, inplace=True)

    # Range checks (FAO realistic limits)
    df = df[(df["RH"] >= 0) & (df["RH"] <= 100)]
    df = df[(df["T"] > -10) & (df["T"] < 55)]
    df = df[(df["WS"] >= 0) & (df["WS"] < 20)]
    df = df[(df["Rs"] >= 0)]
    df = df[(df["P"] > 70) & (df["P"] < 110)]

    df.dropna(inplace=True)

    out = f"data/processed/{city}_hourly_clean.csv"
    df.to_csv(out)

    print(f"✔ Cleaned file saved: {out}")

print("\n✅ ALL HOURLY DATA SCIENTIFICALLY CLEANED")
