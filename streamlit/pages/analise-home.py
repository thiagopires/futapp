import streamlit as st
import pandas as pd

from utils.functions import *

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
st.set_page_config(layout="wide")
st.title("⚽ Análise Home")

# Init

data_analise = st.date_input("Data da Análise", get_today())
df_matches = load_daymatches(data_analise)
df_hist = load_histmatches()

st.divider()

st.subheader("Filtro de Odds")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    odd_h_min = st.number_input("Odd_H_Min", value=1.40, min_value=1.10, max_value=100.00)
    odd_h_max = st.number_input("Odd_H_Max", value=2.00, min_value=1.10, max_value=100.00)
with col2:
    odd_d_min = st.number_input("Odd_D_Min", value=2.50, min_value=1.10, max_value=100.00)
    odd_d_max = st.number_input("Odd_D_Max", value=10.00, min_value=1.10, max_value=100.00)
with col3:
    odd_a_min = st.number_input("Odd_A_Min", value=4.00, min_value=1.10, max_value=100.00)
    odd_a_max = st.number_input("Odd_A_Max", value=50.00, min_value=1.10, max_value=100.00)
with col4:
    odd_over25_ft_min = st.number_input("Odd_Over25_FT_Min", value=1.30, min_value=1.10, max_value=100.00)
    odd_over25_ft_max = st.number_input("Odd_Over25_FT_Max", value=2.00, min_value=1.10, max_value=100.00)
with col5:
    odd_btts_min = st.number_input("Odd_BTTS_Min", value=1.30, min_value=1.10, max_value=100.00)
    odd_btts_max = st.number_input("Odd_BTTS_Max", value=2.00, min_value=1.10, max_value=100.00)

st.subheader("Outros Filtros")

st.divider()

st.subheader("Jogos que atendem a esses filtros")


df_matches = df_matches.loc[
    (df_matches["Odd_H_FT"] >= odd_h_min) &
    (df_matches["Odd_H_FT"] <= odd_h_max) &

    (df_matches["Odd_D_FT"] >= odd_d_min) &
    (df_matches["Odd_D_FT"] <= odd_d_max) &

    (df_matches["Odd_A_FT"] >= odd_a_min) &
    (df_matches["Odd_A_FT"] <= odd_a_max) &

    (df_matches["Odd_Over25_FT"] >= odd_over25_ft_min) &
    (df_matches["Odd_Over25_FT"] <= odd_over25_ft_max) &

    (df_matches["Odd_BTTS_Yes"] >= odd_btts_min) &
    (df_matches["Odd_BTTS_Yes"] <= odd_btts_max)
]

print_dataframe(df_matches[['League','Rodada','Time','Home','Away','Odd_H_FT','Odd_D_FT','Odd_A_FT','Odd_Over05_HT','Odd_Over15_FT','Odd_Over25_FT','Odd_BTTS_Yes']])

st.divider()

st.subheader("Selecione o Mandante e o Placar para a análise")

colb1, colb2 = st.columns(2)
with colb1:
    mandante = st.selectbox("Escolha o Mandante", df_matches['Home'])
with colb2:
    placar = st.selectbox("Escolha o Placar", ['0x0','0x1','0x2','0x3','1x0','1x1','1x2','1x3','2x0','2x1','2x2','2x3','3x3'])

df_hist_mandante_placar = df_hist.loc[
    (df_hist['Home'] == mandante) & 
    (df_hist['Resultado_FT'].str.replace("-","x") == placar) &
    (df_hist['Season'] == get_season()) # vrificar
]

# if len(df_hist_mandante_placar) > 0:
#     print_dataframe(df_hist_mandante_placar[['League','Rodada','Time','Home','Away','Odd_H_FT','Odd_D_FT','Odd_A_FT','Odd_Over05_HT','Odd_Over15_FT','Odd_Over25_FT','Odd_BTTS_Yes']])
# else:
#     st.write("Sem jogos com este placar.")

st.divider()

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

with col1:
    st.button("Profit Acumulado", use_container_width=True)
with col2:
    st.button("Ponto de Saída Punter", use_container_width=True)
    st.button("Ocorrências Gerais", use_container_width=True)
with col3:
    st.button("Ponto de Saída Trader", use_container_width=True)
    st.button("Ponto de Revisão", use_container_width=True)
with col4:
    st.button("Últimos 5 jogos", use_container_width=True)
    st.button("Confronto Direto", use_container_width=True)
with col5:
    st.button("Temporada Atual", use_container_width=True)
    st.button("Temporada Anterior", use_container_width=True)
with col6:
    st.button("Match Odds - Back", use_container_width=True)
    st.button("Match Odds - Lay", use_container_width=True)
with col7:
    if st.button("Over 2.5 FT / BTTS", use_container_width=True):
        st.subheader(f"Over 2.5 FT nos jogos do {mandante}")
        st.write(f"Jogos anteriores do {mandante} que bateram o Over 2.5 FT")

        df_hist_mandante_over25 = df_hist.loc[
            (df_hist['Home'] == mandante) & 
            (df_hist['TotalGoals_FT'] > 2.5)
        ]

        if len(df_hist_mandante_over25) > 0:
            print_dataframe(df_hist_mandante_over25[['League','Rodada','Time','Home','Away','Odd_Over25_FT','Odd_H_FT','Odd_A_FT',]])
        else:
            st.write("Sem jogos.")

        st.subheader(f"BTTS nos jogos do {mandante}")
        st.write(f"Jogos anteriores do {mandante} que bateram o BTTS")

        df_hist_mandante_btts = df_hist.loc[
            (df_hist['Home'] == mandante) & 
            (df_hist['Odd_H_FT'] >= 1) &
            (df_hist['Odd_A_FT'] >= 1)
        ]

        if len(df_hist_mandante_btts) > 0:
            print_dataframe(df_hist_mandante_btts[['League','Rodada','Time','Home','Away','Odd_BTTS_Yes','Odd_H_FT','Odd_A_FT',]])
        else:
            st.write("Sem jogos.")