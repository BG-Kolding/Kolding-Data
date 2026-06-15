import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Training Compensation", page_icon="💶")

kif_tm_id = 12275
kif_u19_tm_id = 60831
kif_youth_tm_id = 75264
denmark_tm_id = 39

def years_bt_12_16(birthday,club_entry,club_exit):
    birthday_12 = birthday.replace(year=birthday.year + 12)
    birthday_16 = birthday.replace(year=birthday.year + 16)
    
    if club_entry >= birthday_16:
        return 0.0
    else:
        if club_entry < birthday_12:
            return (club_exit - birthday_12).days/365
        else:
            if club_exit >= birthday_16:
                return (birthday_16 - club_entry).days/365
            else:
                return (club_exit - club_entry).days/365

def years_bt_16_21(birthday,club_entry,club_exit):
    birthday_16 = birthday.replace(year=birthday.year + 16)
    birthday_22 = birthday.replace(year=birthday.year + 22)
    
    if club_exit <= birthday_16:
        return 0.0
    else:
        if club_entry < birthday_16:
            return (club_exit - birthday_16).days/365
        else:
            return (club_exit - club_entry).days/365

def calc_training_compensation(birthday,club_entry,club_exit,fees_per_year,training_federation,training_category):
    training_12_15 = years_bt_12_16(birthday,club_entry,club_exit)
    training_16_21 = years_bt_16_21(birthday,club_entry,club_exit)
    
    payment_12_15 = training_12_15 * fees_per_year[training_federation][4]
    try:
        payment_16_21 = training_16_21 * fees_per_year[training_federation][training_category]
        return payment_12_15+payment_16_21, training_12_15, training_16_21, payment_12_15, payment_16_21, 'GOOD'
    except:
        st.header(f"Training Category {training_category} does not exist in {training_federation}")
        return 0, training_12_15, training_16_21, payment_12_15, 0, 'BAD'

def get_tm_team_info(club_id):
    url = f"https://tmapi-alpha.transfermarkt.technology/clubs?ids[]={club_id}"
    
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    raw = pd.read_json(soup.getText())
    team = pd.json_normalize(raw['data'])
    return team[['id','name']].set_index('id')['name'].to_dict()

def get_tm_player_info(player_id):
    url = f"https://tmapi-alpha.transfermarkt.technology/players?ids[]={player_id}"
    
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    raw = pd.read_json(soup.getText())
    player = pd.json_normalize(raw['data'])
    return player[['id','name']].set_index('id')['name'].to_dict()

def get_transfer_history_player(player_id):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'}
    url = f'https://tmapi-alpha.transfermarkt.technology/transfer/history/player/{player_id}'
    
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    raw = pd.read_json(soup.getText())
    tdf = pd.concat([pd.json_normalize(raw.loc['history']['data']['pending']),pd.json_normalize(raw.loc['history']['data']['terminated'])])
    del page,soup,raw
    
    team_id_dict = {}
    for club_id in tdf[~tdf['transferSource.clubId'].isna()]['transferSource.clubId'].unique().tolist() + tdf[~tdf['transferDestination.clubId'].isna()]['transferDestination.clubId'].unique().tolist():
        team_id_dict.update(get_tm_team_info(club_id))

    player_info_dict = get_tm_player_info(player_id)

    tdf['Player'] = tdf['details.playerId'].map(player_info_dict)
    tdf['From'] = tdf['transferSource.clubId'].map(team_id_dict)
    tdf['To'] = tdf['transferDestination.clubId'].map(team_id_dict)
    tdf['Transfer Date'] = pd.to_datetime(tdf['details.date'].str[:10]).dt.strftime('%Y-%m-%d')
    tdf['Transfer Fee (€)'] = tdf['details.fee.value']
    tdf['Notes'] = tdf['typeDetails.feeDescription']
    
    return tdf[['Player','From','To','Transfer Date','Transfer Fee (€)','Notes']]


our_training_category = 3
new_training_category = 2
our_training_federation = 'UEFA'

fees_per_year = {
    'AFC':{2:40000, 3:10000, 4:2000},
    'CAF':{2:30000, 3:10000, 4:2000},
    'CONCACAF':{2:40000, 3:10000, 4:2000},
    'CONMEBOL':{1:50000, 2:30000, 3:10000, 4:2000},
    'OFC':{2:30000, 3:10000, 4:2000},
    'UEFA':{1:90000, 2:60000, 3:30000, 4:10000},
}

training_comp_tab, transfermarkt_tab, = st.tabs(['Training Compensation','Transfermarkt Player Transfers'])

with training_comp_tab:
    st.header('Player Information')
    
    birthday = st.date_input(
        label="Birthdate",
        value='2006-01-01',
        format='YYYY-MM-DD')
    club_entry = st.date_input(
        label="Club Entry Date",
        value='2020-07-01',
        format='YYYY-MM-DD')
    club_exit = st.date_input(
        label="Club Exit Date",
        value='2025-06-30',
        format='YYYY-MM-DD')

    training_federation = st.radio(
        label='Federation',
        options=['UEFA','CONMEBOL','CONCACAF','AFC','CAF','OFC']
    )
    training_category = st.radio(
        label='Training Category',
        options=[1,2,3,4],
        index=2
    )

    foc_player_compensation, training_12_15, training_16_21, payment_12_15, payment_16_21, status = calc_training_compensation(birthday,club_entry,club_exit,fees_per_year,training_federation,training_category)

    if status=='GOOD':
        st.header(f"Total Compensation: € {round(foc_player_compensation,2):,}")
        
        st.write(f"{round(training_12_15,2)} Years age 12-15 | *(€ {round(payment_12_15,2):,})*")
        
        st.write(f"{round(training_16_21,2)} Years age 16-21 | *(€ {round(payment_16_21,2):,})*")

with transfermarkt_tab:
    st.header('Player Transfers')

    player_id = st.number_input(
        label='Transfermarkt Player ID',
        value=None,
        step=1
    )

    if player_id is not None:
        player_transfer_history = get_transfer_history_player(player_id)
        player_transfer_history
    