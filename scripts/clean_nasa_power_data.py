import json
import pandas as pd
import os

input_dir = "data/raw/nasa_power"
output_dir = "data/processed"
os.makedirs(output_dir, exist_ok=True)

files = [f for f in os.listdir(input_dir) if f.endswith(".json")]

for file in files:
    print(f"Cleaning {file}...")

    with open(os.path.join(input_dir, file)) as f:
        data = json.load(f)

    params = data["properties"]["parameter"]

    records = []

    for date_key in params["T2M"].keys():
        year = int(date_key[:4])
        month = int(date_key[4:])

        # ❌ Remove annual value
        if month == 13:
            continue

        row = {
            "Year": year,
            "Month": month,
            "Rn": params["ALLSKY_SFC_SW_DWN"][date_key],
            "T": params["T2M"][date_key],
            "RH": params["RH2M"][date_key],
            "WS": params["WS2M"][date_key]
        }

        # Remove missing NASA fill values
        if -999 in row.values():
            continue

        records.append(row)

    df = pd.DataFrame(records)
    city_name = file.replace("_monthly.json", "")
    df.to_csv(f"{output_dir}/{city_name}_clean.csv", index=False)

    print(f"Saved: {city_name}_clean.csv")

print("✅ Cleaning finished — only real months retained.")
