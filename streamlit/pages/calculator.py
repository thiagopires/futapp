import streamlit as st

from utils.functions import *

col_cashout, col_freebet = st.columns(2)
with col_cashout:
    tab_bl, tab_lb = st.tabs(["Back/Lay","Lay/Back"])
    with tab_bl:
        odd_back = st.number_input("Odd Back", min_value=1.01, max_value=1000)
        stake_back = st.number_input("Stake Back", min_value=1.00, max_value=9999.99)
        odd_lay = st.number_input("Odd Lay", min_value=1.01, max_value=1000)

        if odd_back and stake_back and odd_lay:
            stake_lay = stake_back/odd_lay*odd_back
            st.write(f"Stake de Lay: {str(stake_lay)}")
            st.write(f"Perda/Lucro: {str(stake_lay-stake_back)}")
    with tab_lb:
        odd_lay = st.number_input("Odd Lay", min_value=1.01, max_value=1000)
        responsabilidade_lay = st.number_input("Responsabilidade Lay", min_value=1.00, max_value=9999.99)
        odd_back = st.number_input("Odd Back", min_value=1.01, max_value=1000)

        if odd_lay and responsabilidade_lay and odd_back:
            stake_lay = responsabilidade_lay / (odd_lay - 1)
            stake_back = stake_lay * odd_lay / odd_back
            lucro_perda = round(responsabilidade_lay - (stake_back * (odd_back - 1)), 2)
            st.write(f"Stake de Back: {str(round(stake_back, 2))}")
            st.write(f"Perda/Lucro: {str(lucro_perda)}")
