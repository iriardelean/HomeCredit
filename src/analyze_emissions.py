import os
import pandas as pd

N_RUNS = 100
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMISSIONS_CSV = os.path.join(PROJECT_ROOT, "emissions", "emissions.csv")


def pct_reduction(baseline: float, optimized: float) -> float:
    return ((baseline - optimized) / baseline) * 100


def main():
    print("--- GREEN MLOPS: WATT-HOUR METRICS ---")
    if not os.path.exists(EMISSIONS_CSV):
        print(f"Error: Could not find {EMISSIONS_CSV}")
        return

    df = pd.read_csv(EMISSIONS_CSV)

    base_rows = df[df["project_name"] == f"Baseline_CSV_{N_RUNS}x"]
    opt_rows = df[df["project_name"] == f"Optimized_Parquet_{N_RUNS}x"]

    if base_rows.empty or opt_rows.empty:
        print(f"No matching rows found for N_RUNS={N_RUNS}. Available project names:")
        print(df["project_name"].unique())
        return

    # Select the most recent 50x benchmark run for each pipeline
    base = base_rows.iloc[-1]
    opt = opt_rows.iloc[-1]

    metrics = {
        "RAM Energy": (base["ram_energy"] * 1000, opt["ram_energy"] * 1000),
        "CPU Energy": (base["cpu_energy"] * 1000, opt["cpu_energy"] * 1000),
        "Total Energy": (base["energy_consumed"] * 1000, opt["energy_consumed"] * 1000),
    }

    print(f"\nCumulative Results ({N_RUNS} runs):")
    for label, (b_wh, o_wh) in metrics.items():
        red = pct_reduction(b_wh, o_wh)
        print(f"  {label:<14} | Baseline: {b_wh:.6f} Wh | Optimized: {o_wh:.6f} Wh | Reduction: {red:.1f}%")

    print(f"\nPer-Run Average (1/{N_RUNS}):")
    for label, (b_wh, o_wh) in metrics.items():
        print(f"  {label:<14} | Baseline: {b_wh / N_RUNS:.6f} Wh | Optimized: {o_wh / N_RUNS:.6f} Wh")


if __name__ == "__main__":
    main()