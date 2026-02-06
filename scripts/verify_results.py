import pandas as pd
import os
import glob

output_dir = "ET0_new"
files = glob.glob(os.path.join(output_dir, "*.csv"))

report = []

for file in files:
    city = os.path.basename(file).split('_')[0]
    df = pd.read_csv(file)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    
    # Monthly aggregation
    monthly = df.resample('ME').agg({
        'T': 'mean',
        'RH': 'mean',
        'WS': 'mean',
        'Rs': 'sum', # Monthly total radiation (MJ/m2/month)
        'ETo_mm_hr': 'sum' # Monthly total ETo (mm/month)
    })
    
    monthly.rename(columns={'ETo_mm_hr': 'ETo_sum'}, inplace=True)
    
    # Add city name
    monthly['City'] = city
    report.append(monthly)

if report:
    final_report = pd.concat(report)

    # Save summary to a new CSV for inspection
    final_report.to_csv("data/eto_monthly_summary.csv")

    # Print some basic stats to the terminal
    print("\n--- Monthly ETo Summary (Sample) ---")
    print(final_report.groupby(['City', final_report.index.month])['ETo_sum'].mean().unstack())

    # Check correlations
    print("\n--- Correlation of ETo with Variables (Aggregation) ---")
    print(final_report[['ETo_sum', 'T', 'RH', 'WS', 'Rs']].corr()['ETo_sum'])
else:
    print("No files found in ET0_new to verify.")
