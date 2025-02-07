import streamlit as st

from utils.functions import *

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
st.set_page_config(layout="wide")

def main_page():

    if st.secrets['ENV'] == 'dev':
        st.info("Ambiente de Desenvolvimento. Branch: dev")

    st.title("Futapp v0.1")
    st.header("⚽ Calculadora")

    def clear_state(keys):
        for key in keys:
            if key in st.session_state:
                del st.session_state[key]

    aba = st.radio("Selecione a aba", ["Back/Lay", "Lay/Back"], key="active_tab")

    col_cashout, col_resultado = st.columns(2)

    # Coluna de Cashout
    with col_cashout:
        st.header("Cashout")

        if aba == "Back/Lay":
            clear_state(["lb_odd_lay", "lb_responsabilidade_lay", "lb_odd_back"])

            st.number_input("Odd Back", key="bl_odd_back")
            st.number_input("Stake Back", key="bl_stake_back")
            st.number_input("Odd Lay", key="bl_odd_lay")

        elif aba == "Lay/Back":
            clear_state(["bl_odd_back", "bl_stake_back", "bl_odd_lay"])

            st.number_input("Odd Lay", key="lb_odd_lay")
            st.number_input("Responsabilidade Lay", key="lb_responsabilidade_lay")
            st.number_input("Odd Back", key="lb_odd_back")

    with col_resultado:
        col1, col2, col3 = st.columns(3)
        with col1:
            # Back/Lay
            if aba == "Back/Lay" and st.session_state.get('bl_odd_back') and st.session_state.get('bl_stake_back') and st.session_state.get('bl_odd_lay'):
                stake_lay = st.session_state['bl_stake_back'] / st.session_state['bl_odd_lay'] * st.session_state['bl_odd_back']
                lucro_perda = round(stake_lay - st.session_state['bl_stake_back'], 2)

                st.write(f"Stake de Lay:")
                container = st.container(border=True)
                container.code(str(round(stake_lay, 2)), language="text")

                st.write(f"Perda/Lucro:")
                container = st.container(border=True)
                container.code(str(lucro_perda), language="text")

            # Lay/Back
            if aba == "Lay/Back" and st.session_state.get('lb_odd_lay') and st.session_state.get('lb_responsabilidade_lay') and st.session_state.get('lb_odd_back'):
                stake_lay = st.session_state['lb_responsabilidade_lay'] / (st.session_state['lb_odd_lay'] - 1)
                stake_back = stake_lay * st.session_state['lb_odd_lay'] / st.session_state['lb_odd_back']
                lucro_perda = round((stake_back * (st.session_state['lb_odd_back'] - 1)) - st.session_state['lb_responsabilidade_lay'], 2)

                st.write(f"Stake de Back:")
                container = st.container(border=True)
                container.code(str(round(stake_back, 2)), language="text")

                st.write(f"Perda/Lucro:")
                container = st.container(border=True)
                container.code(str(lucro_perda), language="text")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    display_sidebar('block')
    main_page()
else:
    login_page()