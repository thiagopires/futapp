import streamlit as st
from utils.functions import *

st.set_page_config(layout="wide")

def main_page():
    st.sidebar.title("Menu")
    st.title("Página Principal")
    st.write("Conteúdo protegido para usuários logados.")
    if st.sidebar.button("Sair"):
        st.session_state["logged_in"] = False
        hide_sidebar()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    show_sidebar()
    main_page()
else:
    login_page()