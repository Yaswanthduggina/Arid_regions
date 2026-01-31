import json
import pandas as pd
import os

cities = ["jaisalmer", "bikaner", "jodhpur", "barmer"]

for city in cities:
    print(f"\n🔄 Merging data for {city}")

    base_path = f"data/raw/{city}_data"

    files = {
        "T":  f"{base_path}/{city}_T2M_hourly.json",
        "RH": f"{base_path}/{city}_RH_hourly.json",
        "WS": f"{base_path}/{city}_WS_hourly.json",
        "Rs": f"{base_path}/{city}_Rs_hourly.json",
        "P":  f"{base_path}/{city}_PS_hourly.json",
    }

    dfs = []

    # Read one variable at a time (RAM safe)
    for var, path in files.items():
        print(f"   Loading {var}")
        with open(path) as f:
            data = json.load(f)

        df = pd.DataFrame.from_dict(data, orient="index", columns=[var])
        dfs.append(df)

    # Merge on timestamp
    merged = pd.concat(dfs, axis=1)

    # Convert timestamp format
    merged.index = pd.to_datetime(merged.index, format="%Y%m%d%H")

    # Drop rows with any missing values
    merged.dropna(inplace=True)

    out_path = f"data/processed/{city}_hourly_merged.csv"
    merged.to_csv(out_path)

    print(f"✔ Saved {out_path}")

print("\n✅ ALL CITIES MERGED SUCCESSFULLY")
