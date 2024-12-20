import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Análise de Confrontos de Futebol",
    page_icon="⚽",
    layout="wide",
)

# Título do dashboard
st.title("⚽ Análise Completa do Confronto de Futebol")

# Entrada para seleção do confronto
st.sidebar.header("Selecione o Confronto")
club1 = st.sidebar.selectbox("Clube 1", ["Nacional", "Benfica", "Porto"])
club2 = st.sidebar.selectbox("Clube 2", ["Nacional", "Benfica", "Porto"])
match_date = st.sidebar.date_input("Data do Jogo")
league = st.sidebar.selectbox("Campeonato", ["Primeira Liga", "Copa de Portugal"])
round_number = st.sidebar.number_input("Rodada", min_value=1, step=1)

# Exibição do confronto
st.subheader(f"Confronto: {club1} x {club2}")
st.write(f"Data: {match_date} | Campeonato: {league} | Rodada: {round_number}")

# Simulação de dados das tabelas (substitua por dados reais)
# Tabela 4: Confronto nos últimos 3 anos
confrontos = pd.DataFrame({
    "Data": ["2023-01-01", "2022-03-15", "2021-07-20"],
    "Clube 1": ["Nacional", "Nacional", "Benfica"],
    "Clube 2": ["Benfica", "Benfica", "Nacional"],
    "Resultado": ["1-2", "0-3", "2-1"]
})
st.subheader("Confronto nos últimos 3 anos")
st.table(confrontos)

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
    st.table(ultimos_casa)
with col2:
    st.subheader("Últimos 10 Jogos - Visitante")
    st.table(ultimos_visitante)

# Tabela 10, 12 e 14: Classificação
classificacao_geral = pd.DataFrame({
    "Posição": [1, 2, 3],
    "Clube": ["Benfica", "Porto", "Sporting"],
    "Pontos": [50, 47, 45]
})
st.subheader("Classificação Geral")
st.table(classificacao_geral)

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

# Outros dados e análises podem ser adicionados conforme necessário
st.write("⚡ Dashboard dinâmico para análise de confrontos! ⚡")
