import streamlit as st

from utils.functions import *

st.set_page_config(layout="wide")
st.title("⚽ Calculadora")

col_cashout, col_freebet = st.columns(2)
with col_cashout:
    st.header("Cashout")
    tab_bl, tab_lb = st.tabs(["Back/Lay","Lay/Back"])
    with tab_bl:
        odd_back = st.number_input("Odd Back", key="bl_odd_back")
        stake_back = st.number_input("Stake Back", key="bl_stake_back")
        odd_lay = st.number_input("Odd Lay", key="bl_odd_lay")

        if odd_back and stake_back and odd_lay:
            stake_lay = stake_back/odd_lay*odd_back
            lucro_perda = str(round(stake_lay-stake_back, 2))

            st.write(f"Stake de Lay:")           
            container = st.container(border=True)
            container.code(str(round(stake_lay, 2)), language="text")
            
            st.write(f"Perda/Lucro:")
            container = st.container(border=True)
            container.code(str(lucro_perda), language="text")
  

    with tab_lb:
        odd_lay = st.number_input("Odd Lay",key="lb_odd_lay")
        responsabilidade_lay = st.number_input("Responsabilidade Lay", key="lb_responsabilidade_lay")
        odd_back = st.number_input("Odd Back", key="lb_odd_back")

        if odd_lay and responsabilidade_lay and odd_back:
            stake_lay = responsabilidade_lay / (odd_lay - 1)
            stake_back = stake_lay * odd_lay / odd_back
            lucro_perda = round((stake_back * (odd_back - 1)) - responsabilidade_lay, 2)
            
            st.write(f"Stake de Back:")
            container = st.container(border=True)
            container.code(str(round(stake_back, 2)), language="text")

            st.write(f"Perda/Lucro: {str(lucro_perda)}")
            container = st.container(border=True)
            container.code(str(lucro_perda), language="text")

with col_freebet:
    st.header("Freebet")
    st.write("ok")
