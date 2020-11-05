import urllib
import json
import streamlit as st
import pandas as pd
import geopandas as gpd

from conts import berlin_pop


@st.cache(show_spinner=False, ttl=3600)
def get_infection_data():
    url = "https://www.berlin.de/lageso/gesundheit/infektionsepidemiologie-infektionsschutz/corona/tabelle-bezirke-gesamtuebersicht/index.php/index/index.json"
    with urllib.request.urlopen(url) as response:
        df = pd.DataFrame(json.loads(response.read())["index"][-7:])

    for col in df.columns[2:]:
        df[col] = df[col].astype(int)

    df.columns = df.columns.str.replace("_", "-").str.title().str.replace(
        "oe", "ö")

    return df.iloc[:, 2:].sum() / berlin_pop, df["Datum"].agg(["min", "max"])


@st.cache(show_spinner=False)
def get_berlin():
    berlin = gpd.read_file("berlin_bezirke.geojson")
    centroids = berlin["geometry"].to_crs(epsg=3035).centroid.to_crs(epsg=4326)
    berlin["lat"] = centroids.y
    berlin["lng"] = centroids.x
    return berlin
