import streamlit as st

from functions import (get_infection_data, get_berlin_incidence,
                       get_prevalence, get_last_day_prevalence,
                       get_pydeck_chart, get_bar_chart, get_line_chart)

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

infection_data = get_infection_data()
berlin_wide, start_date, end_date = get_berlin_incidence(infection_data)

st.title("""
    Berlin event risk assessment: probability of having an infected person
""")
st.markdown(f"""
    Based on 7-day infection data
    between **{start_date}**
    and **{end_date}**.
    The Berlin-wide incidence rate per 100,000
    over that period is **{berlin_wide:.2f}**.
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
        Covid-19 prevalence is estimated based on product of the 7-day
        incidence rate and the ascertainment bias.
        The 7-day incidence rate is the same measure
        as the government uses for assessing Covid-19 dynamics.
        The ascertainment bias (measuring the ratio of unreported cases)
         has not been estimated in Berlin yet.
        However, based on other estimates on seroprevalence,
        it usaually lies between 5 and 10.

        Assuming completely random mixing at event,
        the probility of having an infected person is then
        $1-(1-p)^n$, where $p$ denotes the prevalence and $n$ the event size.

        #### Data source :file_cabinet:
        [COVID-19 in Berlin, Verteilung in den Bezirken - Gesamtübersicht]
        (https://daten.berlin.de/datensaetze/covid-19-berlin-verteilung-den-bezirken-gesamt%C3%BCbersicht)
        [Einwohnerinnen und Einwohner in den Ortsteilen Berlins am 31.12.2019]
        (https://daten.berlin.de/datensaetze/einwohnerinnen-und-einwohner-den-ortsteilen-berlins-am-31122019)

        #### Acknowledgements :wave:
        This tool has taken inspirations from
        [COVID-19 Event Risk Assessment Planning Tool]
        (https://covid19risk.biosci.gatech.edu/).
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

prevalence_ts = get_prevalence(infection_data, undiscovered)
last_day_prevalance = get_last_day_prevalence(prevalence_ts)

c1, c2 = st.beta_columns((2, 3))

c1.plotly_chart(get_bar_chart(last_day_prevalance), use_container_width=True)

c2.pydeck_chart(get_pydeck_chart(last_day_prevalance, nr_of_people))

st.plotly_chart(get_line_chart(prevalence_ts), use_container_width=True)

st.markdown("""
    ## Current regulations as of 24.06.2021 - excerpt
    ### Assemblies and religious events
    Public assemblies may take place outdoors and in enclosed spaces
    without limitation of the number of participants,
    provided that the applicable hygiene and social distancing rules
    are obeyed. Singing together in enclosed spaces is only permitted
    if the hygiene and infection protection standards laid down
    in the framework hygiene plan of the responsible Senate Department
    of Culture and Europe are observed. In addition, participants must
    maintain a distance of at least 1.5 meters from persons
    from other households and wear a medical mask
    (an FFP2 mask must be worn in enclosed spaces).
    In the case of assemblies in enclosed spaces with more than 20 people,
    all participants must present a negative
    Corona test or proof of vaccination or of recovery
    from a Covid 19 infection. The person in charge of
    the assembly must make sure that the assembly
    does not have more people in attendance than
    what is permitted according to the usable area of the place of assembly.
    Furthermore, organizers must draw up a hygiene
    plan that ensures compliance with the social distancing and hygiene rules.

    Worship services and religious or similar events held outdoors
    and in enclosed spaces are permitted with an unlimited number of people.
    It is required that the minimum distances between all participants
    are maintained and the general hygiene guidelines are observed.
    All participants must wear an FFP2 mask if they are not in their seats.


    ### Public and private events
    Events that belong to the culture, entertainment or leisure sector
    – such as concerts, operas,
    theater performances and dance events – are permitted
    subject to strict hygiene requirements.

    Public events in enclosed spaces may be held with
    up to 250 persons. The permissible number of persons is increased
    to a maximum of 1000 if all the requirements of
    the hygiene concept of the senate administration are met.

    Outdoor public events may take place with a maximum of 1000 persons.
    If more than 250 people are present,
    testing is mandatory for all participants.

    Private meetings are only permitted with members of
    your own household and with persons from
    a maximum of four other households,
    as long as no more than ten people are present at the same time.
    Your own children up to 14 years of age as well as vaccinated
    and recovered persons are not included.

    For funerals and related events, the permitted number
    increases to 20 persons in enclosed spaces and 50 persons outside.

    ### Source
    [The Governing Mayor of Berlin – Senate Chancellery](https://www.berlin.de/corona/en/measures/)
""")
