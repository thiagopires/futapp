import streamlit as st
import pandas as pd
from datetime import date

from utils.functions import *

if "authenticated" not in st.session_state or st.session_state.authenticated == False:
    st.write("Faça o login na página 'app'.")
else:
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    st.set_page_config(layout="wide")
    st.title("⚽ Backtesting")

    ### FootyStats ###

    df_hist = load_histmatches()

    operadores_opcoes = {
        "=": "igual",
        ">": "maior que",
        "<": "menor que",
        ">=": "maior ou igual",
        "<=": "menor ou igual",
        "!=": "diferente de"
    }
    operadores_formatados = [f"{descricao} ({simbolo})" for simbolo, descricao in operadores_opcoes.items()]  

    for i in range(1,6):
        cola, colb, colc = st.columns(4)
        with cola: indicador = st.selectbox("Indicador", df_hist.columns[7:], key=f"indicador_{i}")
        with colb: operador_selecionado = st.selectbox("Operador", operadores_formatados, key=f"operador_{i}")
        with colc: valor = st.text_input("Digite o valor:", key=f"valor_{i}")

    if st.button("Salvar"):
        if operador_selecionado == 'igual (=)':
            df_hist = df_hist[(df_hist[indicador] == float(valor))]
        if operador_selecionado == 'maior que (>)':
            df_hist = df_hist[(df_hist[indicador] > float(valor))]
        if operador_selecionado == 'menor que (<)':
            df_hist = df_hist[(df_hist[indicador] < float(valor))]
        if operador_selecionado == 'maior ou igual (>=)':
            df_hist = df_hist[(df_hist[indicador] >= float(valor))]
        if operador_selecionado == 'menor ou igual (<=)':
            df_hist = df_hist[(df_hist[indicador] <= float(valor))]
        if operador_selecionado == 'diferente de (!=)':
            df_hist = df_hist[(df_hist[indicador] != float(valor))]

    # col1, col2 = st.columns(2)
    # with col1:
    #     data_inicial = st.date_input("Data Inicial", date(2022, 2, 10))
    # with col2:
    #     data_final = st.date_input("Data Final", get_today())

    # df_hist = df_hist[(df_hist['Date'] >= pd.to_datetime(data_inicial)) & (df_hist['Date'] <= pd.to_datetime(data_final))]

    # leagues = sorted(df_hist['League'].unique())
    # leagues.insert(0, 'Todas as Ligas')
    # selected_leagues = st.multiselect("Filtrar por Liga", leagues, [leagues[0]])

    # if not (not selected_leagues or "Todas as Ligas" in selected_leagues):
    #     df_hist = df_hist[df_hist['League'].isin(selected_leagues)]

    # seasons = sorted(df_hist['Season'].unique())
    # seasons.insert(0, 'Todas as Temporadas')
    # selected_seasons = st.multiselect("Filtrar por Temporada", seasons, [seasons[0]])

    # if not (not selected_seasons or "Todas as Temporadas" in selected_seasons):
    #     df_hist = df_hist[df_hist['Season'].isin(selected_seasons)]

    print_dataframe(df_hist)


    ### football-data.co.uk ###

    # st.sidebar.header("Filtros")
    # selected_league = st.sidebar.selectbox('Escolha uma liga', ['England','Germany','Italy','Spain','France'])
    # selected_season = st.sidebar.selectbox('Escolha uma temporada', ['2024/2025','2023/2024','2022/2023','2021/2022','2020/2021'])

    # def drop_reset_index(df):
    #     df = df.dropna()
    #     df = df.reset_index(drop=True)
    #     df.index += 1
    #     return df

    # def load_data(league, season):

    #   match league:
    #     case 'England':
    #       league = 'E0'
    #     case 'Germany':
    #       league = 'D1'
    #     case 'Italy':
    #       league = 'I1'
    #     case 'Spain':
    #       league = 'SP1'
    #     case 'France':
    #       league = 'F1'

    #   url = f"https://www.football-data.co.uk/mmz4281/{season[2:4]}{season[7:9]}/{league}.csv"
    #   data = pd.read_csv(url)
    #   return data

    # df = load_data(selected_league, selected_season)

    # df = df[['Div','Date','Time','HomeTeam','AwayTeam','HTHG','HTAG','HTR','FTHG','FTAG','FTR',
    # 'BFEH','BFED','BFEA','BFE>2.5','BFE<2.5','AHh','BFEAHH','BFEAHA']]

    # df.columns = ['League','Date','Time','Home','Away','Goals_H_HT','Goals_A_HT','Result_HT','Goals_H_FT','Goals_A_FT','Result_FT',
    # 'Odd_H_Open','Odd_D_Open','Odd_A_Open','Odd_Over25_Open','Odd_Under25_Open','Asian_Handicap_Open','Odd_AHH_Open','Odd_AHA_Open']

    # df = drop_reset_index(df)

    # st.subheader(f"Dataframe: {selected_league} - {selected_season}")

    # st.dataframe(df)
