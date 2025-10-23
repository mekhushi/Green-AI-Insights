# src/utils.py
import pandas as pd
from pathlib import Path

def save_experiment(row, file_path="../data/emission_results.csv"):
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if file_path.exists():
        df = pd.read_csv(file_path)
        df = df.append(row, ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_csv(file_path, index=False)
