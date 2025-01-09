import streamlit as st

from utils.functions import *

st.set_page_config(layout="wide")
st.title("⚽ Calculadora")

col_cashout, col_resultado = st.columns(2)

# Coluna de Cashout
with col_cashout:
    st.header("Cashout")
    tab_bl, tab_lb = st.tabs(["Back/Lay", "Lay/Back"])

    # Aba Back/Lay
    with tab_bl:
        st.number_input("Odd Back", key="bl_odd_back")
        st.number_input("Stake Back", key="bl_stake_back")
        st.number_input("Odd Lay", key="bl_odd_lay")

    # Aba Lay/Back
    with tab_lb:
        st.number_input("Odd Lay", key="lb_odd_lay")
        st.number_input("Responsabilidade Lay", key="lb_responsabilidade_lay")
        st.number_input("Odd Back", key="lb_odd_back")

with col_resultado:

    # Back/Lay
    if st.session_state.get('bl_odd_back') and st.session_state.get('bl_stake_back') and st.session_state.get('bl_odd_lay'):
        stake_lay = st.session_state['bl_stake_back'] / st.session_state['bl_odd_lay'] * st.session_state['bl_odd_back']
        lucro_perda = round(stake_lay - st.session_state['bl_stake_back'], 2)

        st.write(f"Stake de Lay:")
        container = st.container(border=True)
        container.code(str(round(stake_lay, 2)), language="text")

        st.write(f"Perda/Lucro:")
        container = st.container(border=True)
        container.code(str(lucro_perda), language="text")

    # Lay/Back
    if st.session_state.get('lb_odd_lay') and st.session_state.get('lb_responsabilidade_lay') and st.session_state.get('lb_odd_back'):
        stake_lay = st.session_state['lb_responsabilidade_lay'] / (st.session_state['lb_odd_lay'] - 1)
        stake_back = stake_lay * st.session_state['lb_odd_lay'] / st.session_state['lb_odd_back']
        lucro_perda = round((stake_back * (st.session_state['lb_odd_back'] - 1)) - st.session_state['lb_responsabilidade_lay'], 2)

        st.write(f"Stake de Back:")
        container = st.container(border=True)
        container.code(str(round(stake_back, 2)), language="text")

        st.write(f"Perda/Lucro:")
        container = st.container(border=True)
        container.code(str(lucro_perda), language="text")
