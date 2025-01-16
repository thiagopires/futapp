import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px

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

    indicadores = df_hist.columns[7:]
    indicadores.insert(0, "Selecione")

    operadores_opcoes = {
        "=": "Igual",
        ">": "Maior que",
        "<": "Menor que",
        ">=": "Maior ou igual",
        "<=": "Menor ou igual",
        "!=": "Diferente de"
    }
    operadores_formatados = [f"{descricao} ({simbolo})" for simbolo, descricao in operadores_opcoes.items()] 

    col1, col2 = st.columns(2)
    with col1: data_inicial = st.date_input("Data Inicial", date(2022, 2, 10))
    with col2: data_final = st.date_input("Data Final", get_today())

    leagues = sorted(df_hist['League'].unique())
    leagues.insert(0, 'Todas as Ligas')
    selected_leagues = st.multiselect("Filtrar por Liga", leagues, [leagues[0]])

    if data_final and data_final:
        df_hist = df_hist[(df_hist['Date'] >= pd.to_datetime(data_inicial)) & (df_hist['Date'] <= pd.to_datetime(data_final))]

    if not (not selected_leagues or "Todas as Ligas" in selected_leagues):
        df_hist = df_hist[df_hist['League'].isin(selected_leagues)]

    with st.expander("Filtros"):
        for i in range(1,7):
            cola, colb, colc = st.columns(3)
            with cola: st.selectbox("Indicador", indicadores, key=f"indicador_{i}")
            with colb: st.selectbox("Operador", operadores_formatados, key=f"operador_{i}")
            with colc: st.text_input("Digite o valor:", key=f"valor_{i}")

    metodo = st.selectbox("Método", [
        'Back Casa',
        'Back Visitante',
        'Lay Casa',
        'Lay Visitante',
        'Lay 0x1',
        'Lay 0x2',
        'Lay Goleada Visitante'
    ])

    condicao = st.radio("Condição", ["Favorito/Zebra", "Zebra/Favorito"])
    if condicao == "Favorito/Zebra":
        df_hist = df_hist[df_hist["Odd_H_FT"] < df_hist["Odd_A_FT"]]
    elif condicao == "Zebra/Favorito":
        df_hist = df_hist[df_hist["Odd_H_FT"] > df_hist["Odd_A_FT"]]

    if st.button("Executar"):

        for i in range(1,7):
            indicador = st.session_state[f'indicador_{i}']
            operador_selecionado = st.session_state[f'operador_{i}']
            valor = st.session_state[f'valor_{i}']

            if valor != "":
                st.caption(f"{indicador} {operador_selecionado} {valor}")

                if operador_selecionado == 'Igual (=)':
                    df_hist = df_hist[(df_hist[indicador] == float(valor))]
                if operador_selecionado == 'Maior que (>)':
                    df_hist = df_hist[(df_hist[indicador] > float(valor))]
                if operador_selecionado == 'Menor que (<)':
                    df_hist = df_hist[(df_hist[indicador] < float(valor))]
                if operador_selecionado == 'Maior ou igual (>=)':
                    df_hist = df_hist[(df_hist[indicador] >= float(valor))]
                if operador_selecionado == 'Menor ou igual (<=)':
                    df_hist = df_hist[(df_hist[indicador] <= float(valor))]
                if operador_selecionado == 'Diferente de (!=)':
                    df_hist = df_hist[(df_hist[indicador] != float(valor))]

                df_hist["Status_Metodo"] = "RED"
                df_hist['Profit'] = -1  
                
                if metodo == 'Back Casa':
                    filter = (df_hist["Goals_H_FT"] > df_hist["Goals_A_FT"])
                    df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_H_FT']-1, 2)
                    df_hist.loc[filter, "Status_Metodo"] = "GREEN"
                if metodo == 'Back Visitante':
                    filter = (df_hist["Goals_H_FT"] < df_hist["Goals_A_FT"])
                    df_hist.loc[filter, 'Profit'] = round(df_hist['Goals_A_FT']-1, 2)
                    df_hist.loc[filter, "Status_Metodo"] = "GREEN"
                if metodo == 'Lay Visitante':
                    filter = (df_hist['Goals_H_FT'] >= df_hist['Goals_A_FT'])  
                    df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_DC_1X']-1, 2)
                    df_hist.loc[filter, "Status_Metodo"] = "GREEN"
                if metodo == 'Lay Casa':
                    filter = (df_hist['Goals_H_FT'] <= df_hist['Goals_A_FT'])   
                    df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_DC_X2']-1, 2)
                    df_hist.loc[filter, "Status_Metodo"] = "GREEN"
                if metodo == 'Lay 0x1':
                    df_hist.loc[df_hist["Resultado_FT"] != '0-1', "Status_Metodo"] = "GREEN"
                if metodo == 'Lay 0x2':
                    df_hist.loc[df_hist["Resultado_FT"] != '0-2', "Status_Metodo"] = "GREEN"
                if metodo == 'Lay Goleada Visitante':
                    df_hist.loc[((df_hist['Goals_A_FT'] < 4) | (df_hist['Goals_A_FT'] <= df_hist['Goals_H_FT'])), "Status_Metodo"] = "GREEN"

        total_jogos = len(df_hist)
        total_greens = len(df_hist[(df_hist['Status_Metodo'] == 'GREEN')])
        total_reds = total_jogos - total_greens
        winrate = round(total_greens / total_jogos * 100, 2)
        profit_acumulado = f"{str(round(df_hist['Profit'].sum(), 2))} unidades"

        st.write(f"**Resultado:**")
        st.write(f"Jogos: {total_jogos}, Greens: {total_greens}, Reds: {total_reds}, Winrate: {winrate}%, Profit Acumulado: {profit_acumulado}")

        # Agrupar por data e somar os lucros
        daily_profit = df_hist.groupby("Formatted_Date")["Profit"].sum().reset_index()
        daily_profit = daily_profit.sort_values(by="Formatted_Date")

        # Criar o gráfico de linha com Plotly Express
        fig = px.line(
            daily_profit,
            x="Formatted_Date",
            y="Profit",
            title="Lucro Diário",
            labels={"Formatted_Date": "Data", "Profit": "Lucro"},
            markers=True  # Adiciona marcadores nos pontos
        )

        # Mostrar o gráfico no Streamlit
        st.plotly_chart(fig)

        st.write(f"GREENs:")
        print_dataframe(df_hist.loc[df_hist['Status_Metodo'] == 'GREEN'])

        st.write(f"REDs:")
        print_dataframe(df_hist.loc[df_hist['Status_Metodo'] == 'RED'])

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
