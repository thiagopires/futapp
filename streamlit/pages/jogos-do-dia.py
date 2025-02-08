import streamlit as st
import pandas as pd
import plotly.express as px

from utils.functions import *
from utils.filters import *

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
st.set_page_config(layout="wide")
set_dark_theme()

def main_page():

    if st.secrets['ENV'] == 'dev':
        st.info("Ambiente de Desenvolvimento. Branch: dev")

    st.title("Futapp v0.1")
    st.header("⚽ Jogos do dia")

    # Init

    data_analise = st.date_input("Data da Análise", get_today())
    df_matches = load_daymatches(data_analise)
    df_hist = load_histmatches()

    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_pronto_selecionado = st.selectbox("Filtros Prontos", filtros_prontos)

    df_matches, condicao, metodo = get_details_filtro_pronto(df_matches, None, None, filtro_pronto_selecionado)
    
    # Dataframe
    st.subheader(f"Selecione o jogo para abrir detalhes abaixo:")
    match_selected = st.dataframe(
        df_matches[['League','Rodada','Time','Home','Away','Odd_H_FT','Odd_D_FT','Odd_A_FT','Odd_Over25_FT','Odd_Under25_FT','Odd_BTTS_Yes','Odd_BTTS_No','XG_Total_Pre','XG_Home_Pre','XG_Away_Pre','Odd_DC_1X','Odd_DC_12','Odd_DC_X2']]
        , on_select="rerun"
        , selection_mode="single-row"
        , use_container_width=True
        , hide_index=True
    )

    st.write(f"Quantidade de jogos: {len(df_matches)}")

    if match_selected.get('selection').get('rows'):

        df_match_selected = df_matches.iloc[match_selected.get('selection').get('rows')[0]]

        st.divider()

        # Header
        st.header(f'{df_match_selected["Confronto"].split("-")[1]}')
        st.write(f"{df_match_selected['Formatted_Datetime']} - {df_match_selected["League"]} (Rodada {df_match_selected["Rodada"]})")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Indicadores")
            col11, col12, col13, col14 = st.columns(4)
            col11.metric(label="MO Home", value=df_match_selected["Odd_H_FT"])
            col12.metric(label="MO Draw", value=df_match_selected["Odd_D_FT"])
            col13.metric(label="MO Away", value=df_match_selected["Odd_A_FT"])
            col11.metric(label="Over 0.5 HT", value=df_match_selected["Odd_Over05_HT"])
            col12.metric(label="Over 2.5 FT", value=df_match_selected["Odd_Over25_FT"])
            col13.metric(label="BTTS", value=df_match_selected["Odd_BTTS_Yes"])
        with col2:
            st.subheader("Confrontos diretos nos últimos 3 anos")
            filter_confrontos = (df_hist["Home"].isin([df_match_selected["Home"], df_match_selected["Away"]])) & (df_hist["Away"].isin([df_match_selected["Home"], df_match_selected["Away"]]))
            confrontos = df_hist.loc[filter_confrontos, ["Date", "Season", "Home", "Resultado_FT", "Away"]].sort_values(by="Date", ascending=False)
            df_confrontos = confrontos.style.apply(highlight_result, axis=1, highlight=df_match_selected["Home"])
            print_dataframe(df_confrontos)

        filter_ultimos_casa = (df_match_selected["Home"] == df_hist["Home"]) | (df_match_selected["Home"] == df_hist["Away"])
        ultimos_casa = df_hist.loc[filter_ultimos_casa, ["Date", "Season", "Home", "Resultado_FT", "Away"]].sort_values(by="Date", ascending=False).head(10)
        df_ultimos_casa = ultimos_casa.style.apply(highlight_result, axis=1, highlight=df_match_selected["Home"])

        filter_ultimos_visitante = (df_match_selected["Away"] == df_hist["Home"]) | (df_match_selected["Away"] == df_hist["Away"])
        ultimos_visitante = df_hist.loc[filter_ultimos_visitante, ["Date", "Season", "Home", "Resultado_FT", "Away"]].sort_values(by="Date", ascending=False).head(10)
        df_ultimos_visitante = ultimos_visitante.style.apply(highlight_result, axis=1, highlight=df_match_selected["Away"])

        st.header(f"Últimos 10 Jogos na {df_match_selected['League']}")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader(df_match_selected["Home"])
            print_dataframe(df_ultimos_casa)
        with col2:
            st.subheader(df_match_selected["Away"])
            print_dataframe(df_ultimos_visitante)

        st.subheader("⚽ Classificações nesta competição")

        filter_classificacao = (df_hist["Season"] == get_current_season()) & (df_hist["League"] == df_match_selected["League"])
        df_classificacao = df_hist.loc[filter_classificacao, ["League","Season","Date","Rodada","Home","Away","Goals_H_FT","Goals_A_FT"]]

        classificacao_geral, styled_classificacao_geral = generate_classificacao(df_classificacao, df_match_selected, "ALL")
        classificacao_casa, styled_classificacao_casa = generate_classificacao(df_classificacao, df_match_selected, "HOME")
        classificacao_visitante, styled_classificacao_visitante = generate_classificacao(df_classificacao, df_match_selected, "AWAY")

        tab1, tab2, tab3 = st.tabs(["Geral", "Casa", "Visitante"])
        with tab1:
            print_dataframe(classificacao_geral, styled_classificacao_geral)
        with tab2:
            print_dataframe(classificacao_casa, styled_classificacao_casa)
        with tab3:
            print_dataframe(classificacao_visitante, styled_classificacao_visitante)

        filter_todos_casa = (df_hist["Home"] == df_match_selected["Home"]) & (df_hist["League"] == df_match_selected["League"]) & (df_hist["Season"] == get_current_season())
        todos_casa = df_hist.loc[filter_todos_casa, ["Date", "Home", "Resultado_FT", "Away", "Primeiro_Gol"]].sort_values(by="Date", ascending=False)
        df_todos_casa = todos_casa.style.apply(highlight_result, axis=1, highlight=df_match_selected["Home"])

        filter_todos_visitante = (df_hist["Away"] == df_match_selected["Away"]) & (df_hist["League"] == df_match_selected["League"]) & (df_hist["Season"] == get_current_season())
        todos_visitante = df_hist.loc[filter_todos_visitante, ["Date", "Home", "Resultado_FT", "Away", "Primeiro_Gol"]].sort_values(by="Date", ascending=False)
        df_todos_visitante = todos_visitante.style.apply(highlight_result, axis=1, highlight=df_match_selected["Away"])

        st.header("Todos os jogos Casa/Fora nesta competição")
        st.caption(f'{df_match_selected["League"]} - {get_current_season()} - Época Normal')

        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"{df_match_selected['Home']} em casa")
            print_dataframe(df_todos_casa)
        with col2:
            st.subheader(f"{df_match_selected['Away']} como visitante")
            print_dataframe(df_todos_visitante)

        st.subheader("Distribuição de Gols por Minuto (últimos 10 jogos)")

        home_gols_por_tempo = calcular_gols_por_tempo(df_hist.loc[(df_hist["Season"] == get_current_season())], df_match_selected["Home"])
        away_gols_por_tempo = calcular_gols_por_tempo(df_hist.loc[(df_hist["Season"] == get_current_season())], df_match_selected["Away"])

        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(home_gols_por_tempo, 
                        x='Quantidade',
                        y='Intervalo',
                        orientation="h",
                        color='Tipo de Gol',
                        color_discrete_map={
                            'Gols Marcados': 'lightgreen',
                            'Gols Sofridos': 'lightcoral'
                        },
                        barmode='group',
                        text_auto=True,
                        title=df_match_selected['Home']
            )
            st.plotly_chart(fig, use_container_width=True, key="fig1")
        with col2:
            fig = px.bar(away_gols_por_tempo, 
                        x='Quantidade',
                        y='Intervalo',
                        orientation="h",
                        color='Tipo de Gol',
                        color_discrete_map={
                            'Gols Marcados': 'lightgreen',
                            'Gols Sofridos': 'lightcoral'
                        },
                        barmode='group',
                        text_auto=True,
                        title=df_match_selected['Away']
            )
            st.plotly_chart(fig, use_container_width=True, key="fig2")

        # Tabela 22 e 23: Percurso Casa e Visitante
        # percurso_casa = {
        #     "Sequência de Vitórias": 1,
        #     "Sequência de Empates": 0,
        #     "Sequência de Derrotas": 3,
        #     "Não ganha há": 7,
        #     "Não empata há": 1,
        #     "Não perde há": 3,
        # }
        # percurso_visitante = {
        #     "Sequência de Vitórias": 2,
        #     "Sequência de Empates": 1,
        #     "Sequência de Derrotas": 0,
        #     "Não ganha há": 1,
        #     "Não empata há": 2,
        #     "Não perde há": 5,
        # }
        # col1, col2 = st.columns(2)
        # with col1:
        #     st.subheader("Percurso - Casa")
        #     st.json(percurso_casa)
        # with col2:
        #     st.subheader("Percurso - Visitante")
        #     st.json(percurso_visitante)

        # Título
        st.subheader("⚽ Estatísticas de gols (últimos 10 jogos)")

        # Dados Simulados para Times
        df_home_estatisticas = calcular_estatisticas(df_hist, df_match_selected['Home'])
        df_home_estatisticas_adicionais = calcular_estatisticas_adicionais(df_hist, df_match_selected['Home'], 'Home')

        df_away_estatisticas = calcular_estatisticas(df_hist, df_match_selected['Away'])
        df_away_estatisticas_adicionais = calcular_estatisticas_adicionais(df_hist, df_match_selected['Away'], 'Away')

        col1, col2 = st.columns(2)
        with col1:
            st.subheader(df_match_selected["Home"])
            print_dataframe(df_home_estatisticas.to_dict(orient='records'))
            print_dataframe(df_home_estatisticas_adicionais.to_dict(orient='records'))
        with col2:
            st.subheader(df_match_selected["Away"])
            print_dataframe(df_away_estatisticas.to_dict(orient='records'))
            print_dataframe(df_away_estatisticas_adicionais.to_dict(orient='records'))

        # Outros dados e análises podem ser adicionados conforme necessário
        st.write("⚡ Dashboard dinâmico para análise de confrontos! ⚡")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    display_sidebar('block')
    main_page()
else:
    login_page()
