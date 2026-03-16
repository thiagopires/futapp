import streamlit as st
import pandas as pd

from utils.functions import *
from utils.filters import *

import pages.home as home
import pages.analise_away as analise_away
import pages.analise_home as analise_home
import pages.backtesting as backtesting
import pages.base_de_dados as base_de_dados
import pages.calculadora as calculadora
import pages.jogos_do_dia as jogos_do_dia
import pages.jogos_sem_resultado as jogos_sem_resultado
import pages.metodo_ciclos as metodo_ciclos
import pages.filtros as filtros

st.set_page_config(layout="wide", page_title="Futapp v0.3")

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Opções personalizadas
opcoes = {
    "Página Inicial": "home",
    "Jogos do Dia": "jogos_do_dia",
    "Filtros Prontos": "filtros",
    "Backtesting": "backtesting",
    "Análise Home": "analise_home",
    "Análise Away": "analise_away",
    "Base de Dados": "base_de_dados",
    "Calculadora": "calculadora",
    "Jogos sem Resultado": "jogos_sem_resultado",
    "Método de Ciclos": "metodo_ciclos",
}

# Criando a sidebar com radio buttons
st.sidebar.subheader("Futapp v0.3")
escolha = st.sidebar.radio("Navegação", list(opcoes.keys()))

st.sidebar.divider()

fonte_dados = st.sidebar.radio("Fonte de Dados", ['Betfair','FootyStats'])

display_sidebar('none')

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    display_sidebar('block')
    if opcoes[escolha] == "home":
        home.main_page()

    elif opcoes[escolha] == "jogos_do_dia":
        jogos_do_dia.main_page(fonte_dados)
    
    elif opcoes[escolha] == "filtros":
        filtros.main_page(fonte_dados)

    elif opcoes[escolha] == "backtesting":
        backtesting.main_page(fonte_dados)

    elif opcoes[escolha] == "analise_home":
        analise_home.main_page(fonte_dados)

    elif opcoes[escolha] == "analise_away":
        analise_away.main_page(fonte_dados)

    elif opcoes[escolha] == "base_de_dados":
        base_de_dados.main_page(fonte_dados)

    elif opcoes[escolha] == "calculadora":
        calculadora.main_page()

    elif opcoes[escolha] == "jogos_sem_resultado":
        jogos_sem_resultado.main_page(fonte_dados)

    elif opcoes[escolha] == "metodo_ciclos":
        metodo_ciclos.main_page()
else:
    login_page()







