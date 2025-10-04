import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------
# Load data
# --------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/greenhouse_gas_per_gas.csv")
    return df

df = load_data()

st.title("🌍 Greenhouse Gas Emissions Explorer")

# --------------------------
# Global Map
# --------------------------
st.header("🗺️ Global Total GHG Map")

years = df["year"].dropna().unique()
min_year, max_year = int(years.min()), int(years.max())
map_year = st.slider(
    "Select year for the map",
    min_year,
    max_year,
    max_year
)

map_data = df[df["year"] == map_year].dropna(subset=["iso_code", "emissions"])

# Flat 2D choropleth
fig = px.choropleth(
    map_data,
    locations="iso_code",
    color="emissions",
    hover_name="Name",
    color_continuous_scale="Blues",
    projection="equirectangular"
)

# Lock the view (no zoom/pan) + make it big and clean
fig.update_layout(
    title=f"Total GHG emissions in {map_year}",
    margin={"r":0, "t":50, "l":0, "b":0},
    dragmode=False,
    geo=dict(
        showcoastlines=True, coastlinecolor="white",
        showland=True, landcolor="lightgray",
        showcountries=True, countrycolor="white",
        showocean=True, oceancolor="white",
        showframe=False,
        projection_type="equirectangular",
        fitbounds="locations",
        lataxis=dict(range=[-60, 85]),
        lonaxis=dict(range=[-180, 180])
    )
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------
# Country trends
# --------------------------
st.header("📈 Country Trends")

countries = sorted(df["Name"].dropna().unique())
selected_country = st.selectbox("Select a country", countries)

year_range = st.slider("Select year range", min_year, max_year, (min_year, max_year))

filtered = df[
    (df["Name"] == selected_country) &
    (df["year"].between(year_range[0], year_range[1]))
]

st.line_chart(filtered.set_index("year")["emissions"])
st.dataframe(filtered[["year", "emissions"]].reset_index(drop=True))
