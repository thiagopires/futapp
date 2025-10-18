import streamlit as st
import pandas as pd
from utils.functions import login_page, display_sidebar

# --- Configuração da Página ---
st.set_page_config(
    layout="wide",
    page_title="Fut Analytics Pro",
    page_icon="⚽"
)

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

    # --- Conteúdo da Página Inicial (Opcional) ---
    st.title("Bem-vindo ao Fut Analytics Pro ⚽")
    st.markdown("Use a barra de navegação à esquerda para explorar as diferentes ferramentas de análise.")
    st.info("Selecione uma página na barra lateral para começar.")