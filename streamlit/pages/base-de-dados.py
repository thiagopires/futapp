import streamlit as st
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

st.set_page_config(layout="wide")

st.title("⚽ Base de dados")

st.sidebar.header("Filtros")
selected_league = st.sidebar.selectbox('Escolha uma liga', ['England','Germany','Italy','Spain','France'])
selected_season = st.sidebar.selectbox('Escolha uma temporada', ['2024/2025','2023/2024','2022/2023','2021/2022','2020/2021'])

def drop_reset_index(df):
    df = df.dropna()
    df = df.reset_index(drop=True)
    df.index += 1
    return df

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

  url = f"https://www.football-data.co.uk/mmz4281/{season[2:4]}{season[7:9]}/{league}.csv"
  data = pd.read_csv(url)
  return data

df = load_data(selected_league, selected_season)

df = df[['Div','Date','Time','HomeTeam','AwayTeam','HTHG','HTAG','HTR','FTHG','FTAG','FTR',
'BFEH','BFED','BFEA','BFE>2.5','BFE<2.5','AHh','BFEAHH','BFEAHA']]

df.columns = ['League','Date','Time','Home','Away','Goals_H_HT','Goals_A_HT','Result_HT','Goals_H_FT','Goals_A_FT','Result_FT',
'Odd_H_Open','Odd_D_Open','Odd_A_Open','Odd_Over25_Open','Odd_Under25_Open','Asian_Handicap_Open','Odd_AHH_Open','Odd_AHA_Open']

df = drop_reset_index(df)

st.subheader(f"Dataframe: {selected_league} - {selected_season}")

st.dataframe(df)
