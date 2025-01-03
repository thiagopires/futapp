import streamlit as st
import pandas as pd
import numpy as np
import datetime
from datetime import date

st.set_page_config(layout="wide")
st.title("Jogos do dia")

dia = st.date_input(
  "Data de Análise",
  date.today())

def load_data_matches():
  data_matches = pd.read_csv(f"https://github.com/futpythontrader/YouTube/blob/main/Jogos_do_Dia/FootyStats/Jogos_do_Dia_FootyStats_{str(dia)}.csv?raw=true")
  return data_matches

df_matches = load_data_matches()

st.dataframe(df_matches)
