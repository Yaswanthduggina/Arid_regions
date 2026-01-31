import os

files_to_process = [
    'data/processed/barmer_hourly_clean.csv',
    'data/processed/bikaner_hourly_clean.csv',
    'data/processed/jaisalmer_hourly_clean.csv',
    'data/processed/jodhpur_hourly_clean.csv'
]

for file_path in files_to_process:
    if os.path.exists(file_path):
        with open(file_path, 'r+') as f:
            lines = f.readlines()
            if lines:
                first_line = lines[0]
                if first_line.startswith(','):
                    lines[0] = 'date and time' + first_line
                    f.seek(0)
                    f.writelines(lines)
                    print(f"Added header to {file_path}")
                else:
                    print(f"Header already exists in {file_path}")
            else:
                print(f"File is empty: {file_path}")
    else:
        print(f"File not found: {file_path}")
