# Fut_Analytics_Pro.py (Versão de Teste Simplificada)
import streamlit as st

st.set_page_config(
    layout="wide",
    page_title="Fut Analytics Pro - Teste",
    page_icon="⚽",
    initial_sidebar_state="expanded"
)

# --- Barra Lateral ---
with st.sidebar:
    st.title("Menu de Navegação")
    st.write("As páginas da pasta 'pages' deveriam aparecer aqui.")
    st.divider()
    st.session_state['fonte_dados'] = st.radio(
        "Fonte de Dados",
        ['Betfair', 'FootyStats'],
        key='data_source_selector'
    )

# --- Conteúdo da Página Principal ---
st.title("Página Principal de Teste")
st.info("👈 Verifique a barra lateral à esquerda. As outras páginas apareceram?")

st.warning(
    "Se as páginas aparecerem agora, o problema está na lógica de login do seu arquivo original. "
    "Se elas NÃO aparecerem, o problema está na estrutura de pastas (Passo 1)."
)