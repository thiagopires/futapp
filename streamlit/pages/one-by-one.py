import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta

SEASON_ATUAL = '2024/2025'



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

def print_dataframe(df, pheight=None):
    if isinstance(df, pd.io.formats.style.Styler):
        df = df.set_properties(**{'text-align': 'center'})
        df = df.set_table_styles([
            {'selector': 'th', 'props': [('text-align', 'center')]}
        ])
    st.dataframe(df, height=pheight, use_container_width=True, hide_index=True)

def load_daymatches():
    i = st.session_state.button
    dia = (datetime.now()- timedelta(hours=3) + timedelta(days=i)).strftime("%Y-%m-%d")
    print(dia)
    df = pd.read_csv(f"https://github.com/futpythontrader/YouTube/blob/main/Jogos_do_Dia/FootyStats/Jogos_do_Dia_FootyStats_{dia}.csv?raw=true")
    df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
    df["Formatted_Datetime"] = df["Datetime"].dt.strftime("%d/%m/%Y %H:%M")
    return df

def load_histmatches():
    df = pd.read_csv("https://github.com/futpythontrader/YouTube/blob/main/Bases_de_Dados/FootyStats/Base_de_Dados_FootyStats_(2022_2024).csv?raw=true")
    df[["Date", "Time"]] = df["Date"].str.split(" ", expand=True)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Formatted_Date"] = df["Date"].dt.strftime("%d/%m/%Y")
    df["Resultado_FT"] = df["Goals_H_FT"].astype(str) + "-" + df["Goals_A_FT"].astype(str)
    df["Primeiro_Gol"] = df.apply(first_goal_string, axis=1)
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
    clubes["DIFF"] = clubes["DIFF"].apply(lambda x: f"+{x}" if x > 0 else str(x))

    classificacao = clubes.reset_index()
    classificacao = classificacao[["#", "Clube", "PTS", "P", "W", "D", "L", "DIFF", "Goals"]]

    if type == 'HOME':
        classificacao = classificacao.style.apply(highlight_row, axis=1, highlight=[df_match_selected["Home"]])
        # classificacao = classificacao.style.map(lambda v: 'background-color: lightyellow' if v == df_match_selected["Home"] else '', subset=["Clube"])
    elif type == 'AWAY':
        classificacao = classificacao.style.apply(highlight_row, axis=1, highlight=[df_match_selected["Away"]])
        # classificacao = classificacao.style.map(lambda v: 'background-color: lightyellow' if v == df_match_selected["Away"] else '', subset=["Clube"])
    elif type == 'ALL':
        classificacao = classificacao.style.apply(highlight_row, axis=1, highlight=[df_match_selected["Home"],df_match_selected["Away"]])
        # classificacao = classificacao.style.map(lambda v: 'background-color: lightyellow' if (v == df_match_selected["Home"] or v == df_match_selected["Away"]) else '', subset=["Clube"])

    return classificacao

    # Configuração da página
    st.set_page_config(
        page_title="Análise de Confrontos de Futebol",
        page_icon="⚽",
        layout="wide",
    )

def highlight_result(row, highlight):
    colors = {
        'HOME': ['lightgreen','lightyellow','lightcoral'],
        'AWAY': ['lightcoral','lightyellow','lightgreen']
    }

    colors = colors['HOME'] if row['Home'] == highlight else colors['AWAY']

    Goals = row["Resultado_FT"].split("-")
    Goals_H_FT = Goals[0]
    Goals_A_FT = Goals[1]

    if Goals_H_FT > Goals_A_FT:
        return [f"background-color: {colors[0]}" if col == "Resultado_FT" else "" for col in row.index]
    elif Goals_H_FT == Goals_A_FT:
        return [f"background-color: {colors[1]}" if col == "Resultado_FT" else "" for col in row.index]
    elif Goals_H_FT < Goals_A_FT:
        return [f"background-color: {colors[2]}" if col == "Resultado_FT" else "" for col in row.index]

def highlight_row(row, highlight):
    if row["Clube"] in highlight:
        return ['background-color: #FFE0A6'] * len(row)
    return [''] * len(row)


import ast

def calcular_gols_por_tempo(df, team_name):
    ranges = {
        "0-15": range(0, 16),
        "16-30": range(16, 31),
        "31-45": range(31, 46),
        "46-60": range(46, 61),
        "61-75": range(61, 76),
        "76-90": range(76, 91),
    }

    gols_marcados = {r: 0 for r in ranges.keys()}
    gols_sofridos = {r: 0 for r in ranges.keys()}

    # Filtrar apenas jogos do time (Home ou Away)
    jogos_time = df[(df['Home'] == team_name) | (df['Away'] == team_name)]

    for _, row in jogos_time.iterrows():
        home_team = row['Home']
        away_team = row['Away']

        # Função para ajustar minutos com '+' (exemplo: '45+3' -> 45)
        def ajustar_minuto(minuto):
            if '+' in minuto:
                return int(minuto.split('+')[0])
            return int(minuto)

        # Processando gols do time da casa
        if team_name == home_team:
            home_minutes = [ajustar_minuto(m) for m in ast.literal_eval(row['Goals_H_Minutes'])]
            away_minutes = [ajustar_minuto(m) for m in ast.literal_eval(row['Goals_A_Minutes'])]

            for minuto in home_minutes:
                for intervalo, range_values in ranges.items():
                    if minuto in range_values:
                        gols_marcados[intervalo] += 1
            
            for minuto in away_minutes:
                for intervalo, range_values in ranges.items():
                    if minuto in range_values:
                        gols_sofridos[intervalo] += 1

        # Processando gols do time visitante
        elif team_name == away_team:
            away_minutes = [ajustar_minuto(m) for m in ast.literal_eval(row['Goals_A_Minutes'])]
            home_minutes = [ajustar_minuto(m) for m in ast.literal_eval(row['Goals_H_Minutes'])]

            for minuto in away_minutes:
                for intervalo, range_values in ranges.items():
                    if minuto in range_values:
                        gols_marcados[intervalo] += 1
            
            for minuto in home_minutes:
                for intervalo, range_values in ranges.items():
                    if minuto in range_values:
                        gols_sofridos[intervalo] += 1

    df_gols = pd.DataFrame({
        "Intervalo": gols_marcados.keys(),
        "Gols Marcados": gols_marcados.values(),
        "Gols Sofridos": gols_sofridos.values()
    })

    return df_gols





# Init 
st.set_page_config(layout="wide")

if 'button' not in st.session_state:
    st.session_state.button = 0

# Sidebar
st.sidebar.header("Selecione o Confronto")

left, middle, right = st.sidebar.columns(3)
if left.button("Hoje", use_container_width=True):
    st.session_state.button = 0
if middle.button("Amanhã", use_container_width=True):
    st.session_state.button = 1
if right.button("D.Amanhã", use_container_width=True):
    st.session_state.button = 2

df_matches = load_daymatches()
df_hist = load_histmatches()

df_matches["Confronto"] = df_matches["Time"] + " - " + df_matches["Home"] + " vs. " + df_matches["Away"]
matches = df_matches["Confronto"].value_counts().index
match_selected = st.sidebar.selectbox("Confronto", matches)

df_match_selected = df_matches[df_matches["Confronto"].str.contains(match_selected, na=False)].iloc[0]

# Título do dashboard
st.title("⚽ Análise Completa do Confronto de Futebol")

# Header
st.header(f'{df_match_selected["Confronto"].split("-")[1]}')
st.subheader(f"{df_match_selected['Formatted_Datetime']} - {df_match_selected["League"]} (Rodada {df_match_selected["Rodada"]})")
st.divider()

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
with col2:
    st.subheader("Confrontos diretos nos últimos 3 anos")
    filter_confrontos = (df_hist["Home"].isin([df_match_selected["Home"], df_match_selected["Away"]])) & (df_hist["Away"].isin([df_match_selected["Home"], df_match_selected["Away"]]))
    confrontos = df_hist.loc[filter_confrontos, ["Date", "Season", "Home", "Resultado_FT", "Away"]].sort_values(by="Date", ascending=False)
    df_confrontos = confrontos.style.apply(highlight_result, axis=1, highlight=df_match_selected["Home"])
    print_dataframe(df_confrontos)

filter_ultimos_casa = (df_match_selected["Home"] == df_hist["Home"]) | (df_match_selected["Home"] == df_hist["Away"])
ultimos_casa = df_hist.loc[filter_ultimos_casa, ["Date", "Season", "Home", "Resultado_FT", "Away"]].sort_values(by="Date", ascending=False).head(10)
df_ultimos_casa = ultimos_casa.style.apply(highlight_result, axis=1, highlight=df_match_selected["Home"])

filter_ultimos_visitante = (df_match_selected["Away"] == df_hist["Home"]) | (df_match_selected["Away"] == df_hist["Away"])
ultimos_visitante = df_hist.loc[filter_ultimos_visitante, ["Date", "Season", "Home", "Resultado_FT", "Away"]].sort_values(by="Date", ascending=False).head(10)
df_ultimos_visitante = ultimos_visitante.style.apply(highlight_result, axis=1, highlight=df_match_selected["Away"])

st.header(f"Últimos 10 Jogos na {df_match_selected['League']}")

col1, col2 = st.columns(2)
with col1:
    st.subheader(df_match_selected["Home"])
    print_dataframe(df_ultimos_casa)
with col2:
    st.subheader(df_match_selected["Away"])
    print_dataframe(df_ultimos_visitante)

st.subheader("⚽ Classificações nesta competição")

filter_classificacao = (df_hist["Season"] == SEASON_ATUAL) & (df_hist["League"] == df_match_selected["League"])
df_classificacao = df_hist.loc[filter_classificacao, ["League","Season","Date","Rodada","Home","Away","Goals_H_FT","Goals_A_FT"]]

classificacao_geral = generate_classificacao(df_classificacao, "ALL")
classificacao_casa = generate_classificacao(df_classificacao, "HOME")
classificacao_visitante = generate_classificacao(df_classificacao, "AWAY")

tab1, tab2, tab3 = st.tabs(["Geral", "Casa", "Visitante"])
with tab1:
    # st.subheader("Geral")
    print_dataframe(classificacao_geral, 740)
with tab2:
    # st.subheader("Casa")
    print_dataframe(classificacao_casa, 740)
with tab3:
    # st.subheader("Visitante")
    print_dataframe(classificacao_visitante, 740)

filter_todos_casa = (df_hist["Home"] == df_match_selected["Home"]) & (df_hist["League"] == df_match_selected["League"])
todos_casa = df_hist.loc[filter_todos_casa, ["Date", "Home", "Resultado_FT", "Away", "Primeiro_Gol"]].sort_values(by="Date", ascending=False)
df_todos_casa = todos_casa.style.apply(highlight_result, axis=1, highlight=df_match_selected["Home"])

filter_todos_visitante = (df_hist["Away"] == df_match_selected["Away"]) & (df_hist["League"] == df_match_selected["League"])
todos_visitante = df_hist.loc[filter_todos_visitante, ["Date", "Home", "Resultado_FT", "Away", "Primeiro_Gol"]].sort_values(by="Date", ascending=False)
df_todos_visitante = todos_visitante.style.apply(highlight_result, axis=1, highlight=df_match_selected["Away"])

st.header("Todos os jogos Casa/Fora nesta competição")
st.caption(f'{df_match_selected["League"]} - {SEASON_ATUAL} - Época Normal')

col1, col2 = st.columns(2)
with col1:
    st.subheader(df_match_selected["Home"])
    print_dataframe(df_todos_casa)
with col2:
    st.subheader(df_match_selected["Away"])
    print_dataframe(df_todos_visitante)



# Tabela 25 e 26: Gols Casa e Visitante

# df_gols = gols_por_minuto(df_hist, df_match_selected["Home"], df_match_selected["Away"])
st.subheader("Distribuição de Gols por Minuto")


home_gols_por_tempo = calcular_gols_por_tempo(df_hist.loc[(df_hist["Season"] == SEASON_ATUAL)], df_match_selected["Home"])
away_gols_por_tempo = calcular_gols_por_tempo(df_hist.loc[(df_hist["Season"] == SEASON_ATUAL)], df_match_selected["Away"])

col1, col2 = st.columns(2)
with col1:
    # print_dataframe(home_gols_por_tempo)
    fig = px.bar(home_gols_por_tempo, 
                 x=['Gols Marcados','Gols Sofridos'],
                 y='Intervalo',
                 orientation="h",
                 barmode='group',
                 text_auto=True,
                 title=f"Distribuição dos Gols por Intervalo de Tempo - {df_match_selected['Home']}"
    )
    st.plotly_chart(fig, use_container_width=True, key="fig1")
with col2:
    # print_dataframe(away_gols_por_tempo)
    fig = px.bar(away_gols_por_tempo, 
                 x=['Gols Marcados','Gols Sofridos'],
                 y='Intervalo',
                 orientation="h",
                 barmode='group',
                 text_auto=True,
                 title=f"Distribuição dos Gols por Intervalo de Tempo - {df_match_selected['Away']}"
    )
    st.plotly_chart(fig, use_container_width=True, key="fig2")

# col1, col2 = st.columns(2)
# with col1:
#     st.plotly_chart(gols_por_minuto(df_hist, df_match_selected["Home"]), use_container_width=True, key="fig1")
# with col2:
#     st.plotly_chart(gols_por_minuto(df_hist, df_match_selected["Away"]), use_container_width=True, key="fig2")



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


