import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px
import random

from utils.functions import *
from utils.filters import *

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
st.set_page_config(layout="wide")

def main_page():

    if st.secrets['ENV'] == 'dev':
        st.info("Ambiente de Desenvolvimento. Branch: dev")

    st.title("Futapp v0.1")
    st.header("⚽ Backtesting")

    fonte_dados = st.selectbox("Fonte de Dados", ['Betfair','FootyStats'])
    df_hist = load_histmatches(fonte_dados)

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
    with col1: data_inicial = st.date_input("Data Inicial", date(2024, 7, 1))
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
            metodo = st.selectbox("Método", metodos)
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
        filtro_pronto_selecionado = st.selectbox("Filtros Prontos", filtros_prontos)

    df_hist, condicao, metodo = get_details_filtro_pronto(df_hist, condicao, metodo, filtro_pronto_selecionado)


    st.divider()


    if filtro_pronto_selecionado != "Sem filtro" or executar:
        
        df_hist, odd_media = get_result_filtro_pronto(df_hist, metodo)

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
                    "font": {"size": 24}
                },
                xaxis=dict(showgrid=True, gridcolor="lightgray"),
                yaxis=dict(showgrid=True, gridcolor="lightgray"),
                xaxis_title="Data",
                yaxis_title="Unidades/Stakes",
                font=dict(family="Arial", size=14),
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
                line=dict(width=2),
                marker=dict(size=8, symbol="circle", color="red"),
                hovertemplate="<b>Data:</b> %{x}<br><b>Lucro:</b> %{y}<extra></extra>"
            )

            st.plotly_chart(fig)

            col1, col2 = st.columns(2)
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

            col1, col2 = st.columns(2)
            with col1:
                st.write("**Resultado por Liga**")
                report = df_hist.groupby(["League", "Status_Metodo"]).size().unstack(fill_value=0).reset_index()
                report['Winrate'] = round((report['GREEN'] / (report['GREEN'] + report['RED'])) * 100, 2)
                # report["Cumulative_Profit"] = report["Profit"].cumsum()
                st.dataframe(report)
            with col1:
                st.write("**Resultado por FX (Prob, CV) do MO**")
                report = df_hist.groupby(["League", "FX_Probabilidade_A", "FX_CV_HDA", "Status_Metodo"]).size().unstack(fill_value=0).reset_index()
                report = report[report['GREEN'] + report['RED'] > 0]
                report['Winrate'] = round((report['GREEN'] / (report['GREEN'] + report['RED'])) * 100, 2)
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
            st.info("Sem jogos.")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    display_sidebar('block')
    main_page()
else:
    login_page()