import dash
from dash import dcc, html, Input, Output, State, Patch
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots

# ----------------------------------------------------
# Load data
# ----------------------------------------------------
df = pd.read_csv("data/greenhouse_gas_with_population.csv")
df_sector = pd.read_csv("data/greenhouse_gas_per_sector.csv")

df = df.dropna(subset=["year", "iso_code", "emissions_per_capita", "emissions"])
df["year"] = df["year"].astype(int)
df['emissions_per_capita_equalized'] = df['emissions_per_capita'].rank(pct=True) * 100

global_trend = (
    df.groupby("year", as_index=False)["emissions"]
    .sum()
    .rename(columns={"emissions": "global_emissions"})
).sort_values("year")

years = sorted(global_trend["year"].unique())
min_year, max_year = int(min(years)), int(max(years))

# Milestones
milestones = [
    (2015, "Paris Agreement Adoption"),
    (2016, "Paris Agreement Signing"),
    (2018, "COP24 Katowice"),
    (2023, "COP28 Global Stocktake")
]

# Pre-calculate max emission for performance
max_emission = global_trend["global_emissions"].max()

# Calculate the red line trace index (global line + milestones*1 + red line = trace index)
RED_LINE_TRACE_IDX = 1 + len(milestones)  # After global line and milestone lines
MAP_TRACE_IDX = RED_LINE_TRACE_IDX + 1  # After red line

# ----------------------------------------------------
# Helper: Build combined line+map figure for a given year
# ----------------------------------------------------
def build_main_figure(year):
    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.35, 0.65],
        specs=[[{"type": "xy"}], [{"type": "choropleth"}]],
        vertical_spacing=0.05
    )

    # --- 1️⃣ Global emissions line ---
    fig.add_trace(
        go.Scatter(
            x=global_trend["year"],
            y=global_trend["global_emissions"],
            mode="lines",
            line=dict(color="blue", width=3),
            name="Global emissions"
        ),
        row=1, col=1
    )

    # --- 2️⃣ Orange milestone lines with labels ---
    for milestone_year, milestone_label in milestones:
        if min_year <= milestone_year <= max_year:
            # Add vertical line
            fig.add_trace(
                go.Scatter(
                    x=[milestone_year, milestone_year],
                    y=[0, max_emission],
                    mode="lines",
                    line=dict(color="orange", dash="dot", width=1.5),
                    name=milestone_label,
                    hovertemplate=f"<b>{milestone_label}</b><br>{milestone_year}<extra></extra>",
                    showlegend=False
                ),
                row=1, col=1
            )
            
            # Add text annotation for the label
            fig.add_annotation(
                x=milestone_year,
                y=max_emission * 0.95,
                text=milestone_label,
                showarrow=False,
                textangle=-90,
                xanchor="right",
                yanchor="middle",
                font=dict(size=10, color="orange"),
                row=1, col=1
            )

    # --- 3️⃣ Red vertical line for selected year ---
    fig.add_trace(
        go.Scatter(
            x=[year, year],
            y=[0, max_emission],
            mode="lines",
            line=dict(color="red", dash="dash", width=2),
            name="Selected year",
            hoverinfo="skip"
        ),
        row=1, col=1
    )

    # --- 4️⃣ Choropleth map ---
    map_df = df[df["year"] == year]
    fig.add_trace(
        go.Choropleth(
            locations=map_df["iso_code"],
            z=map_df["emissions_per_capita_equalized"],
            text=map_df["Name"],
            customdata=map_df[["emissions_per_capita"]],
            hovertemplate="<b>%{text}</b><br>Emissions per capita: %{customdata[0]:.2f} tCO₂e<extra></extra>",
            colorscale="Reds",
            zmin=0,
            zmax=100,
            colorbar=dict(title="Emissions<br>(percentile)", thickness=15, len=0.6, y=0.25),
            marker_line_width=0.5,
            name="",
        ),
        row=2, col=1
    )

    # --- 5️⃣ Alignment and styling fixes ---
    fig.update_xaxes(
        range=[min_year, max_year],
        fixedrange=True,
        row=1, col=1
    )

    fig.update_yaxes(title_text="Global Emissions (MtCO₂e)", row=1, col=1)

    fig.update_geos(
        showcoastlines=True,
        coastlinecolor="white",
        landcolor="lightgray",
        fitbounds="locations",
        row=2, col=1
    )

    fig.update_layout(
        height=950,
        margin=dict(l=40, r=40, t=60, b=40),
        template="plotly_white",
        clickmode="event+select",
        showlegend=False,
        uirevision='constant',
        transition={'duration': 0}  # Disable transitions for instant updates
    )

    return fig


# ----------------------------------------------------
# Helper: Build sector breakdown for a selected country/year
# ----------------------------------------------------
def build_sector_chart(iso_code, year):
    dff = df_sector[(df_sector["iso_code"] == iso_code) & (df_sector["year"] == year)]
    if dff.empty:
        return go.Figure()
    sector_totals = dff.groupby("sector", as_index=False)["emissions"].sum().sort_values("emissions")
    fig = go.Figure(go.Bar(
        y=sector_totals["sector"],
        x=sector_totals["emissions"],
        orientation='h',
        marker=dict(color=sector_totals["emissions"], colorscale='Reds', showscale=False),
        text=sector_totals["emissions"].round(2),
        texttemplate='%{text} MtCO₂e',
        textposition='outside'
    ))
    fig.update_layout(
        title=f"Emissions by Sector ({year})",
        xaxis_title="Emissions (MtCO₂e)",
        height=400,
        template="plotly_white",
        margin=dict(l=10, r=150, t=40, b=40),
    )
    return fig


# ----------------------------------------------------
# Dash App setup
# ----------------------------------------------------
app = dash.Dash(__name__)
app.title = "Global Greenhouse Gas Emissions"

app.layout = html.Div([
    html.H1("Global Greenhouse Gas Emissions"),

    html.Div([
        html.Label("Select Year:", style={"marginBottom": "5px"}),
        dcc.Slider(
            id="year-slider",
            min=int(min_year),
            max=int(max_year),
            step=1,
            marks={int(y): str(int(y)) for y in years if y % 5 == 0},
            value=int(max_year),
            updatemode="drag",
            tooltip={"placement": "bottom", "always_visible": True},
        ),
    ], style={"marginBottom": "10px", "marginTop": "10px"}),

    dcc.Graph(
        id="main-figure", 
        figure=build_main_figure(max_year),
        config={'displayModeBar': False},
        style={'transition': 'none'}  # Disable CSS transitions
    ),

    html.Hr(),
    html.Div(id="country-info"),

    dcc.Graph(id="sector-figure"),

    # Hidden store to remember selected country
    dcc.Store(id="selected-country", data=None)
])


# ----------------------------------------------------
# Callbacks
# ----------------------------------------------------
@app.callback(
    Output("main-figure", "figure"),
    Input("year-slider", "value"),
    prevent_initial_call=True
)
def update_year(year):
    """Use Patch to update only the red line and map data"""
    patched_figure = Patch()
    
    # Update red line (trace at RED_LINE_TRACE_IDX)
    patched_figure['data'][RED_LINE_TRACE_IDX]['x'] = [year, year]
    patched_figure['data'][RED_LINE_TRACE_IDX]['y'] = [0, max_emission]
    
    # Update map data (trace at MAP_TRACE_IDX)
    map_df = df[df["year"] == year]
    patched_figure['data'][MAP_TRACE_IDX]['locations'] = map_df["iso_code"].tolist()
    patched_figure['data'][MAP_TRACE_IDX]['z'] = map_df["emissions_per_capita_equalized"].tolist()
    patched_figure['data'][MAP_TRACE_IDX]['text'] = map_df["Name"].tolist()
    patched_figure['data'][MAP_TRACE_IDX]['customdata'] = map_df[["emissions_per_capita"]].values.tolist()
    
    return patched_figure


@app.callback(
    Output("selected-country", "data"),
    Input("main-figure", "clickData"),
    State("selected-country", "data")
)
def update_country(clickData, current_country):
    if clickData and "location" in clickData["points"][0]:
        return clickData["points"][0]["location"]
    return current_country


@app.callback(
    [Output("country-info", "children"),
     Output("sector-figure", "figure")],
    [Input("selected-country", "data"),
     Input("year-slider", "value")]
)
def display_country_info(selected_iso, year):
    if not selected_iso:
        return html.Div("Click on a country to see details"), go.Figure()

    dff = df[df["iso_code"] == selected_iso].sort_values("year")
    if dff.empty:
        return html.Div("No data for this country"), go.Figure()

    country_name = dff.iloc[0]["Name"]
    year_data = dff[dff["year"] == year]
    if year_data.empty:
        return html.Div(f"No data for {country_name} in {year}"), go.Figure()

    info = year_data.iloc[0]
    metrics = html.Div([
        html.H3(country_name),
        html.Div([
            html.Div(f"Year: {year}", style={"display": "inline-block", "marginRight": "20px"}),
            html.Div(f"Emissions per Capita: {info['emissions_per_capita']:.2f} tCO₂e", style={"display": "inline-block", "marginRight": "20px"}),
            html.Div(f"Total Emissions: {info['emissions']:.2f} MtCO₂e", style={"display": "inline-block"})
        ]),
    ])

    fig_sector = build_sector_chart(selected_iso, year)
    return metrics, fig_sector


# ----------------------------------------------------
# Run server
# ----------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)