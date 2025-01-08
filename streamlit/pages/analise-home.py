import streamlit as st
import pandas as pd
from datetime import datetime

from utils.functions import *

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
st.set_page_config(layout="wide")
st.title("⚽ Análise Home")

# Init

data_analise = st.date_input("Data da Análise", datetime.today())
df_matches = load_daymatches(data_analise)
df_hist = load_histmatches()

st.divider()

st.subheader("Filtro de Odds")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    odd_h_min = st.number_input("Odd_H_Min", value=1.10, min_value=1.10, max_value=100.00)
    odd_h_max = st.number_input("Odd_H_Max", value=100.00, min_value=1.10, max_value=100.00)
with col2:
    odd_d_min = st.number_input("Odd_D_Min", value=1.10, min_value=1.10, max_value=100.00)
    odd_d_max = st.number_input("Odd_D_Max", value=100.00, min_value=1.10, max_value=100.00)
with col3:
    odd_a_min = st.number_input("Odd_A_Min", value=1.10, min_value=1.10, max_value=100.00)
    odd_a_max = st.number_input("Odd_A_Max", value=100.00, min_value=1.10, max_value=100.00)
with col4:
    odd_over25_ft_min = st.number_input("Odd_Over25_FT_Min", value=1.10, min_value=1.10, max_value=100.00)
    odd_over25_ft_max = st.number_input("Odd_Over25_FT_Max", value=100.00, min_value=1.10, max_value=100.00)
with col5:
    odd_btts_min = st.number_input("Odd_BTTS_Min", value=1.10, min_value=1.10, max_value=100.00)
    odd_btts_max = st.number_input("Odd_BTTS_Max", value=100.00, min_value=1.10, max_value=100.00)

st.subheader("Outros Filtros")