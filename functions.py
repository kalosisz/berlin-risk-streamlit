import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import pydeck as pdk

from retrying import retry

from constants import berlin_pop


@st.cache(show_spinner=False, max_entries=1, ttl=3600)
@retry(wait_fixed=1000, stop_max_attempt_number=10)
def get_infection_data():
    csv_loc = "https://www.berlin.de/lageso/gesundheit/infektionsepidemiologie-infektionsschutz/corona/tabelle-bezirke-gesamtuebersicht/index.php/index/all.csv"
    df = pd.read_csv(csv_loc, sep=";")
    df = df.drop('id', axis=1)
    df['Date'] = pd.to_datetime(df['datum'])
    df = df.set_index('Date')
    df = df.rolling(7).sum().dropna()

    df.columns = df.columns.str.replace("_", "-").str.title().str.replace(
        "oe", "ö")

    return df


def format_timestamp(ts):
    return ts.strftime("%Y-%m-%d")


def get_berlin_incidence(df):
    last_day = df.iloc[-1]
    city_wide = 100_000 * last_day.sum() / berlin_pop.sum()

    start_date = last_day.name - pd.Timedelta(days=6)
    end_date = last_day.name

    return city_wide, format_timestamp(start_date), format_timestamp(end_date)


def get_prevalence(df, undiscovered):
    return undiscovered * df / berlin_pop


def get_last_day_prevalence(prevalence_ts):
    last_day_prevalance = prevalence_ts.iloc[-1].rename(
        "Estimated prevalence").to_frame()
    last_day_prevalance.index.names = ["Bezirk"]

    return last_day_prevalance


@st.cache(show_spinner=False, max_entries=1)
def get_berlin():
    berlin = gpd.read_file("berlin_bezirke.geojson")
    centroids = berlin["geometry"].to_crs(epsg=3035).centroid.to_crs(epsg=4326)
    berlin["lat"] = centroids.y
    berlin["lng"] = centroids.x
    to_take = ['geometry', 'lat', 'lng', 'name']
    return berlin[to_take]


def get_probabilities(last_day, nr_of_people):
    berlin = get_berlin()
    probability = (1 - (1 - last_day).pow(nr_of_people)).reset_index()
    berlin = berlin.merge(probability, left_on="name", right_on="Bezirk")
    berlin["estimate"] = berlin["Estimated prevalence"]
    berlin["estimate_pct"] = (100 *
                              berlin["estimate"]).round(2).astype(str) + "%"

    return berlin


def get_pydeck_chart(last_day, nr_of_people):
    probabilities = get_probabilities(last_day, nr_of_people)
    deck = pdk.Deck(
        tooltip={
            "text": "{Bezirk}",
        },
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(latitude=52.52,
                                         longitude=13.4,
                                         zoom=9,
                                         min_zoom=9,
                                         max_zoom=10),
        layers=[
            pdk.Layer(
                'GeoJsonLayer',
                data=probabilities,
                getLineWidth=25,
                get_fill_color='[204, 0, 0, 255 * estimate]',
                pickable=True,
            ),
            pdk.Layer(
                "TextLayer",
                data=probabilities,
                sizeMinPixels=10,
                sizeMaxPixels=20,
                get_position=['lng', 'lat'],
                get_text='estimate_pct',
            )
        ],
    )

    return deck


def get_bar_chart(last_day):
    fig = px.bar(last_day.reset_index(), x="Bezirk", y="Estimated prevalence")
    fig.update_yaxes(range=[0, 0.05])
    fig.update_yaxes(tickformat=".2%")
    fig.update_xaxes(tickangle=-45)

    return fig


def get_line_chart(ts):
    x_name = 'Date'
    y_name = 'Estimated prevalence'
    group_name = 'Bezirk'
    long = ts.reset_index().iloc[-90:].melt(id_vars=x_name,
                                            var_name=group_name,
                                            value_name=y_name)

    fig = px.line(long,
                  x=x_name,
                  y=y_name,
                  color=group_name,
                  color_discrete_sequence=px.colors.qualitative.Alphabet_r)
    fig.update_yaxes(range=[0, 0.05])
    fig.update_yaxes(tickformat=".2%")
    fig.update_layout(title={
        'text': 'Historical estimated prevalance of last 90 days',
        'x': 0.5
    })

    return fig