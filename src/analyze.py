# src/analyze.py
import pandas as pd
import plotly.express as px
from pathlib import Path

CSV = Path("../data/emission_results.csv")
if not CSV.exists():
    print("No results found. Run experiments first.")
    exit()

df = pd.read_csv(CSV)
df['accuracy'] = df['accuracy'].astype(float)
df['emissions_kg'] = df['emissions_kg'].astype(float)

# Scatter: energy vs accuracy
fig = px.scatter(df, x="emissions_kg", y="accuracy", color="model",
                 size="duration_s", hover_data=["dataset","note","timestamp"],
                 title="Emissions (kg CO2) vs Accuracy")
fig.show()

# Save summary CSV
summary = df.groupby("model").agg({
    "emissions_kg":"mean",
    "accuracy":"mean",
    "duration_s":"mean",
    "timestamp":"count"
}).rename(columns={"timestamp":"runs"})
summary.to_csv("../data/summary_by_model.csv")
print("Saved summary_by_model.csv")
