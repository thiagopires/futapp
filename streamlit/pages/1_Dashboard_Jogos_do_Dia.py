import streamlit as st
import pandas as pd
from utils.functions import *
from utils.filters import *
import plotly.express as px

st.set_page_config(layout="wide", page_title="Dashboard de Jogos", page_icon="📊")

def main_page(fonte_dados):
    if st.secrets['ENV'] == 'dev':
        st.info("Ambiente de Desenvolvimento")

    st.title("📊 Dashboard - Jogos do Dia")

    # --- Filtros Principais ---
    c1, c2 = st.columns([1, 3])
    with c1:
        data_analise = st.date_input("Data da Análise", get_today())
    with c2:
        filtro_pronto_selecionado = st.selectbox("Aplicar Estratégia (Filtro Rápido)", filtros_prontos[fonte_dados], index=0)

    df_matches = load_daymatches(data_analise, fonte_dados)

    if df_matches.empty:
        st.warning(f"Nenhum dado encontrado para a data {data_analise.strftime('%d/%m/%Y')}. Por favor, selecione outra data.")
        return

    # Aplica filtro pronto, se selecionado
    if filtro_pronto_selecionado != "Sem filtro":
        df_matches, _, _ = get_details_filtro_pronto(df_matches.copy(), None, None, filtro_pronto_selecionado)
        st.success(f"Filtro '{filtro_pronto_selecionado}' aplicado. {len(df_matches)} jogos encontrados.")

    st.divider()
    
    # --- Tabela de Jogos Selecionável ---
    st.subheader("Selecione um jogo para análise detalhada")
    
    df_display_cols = ['League', 'Time', 'Home', 'Away', 'Odd_H_FT', 'Odd_D_FT', 'Odd_A_FT', 'Odd_Over25_FT', 'Odd_BTTS_Yes']
    
    # Garantir que apenas colunas existentes sejam mostradas
    display_cols = [col for col in df_display_cols if col in df_matches.columns]
    
    selecao = st.dataframe(
        df_matches[display_cols],
        on_select="rerun",
        selection_mode="single-row",
        use_container_width=True,
        hide_index=True
    )
    
    st.caption(f"Última atualização da base: {last_refresh_daymatches()} | Total de jogos na lista: {len(df_matches)}")

    # --- Seção de Análise Detalhada (se um jogo for selecionado) ---
    if selecao.selection.rows:
        df_hist = load_histmatches(fonte_dados)
        jogo_idx = selecao.selection.rows[0]
        jogo_selecionado = df_matches.iloc[jogo_idx]

        st.divider()

        # Título da Análise
        st.header(f"🔍 Análise: {jogo_selecionado['Home']} vs {jogo_selecionado['Away']}")
        st.caption(f"{jogo_selecionado['Formatted_Datetime']} | {jogo_selecionado['League']}")

        # Abas para organizar o conteúdo
        tab_geral, tab_desempenho, tab_classificacao, tab_gols = st.tabs(["Visão Geral", "Desempenho Recente", "Classificação", "Análise de Gols"])

        with tab_geral:
            st.subheader("Principais Mercados e Confronto Direto")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Probabilidades (Match Odds)**")
                c1, c2, c3 = st.columns(3)
                c1.metric("Casa", jogo_selecionado["Odd_H_FT"])
                c2.metric("Empate", jogo_selecionado["Odd_D_FT"])
                c3.metric("Fora", jogo_selecionado["Odd_A_FT"])

                st.write("**Mercado de Gols**")
                c1, c2, c3 = st.columns(3)
                c1.metric("Over 2.5", jogo_selecionado.get("Odd_Over25_FT", "N/A"))
                c2.metric("BTTS Sim", jogo_selecionado.get("Odd_BTTS_Yes", "N/A"))
                c3.metric("Over 0.5 HT", jogo_selecionado.get("Odd_Over05_HT", "N/A"))
                
            with col2:
                st.write("**Confrontos Diretos (H2H)**")
                filter_confrontos = (df_hist["Home"].isin([jogo_selecionado["Home"], jogo_selecionado["Away"]])) & (df_hist["Away"].isin([jogo_selecionado["Home"], jogo_selecionado["Away"]]))
                confrontos = df_hist.loc[filter_confrontos, ["Date", "Season", "Home", "Resultado_FT", "Away"]].sort_values(by="Date", ascending=False).head(10)
                if not confrontos.empty:
                    df_confrontos = confrontos.style.apply(highlight_result, axis=1, highlight=jogo_selecionado["Home"])
                    print_dataframe(df_confrontos)
                else:
                    st.info("Nenhum confronto direto encontrado na base histórica.")

        with tab_desempenho:
            st.subheader("Últimos 10 Jogos (Geral)")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{jogo_selecionado['Home']}**")
                filter_ultimos_casa = (jogo_selecionado["Home"] == df_hist["Home"]) | (jogo_selecionado["Home"] == df_hist["Away"])
                ultimos_casa = df_hist.loc[filter_ultimos_casa, ["Date", "Season", "Home", "Resultado_FT", "Away"]].sort_values(by="Date", ascending=False).head(10)
                df_ultimos_casa = ultimos_casa.style.apply(highlight_result, axis=1, highlight=jogo_selecionado["Home"])
                print_dataframe(df_ultimos_casa)
            with col2:
                st.write(f"**{jogo_selecionado['Away']}**")
                filter_ultimos_visitante = (jogo_selecionado["Away"] == df_hist["Home"]) | (jogo_selecionado["Away"] == df_hist["Away"])
                ultimos_visitante = df_hist.loc[filter_ultimos_visitante, ["Date", "Season", "Home", "Resultado_FT", "Away"]].sort_values(by="Date", ascending=False).head(10)
                df_ultimos_visitante = ultimos_visitante.style.apply(highlight_result, axis=1, highlight=jogo_selecionado["Away"])
                print_dataframe(df_ultimos_visitante)

        with tab_classificacao:
            st.subheader(f"Classificação - {jogo_selecionado['League']}")
            filter_classificacao = (df_hist["Season"] == get_current_season()) & (df_hist["League"] == jogo_selecionado["League"])
            df_classificacao = df_hist.loc[filter_classificacao]

            if not df_classificacao.empty:
                t1, t2, t3 = st.tabs(["Tabela Geral", "Mandantes", "Visitantes"])
                with t1:
                    _, styled_geral = generate_classificacao(df_classificacao.copy(), jogo_selecionado, "ALL")
                    print_dataframe(styled_geral)
                with t2:
                    _, styled_casa = generate_classificacao(df_classificacao.copy(), jogo_selecionado, "HOME")
                    print_dataframe(styled_casa)
                with t3:
                    _, styled_visitante = generate_classificacao(df_classificacao.copy(), jogo_selecionado, "AWAY")
                    print_dataframe(styled_visitante)
            else:
                st.info("Não há dados de classificação para a temporada atual desta liga.")

        with tab_gols:
            st.subheader("Estatísticas de Gols (Últimos 10 jogos)")
            
            # Gráficos
            st.write("**Distribuição de Gols por Minuto**")
            col1, col2 = st.columns(2)
            with col1:
                home_gols_por_tempo = calcular_gols_por_tempo(df_hist, jogo_selecionado["Home"])
                fig_home = px.bar(home_gols_por_tempo, x='Gols', y='Intervalo', orientation="h", color='Tipo de Gol',
                                  color_discrete_map={'Gols Marcados': '#2E8B57', 'Gols Sofridos': '#FF4500'},
                                  barmode='group', text_auto=True, title=jogo_selecionado['Home'])
                st.plotly_chart(fig_home, use_container_width=True)
            with col2:
                away_gols_por_tempo = calcular_gols_por_tempo(df_hist, jogo_selecionado["Away"])
                fig_away = px.bar(away_gols_por_tempo, x='Gols', y='Intervalo', orientation="h", color='Tipo de Gol',
                                  color_discrete_map={'Gols Marcados': '#2E8B57', 'Gols Sofridos': '#FF4500'},
                                  barmode='group', text_auto=True, title=jogo_selecionado['Away'])
                st.plotly_chart(fig_away, use_container_width=True)
            
            st.divider()

            # Tabelas de Estatísticas
            st.write("**Métricas de Desempenho**")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{jogo_selecionado['Home']}**")
                df_home_estatisticas = calcular_estatisticas(df_hist, jogo_selecionado['Home'])
                print_dataframe(df_home_estatisticas)
            with col2:
                st.write(f"**{jogo_selecionado['Away']}**")
                df_away_estatisticas = calcular_estatisticas(df_hist, jogo_selecionado['Away'])
                print_dataframe(df_away_estatisticas)

# --- Ponto de Entrada ---
# A variável 'fonte_dados' agora vem do session_state, definido no app principal
main_page(st.session_state.get('fonte_dados', 'Betfair'))