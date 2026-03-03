import pandas as pd
import os
import glob

# Directory setup
INPUT_DIR = "ET0_new"
OUTPUT_DIR = "data"
files = glob.glob(os.path.join(INPUT_DIR, "*_hourly_ETo.csv"))

all_summaries = []

print("🔄 Calculating Yearly ETo for all cities...")

for file in files:
    city = os.path.basename(file).split('_')[0]
    print(f"  Processing {city}...")
    
    # Load hourly data
    df = pd.read_csv(file)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    
    # Resample to Yearly and sum ETo
    yearly = df['ETo_mm_hr'].resample('YE').sum().to_frame()
    yearly.index = yearly.index.year
    yearly.index.name = 'Year'
    yearly.columns = ['Total_ETo_mm']
    yearly['City'] = city
    
    all_summaries.append(yearly)

# Combine all cities
if all_summaries:
    final_yearly_report = pd.concat(all_summaries).reset_index()
    
    # Pivot for easier reading: Years as rows, Cities as columns
    pivot_report = final_yearly_report.pivot(index='Year', columns='City', values='Total_ETo_mm')
    
    # Save results
    summary_path = os.path.join(OUTPUT_DIR, "eto_yearly_summary.csv")
    pivot_report.to_csv(summary_path)
    print(f"\n✅ Yearly summary saved to {summary_path}")
    
    # Display the summary
    print("\n--- Yearly ETo Totals (mm/year) ---")
    print(pivot_report.round(2))
else:
    print("❌ No data files found in ET0_new.")
