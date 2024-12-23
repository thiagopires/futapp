import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from datetime import date, timedelta

def print_dataframe(df, pheight=None):
    st.dataframe(df, height=pheight, use_container_width=True, hide_index=True)

def load_daymatches(i):
    dia = date.today() + timedelta(days=i)
    df = pd.read_csv(f"https://github.com/futpythontrader/YouTube/blob/main/Jogos_do_Dia/FootyStats/Jogos_do_Dia_FootyStats_{str(dia)}.csv?raw=true")
    df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
    df["Formatted_Datetime"] = df["Datetime"].dt.strftime("%d/%m/%Y %H:%M")
    return df

def load_histmatches():
    df = pd.read_csv("https://github.com/futpythontrader/YouTube/blob/main/Bases_de_Dados/FootyStats/Base_de_Dados_FootyStats_(2022_2024).csv?raw=true")
    df[["Date", "Time"]] = df["Date"].str.split(" ", expand=True)
    df["Date"] = pd.to_datetime(df["Date"])
    # df["Date"] = df["Date"].dt.date
    df["Formatted_Date"] = df["Date"].dt.strftime("%d/%m/%Y")
    df["Resultado_FT"] = df["Goals_H_FT"].astype(str) + "-" + df["Goals_A_FT"].astype(str)
    return df

def atualizar_estatisticas(row, clubes, casa=True):
    clube = row["Home"] if casa else row["Away"]
    gols_favor = row["Goals_H_FT"] if casa else row["Goals_A_FT"]
    gols_contra = row["Goals_A_FT"] if casa else row["Goals_H_FT"]
    pontos = 3 if (row["Home_Win"] if casa else row["Away_Win"]) else 1 if row["Draw"] else 0

    clubes.loc[clube, "P"] += 1
    clubes.loc[clube, "W"] += 1 if (row["Home_Win"] if casa else row["Away_Win"]) else 0
    clubes.loc[clube, "D"] += 1 if row["Draw"] else 0
    clubes.loc[clube, "L"] += 1 if not row["Draw"] and not (row["Home_Win"] if casa else row["Away_Win"]) else 0
    clubes.loc[clube, "GF"] += gols_favor
    clubes.loc[clube, "GC"] += gols_contra
    clubes.loc[clube, "PTS"] += pontos
    clubes.loc[clube, "DIFF"] += gols_favor - gols_contra

def generate_classificacao(df, type):
    # Calculando o resultado do jogo
    df["Home_Win"] = df["Goals_H_FT"] > df["Goals_A_FT"]
    df["Away_Win"] = df["Goals_H_FT"] < df["Goals_A_FT"]
    df["Draw"] = df["Goals_H_FT"] == df["Goals_A_FT"]
    
    # Inicializando as tabelas de pontos
    clubes = pd.DataFrame({"Clube": pd.concat([df["Home"], df["Away"]]).unique()})
    clubes.set_index("Clube", inplace=True)
    columns = ["PTS", "P", "W", "D", "L", "GF", "GC", "DIFF"]
    for col in columns:
        clubes[col] = 0
    
    # Atualizando estatísticas para todos os jogos
    for _, row in df.iterrows():
        if type == 'HOME':
            atualizar_estatisticas(row, clubes, casa=True)
        elif type == 'AWAY':
            atualizar_estatisticas(row, clubes, casa=False)
        elif type == 'ALL':
            atualizar_estatisticas(row, clubes, casa=True)
            atualizar_estatisticas(row, clubes, casa=False)
    
    # Adicionando a posição e ordenando

    clubes = clubes.sort_values(by=["PTS", "DIFF", "GF"], ascending=False)
    clubes["Goals"] = clubes["GF"].astype(str) + ":" + clubes["GC"].astype(str)
    clubes["#"] = range(1, len(clubes) + 1)

    classificacao = clubes.reset_index()
    classificacao = classificacao[["#", "Clube", "PTS", "P", "W", "D", "L", "DIFF", "Goals"]]

    if type == 'HOME':
        classificacao = classificacao.style.map(lambda v: 'background-color: yellow' if v == df_match_selected["Home"] else '', subset=["Clube"])
    elif type == 'AWAY':
        classificacao = classificacao.style.map(lambda v: 'background-color: yellow' if v == df_match_selected["Away"] else '', subset=["Clube"])
    elif type == 'ALL':
        classificacao = classificacao.style.map(lambda v: 'background-color: yellow' if (v == df_match_selected["Home"] or v == df_match_selected["Away"]) else '', subset=["Clube"])

    return classificacao

    # Configuração da página
    st.set_page_config(
        page_title="Análise de Confrontos de Futebol",
        page_icon="⚽",
        layout="wide",
    )

# Carregando as bases
df_matches = load_daymatches(0)
df_hist = load_histmatches()

# Sidebar
st.sidebar.header("Selecione o Confronto")

left, middle, right = st.sidebar.columns(3)
if left.button("Hoje", use_container_width=True):
    df_matches = load_daymatches(0)
if middle.button("Amanhã", use_container_width=True):
    df_matches = load_daymatches(1)
if right.button("D.Amanhã", use_container_width=True):
    df_matches = load_daymatches(2)

df_matches["Confronto"] = df_matches["Home"] + " vs. " + df_matches["Away"]
matches = df_matches["Confronto"].value_counts().index
match_selected = st.sidebar.selectbox("Confronto", matches)
df_match_selected = df_matches[df_matches["Confronto"] == match_selected].iloc[0]

# Título do dashboard
st.title("⚽ Análise Completa do Confronto de Futebol")

# club1 = st.sidebar.selectbox("Clube 1", ["Nacional", "Benfica", "Porto"])
# club2 = st.sidebar.selectbox("Clube 2", ["Nacional", "Benfica", "Porto"])
# match_date = st.sidebar.date_input("Data do Jogo")
# league = st.sidebar.selectbox("Campeonato", ["Primeira Liga", "Copa de Portugal"])
# round_number = st.sidebar.number_input("Rodada", min_value=1, step=1)

# Header
st.caption(f"{df_match_selected['Formatted_Datetime']} - {df_match_selected["League"]} (Rodada {df_match_selected["Rodada"]})")
st.subheader(df_match_selected["Confronto"])
st.divider()

# st.write(f"*Data:* {str(df_match_selected["Datetime"])} | *Campeonato:* {df_match_selected["League"]} | *Rodada:* {df_match_selected["Rodada"]}")

# Dados Simulados para Confrontos
# confrontos = pd.DataFrame({
#     "Data": ["2023-01-01", "2022-03-15", "2021-07-20"],
#     "Clube 1": ["Nacional", "Nacional", "Benfica"],
#     "Clube 2": ["Benfica", "Benfica", "Nacional"],
#     "Resultado": ["1-2", "0-3", "2-1"]
# })

filter_confrontos = (df_hist["Home"].isin([df_match_selected["Home"], df_match_selected["Away"]])) & (df_hist["Away"].isin([df_match_selected["Home"], df_match_selected["Away"]]))
confrontos = df_hist.loc[filter_confrontos, ["Date", "Season", "Home", "Resultado_FT", "Away"]].sort_values(by="Date", ascending=False)

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
# ultimos_casa = pd.DataFrame({
#     "Data": ["2023-12-01", "2023-11-28", "2023-11-15"],
#     "Adversário": ["Porto", "Sporting", "Braga"],
#     "Resultado": ["2-0", "1-1", "0-3"]
# })
# ultimos_visitante = pd.DataFrame({
#     "Data": ["2023-12-02", "2023-11-27", "2023-11-14"],
#     "Adversário": ["Portimonense", "Boavista", "Vitória SC"],
#     "Resultado": ["1-1", "3-2", "0-1"]
# })

filter_ultimos_casa = df_hist["Home"] == df_match_selected["Home"]
ultimos_casa = df_hist.loc[filter_ultimos_casa, ["Date", "Home", "Resultado_FT", "Away"]].tail(10).sort_values(by="Date", ascending=False)

filter_ultimos_visitante = df_hist["Away"] == df_match_selected["Away"]
ultimos_visitante = df_hist.loc[filter_ultimos_visitante, ["Date", "Home", "Resultado_FT", "Away"]].tail(10).sort_values(by="Date", ascending=False)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Últimos 10 Jogos - Casa")
    print_dataframe(ultimos_casa)
with col2:
    st.subheader("Últimos 10 Jogos - Visitante")
    print_dataframe(ultimos_visitante)

st.subheader("⚽ Classificações nesta competição")

# classificacao_geral = pd.DataFrame({
#     "Posição": [1, 2, 3, 4],
#     "Clube": ["Benfica", "Porto", "Sporting", "Braga"],
#     "Pontos": [50, 47, 45, 42],
#     "Jogos": [20, 20, 20, 20],
#     "Vitórias": [16, 15, 14, 13],
#     "Empates": [2, 2, 3, 3],
#     "Derrotas": [2, 3, 3, 4],
# })

# classificacao_casa = pd.DataFrame({
#     "Posição": [1, 2, 3, 4],
#     "Clube": ["Benfica", "Porto", "Braga", "Sporting"],
#     "Pontos em Casa": [30, 28, 26, 24],
#     "Jogos em Casa": [10, 10, 10, 10],
#     "Vitórias em Casa": [10, 9, 8, 8],
#     "Empates em Casa": [0, 1, 2, 0],
#     "Derrotas em Casa": [0, 0, 0, 2],
# })

# classificacao_visitante = pd.DataFrame({
#     "Posição": [1, 2, 3, 4],
#     "Clube": ["Porto", "Benfica", "Sporting", "Braga"],
#     "Pontos Fora": [25, 23, 21, 18],
#     "Jogos Fora": [10, 10, 10, 10],
#     "Vitórias Fora": [8, 7, 7, 6],
#     "Empates Fora": [1, 2, 0, 0],
#     "Derrotas Fora": [1, 1, 3, 4],
# })

filter_classificacao = (df_hist["Season"] == "2024/2025") & (df_hist["League"] == df_match_selected["League"])
df_classificacao = df_hist.loc[filter_classificacao, ["League","Season","Date","Rodada","Home","Away","Goals_H_FT","Goals_A_FT"]]

classificacao_geral = generate_classificacao(df_classificacao, "ALL")
classificacao_casa = generate_classificacao(df_classificacao, "HOME")
classificacao_visitante = generate_classificacao(df_classificacao, "AWAY")

tab1, tab2, tab3 = st.tabs(["Geral", "Casa", "Visitante"])
with tab1:
    # st.subheader("Geral")
    print_dataframe(classificacao_geral, 750)
with tab2:
    # st.subheader("Casa")
    print_dataframe(classificacao_casa, 750)
with tab3:
    # st.subheader("Visitante")
    print_dataframe(classificacao_visitante, 750)

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
percurso_casa = {
    "Sequência de Vitórias": 1,
    "Sequência de Empates": 0,
    "Sequência de Derrotas": 3,
    "Não ganha há": 7,
    "Não empata há": 1,
    "Não perde há": 3,
}
percurso_visitante = {
    "Sequência de Vitórias": 2,
    "Sequência de Empates": 1,
    "Sequência de Derrotas": 0,
    "Não ganha há": 1,
    "Não empata há": 2,
    "Não perde há": 5,
}
col1, col2 = st.columns(2)
with col1:
    st.subheader("Percurso - Casa")
    st.json(percurso_casa)
with col2:
    st.subheader("Percurso - Visitante")
    st.json(percurso_visitante)    

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
    st.subheader(df_match_selected["Home"])
    print_dataframe(df_time_1.to_dict(orient='records'))
    print_dataframe(df_time_11.to_dict(orient='records'))
with col2:
    st.subheader(df_match_selected["Away"])
    print_dataframe(df_time_2.to_dict(orient='records'))
    print_dataframe(df_time_22.to_dict(orient='records'))

# Outros dados e análises podem ser adicionados conforme necessário
st.write("⚡ Dashboard dinâmico para análise de confrontos! ⚡")