import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def get_today():
    now = datetime.now()
    adjusted_time = now - timedelta(hours=3)
    return adjusted_time.date()

def print_dataframe(df, styled_df=None):
    if isinstance(styled_df, pd.io.formats.style.Styler):
        styled_df = styled_df.set_properties(**{'text-align': 'center'})
        styled_df = styled_df.set_table_styles([
            {'selector': 'th', 'props': [('text-align', 'center')]}
        ])
        st.dataframe(styled_df, height=len(df)*38, use_container_width=True, hide_index=True)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

def load_daymatches(dt):
    df = pd.read_csv(f"https://github.com/futpythontrader/YouTube/blob/main/Jogos_do_Dia/FootyStats/Jogos_do_Dia_FootyStats_{dt}.csv?raw=true")
    df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
    df["Formatted_Datetime"] = df["Datetime"].dt.strftime("%d/%m/%Y %H:%M")
    df["Confronto"] = df["Time"] + " - " + df["Home"] + " vs. " + df["Away"]
    return df

def load_histmatches():

    def first_goal_string(row):
        def parse_minutes(value, team):
            # Garantir que a entrada seja uma string e remover caracteres problemáticos
            value = str(value).replace("[", "").replace("]", "").replace("'", "")
            # Dividir em minutos e processar apenas números válidos
            return [
                (int(x.split('+')[0]), team)
                for x in value.split(',')
                if x.strip().isdigit() or '+' in x
            ]

        try:
            # Extrair e processar minutos para Home e Away
            home = parse_minutes(row['Goals_H_Minutes'], 'Home')
            away = parse_minutes(row['Goals_A_Minutes'], 'Away')
        except Exception as e:
            # Tratar casos de erro inesperado
            print(f"Erro ao processar linha: {row}. Detalhes: {e}")
            home = []
            away = []

        # Combinar os minutos de ambas as colunas
        all_goals = home + away

        # Identificar o menor minuto e sua origem
        if all_goals:
            first = min(all_goals, key=lambda x: x[0])  # Ordenar pelo minuto
            return f"{first[0]}' {first[1]}"  # Formatar como "minuto' origem"
        else:
            return '-'  # Caso não haja gols
    
    df = pd.read_csv("https://github.com/futpythontrader/YouTube/blob/main/Bases_de_Dados/FootyStats/Base_de_Dados_FootyStats_(2022_2024).csv?raw=true")
    df[["Date", "Time"]] = df["Date"].str.split(" ", expand=True)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Formatted_Date"] = df["Date"].dt.strftime("%d/%m/%Y")
    df["Resultado_FT"] = df["Goals_H_FT"].astype(str) + "-" + df["Goals_A_FT"].astype(str)
    df["Primeiro_Gol"] = df.apply(first_goal_string, axis=1)
    # df['Placar'] = f"{str(df['Goals_H_FT'])}x{str(df['Goals_A_FT'])}"
    return df

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

st.divider()

st.subheader("Jogos que atendem a esses filtros")

st.write(f"odd_h_min: {odd_h_min}")
st.write(f"odd_h_max: {odd_h_max}")

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

print_dataframe(df_matches)

st.divider()

st.subheader("Selecione o Mandante e o Placar para a análise")

colb1, colb2 = st.columns(2)
with colb1:
    mandante = st.selectbox("Escolha o Mandante", df_matches['Home'])
with colb2:
    placar = st.selectbox("Escolha o Placar", ['0x0','0x1','0x2','0x3','1x0','1x1','1x2','1x3','2x0','2x1','2x2','2x3','3x3'])

df_hist.loc[(df_hist['Home'] == mandante) & (df_hist['Resultado_FT'].replace("-","x") == placar)]

if len(df_hist) > 0:
    print_dataframe(df_hist)
else:
    st.write("Sem jogos com este placar.")