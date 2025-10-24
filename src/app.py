# src/app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Page config
st.set_page_config(page_title="AI Energy Tracker", layout="wide", page_icon="⚡")

# Custom CSS
st.markdown(
    """
    <style>
    .reportview-container {background-color: #f9f9f9;}
    .sidebar .sidebar-content {background-color: #e6e6e6; padding: 20px;}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("⚡ AI Energy Tracker Dashboard")

# Load CSV
CSV = Path("../data/emission_results.csv")
if not CSV.exists():
    st.warning("No experiment results found. Run src/run_experiment.py first.")
    st.stop()

df = pd.read_csv(CSV)

# Compute Green Score
df['green_score'] = df['accuracy'] / (df['emissions_kg'].replace(0, 1e-6))

# Sidebar filters
st.sidebar.header("Filters")
datasets = st.sidebar.multiselect("Select Dataset(s)", options=df['dataset'].unique(), default=df['dataset'].unique())
models = st.sidebar.multiselect("Select Model(s)", options=df['model'].unique(), default=df['model'].unique())
notes_filter = st.sidebar.text_input("Filter by Note (optional)")

# Safe filtering
if notes_filter:
    filtered_df = df[
        (df['dataset'].isin(datasets)) &
        (df['model'].isin(models)) &
        (df['note'].astype(str).str.contains(notes_filter, case=False, na=False))
    ]
else:
    filtered_df = df[
        (df['dataset'].isin(datasets)) &
        (df['model'].isin(models))
    ]

# Top metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Experiments", len(filtered_df))
col2.metric("Average Accuracy", f"{filtered_df['accuracy'].mean():.2f}")
col3.metric("Average CO₂ (kg)", f"{filtered_df['emissions_kg'].mean():.4f}")
col4.metric("Max Green Score", f"{filtered_df['green_score'].max():.2f}")

st.markdown("---")

# Tabs for charts
tab1, tab2, tab3, tab4 = st.tabs(["Emissions vs Accuracy", "Duration vs Accuracy", "CO₂ per Model", "Green Score"])

with tab1:
    st.subheader("Emissions vs Accuracy")
    fig1 = px.scatter(
        filtered_df, x="emissions_kg", y="accuracy", color="model",
        size="duration_s", hover_data=["dataset","note","timestamp","green_score"],
        title="CO₂ Emissions vs Model Accuracy"
    )
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    st.subheader("Training Duration vs Accuracy")
    fig2 = px.scatter(
        filtered_df, x="duration_s", y="accuracy", color="dataset",
        size="emissions_kg", hover_data=["model","note","green_score"],
        title="Training Duration vs Accuracy"
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("Average CO₂ Emissions per Model")
    avg_co2 = filtered_df.groupby("model")["emissions_kg"].mean().reset_index()
    fig3 = px.bar(
        avg_co2, x="model", y="emissions_kg", color="model",
        title="Average CO₂ Emissions by Model"
    )
    st.plotly_chart(fig3, use_container_width=True)

with tab4:
    st.subheader("Average Green Score per Model")
    avg_green = filtered_df.groupby("model")["green_score"].mean().reset_index().sort_values(by="green_score", ascending=False)
    fig4 = px.bar(
        avg_green, x="model", y="green_score", color="green_score",
        color_continuous_scale="Viridis", title="Average Green Score by Model"
    )
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# Detailed experiment table
st.subheader("Experiment Details")
st.dataframe(filtered_df.reset_index(drop=True))
st.markdown(f"Data last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
