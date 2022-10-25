#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 20:21:38 2022

@author: timyouell
"""

import streamlit as st
# import pandas as pd
from fpl_api_collection import (
    get_league_table, get_current_gw, get_fixture_dfs
)
from fpl_utils import (
    define_sidebar
)

base_url = 'https://fantasy.premierleague.com/api/'

st.set_page_config(page_title='PL Table', page_icon=':sports-medal:', layout='wide')
define_sidebar()

st.title('English Premier League Table')

league_df = get_league_table()

league_df.drop('id', axis=1, inplace=True)
league_df.set_index('team', inplace=True)
league_df['GF'] = league_df['GF'].astype(int)
league_df['GA'] = league_df['GA'].astype(int)
league_df['GD'] = league_df['GD'].astype(int)

league_df['Pts/Game'] = (league_df['Pts']/league_df['GP']).round(2)
league_df['GF/Game'] = (league_df['GF']/league_df['GP']).round(2)
league_df['GA/Game'] = (league_df['GA']/league_df['GP']).round(2)
league_df['CS/Game'] = (league_df['CS']/league_df['GP']).round(2)

team_fdr_df, team_fixt_df = get_fixture_dfs()

ct_gw = get_current_gw()

new_fixt_df = team_fixt_df.loc[:, ct_gw:(ct_gw+2)]
new_fixt_df.columns = ['GW' + str(col) for col in new_fixt_df.columns.tolist()]

league_df = league_df.join(new_fixt_df)

float_cols = league_df.select_dtypes(include='float64').columns.values
st.dataframe(league_df.style.format(subset=float_cols, formatter='{:.2f}'), height=740, width=1000)
