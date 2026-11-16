import pandas as pd

csv_path = "../emissions/emissions.csv"
df = pd.read_csv(csv_path)

df = df[df['project_name'].isin(['Baseline_CSV', 'Optimized_Parquet'])]
df = df.drop_duplicates(subset=['project_name'], keep='last')

metrics = df[['project_name', 'duration', 'cpu_energy', 'ram_energy', 'energy_consumed']].copy()

metrics['cpu_Wh'] = metrics['cpu_energy'] * 1000
metrics['ram_Wh'] = metrics['ram_energy'] * 1000
metrics['total_Wh'] = metrics['energy_consumed'] * 1000

print("\n--- GREEN MLOPS: WATT-HOUR METRICS ---")
for index, row in metrics.iterrows():
    print(f"\nProject: {row['project_name']}")
    print(f"Duration: {row['duration']:.4f} seconds")
    print(f"CPU Energy: {row['cpu_Wh']:.6f} Wh")
    print(f"RAM Energy: {row['ram_Wh']:.6f} Wh")
    print(f"Total Energy: {row['total_Wh']:.6f} Wh")