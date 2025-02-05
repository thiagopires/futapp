import streamlit as st
from utils.functions import *

st.set_page_config(layout="wide")
display_sidebar('none')

def main_page():
    st.title("Página Principal")
    st.write("Conteúdo protegido para usuários logados.")
    # if st.sidebar.button("Sair"):
    #     st.session_state["logged_in"] = False
    #     display_sidebar('none')
    #     login_page()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    display_sidebar('block')
    main_page()
else:
    login_page()