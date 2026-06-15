import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import numpy as np
from urllib.parse import quote
import math
import joblib
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from io import BytesIO
import requests
import warnings
warnings.filterwarnings('ignore')

def get_angle(x1,y1,x2,y2):
    return abs(math.degrees(math.atan2(y2-y1, x2-x1)))

# Load Data
@st.cache_data(ttl=60*10)

#########################################################################################################################
def load_data(lg_ssn,match_url):
    url = f"https://raw.githubusercontent.com/BG-Kolding/Kolding-Data/refs/heads/main/Event_Data/{lg_ssn}/result%20{match_url}.csv"
    encoded_url = quote(url, safe=':/%?=&')
    data = pd.read_csv(encoded_url)

    data = data.drop_duplicates(subset=['id','timeStamp','contestantId'])
    try:
        data = data.drop(columns=['Gamestate'])
    except:
        pass
    data['Match'] = match

    #####################
    df_base = data.copy()
    df_base = df_base[df_base['periodId']!=5].reset_index(drop=True)

    type_cols = [col for col in df_base.columns if '/qualifierId' in col]

    # Initialize GKx and GKy columns with 0.0
    df_base['GKx'] = 0.0
    df_base['GKy'] = 0.0
    # Iterate over each row index and row values of df_base
    for i, row in df_base.iterrows():
        # Find index where col == 230 (for GKx) or 231 (for GKy)
        idx_gkx = np.where(row[type_cols] == 230)[0]
        idx_gky = np.where(row[type_cols] == 231)[0]
        
        # Set GKx value if qualifier 230 is found
        if len(idx_gkx) > 0:
            gkx_col = f'qualifier/{idx_gkx[0]}/value'  # Get qualifier column name for GKx
            df_base.at[i, 'GKx'] = float(row[gkx_col])
        
        # Set GKy value if qualifier 231 is found
        if len(idx_gky) > 0:
            gky_col = f'qualifier/{idx_gky[0]}/value'  # Get qualifier column name for GKy
            df_base.at[i, 'GKy'] = float(row[gky_col])
    
    # Initialize GKx and GKy columns with 0.0
    df_base['pass_angle'] = 0.0
    df_base['pass_length'] = 0.0
    # Iterate over each row index and row values of df_base
    for i, row in df_base.iterrows():
        # Find index where col == 230 (for GKx) or 231 (for GKy)
        idx_gkx = np.where(row[type_cols] == 213)[0]
        idx_gky = np.where(row[type_cols] == 212)[0]
        
        # Set GKx value if qualifier 230 is found
        if len(idx_gkx) > 0:
            gkx_col = f'qualifier/{idx_gkx[0]}/value'  # Get qualifier column name for GKx
            df_base.at[i, 'pass_angle'] = float(row[gkx_col])
        
        # Set GKy value if qualifier 231 is found
        if len(idx_gky) > 0:
            gky_col = f'qualifier/{idx_gky[0]}/value'  # Get qualifier column name for GKy
            df_base.at[i, 'pass_length'] = float(row[gky_col])
    
    # Initialize GKx and GKy columns with 0.0
    df_base['endX'] = 0.0
    df_base['endY'] = 0.0
    # Iterate over each row index and row values of df_base
    for i, row in df_base.iterrows():
        # Find index where col == 230 (for GKx) or 231 (for GKy)
        idx_gkx = np.where(row[type_cols] == 140)[0]
        idx_gky = np.where(row[type_cols] == 141)[0]
        
        # Set GKx value if qualifier 230 is found
        if len(idx_gkx) > 0:
            gkx_col = f'qualifier/{idx_gkx[0]}/value'  # Get qualifier column name for GKx
            df_base.at[i, 'endX'] = float(row[gkx_col])
        
        # Set GKy value if qualifier 231 is found
        if len(idx_gky) > 0:
            gky_col = f'qualifier/{idx_gky[0]}/value'  # Get qualifier column name for GKy
            df_base.at[i, 'endY'] = float(row[gky_col])
    
    df_base['GoalMouthY'] = 0.0
    df_base['GoalMouthZ'] = 0.0
    # Iterate over each row index and row values of df_base
    for i, row in df_base.iterrows():
        # Find index where col == 230 (for GKx) or 231 (for GKy)
        idx_gkx = np.where(row[type_cols] == 102)[0]
        idx_gky = np.where(row[type_cols] == 103)[0]
        
        # Set GKx value if qualifier 230 is found
        if len(idx_gkx) > 0:
            gkx_col = f'qualifier/{idx_gkx[0]}/value'  # Get qualifier column name for GKx
            df_base.at[i, 'GoalMouthY'] = float(row[gkx_col])
        
        # Set GKy value if qualifier 231 is found
        if len(idx_gky) > 0:
            gky_col = f'qualifier/{idx_gky[0]}/value'  # Get qualifier column name for GKy
            df_base.at[i, 'GoalMouthZ'] = float(row[gky_col])
    
    # Initialize GKx and GKy columns with 0.0
    df_base['RelatedEvent'] = 0
    df_base['RelatedEvent2'] = 0
    
    # Iterate over each row index and row values of df_base
    for i, row in df_base.iterrows():
        # Find index where col == 230 (for GKx) or 231 (for GKy)
        var3 = np.where(row[type_cols] == 388)[0]
        var4 = np.where(row[type_cols] == 55)[0]
        var5 = np.where(row[type_cols] == 216)[0]
    
        # Set GKy value if qualifier 231 is found
        if len(var4) > 0:
            var4_col = f'qualifier/{var4[0]}/value'  # Get qualifier column name for GKy
            df_base.at[i, 'RelatedEvent'] = int(float(row[var4_col]))
    
        # Set GKy value if qualifier 231 is found
        if len(var5) > 0:
            var5_col = f'qualifier/{var5[0]}/value'  # Get qualifier column name for GKy
            df_base.at[i, 'RelatedEvent2'] = int(float(row[var5_col]))
    

    # Initialize all categorical columns with zeros
    categorical_cols = ['Header', 'Left Foot', 'Right Foot', 'ShotFromCorner', 'Penalty', 
                         'Volley', 'RegularPlay', 'FastBreak', 'SetPiece', 'CornerTaken', 
                         'FreeKick', 'Assisted', 'ThrowInSetPiece',
                        'Red Card', 'isOwnGoal','GK','ThrowIn','FK','Cross','Cutback','KickOff',
                        'HeadPass','ThroughBall','LayOff','Switch','GKStart',
                        'InSwinger','OutSwinger','PlayersOnBothPosts','PlayerOnNearPost','PlayerOnFarPost','NoPlayersOnPosts',
                        'DrivenCross','FloatedCross','OverhitCross','LongBall',
                        'TakeOnSpace','TakeOnOvertake','Defensive1v1','DefDuel','OffDuel',
                        'IndividualPlay','FollowsDribble','FirstTouchShot',
                        'BlockedShot','OwnGoal'
                       ]
    df_base[categorical_cols] = 0
    
    # Iterate over each row index and row values of df_base
    for i, row in df_base.iterrows():
        # Iterate over type_cols and set categorical columns based on conditions
        for col_idx, col_name in enumerate(type_cols):
            col_value = row[col_name]
            
            if col_value == 15:
                df_base.at[i, 'Header'] = 1
            elif col_value == 72:
                df_base.at[i, 'Left Foot'] = 1
            elif col_value == 20:
                df_base.at[i, 'Right Foot'] = 1
            elif col_value == 9:
                df_base.at[i, 'Penalty'] = 1
            elif col_value == 108:
                df_base.at[i, 'Volley'] = 1
            elif col_value == 22:
                df_base.at[i, 'RegularPlay'] = 1
            elif col_value == 23:
                df_base.at[i, 'FastBreak'] = 1
            elif col_value == 24:
                df_base.at[i, 'SetPiece'] = 1
            elif col_value == 25:
                df_base.at[i, 'ShotFromCorner'] = 1
            elif col_value == 26:
                df_base.at[i, 'FreeKick'] = 1
            elif col_value == 29:
                df_base.at[i, 'Assisted'] = 1
            elif col_value == 160:
                df_base.at[i, 'ThrowInSetPiece'] = 1
            elif col_value == 32:
                df_base.at[i, 'Red Card'] = 1
            elif col_value == 33:
                df_base.at[i, 'Red Card'] = 1
            elif col_value == 28:
                df_base.at[i, 'isOwnGoal'] = 1
            elif col_value == 28:
                df_base.at[i, 'OwnGoal'] = 1
            elif col_value == 124:
                df_base.at[i, 'GK'] = 1
            elif col_value == 107:
                df_base.at[i, 'ThrowIn'] = 1
            elif col_value == 5:
                df_base.at[i, 'FK'] = 1
            elif col_value == 6:
                df_base.at[i, 'CornerTaken'] = 1
            elif col_value == 2:
                df_base.at[i, 'Cross'] = 1
            elif col_value == 195:
                df_base.at[i, 'Cutback'] = 1
            elif col_value == 279:
                df_base.at[i, 'KickOff'] = 1
            elif col_value == 3:
                df_base.at[i, 'HeadPass'] = 1
            elif col_value == 4:
                df_base.at[i, 'ThroughBall'] = 1
            elif col_value == 156:
                df_base.at[i, 'LayOff'] = 1
            elif col_value == 196:
                df_base.at[i, 'Switch'] = 1
            elif col_value == 240:
                df_base.at[i, 'GKStart'] = 1
            elif col_value == 223:
                df_base.at[i, 'InSwinger'] = 1
            elif col_value == 224:
                df_base.at[i, 'OutSwinger'] = 1
            elif col_value == 219:
                df_base.at[i, 'PlayersOnBothPosts'] = 1
            elif col_value == 220:
                df_base.at[i, 'PlayerOnNearPost'] = 1
            elif col_value == 221:
                df_base.at[i, 'PlayerOnFarPost'] = 1
            elif col_value == 222:
                df_base.at[i, 'NoPlayersOnPosts'] = 1
    
            elif col_value == 386:
                df_base.at[i, 'DrivenCross'] = 1
            elif col_value == 387:
                df_base.at[i, 'FloatedCross'] = 1
            elif col_value == 345:
                df_base.at[i, 'OverhitCross'] = 1
    
            elif col_value == 1:
                df_base.at[i, 'LongBall'] = 1
    
            elif col_value == 464:
                df_base.at[i, 'TakeOnSpace'] = 1
            elif col_value == 465:
                df_base.at[i, 'TakeOnOvertake'] = 1
            elif col_value == 467:
                df_base.at[i, 'Defensive1v1'] = 1
            elif col_value == 285:
                df_base.at[i, 'DefDuel'] = 1
            elif col_value == 286:
                df_base.at[i, 'OffDuel'] = 1
            elif col_value == 215:
                df_base.at[i, 'IndividualPlay'] = 1
            elif col_value == 254:
                df_base.at[i, 'FollowsDribble'] = 1
            elif col_value == 328:
                df_base.at[i, 'FirstTouchShot'] = 1
            elif col_value == 82:
                df_base.at[i, 'BlockedShot'] = 1

    
    # for i in range(len(df_base)):
    #     tid = df_base.contestantId[i]
    #     if df_base.isOwnGoal[i] == 1:
    #         if tid == teamId_h:
    #             df_base.contestantId[i] = teamId_a
    #             df_base.x[i] = 100-df_base.x[i]
    #             df_base.y[i] = 100-df_base.y[i]
    #         elif tid == teamId_a:
    #             df_base.contestantId[i] = teamId_h

#########################################################################################################

    data = df_base.copy()

    data['Match'] = 'This'
    data = data.drop_duplicates(subset=['id','timeStamp','contestantId'])
    data = data[data['timeStamp']!="0001-01-01T00:01:15Z"].reset_index(drop=True)
    data = data[data['timeStamp']!="0001-01-01T00:01:15.001Z"].reset_index(drop=True)
    data = data[data['periodId']!=14].reset_index(drop=True)
    data = data[data['typeId']!=32].reset_index(drop=True)
    data = data[data['typeId']!=30].reset_index(drop=True)
    try:
        data = data.drop(columns=['Gamestate'])
    except:
        pass
    
    # Sort events by timestamp if needed (assuming data is not already sorted)
    data['timeStamp'] = pd.to_datetime(data['timeStamp'], format='mixed')
    data = data.sort_values(by=['Match', 'timeStamp'],ascending=[False,True]).reset_index(drop=True)
    
    
    # Initialize gamestate dictionaries for each match and team
    gamestate_dict = {}
    gamestate_df_full = pd.DataFrame()
    
    # Calculate Gamestate for each match
    for match_id, match_data in data.groupby('Match'):
        # Initialize gamestate for this match
        gamestate = {team_id: 0 for team_id in match_data['contestantId'].unique()}
        gamestate_list = []
        gamestate_game = []
        gamestate_ts = []
        gamestate_id = []
    
        # Iterate through events in this match
        for index, row in match_data.iterrows():
            # Update gamestate based on the team scoring the goal
            if row['typeId'] == 16:  # Assuming typeId 16 represents a goal event
                if row['isOwnGoal'] == 1:
                    var = -1
                else:
                    var = 1
                scoring_team = row['contestantId']
                gamestate[scoring_team] += var
                for team_id in gamestate:
                    if team_id != scoring_team:
                        gamestate[team_id] -= var
            
            # Calculate gamestate difference for the event
            gamestate_diff = gamestate[row['contestantId']] # Assuming two teams with IDs 1 and 2
    
            # Append current gamestate difference for this event
            gamestate_list.append(gamestate_diff)
            gamestate_game.append(match_id)
            gamestate_ts.append(row['timeStamp'])
            gamestate_id.append(row['id'])
        
        # Create a DataFrame with gamestate differences
        gamestate_df = pd.DataFrame({'Gamestate': gamestate_list, 'Match': gamestate_game, 'timeStamp': gamestate_ts, 'id': gamestate_id})
        gamestate_df_full = pd.concat([gamestate_df_full,gamestate_df],ignore_index=True)
        
    merged_df = pd.merge(data, gamestate_df_full, on=['Match', 'timeStamp', 'id'], how='inner')
        
    return merged_df
    
def add_xg(data):
    le = LabelEncoder()

    df = data
    df = df[(df.typeId.between(13,16)) & (df.isOwnGoal==0)].reset_index(drop=True)
    df['distance_to_goal'] = [math.dist([df.x[i],df.y[i]], [100,50]) for i in range(len(df))]
    df['angle_to_goal'] = [get_angle(df.x[i],df.y[i],100,50)  for i in range(len(df))]

    df_base = df.copy()
    
    
    df = df_base.copy()
    df['GKx'] = [98.2 if df.GKx[w]==0 else df.GKx[w] for w in range(len(df))]
    df['GKy'] = [50 if df.GKy[w]==0 else df.GKy[w] for w in range(len(df))]
    pen_df = df[df.Penalty==1].copy()
    df = df[df.Penalty==0].reset_index(drop=True)
    
    df['Goal'] = [1 if df.typeId[i]==16 else 0 for i in range(len(df))]

    ####################################
    ######### DO NOT EDIT THIS #########
    ####################################
    numeric_features = ['x','y',
                        # 'timeMin','timeSec',
                        # 'Gamestate',
                        'Header',
                        'Left Foot','Right Foot',
                        'GKx','GKy',
                        'ShotFromCorner','ThrowInSetPiece','SetPiece','FastBreak','RegularPlay',
                        # 'FreeKick',
                        'Assisted',
                        'distance_to_goal','angle_to_goal',
                        ]
    # categorical_features = ['GS']
    categorical_features = []
    cat_val = categorical_features + ['Goal']
    
    all_f = numeric_features + categorical_features + ['Goal']
    ####################################
    ####################################
    ####################################
    
    df_pred = df[all_f].copy()
    
    for i in range(len(categorical_features)):
        df_pred[f'{categorical_features[i]} encoded'] = le.fit_transform(df_pred[categorical_features[i]])

    xGmodel = joblib.load(BytesIO(requests.get("https://github.com/BG-Kolding/Kolding-Data/raw/refs/heads/main/Logistic%20xG%20Model.pkl").content))
    transfer_values = xGmodel.predict_proba(df_pred.drop(cat_val, axis=1))[:, 1]
        
    df['xG'] = transfer_values

    pen_df['xG'] = 0.76
    df = pd.concat([df,pen_df],ignore_index=True)

    return df



#########################################################################################################################
    
def load_lookup():
    url = "https://raw.githubusercontent.com/BG-Kolding/Kolding-Data/refs/heads/main/Chalkboard_League_Lookups.csv"
    df = pd.read_csv(url, encoding='utf-8-sig')
    return df
lookup = load_lookup()
    
# Sidebar Selection Mode
with st.sidebar:
    league = st.selectbox("League", lookup.League.unique().tolist(), index=lookup.League.unique().tolist().index('Danish 1. Division'))
    season = st.selectbox("Season", sorted(lookup[lookup.League==league].Season.unique().tolist(),reverse=True))

match_list = pd.read_csv(f"https://raw.githubusercontent.com/griffisben/Post_Match_App/main/Stat_Files/{league.replace(' ','%20')}%20{season}.csv")
match_list['MatchDate'] = match_list.Match + " " + match_list.Date

id_lookup_url = f"https://raw.githubusercontent.com/BG-Kolding/Kolding-Data/refs/heads/main/ID_Lookups/{league.replace(" ","%20")}%20ID%20Lookups%20{season}.csv"
id_lookup = pd.read_csv(id_lookup_url)
id_dict = id_lookup.set_index('ID')['Team'].to_dict()


team_list = sorted(match_list.Team.unique().tolist())
with st.sidebar:
    if "Kolding" in team_list:
        team = st.selectbox("Team", team_list, index=team_list.index('Kolding'))
    else:
        team = st.selectbox("Team", team_list)
        
team_matches = match_list[match_list.Team==team].MatchDate.tolist()
with st.sidebar:
    match = st.selectbox("Match", team_matches)



#######################
df = load_data(f'{league.replace(" ","%20")}%20{season}',match.replace(" ","%20"))
max_mins = df.timeMin.max()
xgdf = add_xg(df)
df = pd.concat([df[~df.typeId.between(13,16)],xgdf])
df = df.sort_values(by=['timeStamp'],ascending=True).reset_index(drop=True)
df['Team'] = df['contestantId'].map(id_dict)

# Filter players based on team and match
team_match_players = df[(df["Team"] == team) & (~(df.playerName.isna()))]["playerName"].unique().tolist()
team_match_players = sorted(team_match_players)

with st.sidebar:
    with st.form('Options Select'):
        st.header('Event Filtering Options')
        submitted = st.form_submit_button("Generate Image")
        players = st.multiselect("Select Players (blank for all)", team_match_players)
        event_types = st.multiselect("Select Event Types (blank for all)", ["Pass", "Shot", "Tackle", "Interception", "Dribble", "Aerial", "Missed Tackle", "Ball Recovery", "Blocked Pass"])
        include_set_pieces = st.checkbox("Include Set Piece Passes/Shots", value=True)
        pass_types = st.multiselect("Select Pass Outcome (blank for all)", ["Complete", "Incomplete", "Shot Assist"])
        only_certain_passes = st.selectbox("Specific Pass Type?", ["All","Into Final Third","Into Box"])

filtered_df = df[(df["Team"] == team)]
if players:
    filtered_df = filtered_df[filtered_df["playerName"].isin(players)]

filtered_df['IntoBox'] = ((filtered_df.endX>=83) & (filtered_df.endY.between(21.1,78.9)) & (~((filtered_df.x>=83) & (filtered_df.y.between(21.1,78.9))))).astype(int)
filtered_df['IntoFinalThird'] = ((filtered_df.x<66.666) & (filtered_df.endX>=66.666)).astype(int)
    
# Apply Event Type Filters
if event_types:
    type_map = {"Pass": 1, "Shot": [13, 14, 15, 16], "Dribble": 3, "Tackle": 7, "Interception": 8, "Aerial": 44, "Ball Recovery": 49, "Blocked Pass": 74, "Missed Tackle": [45, 83]}
    selected_ids = [type_map[event] for event in event_types]
    selected_ids = [x if isinstance(x, list) else [x] for x in selected_ids]
    selected_ids = [item for sublist in selected_ids for item in sublist]
    filtered_df = filtered_df[filtered_df["typeId"].isin(selected_ids)]

if not include_set_pieces:
    filtered_df = filtered_df[~((filtered_df["typeId"] == 1) & (filtered_df[["FK", "GK", "ThrowIn", "CornerTaken", "KickOff"]].sum(axis=1) > 0))]
    filtered_df = filtered_df[~((filtered_df["typeId"].between(13, 16)) & (filtered_df["CornerTaken"] == 1))]
    filtered_df = filtered_df[~((filtered_df["Penalty"] == 1))]

if pass_types:
    if "Complete" not in pass_types:
        filtered_df = filtered_df[~((filtered_df["typeId"] == 1) & (filtered_df["outcome"] == 1) & (filtered_df["assist"] != 1) & (filtered_df["keyPass"] != 1))]
    if "Incomplete" not in pass_types:
        filtered_df = filtered_df[~((filtered_df["typeId"] == 1) & (filtered_df["outcome"] == 0))]
    if "Shot Assist" not in pass_types:
        filtered_df = filtered_df[~((filtered_df["typeId"] == 1) & ((filtered_df["assist"] == 1) | (filtered_df["keyPass"] == 1)))]
if only_certain_passes == "Into Box":
        filtered_df = filtered_df[(df.typeId!=1) | ((df.typeId==1) & (filtered_df.IntoBox==1))]
if only_certain_passes == "Into Final Third":
        filtered_df = filtered_df[(df.typeId!=1) | ((df.typeId==1) & (filtered_df.IntoFinalThird==1))]


with st.form('Minute Selection'):
    submitted = st.form_submit_button("Update Data with Time Bands")
    minute_range = st.slider("Time", min_value=0, max_value=max_mins, value=(0,max_mins))
    filtered_df = filtered_df[filtered_df.timeMin.between(minute_range[0],minute_range[1])]

# Draw Pitch
pitch = Pitch(pitch_type='opta', pitch_color='#fbf9f4', line_color='#4A2E19', line_zorder=0, half=False)
fig, axs = pitch.grid(endnote_height=0.045, endnote_space=0, figheight=12,
                      title_height=0.045, title_space=0,
                      axis=False,
                      grid_height=0.86)
fig.set_facecolor('#fbf9f4')

# Define colors for event types
cmp_color = '#4c94f6'
inc_color = 'silver'
key_color = '#f6ba00'
won_color = 'tab:blue'
lost_color = 'tab:orange'

tkls = 0
goals = 0
shots = 0
passes = 0
miss_tkl = 0
interceptions = 0
dribbles = 0
aerials = 0
recoveries = 0
blocks = 0
# Plot Events
for _, row in filtered_df.iterrows():
    if row['typeId'] == 1:  # Passes (Comet style)
        if passes == 0:
            pass_color = cmp_color if row['outcome'] == 1 else inc_color
            if row.get('assist', 0) == 1 or row.get('keyPass', 0) == 1:
                pass_color = key_color
            pitch.lines(row['x'], row['y'], row['endX'], row['endY'],
                        comet=True, alpha=0.3, lw=5, color=pass_color, ax=axs['pitch'],label="Pass")
            pitch.scatter(row['endX'], row['endY'], s=45, ec='k', lw=.3, c=pass_color, zorder=2, ax=axs['pitch'])
            passes += 1
        else:
            pass_color = cmp_color if row['outcome'] == 1 else inc_color
            if row.get('assist', 0) == 1 or row.get('keyPass', 0) == 1:
                pass_color = key_color
            pitch.lines(row['x'], row['y'], row['endX'], row['endY'],
                        comet=True, alpha=0.3, lw=5, color=pass_color, ax=axs['pitch'])
            pitch.scatter(row['endX'], row['endY'], s=45, ec='k', lw=.3, c=pass_color, zorder=2, ax=axs['pitch'])
            passes += 1
        
    elif row['typeId'] in [13, 14, 15]:  # Shots
        if shots == 0:
            pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='lightgrey', ec='k', s=(800 * row.get('xG', 0.05))+75, label="Shot")
            shots += 1
        else:
            pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='lightgrey', ec='k', s=(800 * row.get('xG', 0.05))+75)
            shots += 1
    elif row['typeId'] in [16]:  # Goals
        if goals == 0:
            pitch.scatter(row['x'], row['y'], ax=axs['pitch'], marker='football', c='gold', s=(800 * row.get('xG', 0.05))+75, zorder=3, label="Goal")
            goals += 1
        else:
            pitch.scatter(row['x'], row['y'], ax=axs['pitch'], marker='football', c='gold', s=(800 * row.get('xG', 0.05))+75, zorder=3,)
            goals += 1
    elif row['typeId'] == 7:  # Tackles
        if tkls == 0:
            pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='tab:blue', ec='k', marker='D', s=65, label="Tackle")
            tkls += 1
        else:
            pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='tab:blue', ec='k', marker='D', s=65)
            tkls += 1
    elif row['typeId'] in [45, 83]:  # Missed Tackles
        if miss_tkl == 0:
            pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='tab:orange', ec='k', marker='D', s=65, label="Missed Tackle")
            miss_tkl += 1
        else:
            pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='tab:orange', ec='k', marker='D', s=65)
            miss_tkl += 1
    elif row['typeId'] == 8:  # Interceptions
        if interceptions == 0:
            pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='tab:blue', ec='k', marker='s', s=65, label="Interception")
            interceptions += 1
        else:
            pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='tab:blue', ec='k', marker='s', s=65)
            interceptions += 1
    elif row['typeId'] == 3:  # Dribbles
        dribble_color = won_color if row['outcome'] == 1 else lost_color
        if dribbles == 0:
            pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color=dribble_color, ec='k', marker='>', s=65, label="Dribble")
            dribbles += 1
        else:
            pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color=dribble_color, ec='k', marker='>', s=65)
            dribbles += 1
    elif row['typeId'] == 44:  # Aerials
        aerial_color = won_color if row['outcome'] == 1 else lost_color
        if aerials == 0:
            pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color=aerial_color, ec='k', marker='^', s=65, label="Aerial")
            aerials += 1
        else:
            pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color=aerial_color, ec='k', marker='^', s=65)
            aerials += 1
    elif row['typeId'] == 49:  # Ball Recoveries
        if recoveries == 0:
            pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='k', marker='x', s=65, label="Recovery")
            recoveries += 1
        else:
            pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='k', marker='x', s=65,)
            recoveries += 1
    elif row['typeId'] == 74:  # Blocked Passes
        if blocks == 0:
            pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='silver', ec='k', marker='<', s=65, label="Blocked Pass")
            blocks += 1
        else:
            pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='silver', ec='k', marker='<', s=65,)
            blocks += 1
            
# setup the legend
legend = axs['pitch'].legend(facecolor='#fbf9f4', handlelength=5, edgecolor='#4A2E19', loc='lower left')
for text in legend.get_texts():
    text.set_fontsize(15)

if minute_range[0] == 0:
    if minute_range[1] == max_mins:
        minute_text = ""
    else:
        minute_text = f" | {minute_range[0]}' - {minute_range[1]}'"
else:
    minute_text = f" | {minute_range[0]}' - {minute_range[1]}'"
if players:
    if len(players) > 1:
        axs['title'].text(.5, 1.2, f"{', '.join(players[:-1])} & {players[-1]} Actions", va='center', ha='center',
                          fontsize=28, color='#4A2E19')
        axs['title'].text(.5, .25, f"{team} | {match}{minute_text}", va='center', ha='center',
                          fontsize=20, color='#4A2E19')
    else:
        axs['title'].text(.5, 1.2, f"{players[0]} Actions", va='center', ha='center',
                          fontsize=28, color='#4A2E19')
        axs['title'].text(.5, .25, f"{team} | {match}{minute_text}", va='center', ha='center',
                          fontsize=20, color='#4A2E19')
else:
    axs['title'].text(.5, 1.2, f"{team} Actions", va='center', ha='center',
                      fontsize=28, color='#4A2E19')
    axs['title'].text(.5, .25, f"{match}{minute_text}", va='center', ha='center',
                      fontsize=20, color='#4A2E19')


if not include_set_pieces:
    axs['endnote'].text(.5, .5, "Excludes set piece passes & shots and penalties", va='center', ha='center',
                        fontsize=14, color='#4A2E19')

axs['endnote'].text(0, .5, "Data via Opta", va='center', ha='left',
                    fontsize=14, color='#4A2E19')
axs['endnote'].text(1, .5, "Shots sized for xG\nFor aerials & dribbles: blue = win, orange = loss\nPasses: blue = complete, grey = incomplete, gold = shot assist", va='center', ha='right',
                    fontsize=14, color='#4A2E19')


st.pyplot(fig)

# filtered_df = filtered_df[['playerName','typeId','timeMin','timeSec','outcome','x','y','endX','endY','IntoBox','IntoFinalThird',]].rename(columns={
#     'playerName':'Player','timeMin':'Minute','timeSec':'Second','Sequence':'Poss. ID','seq_xT':'xT of Poss.','seq_xG':'xG of Poss.','Passes in Sequence':'Passes in Poss.'
# })
# filtered_df

