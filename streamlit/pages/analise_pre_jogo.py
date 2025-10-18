import streamlit as st
import pandas as pd
from utils.functions import *
from utils.filters import *

st.set_page_config(layout="wide", page_title="Análise Pré-Jogo", page_icon="🔍")

def main_page(fonte_dados):
    if st.secrets['ENV'] == 'dev':
        st.info("Ambiente de Desenvolvimento")
        
    st.title("🔍 Análise Detalhada Pré-Jogo")

    # --- Carregamento de Dados ---
    data_analise = st.date_input("Data dos Jogos", get_today())
    df_matches = load_daymatches(data_analise, fonte_dados)
    df_hist = load_histmatches(fonte_dados)

    if df_matches.empty:
        st.warning(f"Nenhum jogo encontrado para a data {data_analise.strftime('%d/%m/%Y')}.")
        return

    # --- Seleção do Jogo ---
    st.subheader("1. Selecione o Jogo para Análise")
    
    leagues = sorted(df_matches['League'].unique())
    selected_league = st.selectbox("Filtrar por Liga", leagues)

    df_league_matches = df_matches[df_matches['League'] == selected_league]
    
    # Criar uma lista de jogos formatados para o selectbox
    match_options = [f"{row['Time']} - {row['Home']} vs {row['Away']}" for index, row in df_league_matches.iterrows()]
    
    if not match_options:
        st.info("Nenhum jogo disponível para a liga selecionada nesta data.")
        return
        
    selected_match_str = st.selectbox("Escolha o Jogo", match_options)

    # Encontrar o jogo selecionado no DataFrame
    home_team = selected_match_str.split(' - ')[1].split(' vs ')[0]
    away_team = selected_match_str.split(' vs ')[1]
    jogo_selecionado = df_league_matches[(df_league_matches['Home'] == home_team) & (df_league_matches['Away'] == away_team)].iloc[0]

    st.divider()

    # --- Seleção da Análise ---
    st.subheader("2. Escolha o Tipo de Análise")
    
    col1, col2 = st.columns(2)
    with col1:
        time_analisado = st.radio(
            "Analisar qual time?",
            (f"Mandante ({jogo_selecionado['Home']})", f"Visitante ({jogo_selecionado['Away']})"),
            horizontal=True
        )
        team_name = jogo_selecionado['Home'] if "Mandante" in time_analisado else jogo_selecionado['Away']
        side = 'Home' if "Mandante" in time_analisado else 'Away'

    with col2:
        tipo_analise = st.selectbox(
            "Selecione a análise desejada",
            [
                "Ponto de Saída (Resultado Final)",
                "Ponto de Saída (Trader @75')",
                "Ponto de Revisão (Resultado HT)",
                "Desempenho em Mercados (Over/BTTS)",
                "Desempenho em Mercados (Match Odds)",
                "Últimos 10 Jogos e H2H",
                "Singularidades (Placares Raros)"
            ]
        )
    
    placar = None
    if "Ponto de" in tipo_analise or "Singularidades" in tipo_analise:
        placar = st.selectbox(
            "Escolha o Placar de Referência",
            ['0x0', '1x0', '0x1', '1x1', '2x0', '0x2', '2x1', '1x2', '2x2', 'Goleada_H', 'Goleada_A']
        )

    st.divider()

    # --- Exibição dos Resultados ---
    st.header(f"Resultados da Análise para: {team_name}")

    if tipo_analise == "Ponto de Saída (Resultado Final)":
        st.write(f"**Jogos anteriores do {team_name} (como {side}) que terminaram em {placar}.**")
        aba_ponto_de_saida_punter(df_hist, team_name, side, placar)

    elif tipo_analise == "Ponto de Saída (Trader @75')":
        st.write(f"**Jogos anteriores do {team_name} (como {side}) que estavam {placar} aos 75 minutos.**")
        aba_ponto_de_saida_trader(df_hist, team_name, side, placar)

    elif tipo_analise == "Ponto de Revisão (Resultado HT)":
        st.write(f"**Jogos anteriores do {team_name} (como {side}) com resultado de {placar} no intervalo.**")
        aba_ponto_de_revisao_ht(df_hist, team_name, side, placar)

    elif tipo_analise == "Desempenho em Mercados (Over/BTTS)":
        st.subheader(f"Over 2.5 FT nos jogos do {team_name} (como {side})")
        aba_over25(df_hist, team_name, side)
        st.divider()
        st.subheader(f"BTTS Sim nos jogos do {team_name} (como {side})")
        aba_btts(df_hist, team_name, side)
        
    elif tipo_analise == "Desempenho em Mercados (Match Odds)":
        st.subheader(f"Análise de Back")
        st.write(f"**Back {side} (Apostar a favor do {team_name})**")
        aba_back_home(df_hist, team_name, side) if side == 'Home' else aba_back_away(df_hist, team_name, side)
        st.write(f"**Back Empate (Apostar no empate nos jogos do {team_name})**")
        aba_back_draw(df_hist, team_name, side)
        
        st.divider()
        st.subheader(f"Análise de Lay")
        st.write(f"**Lay {side} (Apostar contra o {team_name})**")
        aba_lay_home(df_hist, team_name, side) if side == 'Home' else aba_lay_away(df_hist, team_name, side)
        st.write(f"**Lay Empate (Apostar contra o empate nos jogos do {team_name})**")
        aba_lay_draw(df_hist, team_name, side)

    elif tipo_analise == "Últimos 10 Jogos e H2H":
        st.subheader(f"Últimos 10 jogos do {team_name} (como {side})")
        aba_ult10(df_hist, team_name, side)
        st.divider()
        st.subheader("Confronto Direto (H2H)")
        aba_confrontodireto(df_hist, jogo_selecionado['Home'], jogo_selecionado['Away'])

    elif tipo_analise == "Singularidades (Placares Raros)":
        st.subheader(f"Resultados que NÃO ocorreram para o {team_name} (como {side})")
        resultados_singulares(df_hist, team_name, side)
        st.divider()
        st.subheader(f"Análise de Ocorrência para o Placar: {placar}")
        analise_ocorrencia_placar(df_hist, jogo_selecionado['Home'], jogo_selecionado['Away'], placar)


# --- Ponto de Entrada ---
# main_page(st.session_state.get('fonte_dados', 'Betfair'))