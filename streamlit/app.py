import streamlit as st
from utils.functions import *

st.set_page_config(layout="wide")

def login_page():
    
    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.title("Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if validate_login(username, password):
            st.session_state["logged_in"] = True
            st.success("Login realizado com sucesso!")
        else:
            st.error("Usuário ou senha inválidos!")

def main_page():
    st.sidebar.title("Menu")
    st.title("Página Principal")
    st.write("Conteúdo protegido para usuários logados.")
    if st.sidebar.button("Sair"):
        st.session_state["logged_in"] = False
        st.sidebar.empty()

# Controle de fluxo baseado no estado de login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    main_page()
else:
    login_page()