import streamlit as st
import pandas as pd
import numpy as np

st.title("Web App Football Data")

st.sidebar.header("Leagues")
selected_league = st.sidebar.selectbox('League', ['England','Germany','Italy','Spain','France'])

st.sidebar.header("Season")
selected_season = st.sidebar.selectbox('Season', ['2024/2025','2023/2024','2022/2023','2021/2022','2020/2021'])

def load_data(league, season):

  match league:
    case 'England':
      league = 'E0'
    case 'Germany':
      league = 'D1'
    case 'Italy':
      league = 'I1'
    case 'Spain':
      league = 'SP1'
    case 'France':
      league = 'F1'

  season = season[2,2]+season[7,2]
  
  url = f"https://www.football-data.co.uk/mmz4281/{season}/{league}.csv"
  data = pd.read_csv(url)
  return data

df = load_data(selected_league, selected_season)

st.subheader(f"Dataframe: {selected_league} - {selected_season}")

st.dataframe(df)
