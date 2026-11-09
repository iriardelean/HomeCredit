import pandas as pd
import xgboost as xgb
from codecarbon import EmissionsTracker
import time

tracker = EmissionsTracker(project_name="Environment_Test", output_dir="../emissions")

tracker.start()

print("Generating dummy data...")
dummy_df = pd.DataFrame({'feature_1': range(1000000), 'feature_2': range(1000000)})
dummy_df = dummy_df.astype('float32')

print("Simulating computation...")
time.sleep(2)

emissions = tracker.stop()
print(f"\nTest complete. Estimated CO2 emissions: {emissions} kg")