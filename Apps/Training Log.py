import pandas as pd
import datetime
import streamlit as st
import warnings
warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
import numpy as np
import matplotlib

##### Set a title for the app's page
st.set_page_config(page_title="Training Log", page_icon="🏋")

def make_unique_list(df, col):
    concept_list = df[col].unique().tolist()
    concept_list = [i.split(', ') for i in concept_list]
    concept_list = [x for xs in concept_list for x in xs]
    concept_list = sorted(set(concept_list))
    return concept_list

def get_right_list(var):
    if var == 'Concepts':
        return concept_list
    if var == 'Subconcepts':
        return subconcept_list
    if var == 'Offensive roles':
        return off_role_list
    if var == 'Defensive roles':
        return def_role_list
    if var == 'Type of drill':
        return drill_type_list
    if var == 'Phase of the game':
        return phase_list

def make_graph_df(x_var,y_var,min_date,max_date):
    graph_list = get_right_list(x_var)
    graph_df = pd.DataFrame()
    for c in graph_list:
        df1 = pd.DataFrame({'Metric':[c],'Value':[df[(df[x_var].str.contains(c)) & (df['Date'].between(training_date_range[0],training_date_range[1]))][y_var].mean()]})
        graph_df = pd.concat([graph_df,df1],ignore_index=True)

    return graph_df


##### Load the data
df = pd.read_excel("https://github.com/BG-Kolding/Kolding-Data/raw/refs/heads/main/KIF%20Training%20Log.xlsx")
df.Date = pd.to_datetime(df.Date)

concept_list = make_unique_list(df, 'Concepts')
subconcept_list = make_unique_list(df, 'Subconcepts')
off_role_list = make_unique_list(df, 'Offensive roles')
def_role_list = make_unique_list(df, 'Defensive roles')
drill_type_list = make_unique_list(df, 'Type of drill')
phase_list = make_unique_list(df, 'Phase of the game')
space_list = make_unique_list(df, 'Space')


##### Create the sidebar with the main filters
with st.sidebar:
    st.header('Filtering Options')
    
    training_date_range = st.date_input(
        label="Training Date Range",
        value=(min(df.Date), max(df.Date)),
        min_value=min(df.Date), max_value=max(df.Date),
        format='YYYY-MM-DD')

    concepts_filters = st.multiselect("Concepts  \n(Leave blank for all concepts)", concept_list)
    subconcepts_filters = st.multiselect("Subconcepts  \n(Leave blank for all subconcepts)", subconcept_list)
    off_role_filters = st.multiselect("Offensive Roles  \n(Leave blank for all subconcepts)", off_role_list)
    def_role_filters = st.multiselect("Defensive Roles  \n(Leave blank for all subconcepts)", def_role_list)
    drill_type_filters = st.multiselect("Drill Type  \n(Leave blank for all subconcepts)", drill_type_list)
    phase_filters = st.multiselect("Phase of Play  \n(Leave blank for all subconcepts)", phase_list)
    space_filters = st.multiselect("Space  \n(Leave blank for all subconcepts)", space_list)


concepts_filters = "|".join(concepts_filters) 
subconcepts_filters = "|".join(subconcepts_filters) 
off_role_filters = "|".join(off_role_filters) 
def_role_filters = "|".join(def_role_filters) 
drill_type_filters = "|".join(drill_type_filters) 
phase_filters = "|".join(phase_filters) 
space_filters = "|".join(space_filters) 

##### Convert date range to a list
training_date_range = list(training_date_range)
training_date_range[0] = pd.to_datetime(training_date_range[0])
training_date_range[1] = pd.to_datetime(training_date_range[1])

### Filter the data given the parameters
filtered_log = df[

(df["Concepts"].str.contains(concepts_filters)) &
(df["Subconcepts"].str.contains(subconcepts_filters)) &
(df["Offensive roles"].str.contains(off_role_filters)) &
(df["Defensive roles"].str.contains(def_role_filters)) &
(df["Type of drill"].str.contains(drill_type_filters)) &
(df["Phase of the game"].str.contains(phase_filters)) &
(df["Space"].str.contains(space_filters)) &

((df["Date"]>=training_date_range[0]) & (df["Date"]<=training_date_range[1]))

].reset_index(drop=True)

filtered_log['Date'] = filtered_log['Date'].dt.strftime('%B %d, %Y')

##### Initialize the tabs
filtered_log_tab, average_tab, full_log_tab = st.tabs(['Filtered Log','Drill Time Stats','Full Log'])

##### Filtered log tab
with filtered_log_tab:
   filtered_log

with full_log_tab:
   df

with average_tab:
    x_var = st.selectbox('Metric to Plot', ['Concepts','Subconcepts','Offensive roles','Defensive roles','Type of drill','Phase of the game','Space'])
    y_var = st.selectbox('Average Metric', ['Time of the drill','Real time of the drill','Time for each set','Nº sets','Time between sets'])

    graph_df = make_graph_df(x_var,y_var,training_date_range[0],training_date_range[1])
    graph_df = graph_df.sort_values(by=['Value'],ascending=False).reset_index(drop=True)

    fig_avg, ax = plt.subplots()
    ax.bar(graph_df.Metric, graph_df.Value)

    if training_date_range[0] != training_date_range[1]:
        ax.set_title(f"Average {y_var.title()} by {x_var.title()}\n{training_date_range[0].strftime('%B %d, %Y')} - {training_date_range[1].strftime('%B %d, %Y')}")
    else:
        ax.set_title(f"Average {y_var.title()} by {x_var.title()}\n{training_date_range[0].strftime('%B %d, %Y')}")
    # ax.set_xlabel(x_var.title())
    plt.xticks(rotation=90)
    ax.set_ylabel('Minutes')
    # ax.legend()
    ax.grid(False)

    st.pyplot(fig_avg)


