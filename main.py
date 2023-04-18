import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import altair as alt
import re
import pickle

st.set_page_config(
    page_title="NBA Teams Playoff Performance Dashboard",
    page_icon="✅",
    layout="wide",
)

# PARALLEL COORDINATES GRAPH
df = pd.read_csv('./advanced.csv')

#NBA PLAYOFF TEAMS DATASET
df2=pd.read_csv('./all_nba.csv')

container = st.container()
all_team = st.checkbox("Select all teams")

with open('./teamlookup.pkl', 'rb') as handle:
    teamlookup = pickle.load(handle)


plist = df['Playoffs'].unique().tolist()
playoffs_selected = st.multiselect(
    "Select playoff performance: ", sorted(plist), default=sorted(plist))
mask_playoffs = df['Playoffs'].isin(playoffs_selected)

# This is to show lines by season
ftlist = df['Full Team'].unique().tolist()
if all_team:
    teams_selected = container.multiselect(
        "Select individual seasons: ", ftlist, default=ftlist)
    mask_teams = df['Full Team'].isin(teams_selected)
else:
    teams_selected = container.multiselect(
        "Select individual seasons: ", ftlist, default='Bounds')
    mask_teams = df['Full Team'].isin(teams_selected)


df_filtered = df[mask_playoffs & mask_teams]

fig = px.parallel_coordinates(df_filtered, color="Playoffs",
                              dimensions=['o_eFG%', 'DRtg', 'W%', 'NRtg', 'ORtg', 'eFG%',
                                          'TS%'],
                              color_continuous_scale=px.colors.diverging.RdYlGn,
                              color_continuous_midpoint=3.5,
                              title="Key Stats for NBA Team by Playoff Performance")

fig.update_layout(margin=dict(l=40))

col1, col2 = st.columns([6, 1])
col1.plotly_chart(fig, use_container_width=True)
col2.write("*Playoff Legend:  \n6-Won the NBA Finals, 5-Made the NBA Finals, 4-Made the Conference Finals, 3-Made the 2nd Round, 2-Made the 1st Round, 1-Missed the Playoffs")
col2.write("*Team Legend:  \nBounds - sets the lower and upper bound for plot so dimensions don't change when teams are removed, a * symbol means that the team made the playoffs")


# DOUBLE LINE GRAPH
line_OUTPUT = "./line_graph_data.csv"
line_df = pd.read_csv(filepath_or_buffer=line_OUTPUT)
line_df["netRTG"] = line_df["oRTG"] - line_df["dRTG"]

# PPG,APG,RPG,oRTG,dRTG,eFGPerc,OeFGPerc
stats = ["Win%", "PPG", "APG", "RPG", "netRTG",
         "eFGPerc", "OeFGPerc"]  # "oRTG", "dRTG"
domain_ = ["Made Playoffs", "Missed Playoffs"]
range_ = ["green", "red"]

line_stat_names = {
    "Win%": "Win %",
    "PPG": "Points/gm",
    "APG": "Assists/gm",
    "RPG": "Rebounds/gm",
    "oRTG": "Offensive Rating",
    "dRTG": "Defensive Rating",
    "eFGPerc": "Effective Field Goal %",
    "OeFGPerc": "Opposing Effective Field Goal %",
    "netRTG": "Net Rating"}

line_graph_ranges = {
    "Win%": {
        "max": .8,
        "min": .2,
    }, "PPG": {
        "max": 120,
        "min": 90,
    }, "APG": {
        "max": 28,
        "min": 20,
    }, "RPG": {
        "max": 50,
        "min": 40,
    }, "oRTG": {
        "max": 120,
        "min": 95,
    }, "dRTG": {
        "max": 120,
        "min": 95,
    }, "eFGPerc": {
        "max": .6,
        "min": .44,
    }, "OeFGPerc": {
        "max": .6,
        "min": .44,
    }, "netRTG": {
        "max": 10,
        "min": -10,
    }
}

team_list=[]
for element in teams_selected[1:]:
    s1=element.replace("*",'')
    s1=re.sub(r'\b\d+\b(?! ers\b)', '', s1).strip()
    if s1 == 'Charlotte Bobcats':
        s1='Charlotte Hornets'
    if s1 == 'New Orleans Hornets':
        s1='New Orleans Pelicans'
    if s1 == 'New Jersey Nets':
        s1='Brooklyn Nets'
    if s1 =='Bounds':
        continue
    team_list.append(s1)


# create two columns for charts to be on the same row
fig_col1, fig_col2 = st.columns(2)

with fig_col1:
    stat = fig_col1.radio(
        label="Line Plot Filter:",
        options=stats,
        horizontal=True)

    chart = alt.Chart(line_df).mark_line(point=True).encode(
        x=alt.X('Year:O'),
        y=alt.Y(
            stat,
            scale=alt.Scale(
                domain=[
                    line_graph_ranges[stat]["min"],
                    line_graph_ranges[stat]["max"]
                ]
            )
        ),
        color=alt.Color(
            "Result:N",
            scale=alt.Scale(domain=domain_, range=range_)
        ),
    ).properties(
        title=line_stat_names[stat] + " since 2010",
        height=450,
        width=650
    )
    fig_col1.altair_chart(chart)

def extract_team_df(df,team_id):
    return df[df['TEAM_ID']==team_id]

with fig_col2:

    options = fig_col2.multiselect('Select 3 Stats to in 3D:', ['MIN', 'PTS', 'FGM','FGA','FG_PCT','FG3M','FG3A','FG3_PCT','FTM','FTA','FT_PCT','OREB','DREB','REB','AST','STL','BLK','TOV','PF','PLUS_MINUS'],default=['AST','FG_PCT','PLUS_MINUS'])

    if len(options) < 3 or len(options) >3:
        st.error('Please select EXACTLY three options!')

    if len(team_list)==0:
        xs=list(df2[options[0]])
        ys=list(df2[options[1]])
        zs=list(df2[options[2]])
        
        labels=list(df2['CHAMP'])
        marker_dict = {1: '^', 0: 'o'}
        color_dict = {1: 'green', 0: '#fe7c73'}
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.set_xlabel(options[0])
        ax.set_ylabel(options[1])
        ax.set_zlabel(options[2])
        for i,val in enumerate(xs):
            ax.scatter(xs[i],ys[i],zs[i],marker=marker_dict[labels[i]],c=color_dict[labels[i]])
        fig_col2.write(fig,)
        st.write('Historical 3D Scatter Plot of All NBA Playoff Teams (2010-2022). Green Hat denotes Championship. Red Circle denotes Lost.')


    else:
        list_dfs=[]
        for ele in team_list[:]:
            list_dfs.append(extract_team_df(df2,teamlookup[ele]))
        display_df=pd.concat(list_dfs)
        xs=list(display_df[options[0]])
        ys=list(display_df[options[1]])
        zs=list(display_df[options[2]])
        labels=list(display_df['CHAMP'])
        marker_dict = {1: '^', 0: 'o'}
        color_dict = {1: 'green', 0: '#fe7c73'}
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.set_xlabel(options[0])
        ax.set_ylabel(options[1])
        ax.set_zlabel(options[2])
        for i,val in enumerate(xs):
            ax.scatter(xs[i],ys[i],zs[i],marker=marker_dict[labels[i]],c=color_dict[labels[i]])
        fig_col2.write(fig)
        st.write('Historical 3D Scatter Plot by Selected Teams from 2010-2022 Playoffs. Green Hat denotes Championship. Red Circle denotes Lost.')