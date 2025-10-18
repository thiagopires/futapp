import streamlit as st
import pandas as pd
from utils.functions import login_page, display_sidebar

import pages.analise_pre_jogo as analise_pre_jogo
import pages.backtesting as backtesting
import pages.dashboard_jogos_do_dia as dashboard_jogos_do_dia
# import pages.calculadora as calculadora
# import pages.jogos_sem_resultado as jogos_sem_resultado
# import pages.base_de_dados as base_de_dados

# --- Configuração da Página ---
st.set_page_config(
    layout="wide",
    page_title="Fut Analytics Pro",
    page_icon="⚽"
)

opcoes = {
    "Página Inicial": "home",
    "Análise Pré Jogo": "analise_pre_jogo",
    "Backtesting": "backtesting",
    "Dashboard Jogos do Dia": "dashboard_jogos_do_dia",
    # "Base de Dados": "base_de_dados",
    # "Calculadora": "calculadora",
    # "Jogos sem Resultado": "jogos_sem_resultado",
}

# --- Gerenciamento de Estado de Login ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# --- Lógica de Exibição ---
if not st.session_state["logged_in"]:
    login_page()
else:
    # --- Barra Lateral ---
    with st.sidebar:
        st.subheader("Fut Analytics Pro")
        st.caption("v1.0")
        
        # O Streamlit gera a navegação a partir dos arquivos na pasta /pages
        escolha = st.sidebar.radio("Navegação", list(opcoes.keys()))

        st.divider()
        
        # Adiciona o seletor de fonte de dados à barra lateral
        # Usando st.session_state para manter a escolha entre as páginas
        if 'fonte_dados' not in st.session_state:
            st.session_state['fonte_dados'] = 'Betfair' # Valor padrão

        st.session_state['fonte_dados'] = st.radio(
            "Fonte de Dados",
            ['Betfair', 'FootyStats'],
            key='data_source_selector'
        )
        
        st.divider()
        st.caption("Desenvolvido por Thiago Pires")

    if opcoes[escolha] == "home":
        st.title("Bem-vindo ao Fut Analytics Pro ⚽")
        st.markdown("Use a barra de navegação à esquerda para explorar as diferentes ferramentas de análise.")
        st.info("Selecione uma página na barra lateral para começar.")

    elif opcoes[escolha] == "analise_pre_jogo":
        analise_pre_jogo.main_page(st.session_state['fonte_dados'])

    elif opcoes[escolha] == "backtesting":
        backtesting.main_page(st.session_state['fonte_dados'])

    elif opcoes[escolha] == "dashboard_jogos_do_dia":
        dashboard_jogos_do_dia.main_page(st.session_state['fonte_dados'])

        # elif opcoes[escolha] == "base_de_dados":
        #     base_de_dados.main_page(fonte_dados)

        # elif opcoes[escolha] == "calculadora":
        #     calculadora.main_page()

        # elif opcoes[escolha] == "jogos_sem_resultado":
        #     jogos_sem_resultado.main_page(fonte_dados)
    