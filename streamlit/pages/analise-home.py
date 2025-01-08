import streamlit as st
import pandas as pd
import plotly.express as px
import ast
from datetime import datetime

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

def load_daymatches(dt):
    df = pd.read_csv(f"https://github.com/futpythontrader/YouTube/blob/main/Jogos_do_Dia/FootyStats/Jogos_do_Dia_FootyStats_{dt}.csv?raw=true")
    df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
    df["Formatted_Datetime"] = df["Datetime"].dt.strftime("%d/%m/%Y %H:%M")
    df["Confronto"] = df["Time"] + " - " + df["Home"] + " vs. " + df["Away"]
    return df

def load_histmatches():
    df = pd.read_csv("https://github.com/futpythontrader/YouTube/blob/main/Bases_de_Dados/FootyStats/Base_de_Dados_FootyStats_(2022_2024).csv?raw=true")
    df[["Date", "Time"]] = df["Date"].str.split(" ", expand=True)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Formatted_Date"] = df["Date"].dt.strftime("%d/%m/%Y")
    df["Resultado_FT"] = df["Goals_H_FT"].astype(str) + "-" + df["Goals_A_FT"].astype(str)
    df["Primeiro_Gol"] = df.apply(first_goal_string, axis=1)
    return df

st.set_page_config(layout="wide")

st.title("⚽ Análise Home")

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