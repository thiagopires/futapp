import streamlit as st

from utils.functions import *

col_cashout, col_freebet = st.columns(2)
with col_cashout:
    tab_bl, tab_lb = st.tabs(["Back/Lay","Lay/Back"])
    with tab_bl:
        odd_back = st.number_input("Odd Back", key="bl_odd_back", min_value=1.01, max_value=1000.00)
        stake_back = st.number_input("Stake Back", key="bl_stake_back", min_value=1.00, max_value=9999.99)
        odd_lay = st.number_input("Odd Lay", key="bl_odd_lay", min_value=1.01, max_value=1000.00)

        if odd_back and stake_back and odd_lay:
            stake_lay = stake_back/odd_lay*odd_back
            st.write(f"Stake de Lay: {str(stake_lay)}")
            st.write(f"Perda/Lucro: {str(stake_lay-stake_back)}")
    with tab_lb:
        odd_lay = st.number_input("Odd Lay",key="lb_odd_lay", min_value=1.01, max_value=1000.00)
        responsabilidade_lay = st.number_input("Responsabilidade Lay", key="lb_responsabilidade_lay", min_value=1.00, max_value=9999.99)
        odd_back = st.number_input("Odd Back", key="lb_odd_back", min_value=1.01, max_value=1000.00)

        if odd_lay and responsabilidade_lay and odd_back:
            stake_lay = responsabilidade_lay / (odd_lay - 1)
            stake_back = stake_lay * odd_lay / odd_back
            lucro_perda = round(responsabilidade_lay - (stake_back * (odd_back - 1)), 2)
            st.write(f"Stake de Back: {str(round(stake_back, 2))}")
            st.write(f"Perda/Lucro: {str(lucro_perda)}")

with col_freebet:
    st.write("ok")
