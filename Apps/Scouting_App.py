import streamlit as st

st.set_page_config(
    page_title="KIF Analysis Apps",
    page_icon="⚽",
)

st.write("# Kolding IF Data Apps")

st.sidebar.success("Click on an app above ☝️")

st.markdown(
    """
    ### 🔎 KIF Scouting
    An all-in-one scouting tool to get player radars, search for players meeting data criteria, analyze similar players, plot scatter plots, rank players in pre-made or custom position-roles, and more
    ### 🌍 Global Role Ranking
    A quick and easy way to rank players across multiple leagues at the same time, using the roles from the main KIF Scouting app
    ### 📋 Post-Match Analysis
    Get post-match dashboards for games from leagues around the world, as well as analyze a team's data across the season to see development & trends. League-wide metric ranking and scatter plots are also available
    ### 📊 Team Playstyle Profiles
    Analyze teams' playstyles in 9 different metrics for a single season, see their development across multiple seasons, see what other teams had the most similar style, and use filters to find teams meeting custom criteria
    ### 🌍 Crossing Analysis
    Visualize & analyze crosses from Chip, Golden, and Early Cross zones as well as to Far or Near post or Center. See xG and Effectiveness metrics for all as well as league rankings for crosses made and conceded.
    ### 👥 League Style Similarities
    Click the button in the sidebar to go to the league similarity dashboard. There, you will see what leagues are most similary style to each other, and hover over them to see the league quality, relative to 1. Division    
"""
)
st.sidebar.link_button("League Similarity Tableau", "https://public.tableau.com/shared/PQMYRQXPG?:display_count=n&:origin=viz_share_link")
