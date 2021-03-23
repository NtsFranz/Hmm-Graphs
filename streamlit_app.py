from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
import sqlite3
import requests

"""
# hmmmmmm
Contains data about bets on upcoming matches this week.
Refresh to see new bets.
"""

def get_all_upcoming() -> list:
    c = sqlite3.connect("hmm.db")
    c.row_factory = sqlite3.Row
    curr = c.cursor()
    query = """
    SELECT * FROM 
        (SELECT * FROM `Matches` WHERE (called=0 OR called="False") AND DateScheduled > DateTime('now')) Matches 
        LEFT JOIN `Bets`
    ON 
        Bets.week = Matches.week AND 
        Bets.HomeTeam = Matches.HomeTeam AND 
        Bets.AwayTeam = Matches.AwayTeam
    ORDER BY `time`;
    """
    curr.execute(query)
    ret = curr.fetchall()
    c.close()

    all_bets = [dict(b) for b in ret]

    return all_bets


def get_all_upcoming_web() -> list:
    r = requests.get('http://ntsfranz.crabdance.com/hmm/all_upcoming')
    return r.json()


data_load_state = st.text('Loading data...')
data = get_all_upcoming_web()
data_load_state.text('Loading data...done!')

df = pd.DataFrame(data)

if len(df) == 0:
    "No matches"
else:

    "Most bet-on matches"
    grouped = df.groupby(['week', 'HomeTeam', 'AwayTeam']).agg({'DateScheduled': 'max','bet_amount': 'sum'})
    grouped = grouped.sort_values('bet_amount', ascending=False)
    grouped.columns = ["Date Scheduled", 'Total bet amount']
    grouped = grouped.reset_index()
    st.table(grouped)

    "Most bet-on teams"
    grouped_by_team = df.groupby(['week', 'HomeTeam', 'AwayTeam', 'bet_team']).agg({'bet_amount': 'sum'})
    grouped_by_team = grouped_by_team.sort_values('bet_amount', ascending=False)
    grouped_by_team.columns = ['Total bet amount']
    grouped_by_team = grouped_by_team.reset_index()
    st.table(grouped_by_team)


    for index, match in grouped.iterrows():
        match_bets = df[df['week'] == match['week']]
        match_bets = match_bets[match_bets['HomeTeam']== match['HomeTeam']]
        match_bets = match_bets[match_bets['AwayTeam']==match['AwayTeam']]
        # st.table(match_bets)
        home_cum_bet = 0
        away_cum_bet = 0
        total_cum_bet = 0
        percentages = []
        if len(match_bets) > 0:
            for index, bet in match_bets.iterrows():
                total_cum_bet += bet['bet_amount']
                if bet['bet_team'] == bet['HomeTeam']:
                    home_cum_bet += bet['bet_amount']
                if bet['bet_team'] == bet['AwayTeam']:
                    away_cum_bet += bet['bet_amount']
                    
                percentages.append({
                    # 'time': bet['time'], 
                    bet['HomeTeam']: home_cum_bet/total_cum_bet - .5,
                    bet['AwayTeam']: away_cum_bet/total_cum_bet - .5
                    })


            perc_df = pd.DataFrame(percentages)

            bet["HomeTeam"] + " vs. " + bet["AwayTeam"]
            st.area_chart(perc_df)
