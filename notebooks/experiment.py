import pandas as pd
import plotly.express as px

df = pd.read_csv("../data/emission_results.csv")
df.head()

# Plot emissions vs accuracy
fig = px.scatter(df, x="emissions_kg", y="accuracy", color="model", size="duration_s")
fig.show()
