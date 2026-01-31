# Project Status and Commands Used

## Data Extraction

The `scripts` folder contains several Python scripts used to download data from the NASA POWER API. These scripts download hourly data for the following parameters:

-   Mean temperature (°C) (T2M)
-   Relative humidity (%) (RH2M)
-   Wind speed at 2 m (m/s) (WS2M)
-   Incoming solar radiation (W/m^2) (ALLSKY_SFC_SW_DWN)
-   Surface pressure (kPa) (PS)

The data was downloaded for four cities: Jaisalmer, Bikaner, Jodhpur, and Barmer, for the years 2001 to 2025.

**Note:** Error handling has been added to all download scripts to make them more robust against network errors.

### Commands Used to Run the Scripts

The following commands can be used to re-download the data:

```bash
python scripts/download_ALLSKY_SFC_SW_DWN_for_4cities.py
python scripts/download_PS_for_4cities.py
python scripts/download_RH2M_for_4cities.py
python scripts/download_T2M_for_4cities.py
python scripts/download_WS2M_for_4cities.py
```

## Data Processing and ETo Calculation

The original data merging and cleaning scripts have been consolidated into a single, more robust script: `scripts/process_data.py`. This script performs the following steps:

1.  Loads the raw hourly data for each of the four cities.
2.  Merges the data for each city into a single DataFrame.
3.  Performs data cleaning, including:
    -   Replacing fill values (-999) with NaN.
    -   Applying range checks to the data.
    -   Logging the number of rows removed at each step.
4.  Calculates the daily reference evapotranspiration (ETo).
5.  Saves the processed daily data to new CSV files in the `data/processed` directory.

### ETo Calculation

The reference evapotranspiration (ETo) is calculated using the FAO-56 Penman-Monteith method, as implemented in the `pyet` Python library. This method requires the following variables:
-   Mean, minimum, and maximum daily temperature
-   Mean daily relative humidity
-   Mean daily wind speed
-   Daily total solar radiation
-   Latitude and altitude of the location

The `process_data.py` script aggregates the hourly data to daily values and then uses `pyet.pm_fao56` to calculate ETo.

### Project Structure

The current project structure is as follows:
```
C:\Reasearch paper\
├───.git\
├───data\
│   ├───processed\
│   │   ├───barmer_daily_processed.csv
│   │   ├───bikaner_daily_processed.csv
│   │   ├───jaisalmer_daily_processed.csv
│   │   └───jodhpur_daily_processed.csv
│   └───raw\
│       ├───barmer_data\
│       │   ├───barmer_PS_hourly.json
│       │   ├───barmer_RH_hourly.json
│       │   ├───barmer_Rs_hourly.json
│       │   ├───barmer_T2M_hourly.json
│       │   └───barmer_WS_hourly.json
│       ├───bikaner_data\
│       │   ├───bikaner_PS_hourly.json
│       │   ├───bikaner_RH_hourly.json
│       │   ├───bikaner_Rs_hourly.json
│       │   ├───bikaner_T2M_hourly.json
│       │   └───bikaner_WS_hourly.json
│       ├───jaisalmer_data\
│       │   ├───jaisalmer_PS_hourly.json
│       │   ├───jaisalmer_RH_hourly.json
│       │   ├───jaisalmer_Rs_hourly.json
│       │   ├───jaisalmer_T2M_hourly.json
│       │   └───jaisalmer_WS_hourly.json
│       └───jodhpur_data\
│           ├───jodhpur_PS_hourly.json
│           ├───jodhpur_RH_hourly.json
│           ├───jodhpur_Rs_hourly.json
│           ├───jodhpur_T2M_hourly.json
│           └───jodhpur_WS_hourly.json
├───notes\
│   └───data_integrity_notes.md
└───scripts\
    ├───download_ALLSKY_SFC_SW_DWN_for_4cities.py
    ├───download_PS_for_4cities.py
    ├───download_RH2M_for_4cities.py
    ├───download_T2M_for_4cities.py
    ├───download_WS2M_for_4cities.py
    └───process_data.py
```

### Commands Used

To run the full data processing pipeline, the following commands are used:

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the processing script:**
    ```bash
    python scripts/process_data.py
    ```

### Code: `scripts/process_data.py`

```python
import pandas as pd
import pyet
import os
import numpy as np

# City data (latitude and altitude)
CITY_DATA = {
    'barmer': {'lat': 25.75, 'alt': 227},
    'bikaner': {'lat': 28.01, 'alt': 242},
    'jaisalmer': {'lat': 26.91, 'alt': 238},
    'jodhpur': {'lat': 26.28, 'alt': 244}
}

# File paths
RAW_DATA_DIR = os.path.join('data', 'raw')
PROCESSED_DATA_DIR = os.path.join('data', 'processed')

# Ensure the processed data directory exists
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# Data columns to load
DATA_COLS = {
    'PS': 'pressure_kpa',
    'RH': 'rh_percent',
    'Rs': 'sol_rad_w_m2',
    'T2M': 'temp_c',
    'WS': 'wind_speed_m_s'
}

for city, city_info in CITY_DATA.items():
    print(f"Processing data for {city}...")

    # Load data for each parameter
    data_frames = []
    for param_code, col_name in DATA_COLS.items():
        file_path = os.path.join(RAW_DATA_DIR, f'{city}_data', f'{city}_{param_code}_hourly.json')
        if os.path.exists(file_path):
            df = pd.read_json(file_path, orient='index')
            df.rename(columns={0: col_name}, inplace=True)
            df.index = pd.to_datetime(df.index, format='%Y%m%d%H')
            df.index.name = 'datetime'
            data_frames.append(df)
        else:
            print(f"  - WARNING: Could not find data file for {param_code} at {file_path}")

    # Merge data frames
    if not data_frames:
        print(f"  - ERROR: No data found for {city}. Skipping.")
        continue

    merged_df = pd.concat(data_frames, axis=1)
    print(f"  - Initial rows: {len(merged_df)}")

    # Convert solar radiation from W/m^2 to MJ/m^2/hr
    # 1 W/m^2 = 0.0036 MJ/m^2/hr
    merged_df['sol_rad_mj_m2_hr'] = merged_df['sol_rad_w_m2'] * 0.0036

    # --- Data Cleaning and Logging ---
    # Replace -999 with NaN
    merged_df.replace(-999, np.nan, inplace=True)

    # Log missing values
    for col in merged_df.columns:
        missing_count = merged_df[col].isna().sum()
        if missing_count > 0:
            print(f"  - Found {missing_count} missing values in '{col}'")

    # Apply range checks
    initial_rows = len(merged_df)
    merged_df = merged_df[merged_df['temp_c'].between(0, 50)]
    rows_after_temp_check = len(merged_df)
    print(f"  - Removed {initial_rows - rows_after_temp_check} rows due to temperature out of range (0-50 C)")

    initial_rows = len(merged_df)
    merged_df = merged_df[merged_df['rh_percent'].between(0, 100)]
    rows_after_rh_check = len(merged_df)
    print(f"  - Removed {initial_rows - rows_after_rh_check} rows due to RH out of range (0-100%)")

    initial_rows = len(merged_df)
    merged_df = merged_df[merged_df['wind_speed_m_s'] >= 0]
    rows_after_ws_check = len(merged_df)
    print(f"  - Removed {initial_rows - rows_after_ws_check} rows due to negative wind speed")

    initial_rows = len(merged_df)
    merged_df = merged_df[merged_df['sol_rad_mj_m2_hr'] >= 0]
    rows_after_rs_check = len(merged_df)
    print(f"  - Removed {initial_rows - rows_after_rs_check} rows due to negative solar radiation")

    # Drop rows with any NaN values and log
    initial_rows = len(merged_df)
    merged_df.dropna(inplace=True)
    rows_after_dropna = len(merged_df)
    print(f"  - Dropped {initial_rows - rows_after_dropna} rows with missing data after cleaning.")
    print(f"  - Final rows: {len(merged_df)}")


    # --- ETo Calculation ---
    # We will calculate ETo on a daily basis
    daily_df = merged_df.resample('D').agg({
        'temp_c': 'mean',
        'wind_speed_m_s': 'mean',
        'sol_rad_mj_m2_hr': 'sum', # sum of hourly radiation to get daily total
        'rh_percent': 'mean',
        'pressure_kpa': 'mean'
    })
    
    # Calculate additional required variables
    daily_df['t_min'] = merged_df['temp_c'].resample('D').min()
    daily_df['t_max'] = merged_df['temp_c'].resample('D').max()
    daily_df.dropna(inplace=True) # drop days with missing aggregated data

    # Rename columns for pyet
    daily_df.rename(columns={
        'temp_c': 'tmean',
        'wind_speed_m_s': 'wind',
        'sol_rad_mj_m2_hr': 'rs',
        'rh_percent': 'rh',
        't_min': 'tmin',
        't_max': 'tmax'
    }, inplace=True)

    # Calculate ETo using pyet
    daily_df['eto_mm_day'] = pyet.pm_fao56(
        tmean=daily_df['tmean'],
        wind=daily_df['wind'],
        rs=daily_df['rs'],
        rh=daily_df['rh'],
        tmax=daily_df['tmax'],
        tmin=daily_df['tmin'],
        elevation=city_info['alt'],
        lat=city_info['lat']
    )

    # Save the processed data
    output_filename = os.path.join(PROCESSED_DATA_DIR, f"{city}_daily_processed.csv")
    daily_df.to_csv(output_filename, index_label='date')

    print(f"  - Saved processed data with ETo to {output_filename}")

print("\nProcessing complete.")