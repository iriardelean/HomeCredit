import pandas as pd
from codecarbon import EmissionsTracker
import os

RAW_CSV_PATH = "../data/raw/application_train.csv"
OPTIMIZED_PARQUET_PATH = "../data/processed/application_train_optimized.parquet"


def optimize_and_save_data():
    print("Preparing optimized dataset (this only runs once)...")
    df = pd.read_csv(RAW_CSV_PATH)

    float_cols = df.select_dtypes(include=['float64']).columns
    df[float_cols] = df[float_cols].astype('float32')

    flag_cols = [col for col in df.columns if col.startswith('FLAG_DOCUMENT')]
    df[flag_cols] = df[flag_cols].astype('int8')

    df.to_parquet(OPTIMIZED_PARQUET_PATH, engine='pyarrow')
    print(f"Optimized dataset saved to {OPTIMIZED_PARQUET_PATH}\n")


def run_baseline():
    print("--- RUNNING BASELINE (CSV + Default Types) ---")
    tracker = EmissionsTracker(project_name="Baseline_CSV", output_dir="../emissions", log_level="error")
    tracker.start()

    df_baseline = pd.read_csv(RAW_CSV_PATH)

    emissions = tracker.stop()
    ram_mb = df_baseline.memory_usage(deep=True).sum() / 1024 ** 2

    print(f"Baseline Emissions: {emissions:.8f} kg CO2")
    print(f"Baseline RAM usage: {ram_mb:.2f} MB\n")
    return df_baseline


def run_optimized():
    print("--- RUNNING OPTIMIZED (Parquet + Downcasted Types) ---")
    tracker = EmissionsTracker(project_name="Optimized_Parquet", output_dir="../emissions", log_level="error")
    tracker.start()

    df_optimized = pd.read_parquet(OPTIMIZED_PARQUET_PATH, engine='pyarrow')

    emissions = tracker.stop()
    ram_mb = df_optimized.memory_usage(deep=True).sum() / 1024 ** 2

    print(f"Optimized Emissions: {emissions:.8f} kg CO2")
    print(f"Optimized RAM usage: {ram_mb:.2f} MB\n")
    return df_optimized


if __name__ == "__main__":
    if not os.path.exists(RAW_CSV_PATH):
        print(f"Error: Could not find the raw data at {RAW_CSV_PATH}.")
        print("Please ensure 'application_train.csv' is extracted in your data/raw/ folder.")
    else:
        if not os.path.exists(OPTIMIZED_PARQUET_PATH):
            os.makedirs(os.path.dirname(OPTIMIZED_PARQUET_PATH), exist_ok=True)
            optimize_and_save_data()

        df_base = run_baseline()
        df_opt = run_optimized()