import streamlit as st
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide")
st.title("🌍 Global Greenhouse Gas Emissions Dashboard")

# -----------------------
# Data loader
# -----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/greenhouse_gas_with_population.csv")
    return df

df = load_data()

# --- Basic checks / preprocessing ---
required_cols = {"year", "iso_code", "Name", "emissions_per_capita", "emissions"}
if not required_cols.issubset(set(df.columns)):
    st.error(f"Data is missing required columns. Need: {required_cols}")
    st.stop()

df = df.dropna(subset=["year", "iso_code", "emissions_per_capita", "emissions"])
df["year"] = df["year"].astype(int)

# --- Histogram equalization for color mapping ---
# Calculate percentile rank (0-100) for each emissions_per_capita value
df['emissions_per_capita_equalized'] = df['emissions_per_capita'].rank(pct=True) * 100

# Compute global totals (absolute emissions, not per capita)
global_trend = (
    df.groupby("year", as_index=False)["emissions"]
    .sum()
    .rename(columns={"emissions": "global_emissions"})
).sort_values("year")

years = sorted(global_trend["year"].unique())
if len(years) == 0:
    st.error("No years found in data.")
    st.stop()

min_year, max_year = int(min(years)), int(max(years))

# ----------------------------------------------------
# Build figure with slider at top, line chart in middle, map at bottom
# ----------------------------------------------------
fig = make_subplots(
    rows=2,
    cols=1,
    row_heights=[0.35, 0.65],
    specs=[[{"type": "xy"}],
           [{"type": "choropleth"}]],
    vertical_spacing=0.08,
)

# Determine color range for equalized values (percentiles 0-100)
zmin = 0
zmax = 100

# Initial year (show latest by default)
initial_year = max_year
initial_map = df[df["year"] == initial_year]

# 1) Add line trace (global trend) in row 1
fig.add_trace(
    go.Scatter(
        x=global_trend["year"],
        y=global_trend["global_emissions"],
        mode="lines",
        line=dict(color="blue", width=3),
        name="Global emissions",
        hovertemplate="%{x}: %{y:.2f}<extra></extra>",
        showlegend=False,
    ),
    row=1, col=1
)

# 2) Add initial red vertical marker in row 1
fig.add_trace(
    go.Scatter(
        x=[initial_year, initial_year],
        y=[0, global_trend["global_emissions"].max()],
        mode="lines",
        line=dict(color="red", dash="dash", width=2),
        name="Selected year",
        hoverinfo="skip",
        showlegend=False,
    ),
    row=1, col=1
)

# 2a) Add green milestone lines for Paris Climate Agreement
milestones = [
    (2015, "Paris Agreement Adoption"),
    (2016, "Paris Agreement Signing"),
    (2018, "COP24 Katowice"),
    (2023, "COP28 Global Stocktake")
]

ymax_trend = global_trend["global_emissions"].max()

for i, (milestone_year, milestone_label) in enumerate(milestones):
    if milestone_year >= min_year and milestone_year <= max_year:
        # Add vertical line
        fig.add_trace(
            go.Scatter(
                x=[milestone_year, milestone_year],
                y=[0, ymax_trend],
                mode="lines",
                line=dict(color="green", dash="dot", width=1.5),
                name=milestone_label,
                hovertemplate=f"<b>{milestone_label}</b><br>Year: {milestone_year}<extra></extra>",
                showlegend=False,
            ),
            row=1, col=1
        )
        
        # Add text label vertically alongside the line, starting from x-axis
        fig.add_annotation(
            x=milestone_year - 0.3,  # Offset slightly to the left
            y=0,
            text=milestone_label,
            showarrow=False,
            font=dict(size=9, color="green"),
            textangle=-90,
            xanchor="right",
            yanchor="bottom",
            row=1, col=1
        )

# 3) Add initial choropleth in row 2 with histogram equalization
fig.add_trace(
    go.Choropleth(
        locations=initial_map["iso_code"],
        z=initial_map["emissions_per_capita_equalized"],
        text=initial_map["Name"],
        customdata=initial_map[["emissions_per_capita"]],
        hovertemplate="<b>%{text}</b><br>Emissions per capita: %{customdata[0]:.10f} tCO₂e<extra></extra>",
        colorscale="Reds",  # Light red to dark red
        zmin=zmin,
        zmax=zmax,
        colorbar=dict(title="Emissions<br>(percentile)", thickness=15, len=0.6, y=0.25),
        marker_line_width=0.5,
    ),
    row=2, col=1
)

# ----------------------------------------------------
# Build frames for animation
# ----------------------------------------------------
frames = []
for year in years:
    map_df = df[df["year"] == year]
    ymax = global_trend["global_emissions"].max()

    # Start with static traces: global line + milestone lines
    frame_traces = [
        go.Scatter(
            x=global_trend["year"],
            y=global_trend["global_emissions"],
            mode="lines",
            line=dict(color="blue", width=3),
            showlegend=False,
            hoverinfo="skip",
        ),
        go.Scatter(
            x=[year, year],
            y=[0, ymax],
            mode="lines",
            line=dict(color="red", dash="dash", width=2),
            showlegend=False,
            hoverinfo="skip",
        ),
    ]
    
    # Add milestone lines to each frame
    for milestone_year, milestone_label in milestones:
        if milestone_year >= min_year and milestone_year <= max_year:
            frame_traces.append(
                go.Scatter(
                    x=[milestone_year, milestone_year],
                    y=[0, ymax],
                    mode="lines",
                    line=dict(color="green", dash="dot", width=1.5),
                    showlegend=False,
                    hovertemplate=f"<b>{milestone_label}</b><br>Year: {milestone_year}<extra></extra>",
                )
            )
    
    # Add choropleth at the end with histogram equalization
    frame_traces.append(
        go.Choropleth(
            locations=map_df["iso_code"],
            z=map_df["emissions_per_capita_equalized"],
            text=map_df["Name"],
            customdata=map_df[["emissions_per_capita"]],
            hovertemplate="<b>%{text}</b><br>Emissions per capita: %{customdata[0]:.2f} tCO₂e<extra></extra>",
            colorscale="Reds",  # Light red to dark red
            zmin=zmin,
            zmax=zmax,
            colorbar=dict(title="Emissions<br>(percentile)", thickness=15, len=0.6, y=0.25),
            marker_line_width=0.5,
            showlegend=False,
        )
    )

    frames.append(go.Frame(data=frame_traces, name=str(year)))

fig.frames = frames

# ----------------------------------------------------
# Build slider steps - positioned at top, aligned with line chart
# ----------------------------------------------------
slider_steps = []
for i, year in enumerate(years):
    step = {
        "label": str(year),
        "method": "animate",
        "args": [
            [str(year)],
            {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}},
        ],
    }
    slider_steps.append(step)

slider = [
    {
        "pad": {"t": 20, "b": 30},
        "active": len(years) - 1,
        "y": 1.02,  # Position above the plot area
        "yanchor": "bottom",
        "x": 0.0,  # Start from the edge
        "xanchor": "left",
        "len": 1.0,  # Full width
        "currentvalue": {
            "prefix": "Year: ",
            "font": {"size": 16},
            "visible": True,
            "xanchor": "left"
        },
        "steps": slider_steps,
    }
]

# ----------------------------------------------------
# Layout configuration
# ----------------------------------------------------
fig.update_layout(
    template="plotly_white",
    sliders=slider,
    height=950,
    margin=dict(l=60, r=40, t=180, b=40),
    showlegend=False,
)

# Axis labels for the line chart
fig.update_xaxes(
    title_text="Year", 
    row=1, col=1,
    dtick=1,  # Show every year
    tickmode='linear',
    range=[min_year, 2024],  # X-axis only goes until 2024
    showgrid=True,
    gridwidth=1,
    gridcolor='lightgray'
)
fig.update_yaxes(
    title_text="Total Global Emissions (MtCO₂e)", 
    row=1, col=1,
    showgrid=True,
    gridwidth=1,
    gridcolor='lightgray'
)

# Map styling
fig.update_geos(
    showcountries=True,
    showcoastlines=True,
    coastlinecolor="white",
    showland=True,
    landcolor="lightgray",
    fitbounds="locations",
    row=2, col=1
)

# ----------------------------------------------------
# Display in Streamlit
# ----------------------------------------------------
st.plotly_chart(fig, use_container_width=True)