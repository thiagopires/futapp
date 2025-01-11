import streamlit as st
import pandas as pd

from utils.functions import *

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
st.set_page_config(layout="wide")
st.title("⚽ Análise Home")

def aba_over25(df_hist, team, side):
    dict = {}
    df = df_hist.loc[
        (df_hist[side] == team) & 
        ((df_hist['Season'] == get_current_season()) | (df_hist['Season'] == get_last_season()))
    ]
    dict['Jogos analisados'] = len(df)

    df['Profit_Over25'] = -1
    df.loc[df['TotalGoals_FT'] > 2.5, 'Profit_Over25'] = round(df['Odd_Over25_FT']-1, 2)

    dict['Profit Acumulado'] = f"{str(round(df['Profit_Over25'].sum(), 2))} unidades"

    df = df.loc[(df_hist['TotalGoals_FT'] > 2.5)]
    dict['Jogos Over 2.5 FT'] = len(df)

    dict['Winrate'] = f"{round((dict['Jogos Over 2.5 FT'] / dict['Jogos analisados']) * 100, 2)}%" if dict['Jogos analisados'] > 0 else "0.0%"
 
    if len(df) > 0:
        st.write(f"Jogos analisados: {dict['Jogos analisados']} — Jogos Over 2.5 FT: {dict['Jogos Over 2.5 FT']} — Winrate: {dict['Winrate']} — Profit Acumulado: {dict['Profit Acumulado']}")
        print_dataframe(df[['League','Season','Date','Home','Away','Odd_Over25_FT','Goals_H_FT','Goals_A_FT','Profit_Over25']])
    else:
        st.write("Sem jogos.")

def aba_btts(df_hist, team, side):
    dict = {}
    df = df_hist.loc[
        (df_hist[side] == team) & 
        ((df_hist['Season'] == get_current_season()) | (df_hist['Season'] == get_last_season()))
    ]
    dict['Jogos analisados'] = len(df)

    df['Profit_BTTS'] = -1
    df.loc[(df['Goals_H_FT'] >= 1) & (df['Goals_A_FT'] >= 1), 'Profit_BTTS'] = round(df['Odd_BTTS_Yes']-1, 2)

    dict['Profit Acumulado'] = f"{str(round(df['Profit_BTTS'].sum(), 2))} unidades"

    df = df.loc[(df['Goals_H_FT'] >= 1) & (df['Goals_A_FT'] >= 1)]
    dict['Jogos BTTS'] = len(df)

    dict['Winrate'] = f"{round((dict['Jogos BTTS'] / dict['Jogos analisados']) * 100, 2)}%" if dict['Jogos analisados'] > 0 else "0.0%"
 
    if len(df) > 0:
        st.write(f"Jogos analisados: {dict['Jogos analisados']} — Jogos BTTS: {dict['Jogos BTTS']} — Winrate: {dict['Winrate']} — Profit Acumulado: {dict['Profit Acumulado']}")
        print_dataframe(df[['League','Season','Date','Home','Away','Odd_BTTS_Yes','Goals_H_FT','Goals_A_FT','Profit_BTTS']])
    else:
        st.write("Sem jogos.")

def aba_ult10(df_hist, team, side):
    df = df_hist.loc[
        (team == df_hist[side]), 
        ['Date','Season','Home','Away','Goals_H_HT','Goals_A_HT','Goals_H_FT','Goals_A_FT','Odd_H_FT','Odd_D_FT','Odd_A_FT','Odd_Over25_FT','Odd_BTTS_Yes']
    ].sort_values(by="Date", ascending=False).head(10)
    
    if len(df) > 0:
        print_dataframe(df)
    else:
        st.write("Sem jogos.")

def set_odds_filtros(reset=False):
    if reset:
        st.session_state['odd_h_min'] = 1.10
        st.session_state['odd_h_max'] = 1000.00
        st.session_state['odd_d_min'] = 1.10
        st.session_state['odd_d_max'] = 1000.00
        st.session_state['odd_a_min'] = 1.10
        st.session_state['odd_a_max'] = 1000.00
        st.session_state['odd_over25_ft_min'] = 1.10
        st.session_state['odd_over25_ft_max'] = 1000.00
        st.session_state['odd_btts_min'] = 1.10
        st.session_state['odd_btts_max'] = 1000.00
    else:
        if "odd_h_min" not in st.session_state: st.session_state['odd_h_min'] = 1.40
        if "odd_h_max" not in st.session_state: st.session_state['odd_h_max'] = 2.00
        if "odd_d_min" not in st.session_state: st.session_state['odd_d_min'] = 2.50
        if "odd_d_max" not in st.session_state: st.session_state['odd_d_max'] = 10.00
        if "odd_a_min" not in st.session_state: st.session_state['odd_a_min'] = 4.00
        if "odd_a_max" not in st.session_state: st.session_state['odd_a_max'] = 50.00
        if "odd_over25_ft_min" not in st.session_state: st.session_state['odd_over25_ft_min'] = 1.30
        if "odd_over25_ft_max" not in st.session_state: st.session_state['odd_over25_ft_max'] = 2.00
        if "odd_btts_min" not in st.session_state: st.session_state['odd_btts_min'] = 1.30
        if "odd_btts_max" not in st.session_state: st.session_state['odd_btts_max'] = 2.00

# Init

data_analise = st.date_input("Data da Análise", get_today())
df_matches = load_daymatches(data_analise)
df_hist = load_histmatches()


st.divider()


st.subheader("Filtro de Odds")
set_odds_filtros(False)
if st.button("Limpar filtros"):
    set_odds_filtros(True)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.number_input("Odd_H_Min", value=st.session_state.odd_h_min, min_value=1.10, max_value=1000.00, key="odd_h_min")
    st.number_input("Odd_H_Max", value=st.session_state.odd_h_max, min_value=1.10, max_value=1000.00, key="odd_h_max")
with col2:
    st.number_input("Odd_D_Min", value=st.session_state.odd_d_min, min_value=1.10, max_value=1000.00, key="odd_d_min")
    st.number_input("Odd_D_Max", value=st.session_state.odd_d_max, min_value=1.10, max_value=1000.00, key="odd_d_max")
with col3:
    st.number_input("Odd_A_Min", value=st.session_state.odd_a_min, min_value=1.10, max_value=1000.00, key="odd_a_min")
    st.number_input("Odd_A_Max", value=st.session_state.odd_a_max, min_value=1.10, max_value=1000.00, key="odd_a_max")
with col4:
    st.number_input("Odd_Over25_FT_Min", value=st.session_state.odd_over25_ft_min, min_value=1.10, max_value=1000.00, key="odd_over25_ft_min")
    st.number_input("Odd_Over25_FT_Max", value=st.session_state.odd_over25_ft_max, min_value=1.10, max_value=1000.00, key="odd_over25_ft_max")
with col5:
    st.number_input("Odd_BTTS_Min", value=st.session_state.odd_btts_min, min_value=1.10, max_value=1000.00, key="odd_btts_min")
    st.number_input("Odd_BTTS_Max", value=st.session_state.odd_btts_max, min_value=1.10, max_value=1000.00, key="odd_btts_max")


st.divider()


st.subheader("Jogos que atendem a esses filtros")

df_matches = df_matches.loc[
    (df_matches["Odd_H_FT"] >= st.session_state.odd_h_min) &
    (df_matches["Odd_H_FT"] <= st.session_state.odd_h_max) &

    (df_matches["Odd_D_FT"] >= st.session_state.odd_d_min) &
    (df_matches["Odd_D_FT"] <= st.session_state.odd_d_max) &

    (df_matches["Odd_A_FT"] >= st.session_state.odd_a_min) &
    (df_matches["Odd_A_FT"] <= st.session_state.odd_a_max) &

    (df_matches["Odd_Over25_FT"] >= st.session_state.odd_over25_ft_min) &
    (df_matches["Odd_Over25_FT"] <= st.session_state.odd_over25_ft_max) &

    (df_matches["Odd_BTTS_Yes"] >= st.session_state.odd_btts_min) &
    (df_matches["Odd_BTTS_Yes"] <= st.session_state.odd_btts_max)
]

print_dataframe(df_matches[['League','Rodada','Time','Home','Away','Odd_H_FT','Odd_D_FT','Odd_A_FT','Odd_Over05_HT','Odd_Over15_FT','Odd_Over25_FT','Odd_BTTS_Yes']])

st.divider()

st.subheader("Selecione o Mandante e o Placar para a análise")

colb1, colb2 = st.columns(2)
with colb1:
    mandante = st.selectbox("Escolha o Mandante", df_matches['Home'])
with colb2:
    placar = st.selectbox("Escolha o Placar", ['0x0','0x1','0x2','0x3','1x0','1x1','1x2','1x3','2x0','2x1','2x2','2x3','3x0','3x1','3x2','3x3'])

# df_hist_mandante_placar = df_hist.loc[
#     (df_hist['Home'] == mandante) & 
#     (df_hist['Resultado_FT'].str.replace("-","x") == placar) &
#     (df_hist['Season'] == get_current_season()) # vrificar
# ]

# if len(df_hist_mandante_placar) > 0:
#     print_dataframe(df_hist_mandante_placar[['League','Rodada','Time','Home','Away','Odd_H_FT','Odd_D_FT','Odd_A_FT','Odd_Over05_HT','Odd_Over15_FT','Odd_Over25_FT','Odd_BTTS_Yes']])
# else:
#     st.write("Sem jogos com este placar.")

st.divider()

st.session_state['active_button'] = ""

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
with col1:
    if st.button("Profit Acumulado", use_container_width=True):
        st.session_state['active_button'] = "Profit Acumulado"
with col2:
    st.button("Ponto de Saída Punter", use_container_width=True)
    st.button("Ocorrências Gerais", use_container_width=True)
with col3:
    st.button("Ponto de Saída Trader", use_container_width=True)
    st.button("Ponto de Revisão", use_container_width=True)
with col4:
    if st.button("Últimos 10 jogos", use_container_width=True):
        st.session_state['active_button'] = "Últimos 10 jogos"
    st.button("Confronto Direto", use_container_width=True)
with col5:
    st.button("Temporada Atual", use_container_width=True)
    st.button("Temporada Anterior", use_container_width=True)
with col6:
    st.button("Match Odds - Back", use_container_width=True)
    st.button("Match Odds - Lay", use_container_width=True)
with col7:
    if st.button("Over 2.5 FT / BTTS", use_container_width=True):
        st.session_state['active_button'] = "Over 2.5 FT / BTTS"
        
###
     
if st.session_state['active_button'] == "Over 2.5 FT / BTTS":
            
    st.subheader(f"Over 2.5 FT nos jogos do {mandante}")
    st.write(f"Jogos anteriores do {mandante} que bateram o Over 2.5 FT")    
    aba_over25(df_hist, mandante, "Home")

    st.subheader(f"BTTS nos jogos do {mandante}")
    st.write(f"Jogos anteriores do {mandante} que bateram o BTTS")
    aba_btts(df_hist, mandante, "Home")

elif st.session_state['active_button'] == "Últimos 10 jogos":

    st.subheader(f"Últimos 10 jogos do {mandante} como Mandante")
    aba_ult10(df_hist, mandante, "Home")

    st.subheader(f"Últimos 10 jogos do {mandante} como Visitante")
    aba_ult10(df_hist, mandante, "Away")

    # df_hist_mandante_btts = df_hist.loc[
    #     (df_hist['Home'] == mandante) & 
    #     (df_hist['Goals_H_FT'] >= 1) &
    #     (df_hist['Goals_A_FT'] >= 1)
    # ]

    # if len(df_hist_mandante_btts) > 0:
    #     print_dataframe(df_hist_mandante_btts[['League','Rodada','Time','Home','Away','Odd_BTTS_Yes','Goals_H_FT','Goals_A_FT']])
    # else:
    #     st.write("Sem jogos.")