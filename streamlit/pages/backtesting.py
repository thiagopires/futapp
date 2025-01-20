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

    indicadores = df_hist.columns
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

    col1, col2, col3 = st.columns(3)
    with col1: data_inicial = st.date_input("Data Inicial", date(2022, 2, 10))
    with col2: data_final = st.date_input("Data Final", get_today())
    with col3:
        seasons = sorted(df_hist['Season'].unique())
        seasons.insert(0, 'Todas as Temporadas')
        selected_seasons = st.multiselect("Filtrar por Temporada", seasons, [seasons[0]])

    leagues = sorted(df_hist['League'].unique())
    leagues.insert(0, 'Todas as Ligas')
    selected_leagues = st.multiselect("Filtrar por Liga", leagues, [leagues[0]])
    if not (not selected_seasons or "Todas as Temporadas" in selected_seasons):
        df_hist = df_hist[df_hist['Season'].isin(selected_seasons)]

    if data_final and data_final:
        df_hist = df_hist[(df_hist['Date'] >= pd.to_datetime(data_inicial)) & (df_hist['Date'] <= pd.to_datetime(data_final))]

    if not (not selected_leagues or "Todas as Ligas" in selected_leagues):
        df_hist = df_hist[df_hist['League'].isin(selected_leagues)]

    with st.expander("Monte o seu filtro:"):
        for i in range(1,9):
            cola, colb, colc, cold = st.columns(4)
            with cola: st.selectbox("Indicador", indicadores, key=f"indicador_{i}")
            with colb: st.selectbox("Tipo", ['Valor Absoluto', 'Valor Relativo'], key=f"tipo_{i}")
            with colc: st.selectbox("Operador", operadores_formatados, key=f"operador_{i}")
            with cold: st.text_input("Digite o valor ou Campo:", key=f"valor_{i}")

    metodo = st.selectbox("Método", [
        'Back Casa',
        'Back Visitante',
        'Lay Casa',
        'Lay Visitante',
        'Lay 0x1',
        'Lay 0x2',
        'Lay Goleada Visitante',
        'Over 0.5 HT',
        'Over 1.5 FT',
        'Over 2.5 FT'
    ])

    # condicao = st.radio("Condição", ["Favorito/Zebra", "Zebra/Favorito"])
    # if condicao == "Favorito/Zebra":
    #     df_hist = df_hist[(df_hist["Odd_H_FT"] < df_hist["Odd_D_FT"]) & (df_hist["Odd_D_FT"] < df_hist["Odd_A_FT"])]
    # elif condicao == "Zebra/Favorito":
    #     df_hist = df_hist[(df_hist["Odd_H_FT"] > df_hist["Odd_D_FT"]) & (df_hist["Odd_D_FT"] > df_hist["Odd_A_FT"])]

    executar = st.button("Executar")
    if executar:
        for i in range(1,9):
            indicador = st.session_state[f'indicador_{i}']
            tipo = st.session_state[f'tipo_{i}']
            operador_selecionado = st.session_state[f'operador_{i}']
            valor = st.session_state[f'valor_{i}']

            if valor != "":
                st.caption(f"{indicador} {operador_selecionado} {valor}")

                if operador_selecionado == 'Igual (=)':
                    filter = (df_hist[indicador] == float(valor)) if tipo == 'Valor Absoluto' else (df_hist[indicador] == df_hist[valor])
                if operador_selecionado == 'Maior que (>)':
                    filter = (df_hist[indicador] > float(valor)) if tipo == 'Valor Absoluto' else (df_hist[indicador] > df_hist[valor])
                if operador_selecionado == 'Menor que (<)':
                    filter = (df_hist[indicador] < float(valor)) if tipo == 'Valor Absoluto' else (df_hist[indicador] < df_hist[valor])
                if operador_selecionado == 'Maior ou igual (>=)':
                    filter = (df_hist[indicador] >= float(valor)) if tipo == 'Valor Absoluto' else (df_hist[indicador] >= df_hist[valor])
                if operador_selecionado == 'Menor ou igual (<=)':
                    filter = (df_hist[indicador] <= float(valor)) if tipo == 'Valor Absoluto' else (df_hist[indicador] <= df_hist[valor])
                if operador_selecionado == 'Diferente de (!=)':
                    filter = (df_hist[indicador] != float(valor)) if tipo == 'Valor Absoluto' else (df_hist[indicador] != df_hist[valor])

                df_hist = df_hist[filter]
    
    st.divider()


    st.write("**Filtros Prontos**")

    # filtro_lay_casa_zebra = st.checkbox("Lay Casa Zebra")
    # if filtro_lay_casa_zebra:
    #     filter = get_filter_lay_casa_zebra(df_hist)
    #     df_hist = df_hist[filter] 
    #     metodo = 'Lay Casa'

    filtro_lay_visitante_zebra = st.checkbox("Lay Visitante Zebra")
    if filtro_lay_visitante_zebra:
        filter = get_filter_lay_visitante_zebra(df_hist)
        df_hist = df_hist[filter] 
        metodo = 'Lay Visitante'

    
    st.divider()


    if filtro_lay_visitante_zebra or filtro_lay_casa_zebra or executar:            
        
        df_hist["Status_Metodo"] = "RED"
        df_hist['Profit'] = -1
        odd_media = ""

        if metodo == 'Back Casa':
            filter = (df_hist["Goals_H_FT"] > df_hist["Goals_A_FT"])
            df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_H_FT']-1, 2)
            df_hist.loc[filter, "Status_Metodo"] = "GREEN"
            odd_media = f"{str(round(df_hist['Odd_H_FT'].mean(), 2))}"
        if metodo == 'Back Visitante':
            filter = (df_hist["Goals_H_FT"] < df_hist["Goals_A_FT"])
            df_hist.loc[filter, 'Profit'] = round(df_hist['Goals_A_FT']-1, 2)
            df_hist.loc[filter, "Status_Metodo"] = "GREEN"
            odd_media = f"{str(round(df_hist['Odd_A_FT'].mean(), 2))}"
        if metodo == 'Lay Visitante':
            filter = (df_hist['Goals_H_FT'] >= df_hist['Goals_A_FT'])  
            df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_DC_1X']-1, 2)
            df_hist.loc[filter, "Status_Metodo"] = "GREEN"
            odd_media = f"{str(round(df_hist['Odd_A_FT'].mean(), 2))}"
        if metodo == 'Lay Casa':
            filter = (df_hist['Goals_H_FT'] <= df_hist['Goals_A_FT'])   
            df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_DC_X2']-1, 2)
            df_hist.loc[filter, "Status_Metodo"] = "GREEN"
            odd_media = f"{str(round(df_hist['Odd_H_FT'].mean(), 2))}"
        if metodo == 'Over 0.5 HT':
            filter = (df_hist['TotalGoals_HT'] >= 1.5)   
            df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_Over05_HT']-1, 2)
            df_hist.loc[filter, "Status_Metodo"] = "GREEN"
            odd_media = f"{str(round(df_hist['Odd_Over05_HT'].mean(), 2))}"
        if metodo == 'Over 1.5 FT':
            filter = (df_hist['TotalGoals_FT'] >= 1.5)   
            df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_Over15_FT']-1, 2)
            df_hist.loc[filter, "Status_Metodo"] = "GREEN"
            odd_media = f"{str(round(df_hist['Odd_Over15_FT'].mean(), 2))}"
        if metodo == 'Over 2.5 FT':
            filter = (df_hist['TotalGoals_FT'] >= 2.5)   
            df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_Over25_FT']-1, 2)
            df_hist.loc[filter, "Status_Metodo"] = "GREEN"
            odd_media = f"{str(round(df_hist['Odd_Over25_FT'].mean(), 2))}"
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
        st.write(f"Jogos: {total_jogos}, Greens: {total_greens}, Reds: {total_reds}, Winrate: {winrate}%, Profit Acumulado: {profit_acumulado}, Odd Média: {odd_media}")

        daily_profit = df_hist.groupby("Date")["Profit"].sum().reset_index()
        daily_profit["Cumulative_Profit"] = daily_profit["Profit"].cumsum()  

        fig = px.line(
            daily_profit,
            x="Date",
            y="Cumulative_Profit",
            title="Lucro Diário",
            labels={"Date": "Data", "Cumulative_Profit": "Unidades/Stakes"},
            markers=True  # Adiciona marcadores nos pontos
        )
        st.plotly_chart(fig)

        st.write(f"**:green[GREENs:]**")
        print_dataframe(df_hist.loc[df_hist['Status_Metodo'] == 'GREEN'])

        st.write(f"**:red[REDs:]**")
        print_dataframe(df_hist.loc[df_hist['Status_Metodo'] == 'RED'])

        st.write("**Detalhes**")

        report = df_hist.groupby(["League", "Month_Year"])["Profit"].sum().reset_index()
        report["Cumulative_Profit"] = report["Profit"].cumsum()
        st.dataframe(report)  

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
