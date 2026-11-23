import gc
import os
import time
import pandas as pd
from codecarbon import EmissionsTracker

N_RUNS = 100

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_CSV_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "application_train.csv")
OPTIMIZED_PARQUET_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "application_train_optimized.parquet")
EMISSIONS_DIR = os.path.join(PROJECT_ROOT, "emissions")


def optimize_and_save_data():
    print("Preparing optimized dataset (this only runs once)...")
    df = pd.read_csv(RAW_CSV_PATH)

    float_cols = df.select_dtypes(include=["float64"]).columns
    df[float_cols] = df[float_cols].astype("float32")

    flag_cols = [col for col in df.columns if col.startswith("FLAG_DOCUMENT")]
    df[flag_cols] = df[flag_cols].astype("int8")

    df.to_parquet(OPTIMIZED_PARQUET_PATH, engine="pyarrow")
    print(f"Optimized dataset saved to {OPTIMIZED_PARQUET_PATH}\n")


def run_baseline(n_runs: int):
    print(f"--- RUNNING BASELINE ({n_runs}x CSV + Default Types) ---")
    tracker = EmissionsTracker(
        project_name=f"Baseline_CSV_{n_runs}x",
        output_dir=EMISSIONS_DIR,
        tracking_mode="process",
        gpu_ids=[],
        log_level="error",
    )
    tracker.start()

    ram_mb = 0.0
    for i in range(n_runs):
        df = pd.read_csv(RAW_CSV_PATH)
        if i == n_runs - 1:
            ram_mb = df.memory_usage(deep=True).sum() / (1024 ** 2)
        del df
        gc.collect()

    emissions = tracker.stop()
    print(f"Baseline Total Emissions ({n_runs}x): {emissions:.8f} kg CO2")
    print(f"Baseline DataFrame RAM usage:      {ram_mb:.2f} MB\n")


def run_optimized(n_runs: int):
    print(f"--- RUNNING OPTIMIZED ({n_runs}x Parquet + Downcasted Types) ---")
    tracker = EmissionsTracker(
        project_name=f"Optimized_Parquet_{n_runs}x",
        output_dir=EMISSIONS_DIR,
        tracking_mode="process",
        gpu_ids=[],
        log_level="error",
    )
    tracker.start()

    ram_mb = 0.0
    for i in range(n_runs):
        df = pd.read_parquet(OPTIMIZED_PARQUET_PATH, engine="pyarrow")
        if i == n_runs - 1:
            ram_mb = df.memory_usage(deep=True).sum() / (1024 ** 2)
        del df
        gc.collect()

    emissions = tracker.stop()
    print(f"Optimized Total Emissions ({n_runs}x): {emissions:.8f} kg CO2")
    print(f"Optimized DataFrame RAM usage:      {ram_mb:.2f} MB\n")


if __name__ == "__main__":
    if not os.path.exists(RAW_CSV_PATH):
        print(f"Error: Could not find the raw data at {RAW_CSV_PATH}.")
        print("Please ensure 'application_train.csv' is extracted in your data/raw/ folder.")
    else:
        os.makedirs(EMISSIONS_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(OPTIMIZED_PARQUET_PATH), exist_ok=True)

        if not os.path.exists(OPTIMIZED_PARQUET_PATH):
            optimize_and_save_data()

        run_baseline(N_RUNS)
        time.sleep(3)
        run_optimized(N_RUNS)