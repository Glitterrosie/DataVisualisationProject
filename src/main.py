import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import random

import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/co2_emissions.csv")
    return df

df = load_data()

st.title("CO₂ Emissions Explorer")

# Define Input Fields
countries = df["Name"].unique()
selected_country = st.selectbox("Select a country", countries)

years = df["year"].unique()
min_year, max_year = int(years.min()), int(years.max())
year_range = st.slider("Select year range", min_year, max_year, (min_year, max_year))

# Prepare Data
filtered = df[
    (df["Name"] == selected_country) &
    (df["year"].between(year_range[0], year_range[1]))
]

# Visualise
st.line_chart(filtered.set_index("year")["co2"])
st.dataframe(filtered[["year", "population", "co2"]].reset_index(drop=True))
