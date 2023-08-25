#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 20:21:38 2022

@author: timyouell
"""

import streamlit as st
import pandas as pd
from fpl_utils.fpl_api_collection import (
    get_league_table, get_current_gw, get_fixture_dfs, get_bootstrap_data
)
from fpl_utils.fpl_utils import (
    define_sidebar
)

base_url = 'https://fantasy.premierleague.com/api/'

st.set_page_config(page_title='PL Table', page_icon=':sports-medal:', layout='wide')
define_sidebar()

st.title('Premier League Table')

league_df = get_league_table()

team_fdr_df, team_fixt_df = get_fixture_dfs()

ct_gw = get_current_gw()

new_fixt_df = team_fixt_df.loc[:, ct_gw:(ct_gw+2)]
new_fixt_cols = ['GW' + str(col) for col in new_fixt_df.columns.tolist()]
new_fixt_df.columns = new_fixt_cols

new_fdr_df = team_fdr_df.loc[:, ct_gw:(ct_gw+2)]

league_df = league_df.join(new_fixt_df)

float_cols = league_df.select_dtypes(include='float64').columns.values

league_df = league_df.reset_index()
league_df.rename(columns={'team': 'Team'}, inplace=True)
league_df.index += 1

league_df['GD'] = league_df['GD'].map('{:+}'.format)


teams_df = pd.DataFrame(get_bootstrap_data()['teams'])

## Very slow to load, works but needs to be sped up.
def get_home_away_str_dict():
    new_fdr_df.columns = new_fixt_cols
    result_dict = {}
    for column in new_fdr_df.columns:
        values = list(new_fdr_df[column])
        strings = list(new_fixt_df[column])
        value_dict = {}
        for value, string in zip(values, strings):
            if value not in value_dict:
                value_dict[value] = []
            value_dict[value].append(string)
        result_dict[column] = value_dict
    
    merged_dict = {}
    for k, dict1 in result_dict.items():
        for key, value in dict1.items():
            if key in merged_dict:
                merged_dict[key].extend(value)
            else:
                merged_dict[key] = value
    for k, v in merged_dict.items():
        decoupled_list = list(set(v))
        merged_dict[k] = decoupled_list
    for i in range(1,6):
        if i not in merged_dict:
            merged_dict[i] = []
    return merged_dict


home_away_dict = get_home_away_str_dict()


def color_fixtures(val):
    bg_color = 'background-color: '
    font_color = 'color: '
    if any(i in val for i in home_away_dict[1]):
        bg_color += '#147d1b'
    elif any(i in val for i in home_away_dict[2]):
        bg_color += '#00ff78'
    elif any(i in val for i in home_away_dict[3]):
        bg_color += '#eceae6'
    elif any(i in val for i in home_away_dict[4]):
        bg_color += '#ff0057'
        font_color += 'white'
    elif any(i in val for i in home_away_dict[5]):
        bg_color += '#920947'
        font_color += 'white'
    else:
        bg_color += ''
    style = bg_color + '; ' + font_color
    return style


st.dataframe(league_df.style.applymap(color_fixtures, subset=new_fixt_cols) \
             .format(subset=float_cols, formatter='{:.2f}'), height=740, width=1150)

