import streamlit as st
import pandas as pd

from utils.functions import *

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
st.set_page_config(layout="wide")

if "authenticated" not in st.session_state or st.session_state.authenticated == False:
    st.write("Faça o login na página 'app'.")
else:

    st.title("⚽ Análise Away")

    def set_odds_filtros(reset=False):
        if reset:
            st.session_state['odd_h_min'] = 1.10
            st.session_state['odd_h_max'] = 1000.00
            st.session_state['odd_d_min'] = 1.10
            st.session_state['odd_d_max'] = 1000.00
            st.session_state['odd_a_min'] = 1.10
            st.session_state['odd_a_max'] = 1000.00
            st.session_state['odd_over25_ft_min'] = 1.10
            st.session_state['odd_over25_ft_max'] = 1000.00
            st.session_state['odd_btts_min'] = 1.10
            st.session_state['odd_btts_max'] = 1000.00
        else:
            if "odd_h_min" not in st.session_state: st.session_state['odd_h_min'] = 1.40
            if "odd_h_max" not in st.session_state: st.session_state['odd_h_max'] = 2.00
            if "odd_d_min" not in st.session_state: st.session_state['odd_d_min'] = 2.50
            if "odd_d_max" not in st.session_state: st.session_state['odd_d_max'] = 10.00
            if "odd_a_min" not in st.session_state: st.session_state['odd_a_min'] = 4.00
            if "odd_a_max" not in st.session_state: st.session_state['odd_a_max'] = 50.00
            if "odd_over25_ft_min" not in st.session_state: st.session_state['odd_over25_ft_min'] = 1.30
            if "odd_over25_ft_max" not in st.session_state: st.session_state['odd_over25_ft_max'] = 2.00
            if "odd_btts_min" not in st.session_state: st.session_state['odd_btts_min'] = 1.30
            if "odd_btts_max" not in st.session_state: st.session_state['odd_btts_max'] = 2.00

    # Init

    data_analise = st.date_input("Data da Análise", get_today())
    df_matches = load_daymatches(data_analise)
    df_hist = load_histmatches(data_analise)


    st.divider()


    st.subheader("Filtro de Odds")
    set_odds_filtros(True)
    if st.button("Limpar filtros"):
        set_odds_filtros(True)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.number_input("Odd_H_Min", value=st.session_state.odd_h_min, min_value=1.10, max_value=1000.00, key="odd_h_min")
        st.number_input("Odd_H_Max", value=st.session_state.odd_h_max, min_value=1.10, max_value=1000.00, key="odd_h_max")
    with col2:
        st.number_input("Odd_D_Min", value=st.session_state.odd_d_min, min_value=1.10, max_value=1000.00, key="odd_d_min")
        st.number_input("Odd_D_Max", value=st.session_state.odd_d_max, min_value=1.10, max_value=1000.00, key="odd_d_max")
    with col3:
        st.number_input("Odd_A_Min", value=st.session_state.odd_a_min, min_value=1.10, max_value=1000.00, key="odd_a_min")
        st.number_input("Odd_A_Max", value=st.session_state.odd_a_max, min_value=1.10, max_value=1000.00, key="odd_a_max")
    with col4:
        st.number_input("Odd_Over25_FT_Min", value=st.session_state.odd_over25_ft_min, min_value=1.10, max_value=1000.00, key="odd_over25_ft_min")
        st.number_input("Odd_Over25_FT_Max", value=st.session_state.odd_over25_ft_max, min_value=1.10, max_value=1000.00, key="odd_over25_ft_max")
    with col5:
        st.number_input("Odd_BTTS_Min", value=st.session_state.odd_btts_min, min_value=1.10, max_value=1000.00, key="odd_btts_min")
        st.number_input("Odd_BTTS_Max", value=st.session_state.odd_btts_max, min_value=1.10, max_value=1000.00, key="odd_btts_max")


    st.divider()


    st.subheader("Jogos que atendem a esses filtros")

    df_matches = df_matches.loc[
        (df_matches["Odd_H_FT"] >= st.session_state.odd_h_min) &
        (df_matches["Odd_H_FT"] <= st.session_state.odd_h_max) &

        (df_matches["Odd_D_FT"] >= st.session_state.odd_d_min) &
        (df_matches["Odd_D_FT"] <= st.session_state.odd_d_max) &

        (df_matches["Odd_A_FT"] >= st.session_state.odd_a_min) &
        (df_matches["Odd_A_FT"] <= st.session_state.odd_a_max) &

        (df_matches["Odd_Over25_FT"] >= st.session_state.odd_over25_ft_min) &
        (df_matches["Odd_Over25_FT"] <= st.session_state.odd_over25_ft_max) &

        (df_matches["Odd_BTTS_Yes"] >= st.session_state.odd_btts_min) &
        (df_matches["Odd_BTTS_Yes"] <= st.session_state.odd_btts_max)
    ]

    print_dataframe(df_matches[['League','Rodada','Time','Home','Away','Odd_H_FT','Odd_D_FT','Odd_A_FT','Odd_Over05_HT','Odd_Over15_FT','Odd_Over25_FT','Odd_BTTS_Yes']])


    st.divider()


    st.subheader("Selecione o Visitante e o Placar para a análise")
    
    if len(df_matches) > 0:
        colb1, colb2 = st.columns(2)
        with colb1:
            visitante = st.selectbox("Escolha o Visitante", df_matches['Away'])
        with colb2:
            placar = st.selectbox("Escolha o Placar", ['0x0','0x1','0x2','0x3','1x0','1x1','1x2','1x3','2x0','2x1','2x2','2x3','3x0','3x1','3x2','3x3'])

        df_match_selected = df_matches.loc[(df_matches['Away'] == visitante)]


        st.divider()


        st.session_state['active_button'] = ""

        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        # with col1:
        #     if st.button("Profit Acumulado", use_container_width=True):
        #         st.session_state['active_button'] = "Profit Acumulado"
        with col2:
            if st.button("Ponto de Saída Punter", use_container_width=True):
                st.session_state['active_button'] = "Ponto de Saída Punter"
        #     st.button("Ocorrências Gerais", use_container_width=True)
        with col3:
            if st.button("Ponto de Saída Trader", use_container_width=True):
                st.session_state['active_button'] = "Ponto de Saída Trader"
            if st.button("Ponto de Revisão HT", use_container_width=True):
                  st.session_state['active_button'] = "Ponto de Revisão HT"
        with col4:
            if st.button("Últimos 10 jogos", use_container_width=True):
                st.session_state['active_button'] = "Últimos 10 jogos"
            if st.button("Confronto Direto", use_container_width=True):
                st.session_state['active_button'] = "Confronto Direto"
        # with col5:
        #     st.button("Temporada Atual", use_container_width=True)
        #     st.button("Temporada Anterior", use_container_width=True)
        with col6:
            if st.button("Match Odds - Back", use_container_width=True):
                st.session_state['active_button'] = "Match Odds - Back"
            if st.button("Match Odds - Lay", use_container_width=True):
                st.session_state['active_button'] = "Match Odds - Lay"
        with col7:
            if st.button("Over 2.5 FT / BTTS", use_container_width=True):
                st.session_state['active_button'] = "Over 2.5 FT / BTTS"
                
        ###

        if len(df_match_selected) > 0:

            mandante = df_match_selected.iloc[0]["Home"]

            if st.session_state['active_button'] == "Over 2.5 FT / BTTS":
                        
                st.write(f"**Over 2.5 FT nos jogos do {visitante}**")
                st.write(f"**Jogos anteriores do {visitante} que bateram o Over 2.5 FT**")    
                aba_over25(df_hist, visitante, "Away")

                st.write(f"**BTTS nos jogos do {visitante}**")
                st.write(f"**Jogos anteriores do {visitante} que bateram o BTTS**")
                aba_btts(df_hist, visitante, "Away")

            elif st.session_state['active_button'] == "Últimos 10 jogos":

                st.write(f"**Últimos 10 jogos do {mandante} como Mandante**")
                aba_ult10(df_hist, mandante, "Home")

                st.write(f"**Últimos 10 jogos do {visitante} como Visitante**")
                aba_ult10(df_hist, visitante, "Away")

            elif st.session_state['active_button'] == "Confronto Direto":
                st.write(f"**Confronto direto - Temporadas passadas**")
                aba_confrontodireto(df_hist, visitante, visitante)

            elif st.session_state['active_button'] == "Match Odds - Back":
                st.write(f"**Back Home (Apostar no {visitante})**")
                aba_back_home(df_hist, visitante, "Away")

                st.write(f"**Back Draw (Apostar no Empate nos jogos do {visitante})**")
                aba_back_draw(df_hist, visitante, "Away")

                st.write(f"**Back Away (Apostar no Adversário do {visitante})**")
                aba_back_away(df_hist, visitante, "Away")

            elif st.session_state['active_button'] == "Match Odds - Lay":
                st.write(f"**Lay Home (Apostar contra o {visitante})**")
                aba_lay_home(df_hist, visitante, "Away")

                st.write(f"**Lay Draw (Apostar cintra o Empate nos jogos do {visitante})**")
                aba_lay_draw(df_hist, visitante, "Away")

                st.write(f"**Lay Away (Apostar contra o Adversário do {visitante})**")
                aba_lay_away(df_hist, visitante, "Away")
                
            elif st.session_state['active_button'] == "Ponto de Revisão HT":
                
                st.write(f"**Jogos anteriores do {visitante} que terminaram em {placar} no HT.**")
                aba_ponto_de_revisao_ht(df_hist, visitante, "Away", placar)

            elif st.session_state['active_button'] == "Ponto de Saída Trader":
                
                st.write(f"**Jogos anteriores do {visitante} que estavam em {placar} no minuto 75.**")
                aba_ponto_de_saida_trader(df_hist, visitante, "Away", placar)

            elif any(item == st.session_state['active_button'] for item in ["", "Ponto de Saída Punter"]):
            # elif st.session_state['active_button'] == "Ponto de Saída Punter":
    
                st.write(f"**Jogos anteriores do {visitante} terminados em {placar}.**")
                aba_ponto_de_saida_punter(df_hist, visitante, "Away", placar)
