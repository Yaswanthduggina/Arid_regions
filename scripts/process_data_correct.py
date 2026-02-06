import pandas as pd
import pyet
import os
import numpy as np

# ===============================
# CITY DETAILS
# ===============================
CITY_DATA = {
    'barmer':    {'lat': 25.75, 'alt': 227},
    'bikaner':   {'lat': 28.01, 'alt': 242},
    'jaisalmer': {'lat': 26.91, 'alt': 238},
    'jodhpur':   {'lat': 26.28, 'alt': 244}
}

# Directory setup
RAW_DATA_DIR = os.path.join('data', 'raw')
PROCESSED_DATA_DIR = os.path.join('data', 'processed')
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# Data Mapping
DATA_COLS = {
    'PS':  'pressure_kpa',
    'RH':  'rh_percent',
    'Rs':  'sol_rad_mj_m2_hr', # Raw NASA AG data is already in MJ/m^2/hr
    'T2M': 'temp_c',
    'WS':  'wind_speed_m_s'
}

for city, city_info in CITY_DATA.items():
    print(f"\nProcessing {city}...")

    # 1. Load raw data for each parameter
    data_frames = []
    for param_code, col_name in DATA_COLS.items():
        file_path = os.path.join(RAW_DATA_DIR, f'{city}_data', f'{city}_{param_code}_hourly.json')
        
        if os.path.exists(file_path):
            df_param = pd.read_json(file_path, orient='index')
            df_param.columns = [col_name]
            df_param.index = pd.to_datetime(df_param.index, format='%Y%m%d%H')
            data_frames.append(df_param)
        else:
            print(f"  - WARNING: Could not find data file for {param_code} at {file_path}")

    if not data_frames:
        print(f"  - ERROR: No data found for {city}. Skipping.")
        continue

    # 2. Merge into single hourly DataFrame
    merged_df = pd.concat(data_frames, axis=1)
    
    # --- Data Cleaning ---
    # Replace NASA fill values with NaN
    merged_df.replace([-999, -99], np.nan, inplace=True)
    
    # Drop rows with any NaN values to ensure ETo calculation correctness
    merged_df.dropna(inplace=True)
    print(f"  - Final hourly rows after cleaning: {len(merged_df)}")

    # 2. Aggregate to DAILY values (Best Practice for pyet FAO-56 accuracy)
    daily_df = merged_df.resample('D').agg({
        'temp_c':           ['mean', 'min', 'max'],
        'wind_speed_m_s':   'mean',
        'sol_rad_mj_m2_hr': 'sum', # sum of hourly MJ values = daily MJ
        'rh_percent':       'mean',
        'pressure_kpa':     'mean'
    })

    # Flatten multi-indexed columns
    daily_df.columns = ['tmean', 'tmin', 'tmax', 'wind', 'rs', 'rh', 'pressure']
    daily_df.dropna(inplace=True) # remove days with insufficient hourly data

    # 3. Calculate ETo using pyet (FAO-56 standard)
    # pyet handles slope of vapor pressure, psychological constant, and Rn automatically
    daily_df['eto_fao56_mm_day'] = pyet.pm_fao56(
        tmean=daily_df['tmean'],
        wind=daily_df['wind'],
        rs=daily_df['rs'],
        rh=daily_df['rh'],
        tmax=daily_df['tmax'],
        tmin=daily_df['tmin'],
        elevation=city_info['alt'],
        lat=city_info['lat']
    )

    # 4. Save results
    output_path = os.path.join(PROCESSED_DATA_DIR, f"{city}_daily_ETo.csv")
    daily_df.to_csv(output_path)
    print(f"  ✔ Saved daily data with ETo to {output_path}")

print("\n✅ DATA PROCESSING AND ETo CALCULATION COMPLETE")
