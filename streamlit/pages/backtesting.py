import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px

from utils.functions import *

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
st.set_page_config(layout="wide")

def main_page():

    st.title("⚽ Backtesting")

    ### FootyStats ###

    df_hist = load_histmatches()

    indicadores = df_hist.columns

    operadores_opcoes = {
        "=": "Igual",
        ">": "Maior que",
        "<": "Menor que",
        ">=": "Maior ou igual",
        "<=": "Menor ou igual",
        "!=": "Diferente de"
    }
    operadores_formatados = [f"{descricao} ({simbolo})" for simbolo, descricao in operadores_opcoes.items()] 

    st.write("**Selecione o período**")

    col1, col2, col3 = st.columns(3)
    with col1: data_inicial = st.date_input("Data Inicial", date(2022, 2, 10))
    with col2: data_final = st.date_input("Data Final", get_today())
    with col3:
        seasons = sorted(df_hist['Season'].unique())
        seasons.insert(0, 'Todas as Temporadas')
        selected_seasons = st.multiselect("Filtrar por Temporada", seasons, [seasons[0]])


    st.divider()


    st.write("**Indicadores**")

    with st.expander("Clique para expandir:"):

        leagues = sorted(df_hist['League'].unique())
        leagues.insert(0, 'Todas as Ligas')
        selected_leagues = st.multiselect("Filtrar por Liga", leagues, [leagues[0]])
        if not (not selected_seasons or "Todas as Temporadas" in selected_seasons):
            df_hist = df_hist[df_hist['Season'].isin(selected_seasons)]

        if data_final and data_final:
            df_hist = df_hist[(df_hist['Date'] >= pd.to_datetime(data_inicial)) & (df_hist['Date'] <= pd.to_datetime(data_final))]

        if not (not selected_leagues or "Todas as Ligas" in selected_leagues):
            df_hist = df_hist[df_hist['League'].isin(selected_leagues)]

        for i in range(1,9):
            cola, colb, colc, cold = st.columns(4)
            with cola: st.selectbox("Indicador", indicadores, key=f"indicador_{i}")
            with colb: st.selectbox("Tipo", ['Valor Absoluto', 'Valor Relativo'], key=f"tipo_{i}")
            with colc: st.selectbox("Operador", operadores_formatados, key=f"operador_{i}")
            with cold: st.text_input("Digite o valor ou Campo:", key=f"valor_{i}")

        col1, col2, col3 = st.columns(3)
        with col1:
            metodo = st.selectbox("Método", [
                'Back Casa',
                'Back Visitante',
                'Back Empate',
                'Lay Casa',
                'Lay Empate',
                'Lay Visitante',
                'Lay 0x1',
                'Lay 1x1',
                'Lay 0x2',
                'Lay 0x3',
                'Lay Goleada Visitante',
                'Over 0.5 HT',                
                'Under 0.5 HT',
                'Over 0.5 FT',
                'Over 1.5 FT',
                'Over 2.5 FT',
                'Under 1.5 FT',
                'Under 2.5 FT',
                'BTTS Sim',
                'BTTS Não'
            ])
        with col2:
            condicao = st.radio("Condição", ["Geral","Favorito/Zebra","Zebra/Favorito"], horizontal=True)
            if condicao == "Favorito/Zebra":
                df_hist = df_hist[(df_hist["Odd_H_FT"] < df_hist["Odd_A_FT"])]
            elif condicao == "Zebra/Favorito":
                df_hist = df_hist[(df_hist["Odd_H_FT"] > df_hist["Odd_A_FT"])]

        executar = st.button("Executar")
    
    string_indicadores = ""

    if executar:
        for i in range(1,9):
            indicador = st.session_state[f'indicador_{i}']
            tipo = st.session_state[f'tipo_{i}']
            operador_selecionado = st.session_state[f'operador_{i}']
            valor = st.session_state[f'valor_{i}']

            if valor != "":
                string_indicadores += f"{indicador} {operador_selecionado} {valor} | "

                if indicador != 'Primeiro_Gol_Marcador':
                    valor = float(valor)

                if operador_selecionado == 'Igual (=)':
                    filter = (df_hist[indicador] == valor) if tipo == 'Valor Absoluto' else (df_hist[indicador] == df_hist[valor])
                if operador_selecionado == 'Maior que (>)':
                    filter = (df_hist[indicador] > valor) if tipo == 'Valor Absoluto' else (df_hist[indicador] > df_hist[valor])
                if operador_selecionado == 'Menor que (<)':
                    filter = (df_hist[indicador] < valor) if tipo == 'Valor Absoluto' else (df_hist[indicador] < df_hist[valor])
                if operador_selecionado == 'Maior ou igual (>=)':
                    filter = (df_hist[indicador] >= valor) if tipo == 'Valor Absoluto' else (df_hist[indicador] >= df_hist[valor])
                if operador_selecionado == 'Menor ou igual (<=)':
                    filter = (df_hist[indicador] <= valor) if tipo == 'Valor Absoluto' else (df_hist[indicador] <= df_hist[valor])
                if operador_selecionado == 'Diferente de (!=)':
                    filter = (df_hist[indicador] != valor) if tipo == 'Valor Absoluto' else (df_hist[indicador] != df_hist[valor])

                df_hist = df_hist[filter]

    st.caption(string_indicadores)


    st.divider()


    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_pronto_selecionado = st.selectbox("Filtros Prontos", [
            "Sem filtro",
            "Lay Visitante Zebra",
            'Lay Visitante v2',
            "Back Casa",
            "Back Empate",
            'Over 2.5 FT',
            # 'Under 2.5 FT',
            'BTTS Sim',
            'Lay 0x1 (até 80min)',
            'Lay 0x2 (até 80min)',
            'Lay 0x3 (até 80min)',
            # 'BTTS Não',
            
        ])

    if filtro_pronto_selecionado == "Lay Visitante Zebra":
        filter = get_filter_lay_visitante_zebra(df_hist)
        df_hist = df_hist[filter]
        condicao = 'Geral'
        metodo = 'Lay Visitante'

    elif filtro_pronto_selecionado == "Over 2.5 FT":
        filter = get_filter_over(df_hist)
        df_hist = df_hist[filter]
        condicao = 'Geral'
        metodo = 'Over 2.5 FT'

    elif filtro_pronto_selecionado == "Under 2.5 FT":
        filter = get_filter_under(df_hist)
        df_hist = df_hist[filter]
        condicao = 'Geral'
        metodo = 'Under 2.5 FT'

    elif filtro_pronto_selecionado == "BTTS Sim":
        filter = get_filter_btts_yes(df_hist)
        df_hist = df_hist[filter]
        condicao = 'Geral'
        metodo = 'BTTS Sim'
    
    # elif filtro_pronto_selecionado == "BTTS Não":
    #     filter = get_filter_btts_no(df_hist)
    #     df_hist = df_hist[filter]
    #     condicao = 'Geral'
    #     metodo = 'BTTS Não' 
    
    elif filtro_pronto_selecionado == "Back Empate":
        filter = get_filter_back_empate(df_hist)
        df_hist = df_hist[filter]
        condicao = 'Geral'
        metodo = 'Back Empate'
    
    elif filtro_pronto_selecionado == "Lay 0x1 (até 80min)":
        filter = get_filter_lay_0x1(df_hist)
        df_hist = df_hist[filter]
        condicao = 'Geral'
        metodo = 'Lay 0x1'
    
    elif filtro_pronto_selecionado == "Lay 0x2 (até 80min)":
        filter = get_filter_lay_0x2(df_hist)
        df_hist = df_hist[filter]
        condicao = 'Geral'
        metodo = 'Lay 0x2'

    elif filtro_pronto_selecionado == "Lay 0x3 (até 80min)":
        filter = get_filter_lay_0x3(df_hist)
        df_hist = df_hist[filter]
        condicao = 'Geral'
        metodo = 'Lay 0x3'

    elif filtro_pronto_selecionado == "Back Casa":
        filter = get_filter_back_casa(df_hist)
        df_hist = df_hist[filter]
        condicao = 'Geral'
        metodo = 'Back Casa'

    elif filtro_pronto_selecionado == "Lay Visitante v2":
        filter = get_filter_lay_visitante_v2(df_hist)
        df_hist = df_hist[filter]
        condicao = 'Geral'
        metodo = 'Lay Visitante'


    st.divider()


    if filtro_pronto_selecionado != "Sem filtro" or executar:
        
        df_hist["Status_Metodo"] = "RED"
        df_hist['Profit'] = -1.0
        odd_media = ""

        if metodo == 'Back Casa':
            filter = (df_hist["Goals_H_FT"] > df_hist["Goals_A_FT"])
            df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_H_FT']-1, 2)
            df_hist.loc[filter, "Status_Metodo"] = "GREEN"
            odd_media = f"{str(round(df_hist['Odd_H_FT'].mean(), 2))}"
        if metodo == 'Back Empate':
            filter = (df_hist["Goals_H_FT"] == df_hist["Goals_A_FT"])
            df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_D_FT']-1, 2)
            df_hist.loc[filter, "Status_Metodo"] = "GREEN"
            odd_media = f"{str(round(df_hist['Odd_D_FT'].mean(), 2))}"
        if metodo == 'Back Visitante':
            filter = (df_hist["Goals_H_FT"] < df_hist["Goals_A_FT"])
            df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_A_FT']-1, 2)
            df_hist.loc[filter, "Status_Metodo"] = "GREEN"
            odd_media = f"{str(round(df_hist['Odd_A_FT'].mean(), 2))}"
        if metodo == 'Lay Visitante':
            filter = (df_hist['Goals_H_FT'] >= df_hist['Goals_A_FT'])  
            df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_DC_1X']-1, 2)
            df_hist.loc[filter, "Status_Metodo"] = "GREEN"
            odd_media = f"{str(round(df_hist['Odd_A_FT'].mean(), 2))}"
        if metodo == 'Lay Empate':
            filter = (df_hist['Goals_H_FT'] != df_hist['Goals_A_FT'])  
            df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_DC_12']-1, 2)
            df_hist.loc[filter, "Status_Metodo"] = "GREEN"
            odd_media = f"{str(round(df_hist['Odd_D_FT'].mean(), 2))}"
        if metodo == 'Lay Casa':
            filter = (df_hist['Goals_H_FT'] <= df_hist['Goals_A_FT'])   
            df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_DC_X2']-1, 2)
            df_hist.loc[filter, "Status_Metodo"] = "GREEN"
            odd_media = f"{str(round(df_hist['Odd_H_FT'].mean(), 2))}"
        if metodo == 'Over 0.5 HT':
            filter = (df_hist['TotalGoals_HT'] >= 0.5)   
            df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_Over05_HT']-1, 2)
            df_hist.loc[filter, "Status_Metodo"] = "GREEN"
            odd_media = f"{str(round(df_hist['Odd_Over05_HT'].mean(), 2))}"
        if metodo == 'Over 0.5 FT':
            filter = (df_hist['TotalGoals_FT'] >= 0.5)   
            df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_Over05_FT']-1, 2)
            df_hist.loc[filter, "Status_Metodo"] = "GREEN"
            odd_media = f"{str(round(df_hist['Odd_Over05_FT'].mean(), 2))}"
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
        if metodo == 'Under 0.5 HT':
            filter = (df_hist['TotalGoals_HT'] <= 0.5)   
            df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_Under05_HT']-1, 2)
            df_hist.loc[filter, "Status_Metodo"] = "GREEN"
            odd_media = f"{str(round(df_hist['Odd_Under05_HT'].mean(), 2))}"
        if metodo == 'Under 1.5 FT':
            filter = (df_hist['TotalGoals_FT'] <= 1.5)   
            df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_Under15_FT']-1, 2)
            df_hist.loc[filter, "Status_Metodo"] = "GREEN"
            odd_media = f"{str(round(df_hist['Odd_Under15_FT'].mean(), 2))}"
        if metodo == 'Under 2.5 FT':
            filter = (df_hist['TotalGoals_FT'] <= 2.5)   
            df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_Under25_FT']-1, 2)
            df_hist.loc[filter, "Status_Metodo"] = "GREEN"
            odd_media = f"{str(round(df_hist['Odd_Under25_FT'].mean(), 2))}"
        if metodo == 'BTTS Sim':
            filter = ((df_hist['Goals_H_FT'] >= 1) & (df_hist['Goals_A_FT'] >= 1))
            df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_BTTS_Yes']-1, 2)
            df_hist.loc[filter, "Status_Metodo"] = "GREEN"
            odd_media = f"{str(round(df_hist['Odd_BTTS_Yes'].mean(), 2))}"
        if metodo == 'BTTS Não':
            filter = ((df_hist['Goals_H_FT'] == 0) | (df_hist['Goals_A_FT'] == 0))
            df_hist.loc[filter, 'Profit'] = round(df_hist['Odd_BTTS_No']-1, 2)
            df_hist.loc[filter, "Status_Metodo"] = "GREEN"
            odd_media = f"{str(round(df_hist['Odd_BTTS_No'].mean(), 2))}"
        if metodo == 'Lay 0x1':
            # df_hist.loc[((df_hist["Resultado_FT"] != '0-1') & (df_hist["Resultado_80"] != '0-1')), "Status_Metodo"] = "GREEN"
            df_hist.loc[(df_hist["Resultado_80"] != '0-1'), "Status_Metodo"] = "GREEN"
            df_hist['Profit'] = 0
        if metodo == 'Lay 1x1':
            # df_hist.loc[((df_hist["Resultado_FT"] != '1-1') & (df_hist["Resultado_80"] != '1-1')), "Status_Metodo"] = "GREEN"
            df_hist.loc[
                (df_hist["Resultado_60"] != '1-1') &
                (df_hist["Primeiro_Gol_Minuto"] < 45) &
                (df_hist["Primeiro_Gol_Marcador"] == "Home"), "Status_Metodo"] = "GREEN"
            df_hist['Profit'] = 0
        if metodo == 'Lay 0x2':
            df_hist.loc[df_hist["Resultado_80"] != '0-2', "Status_Metodo"] = "GREEN"
            df_hist['Profit'] = 0
        if metodo == 'Lay 0x3':
            df_hist.loc[df_hist["Resultado_80"] != '0-3', "Status_Metodo"] = "GREEN"
            df_hist['Profit'] = 0
        if metodo == 'Lay Goleada Visitante':
            df_hist.loc[((df_hist['Goals_A_FT'] < 4) | (df_hist['Goals_A_FT'] <= df_hist['Goals_H_FT'])), "Status_Metodo"] = "GREEN"
            df_hist['Profit'] = 0

        st.write(f"**Resultado:**")

        total_jogos = len(df_hist)
        
        if total_jogos > 0:
            total_greens = len(df_hist[(df_hist['Status_Metodo'] == 'GREEN')])
            total_reds = total_jogos - total_greens
            winrate = round(total_greens / total_jogos * 100, 2)
            profit_acumulado = f"{str(round(df_hist['Profit'].sum(), 2))} unidades"

            
            st.write(f"Jogos: {total_jogos}, Greens: {total_greens}, Reds: {total_reds}, Winrate: {winrate}%, Profit Acumulado: {profit_acumulado}, Odd Média: {odd_media}")

            daily_profit = df_hist.groupby("Date")["Profit"].sum().reset_index()
            daily_profit["Cumulative_Profit"] = daily_profit["Profit"].cumsum()  

            # fig = px.line(
            #     daily_profit,
            #     x="Date",
            #     y="Cumulative_Profit",
            #     title="Lucro Diário",
            #     labels={"Date": "Data", "Cumulative_Profit": "Unidades/Stakes"},
            #     markers=True  # Adiciona marcadores nos pontos
            # )
            # st.plotly_chart(fig)

            fig = px.line(
                daily_profit,
                x="Date",
                y="Cumulative_Profit",
                title="Lucro Diário",
                labels={"Date": "Data", "Cumulative_Profit": "Unidades/Stakes"},
                markers=True
            )

            fig.update_layout(
                template="plotly_white",
                title={
                    "text": "Lucro Diário",
                    "y": 0.9,
                    "x": 0.5,
                    "xanchor": "center",
                    "yanchor": "top",
                    "font": {"size": 24, "color": "darkblue"}
                },
                xaxis=dict(showgrid=True, gridcolor="lightgray"),
                yaxis=dict(showgrid=True, gridcolor="lightgray"),
                xaxis_title="Data",
                yaxis_title="Unidades/Stakes",
                font=dict(family="Arial", size=14),
                plot_bgcolor="white",
                legend=dict(
                    title="Legenda",
                    orientation="h",
                    x=0.5, y=-0.2,
                    xanchor="center",
                    yanchor="top",
                    borderwidth=1,
                )
            )

            fig.update_traces(
                line=dict(color="blue", width=2),
                marker=dict(size=8, symbol="circle", color="red"),
                hovertemplate="<b>Data:</b> %{x}<br><b>Lucro:</b> %{y}<extra></extra>"
            )

            st.plotly_chart(fig)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**Profit por Liga/Mês**")
                report = df_hist.groupby(["League", "Month_Year"])["Profit"].sum().reset_index()
                st.dataframe(report)
            with col2:
                st.write("**Profit acumulado por Liga**")
                report = df_hist.groupby(["League"])["Profit"].sum().reset_index()
                report = report.sort_values(by="Profit", ascending=False)
                report["Cumulative_Profit"] = report["Profit"].cumsum()
                st.dataframe(report)
            with col3:
                st.write("**Resultado por Liga**")
                report = df_hist.groupby(["League", "Status_Metodo"]).size().unstack(fill_value=0).reset_index()
                # report["Cumulative_Profit"] = report["Profit"].cumsum()
                st.dataframe(report)

            st.write(f"**:green[GREENs:]**")
            print_dataframe(
                df_hist.loc[df_hist['Status_Metodo'] == 'GREEN', 
                ['League','Rodada','Date','Time','Home','Away','Resultado_HT','Resultado_FT','Resultado_60','Resultado_70','Resultado_75','Resultado_80','Odd_H_FT','Odd_D_FT','Odd_A_FT','Odd_Over05_FT','Odd_Over15_FT','Odd_Over25_FT','Odd_Under05_FT','Odd_Under15_FT','Odd_Under25_FT','Odd_BTTS_Yes','Odd_BTTS_No','Odd_DC_1X','Odd_DC_12','Odd_DC_X2','XG_Total_Pre','XG_Home_Pre','XG_Away_Pre','Diff_XG_Home_Away_Pre','PPG_Home_Pre','PPG_Away_Pre','Goals_H_Minutes','Goals_A_Minutes','Primeiro_Gol','Status_Metodo','Profit','Probabilidade_H_FT','Probabilidade_D_FT','Probabilidade_A_FT','CV_HDA_FT']]
            )

            st.write(f"**:red[REDs:]**")
            print_dataframe(
                df_hist.loc[df_hist['Status_Metodo'] == 'RED', 
                ['League','Rodada','Date','Time','Home','Away','Resultado_HT','Resultado_FT','Resultado_60','Resultado_70','Resultado_75','Resultado_80','Odd_H_FT','Odd_D_FT','Odd_A_FT','Odd_Over05_FT','Odd_Over15_FT','Odd_Over25_FT','Odd_Under05_FT','Odd_Under15_FT','Odd_Under25_FT','Odd_BTTS_Yes','Odd_BTTS_No','Odd_DC_1X','Odd_DC_12','Odd_DC_X2','XG_Total_Pre','XG_Home_Pre','XG_Away_Pre','Diff_XG_Home_Away_Pre','PPG_Home_Pre','PPG_Away_Pre','Goals_H_Minutes','Goals_A_Minutes','Primeiro_Gol','Status_Metodo','Profit','Probabilidade_H_FT','Probabilidade_D_FT','Probabilidade_A_FT','CV_HDA_FT']]
            )

        else:
            st.write("Sem jogos.")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    display_sidebar('block')
    main_page()
else:
    login_page()


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
