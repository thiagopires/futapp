import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from datetime import date, timedelta

def print_dataframe(df):
    st.dataframe(df, use_container_width=True, hide_index=True)
    
@st.cache_data
def load_daymatches(i):
    dia = date.today() + timedelta(days=i)
    df = pd.read_csv(f"https://github.com/futpythontrader/YouTube/blob/main/Jogos_do_Dia/FootyStats/Jogos_do_Dia_FootyStats_{str(dia)}.csv?raw=true")
    df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
    df["Formatted_Datetime"] = df["Datetime"].dt.strftime("%d/%m/%Y %H:%M")
    return df

@st.cache_data
def load_histmatches():
    df = pd.read_csv("https://github.com/futpythontrader/YouTube/blob/main/Bases_de_Dados/FootyStats/Base_de_Dados_FootyStats_(2022_2024).csv?raw=true")
    df[["Date", "Time"]] = df["Date"].str.split(" ", expand=True)
    df["Date"] = pd.to_date(df["Date"])
    df["Formatted_Date"] = df["Date"].dt.strftime("%d/%m/%Y")
    df["Resultado_FT"] = str(df["Goals_H_FT"]) + "-" + str(df["Goals_A_FT"])
    return df

# Configuração da página
st.set_page_config(
    page_title="Análise de Confrontos de Futebol",
    page_icon="⚽",
    layout="wide",
)

df_matches = load_daymatches(0)
df_hist = load_histmatches()

# Título do dashboard
st.title("⚽ Análise Completa do Confronto de Futebol")

df_matches["Confronto"] = df_matches["Home"] + " vs. " + df_matches["Away"]
matches = df_matches["Confronto"].value_counts().index

# Entrada para seleção do confronto
st.sidebar.header("Selecione o Confronto")
match_selected = st.sidebar.selectbox("Confronto", matches)
df_match_selected = df_matches[df_matches["Confronto"] == match_selected].iloc[0]

# club1 = st.sidebar.selectbox("Clube 1", ["Nacional", "Benfica", "Porto"])
# club2 = st.sidebar.selectbox("Clube 2", ["Nacional", "Benfica", "Porto"])
# match_date = st.sidebar.date_input("Data do Jogo")
# league = st.sidebar.selectbox("Campeonato", ["Primeira Liga", "Copa de Portugal"])
# round_number = st.sidebar.number_input("Rodada", min_value=1, step=1)

# Exibição do confronto
st.caption(f"{df_match_selected['Formatted_Datetime']} - {df_match_selected["League"]} (Rodada {df_match_selected["Rodada"]})")
st.subheader(df_match_selected["Confronto"])
# st.write(f"*Data:* {str(df_match_selected["Datetime"])} | *Campeonato:* {df_match_selected["League"]} | *Rodada:* {df_match_selected["Rodada"]}")
st.divider()

# Dados Simulados para Confrontos
# confrontos = pd.DataFrame({
#     "Data": ["2023-01-01", "2022-03-15", "2021-07-20"],
#     "Clube 1": ["Nacional", "Nacional", "Benfica"],
#     "Clube 2": ["Benfica", "Benfica", "Nacional"],
#     "Resultado": ["1-2", "0-3", "2-1"]
# })
filter_confrontos = (df_hist["Home"].isin([df_match_selected["Home"], df_match_selected["Away"]])) & (df_hist["Away"].isin([df_match_selected["Home"], df_match_selected["Away"]]))
confrontos = df_hist.loc[filter_confrontos, ["Date", "Season", "Home", "Away"]].sort_values(by="Date", ascending=False)

# Dividindo a página em duas colunas
col1, col2 = st.columns(2)
with col1:
    st.subheader("Odds")
    col11, col12, col13 = st.columns(3)
    col11.metric(label="MO Home", value=df_match_selected["Odd_H_FT"])
    col12.metric(label="MO Draw", value=df_match_selected["Odd_D_FT"])
    col13.metric(label="MO Away", value=df_match_selected["Odd_A_FT"])
    col11.metric(label="Over 0.5 HT", value=df_match_selected["Odd_Over05_HT"])
    col12.metric(label="Over 2.5 FT", value=df_match_selected["Odd_Over25_FT"])
    col13.metric(label="BTTS", value=df_match_selected["Odd_BTTS_Yes"])
    # col7.metric(label="BTTS", value="1.95")
with col2:
    st.subheader("Confrontos diretos nos últimos 3 anos")
    print_dataframe(confrontos)

# Tabela 6 e Tabela 7: Últimos 10 jogos
ultimos_casa = pd.DataFrame({
    "Data": ["2023-12-01", "2023-11-28", "2023-11-15"],
    "Adversário": ["Porto", "Sporting", "Braga"],
    "Resultado": ["2-0", "1-1", "0-3"]
})
ultimos_visitante = pd.DataFrame({
    "Data": ["2023-12-02", "2023-11-27", "2023-11-14"],
    "Adversário": ["Portimonense", "Boavista", "Vitória SC"],
    "Resultado": ["1-1", "3-2", "0-1"]
})
col1, col2 = st.columns(2)
with col1:
    st.subheader("Últimos 10 Jogos - Casa")
    print_dataframe(ultimos_casa)
with col2:
    st.subheader("Últimos 10 Jogos - Visitante")
    print_dataframe(ultimos_visitante)

st.subheader("⚽ Classificações nesta competição")

classificacao_geral = pd.DataFrame({
    "Posição": [1, 2, 3, 4],
    "Clube": ["Benfica", "Porto", "Sporting", "Braga"],
    "Pontos": [50, 47, 45, 42],
    "Jogos": [20, 20, 20, 20],
    "Vitórias": [16, 15, 14, 13],
    "Empates": [2, 2, 3, 3],
    "Derrotas": [2, 3, 3, 4],
})

classificacao_casa = pd.DataFrame({
    "Posição": [1, 2, 3, 4],
    "Clube": ["Benfica", "Porto", "Braga", "Sporting"],
    "Pontos em Casa": [30, 28, 26, 24],
    "Jogos em Casa": [10, 10, 10, 10],
    "Vitórias em Casa": [10, 9, 8, 8],
    "Empates em Casa": [0, 1, 2, 0],
    "Derrotas em Casa": [0, 0, 0, 2],
})

classificacao_visitante = pd.DataFrame({
    "Posição": [1, 2, 3, 4],
    "Clube": ["Porto", "Benfica", "Sporting", "Braga"],
    "Pontos Fora": [25, 23, 21, 18],
    "Jogos Fora": [10, 10, 10, 10],
    "Vitórias Fora": [8, 7, 7, 6],
    "Empates Fora": [1, 2, 0, 0],
    "Derrotas Fora": [1, 1, 3, 4],
})

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Geral")
    print_dataframe(classificacao_geral)
with col2:
    st.subheader("Casa")
    print_dataframe(classificacao_casa)
with col3:
    st.subheader("Visitante")
    print_dataframe(classificacao_visitante)

# Tabela 25 e 26: Gols Casa e Visitante
gols = pd.DataFrame({
    "Minuto": ["0-15", "16-30", "31-45", "46-60", "61-75", "76-90"],
    "Gols Casa": [3, 5, 2, 6, 4, 8],
    "Gols Visitante": [2, 3, 4, 3, 6, 5]
})
st.subheader("Distribuição de Gols por Minuto")
fig = px.bar(gols, x="Minuto", y=["Gols Casa", "Gols Visitante"], barmode="group", title="Gols por Minuto")
st.plotly_chart(fig, use_container_width=True)

# Tabela 22 e 23: Percurso Casa e Visitante
percurso_casa = pd.DataFrame({
    "Sequência de Vitórias": 1,
    "Sequência de Empates": 0,
    "Sequência de Derrotas": 3,
    "Não ganha há": 7,
    "Não empata há": 1,
    "Não perde há": 3,
})
percurso_visitante = pd.DataFrame({
    "Sequência de Vitórias": 2,
    "Sequência de Empates": 1,
    "Sequência de Derrotas": 0,
    "Não ganha há": 1,
    "Não empata há": 2,
    "Não perde há": 5,
})
col1, col2 = st.columns(2)
with col1:
    st.subheader("Percurso - Casa")
    print_dataframe(percurso_casa)
with col2:
    st.subheader("Percurso - Visitante")
    print_dataframe(percurso_visitante)


# Título
st.subheader("⚽ Estatísticas de Confrontos de Futebol")

# Dados Simulados para Times
estatisticas_time_1 = {
    "Categoria": [
        "Média de gols marcados por jogo",
        "Média de gols sofridos por jogo",
        "Média de gols marcados + sofridos",
        "Jogos sem sofrer gols",
        "Jogos sem marcar gols",
        "Jogos com Mais de 2,5 Gols",
        "Jogos com Menos de 2,5 Gols"
    ],
    "Casa": [2.83, 0.5, 3.33, "67%", "-", "67%", "33%"],
    "Fora": [3.13, 1.13, 4.26, "38%", "-", "75%", "25%"],
    "Global": [3.0, 0.86, 3.86, "50%", "-", "71%", "29%"],
}

estatisticas_time_11 = {
    "Categoria": [
        "Abre marcador (qualquer altura)",
        "Está a vencer ao intervalo",
        "Vence no final",
        "Reviravoltas"
    ],
    "Casa": ["5 em 6 (83%)", "3 em 5 (60%)", "5 em 5 (100%)", "0 em 1 (0%)"],
    "Global": ["10 em 15 (67%)", "6 em 10 (60%)", "8 em 8 (80%)", "1 em 5 (20%)"]
}

estatisticas_time_2 = {
    "Categoria": [
        "Média de gols marcados por jogo",
        "Média de gols sofridos por jogo",
        "Média de gols marcados + sofridos",
        "Jogos sem sofrer gols",
        "Jogos sem marcar gols",
        "Jogos com Mais de 2,5 Gols",
        "Jogos com Menos de 2,5 Gols"
    ],
    "Casa": [2.83, 0.5, 3.33, "67%", "-", "67%", "33%"],
    "Fora": [3.13, 1.13, 4.26, "38%", "-", "75%", "25%"],
    "Global": [3.0, 0.86, 3.86, "50%", "-", "71%", "29%"],
}

estatisticas_time_22 = {
    "Categoria": [
        "Abre marcador (qualquer altura)",
        "Está a vencer ao intervalo",
        "Vence no final",
        "Reviravoltas"
    ],
    "Casa": ["5 em 6 (83%)", "3 em 5 (60%)", "5 em 5 (100%)", "0 em 1 (0%)"],
    "Global": ["10 em 15 (67%)", "6 em 10 (60%)", "8 em 8 (80%)", "1 em 5 (20%)"]
}

# Converte para DataFrame
df_time_1 = pd.DataFrame(estatisticas_time_1)
df_time_11 = pd.DataFrame(estatisticas_time_11)
df_time_2 = pd.DataFrame(estatisticas_time_2)
df_time_22 = pd.DataFrame(estatisticas_time_22)

col1, col2 = st.columns(2)
with col1:
    st.subheader(club1)
    print_dataframe(df_time_1.to_dict(orient='records'))
    print_dataframe(df_time_11.to_dict(orient='records'))
with col2:
    st.subheader(club2)
    print_dataframe(df_time_2.to_dict(orient='records'))
    print_dataframe(df_time_22.to_dict(orient='records'))

# Outros dados e análises podem ser adicionados conforme necessário
st.write("⚡ Dashboard dinâmico para análise de confrontos! ⚡")
