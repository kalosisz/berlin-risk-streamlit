import streamlit as st
import plotly.express as px
import numpy as np
import pydeck as pdk

from streamlit import caching

from functions import get_berlin, get_infection_data

st.set_page_config(page_title='Berlin risk assessment',
                   page_icon='favicon.ico',
                   layout="wide")

# hide_streamlit_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             </style>
#             """
# st.markdown(
#     hide_streamlit_style,
#     unsafe_allow_html=True,
# )

infection_data, berlin_wide, date = get_infection_data()

st.title("""
    Berlin event risk assessment: probability of having an infected person
""")
st.markdown(f"""
    Based on 7-day infection data 
    between **{date.loc["min"]}** 
    and **{date.loc["max"]}**.
    The Berlin-wide incidence rate per 100,000 over that period is **{100_000 * berlin_wide:.2f}**.
""")

st.sidebar.title("Parameters")
undiscovered = st.sidebar.slider(
    "Ascertainment bias",
    min_value=1,
    max_value=10,
    value=5,
    format="%dx",
)
nr_of_people = st.sidebar.slider(
    "Event size",
    min_value=1,
    max_value=250,
    value=50,
)

st.sidebar.markdown(
    """
        ### Estimation logic :spiral_note_pad:
        Covid-19 prevalence is estimated based on product of the 7-day incidence rate and the ascertainment bias. 
        The 7-day incidence rate is the same measure as the government uses for assessing Covid-19 dynamics. 
        The ascertainment bias (measuring the ratio of unreported cases) has not been estimated in Berlin yet. 
        However, based on other estimates on seroprevalence, it usaually lies between 5 and 10. 

        Assuming completely random mixing at event, the probility of having an infected person is then
        $1-(1-p)^n$, where $p$ denotes the prevalence and $n$ the event size.

        #### Data source :file_cabinet:
        [COVID-19 in Berlin, Verteilung in den Bezirken - Gesamtübersicht](https://daten.berlin.de/datensaetze/covid-19-berlin-verteilung-den-bezirken-gesamt%C3%BCbersicht)
        [Einwohnerinnen und Einwohner in den Ortsteilen Berlins am 31.12.2019](https://daten.berlin.de/datensaetze/einwohnerinnen-und-einwohner-den-ortsteilen-berlins-am-31122019)

        #### Acknowledgements :wave:
        This tool has taken inspirations from [COVID-19 Event Risk Assessment Planning Tool](https://covid19risk.biosci.gatech.edu/).
    """, )

st.sidebar.markdown(
    """
        #### Licence
        <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/">
        <img alt="Creative Commons Licence" style="border-width:0" src="https://i.creativecommons.org/l/by-nc/4.0/88x31.png" />
        </a>
        <br />This work is licensed under a 
        <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/">
        Creative Commons Attribution-NonCommercial 4.0 International License</a>.
    """,
    unsafe_allow_html=True,
)

prevalence = undiscovered * infection_data
prevalence = prevalence.rename("Estimated prevalence").to_frame()
prevalence.index.names = ["Bezirk"]

berlin = get_berlin()
probability = (1 - (1 - prevalence).pow(nr_of_people)).reset_index()
berlin = berlin.merge(probability, left_on="name", right_on="Bezirk")
berlin["estimate"] = berlin["Estimated prevalence"]
berlin["estimate_pct"] = (100 * berlin["estimate"]).round(2).astype(str) + "%"

c1, c2 = st.beta_columns((2, 3))

fig = px.bar(prevalence.reset_index(), x="Bezirk", y="Estimated prevalence")
fig.update_yaxes(range=[0, 0.05])
fig.update_yaxes(tickformat=".2%")
fig.update_xaxes(tickangle=-45)

c1.plotly_chart(fig, use_container_width=True)

c2.pydeck_chart(
    pdk.Deck(
        tooltip={
            "text": "{Bezirk}",
        },
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=52.52,
            longitude=13.4,
            zoom=9,
        ),
        layers=[
            pdk.Layer(
                'GeoJsonLayer',
                data=berlin,
                getLineWidth=25,
                get_fill_color='[204, 0, 0, 255 * estimate]',
                pickable=True,
            ),
            pdk.Layer(
                "TextLayer",
                data=berlin,
                sizeMinPixels=10,
                sizeMaxPixels=20,
                get_position=['lng', 'lat'],
                get_text='estimate_pct',
            )
        ],
    ))

st.markdown("""
    ## Current regulations as of 07.11.2020 - excerpt
    ### Assemblies and religious events
    **Public assemblies** may take place outdoors and in enclosed spaces **without 
    limitation of the number of participants**, provided that the applicable 
    hygiene and social distancing rules are obeyed. 
    **Singing together** in enclosed spaces is only permitted if 
    the hygiene and infection protection standards laid down in 
    the framework hygiene plan of the responsible Senate 
    Department of Culture and Europe are observed. In addition, 
    participants must maintain a distance of at least 1.5 meters from persons from other households. 
    The person in charge of the assembly must make sure that the assembly does not have 
    more people in attendance than what is permitted according to the usable area of the place of assembly. 
    Furthermore, organizers must draw up a hygiene plan that ensures compliance with the social distancing and hygiene rules.

    **Worship services** and **sectarian/religious events** held outdoors and in 
    enclosed spaces are **permitted with an unlimited number of people**. 
    It is required that the minimum distances between all participants are 
    maintained and the general hygiene guidelines are observed.

    ### Public and private events
    Events that belong to the culture, entertainment or leisure sector – such as concerts, operas, 
    theater performances and dance events – are generally not permitted until the end of November 30.

    **Public events in enclosed spaces** may only be held with **no more than 50 persons** until the end of November 30, 2020.

    **Outdoor public events** may take place with a **maximum of 100 persons**.

    Private meetings are permitted with a maximum of 10 persons. 
    The following restrictions apply in addition: only persons from a maximum of two households 
    or members of one household with a maximum of two additional persons from other households may meet.

    For funerals and related events, the permitted number increases to 20 persons in enclosed spaces and 50 persons outside.

    It remains a requirement for permission for all of these events that the organizers 
    ensure compliance with the current social distancing and hygiene rules.

    ### Source 
    [The Governing Mayor of Berlin – Senate Chancellery](https://www.berlin.de/corona/en/measures/)
""")
