import streamlit as st
import pandas as pd
from utils.functions import login_page, display_sidebar

# --- Configuração da Página ---
# Esta configuração se aplica a todas as páginas
st.set_page_config(
    layout="wide",
    page_title="Fut Analytics Pro",
    page_icon="⚽",
    initial_sidebar_state="expanded" # Garante que a barra lateral comece aberta
)

# --- Gerenciamento de Estado de Login ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# --- Lógica de Exibição ---
if not st.session_state["logged_in"]:
    # Se não estiver logado, mostra apenas a página de login e esconde a sidebar
    display_sidebar('none')
    login_page()
else:
    # Se estiver logado, mostra a sidebar e o conteúdo da página principal/home
    display_sidebar('block')

    # --- Barra Lateral ---
    with st.sidebar:
        st.subheader("Fut Analytics Pro")
        st.caption("v1.0 - Comercial")
        
        st.divider()
        
        # O Streamlit irá gerar a navegação automaticamente a partir dos arquivos
        # na pasta /pages. Não é necessário adicionar mais nada aqui para a navegação.
        
        # Adiciona o seletor de fonte de dados à barra lateral
        if 'fonte_dados' not in st.session_state:
            st.session_state['fonte_dados'] = 'Betfair' # Valor padrão

        st.session_state['fonte_dados'] = st.radio(
            "Fonte de Dados",
            ['Betfair', 'FootyStats'],
            key='data_source_selector',
            help="Selecione a fonte de dados para carregar nas análises."
        )
        
        st.divider()
        st.caption("Desenvolvido por Thiago Pires")

    # --- Conteúdo da Página Inicial ---
    # Este conteúdo aparecerá quando você rodar o app
    st.title("Bem-vindo ao Fut Analytics Pro ⚽")
    st.markdown("---")
    st.header("Seu centro de análise de futebol para apostas esportivas.")
    st.info("👈 Use o menu de navegação na barra lateral para explorar as ferramentas.")
    
    st.subheader("Ferramentas Disponíveis:")
    st.markdown("""
        - **📊 Dashboard Jogos do Dia:** Uma visão geral e interativa dos jogos do dia.
        - **🔬 Backtesting:** Teste suas estratégias com dados históricos.
        - **🔍 Análise Pré-Jogo:** Mergulhe fundo nas estatísticas de um jogo específico.
    """)