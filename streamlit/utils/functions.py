import streamlit as st
import pandas as pd
import ast
import telebot
import requests
import time
import urllib
from datetime import datetime, timedelta

import streamlit as st

def send_alert(message):

    bot_id = st.secrets['TELEGRAM_BOT_ID']
    chat_id = st.secrets['TELEGRAM_CHAT_ID']

    try:
        bot = telebot.TeleBot(bot_id)
        response = bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
        return response
    except requests.exceptions.ConnectionError:
        print("Connection error with Telegram. Retrying after 5 seconds...")
        time.sleep(5)
        send_alert(message)

def validate_login(email):
    for key, value in st.secrets["valid_emails"].items():
        if email == value:
            return True
        
    return False

def display_sidebar(value):
    streamlit_style = """
        <style>
        .stSidebar {display: """ + value + """};}
        </style>
    """
    st.markdown(streamlit_style, unsafe_allow_html=True)

def submit_login():
    st.session_state["submit_login"] = True

def login_page():
    
    display_sidebar('none')
    st.session_state["submit_login"] = False

    st.title("Bem vindo ao Futapp.")
    st.header("Login")
    email = st.text_input(
        "Digite seu e-mail cadastrado para acessar", 
        placeholder="email@example.com",
        on_change=submit_login)
    if st.button("Entrar") or st.session_state["submit_login"] == True:
        if st.session_state["logged_in"] == True:
            display_sidebar('block')
        if validate_login(email):
            st.session_state["logged_in"] = True
            st.success(f"Acesso autorizado para {email}! Clique em 'Entrar' novamente!")
            send_alert(f"[{st.secrets['ENV']}] Acesso autorizado para {email}")
        else:
            st.error("Usuário inválido!")

def get_current_season():
    SEASON = '2024/2025'
    return SEASON

def get_last_season():
    SEASON = '2023/2024'
    return SEASON

def get_today(offset=0):
    now = datetime.now()
    adjusted_time = now + timedelta(days=offset) - timedelta(hours=3)
    return adjusted_time.date()

def print_dataframe(df, styled_df=None):
    if not styled_df:
        st.dataframe(df, use_container_width=True, hide_index=True)
    elif isinstance(styled_df, pd.io.formats.style.Styler):
        styled_df = styled_df.set_properties(**{'text-align': 'center'})
        styled_df = styled_df.set_table_styles([
            {'selector': 'th', 'props': [('text-align', 'center')]}
        ])
        st.dataframe(styled_df, height=len(df)*38, use_container_width=True, hide_index=True)       

def load_daymatches(dt, filter_teams=None):

    try:
        df = pd.read_csv(f"https://github.com/futpythontrader/YouTube/blob/main/Jogos_do_Dia/FootyStats/Jogos_do_Dia_FootyStats_{dt}.csv?raw=true")
    
        df['League'] = df['League'].str.replace(' ', ' - ', 1).str.upper()
        df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
        df["Formatted_Datetime"] = df["Datetime"].dt.strftime("%d/%m/%Y %H:%M")
        df["Confronto"] = df["Time"] + " - " + df["Home"] + " vs. " + df["Away"]

        df['Probabilidade_H_FT'] = round((1 / df['Odd_H_FT']),2)
        df['Probabilidade_D_FT'] = round((1 / df['Odd_D_FT']),2)
        df['Probabilidade_A_FT'] = round((1 / df['Odd_A_FT']),2)

        df['CV_HDA_FT'] = round((df[['Odd_H_FT','Odd_D_FT','Odd_A_FT']].std(ddof=0, axis=1) / df[['Odd_H_FT','Odd_D_FT','Odd_A_FT']].mean(axis=1)),2)

        df["Diff_XG_Home_Away_Pre"] = df['XG_Home_Pre'] - df['XG_Away_Pre']

        if filter_teams: df = df[(df["Home"].isin(filter_teams)) | (df["Away"].isin(filter_teams))]

        rename_leagues(df)

        return df

        # df_hist = load_histmatches(dt)

        # for idx, row in df.iterrows():
        #     df_hist_cp = df_hist[(df_hist['Season'] == get_current_season()) & (df_hist['League'] == row['League'])].copy()
        #     classificacao_geral = generate_classificacao_2(df_hist_cp, "ALL")

        #     posicao_home = classificacao_geral.loc[
        #         classificacao_geral["Clube"] == row["Home"], "PTS"
        #     ]
        #     if not posicao_home.empty:
        #         df.loc[idx, 'PTS_Tabela_H'] = posicao_home.values[0]
        #     else:
        #         df.loc[idx, 'PTS_Tabela_H'] = None  # Ou um valor padrão, como -1
            
        #     # Verificar posição do time visitante
        #     posicao_away = classificacao_geral.loc[
        #         classificacao_geral["Clube"] == row["Away"], "PTS"
        #     ]
        #     if not posicao_away.empty:
        #         df.loc[idx, 'PTS_Tabela_A'] = posicao_away.values[0]
        #     else:
        #         df.loc[idx, 'PTS_Tabela_A'] = None

    except urllib.error.HTTPError as e:
        return pd.DataFrame()  # Retorna um DataFrame vazio para evitar erro na aplicação

@st.cache_data
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
            return pd.Series([f"{first[0]}' {first[1]}",first[0],first[1]])  # Formatar como "minuto' origem"
        else:
            return pd.Series(['-',None,"-"])  # Caso não haja gols
    
    def calcular_resultado_minuto(row, minute):
        # Processar os minutos para casa e visitante
        gols_home = [int(minuto.split('+')[0]) for minuto in eval(row['Goals_H_Minutes']) if int(minuto.split('+')[0]) <= minute]
        gols_away = [int(minuto.split('+')[0]) for minuto in eval(row['Goals_A_Minutes']) if int(minuto.split('+')[0]) <= minute]

        # Contar os gols marcados até o minuto x
        gols_home = len(gols_home)
        gols_away = len(gols_away)

        return f"{gols_home}-{gols_away}"

    df = pd.read_csv("https://github.com/futpythontrader/YouTube/blob/main/Bases_de_Dados/FootyStats/Base_de_Dados_FootyStats_(2022_2025).csv?raw=true")
    
    df['League'] = df['League'].str.replace(' ', ' - ', 1).str.upper()
    
    df[["Date", "Time"]] = df["Date"].str.split(" ", expand=True)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Formatted_Date"] = df["Date"].dt.strftime("%d/%m/%Y")
    df['Month_Year'] = pd.to_datetime(df['Date']).dt.strftime('%m/%Y')
    
    df["Resultado_HT"] = df["Goals_H_HT"].astype(str) + "-" + df["Goals_A_HT"].astype(str)
    df["Resultado_FT"] = df["Goals_H_FT"].astype(str) + "-" + df["Goals_A_FT"].astype(str)
    
    df['Resultado_60'] = df.apply(calcular_resultado_minuto, minute=60, axis=1)
    df['Resultado_70'] = df.apply(calcular_resultado_minuto, minute=70, axis=1)
    df['Resultado_75'] = df.apply(calcular_resultado_minuto, minute=75, axis=1)
    df['Resultado_80'] = df.apply(calcular_resultado_minuto, minute=80, axis=1)

    df['Probabilidade_H_FT'] = round((1 / df['Odd_H_FT']),2)
    df['Probabilidade_D_FT'] = round((1 / df['Odd_D_FT']),2)
    df['Probabilidade_A_FT'] = round((1 / df['Odd_A_FT']),2)

    df['CV_HDA_FT'] = round((df[['Odd_H_FT','Odd_D_FT','Odd_A_FT']].std(ddof=0, axis=1) / df[['Odd_H_FT','Odd_D_FT','Odd_A_FT']].mean(axis=1)),2)
    
    df[["Primeiro_Gol","Primeiro_Gol_Minuto","Primeiro_Gol_Marcador"]] = df.apply(first_goal_string, axis=1)
    
    df["Diff_XG_Home_Away_Pre"] = df['XG_Home_Pre'] - df['XG_Away_Pre']

    rename_leagues(df)

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

def generate_classificacao(df, df_match_selected, type):
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

    clubes = clubes.reset_index()
    classificacao_df = clubes[["#", "Clube", "PTS", "P", "W", "D", "L", "DIFF", "Goals"]]
    styled_df = classificacao_df.copy()

    # if type == 'HOME':
    #     styled_df = styled_df.style.apply(highlight_row, axis=1, highlight=[df_match_selected["Home"]])        
    # elif type == 'AWAY':
    #     styled_df = styled_df.style.apply(highlight_row, axis=1, highlight=[df_match_selected["Away"]])
    # elif type == 'ALL':
    #     styled_df = styled_df.style.apply(highlight_row, axis=1, highlight=[df_match_selected["Home"],df_match_selected["Away"]])

    styled_df = styled_df.style.apply(highlight_row, axis=1, highlight=[df_match_selected["Home"],df_match_selected["Away"]])

    return classificacao_df, styled_df

def generate_classificacao_2(df, type):
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

    clubes = clubes.reset_index()
    classificacao_df = clubes[["#", "Clube", "PTS", "P", "W", "D", "L", "DIFF", "Goals"]]

    # if type == 'HOME':
    #     styled_df = styled_df.style.apply(highlight_row, axis=1, highlight=[df_match_selected["Home"]])        
    # elif type == 'AWAY':
    #     styled_df = styled_df.style.apply(highlight_row, axis=1, highlight=[df_match_selected["Away"]])
    # elif type == 'ALL':
    #     styled_df = styled_df.style.apply(highlight_row, axis=1, highlight=[df_match_selected["Home"],df_match_selected["Away"]])

    return classificacao_df

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
        return [f"background-color: {colors[0]}; color: #000" if col == "Resultado_FT" else "" for col in row.index]
    elif Goals_H_FT == Goals_A_FT:
        return [f"background-color: {colors[1]}; color: #000" if col == "Resultado_FT" else "" for col in row.index]
    elif Goals_H_FT < Goals_A_FT:
        return [f"background-color: {colors[2]}; color: #000" if col == "Resultado_FT" else "" for col in row.index]

def highlight_row(row, highlight):
    if row["Clube"] in highlight:
        return ['background-color: #FFE0A6; color: #000'] * len(row)
    return [''] * len(row)

def calcular_gols_por_tempo(df, team_name):
    ranges = {
        "0-15":  range(0, 16),
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

    # Considerar apenas os últimos 10 jogos (ordenados por data)
    jogos_time = jogos_time.sort_values(by='Date', ascending=False).head(10)

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
    }).sort_values(by='Intervalo', ascending=False)

    return df_gols.melt(id_vars='Intervalo', var_name='Tipo de Gol', value_name='Gols')

def calcular_estatisticas(df, team_name):
    # Filtrar jogos do time
    jogos_time = df[(df['Home'] == team_name) | (df['Away'] == team_name)].copy()

    # Considerar apenas os últimos 10 jogos (ordenados por data)
    jogos_time = jogos_time.sort_values(by='Date', ascending=False).head(10)
    
    # Adicionar colunas auxiliares
    jogos_time['Gols_Marcados'] = jogos_time.apply(
        lambda row: row['Goals_H_FT'] if row['Home'] == team_name else row['Goals_A_FT'], axis=1)
    jogos_time['Gols_Sofridos'] = jogos_time.apply(
        lambda row: row['Goals_A_FT'] if row['Home'] == team_name else row['Goals_H_FT'], axis=1)
    jogos_time['Total_Gols'] = jogos_time['Gols_Marcados'] + jogos_time['Gols_Sofridos']
    jogos_time['Sem_Sofrer_Gols'] = jogos_time['Gols_Sofridos'] == 0
    jogos_time['Sem_Marcar_Gols'] = jogos_time['Gols_Marcados'] == 0
    jogos_time['Mais_de_2_5'] = jogos_time['Total_Gols'] > 2.5
    jogos_time['Menos_de_2_5'] = jogos_time['Total_Gols'] <= 2.5

    # Separar jogos em casa e fora
    jogos_casa = jogos_time[jogos_time['Home'] == team_name]
    jogos_fora = jogos_time[jogos_time['Away'] == team_name]

    # Função auxiliar para calcular métricas
    def calcular_metricas(jogos):
        total_jogos = len(jogos)
        if total_jogos == 0:
            return [0, 0, 0, "0%", "0%", "0%", "0%"]
        
        media_gols_marcados = jogos['Gols_Marcados'].mean()
        media_gols_sofridos = jogos['Gols_Sofridos'].mean()
        media_total_gols = jogos['Total_Gols'].mean()
        sem_sofrer_gols = jogos['Sem_Sofrer_Gols'].mean() * 100
        sem_marcar_gols = jogos['Sem_Marcar_Gols'].mean() * 100
        mais_de_2_5 = jogos['Mais_de_2_5'].mean() * 100
        menos_de_2_5 = jogos['Menos_de_2_5'].mean() * 100

        return [
            round(media_gols_marcados, 2),
            round(media_gols_sofridos, 2),
            round(media_total_gols, 2),
            f"{round(sem_sofrer_gols)}%",
            f"{round(sem_marcar_gols)}%",
            f"{round(mais_de_2_5)}%",
            f"{round(menos_de_2_5)}%"
        ]

    # Calcular métricas
    casa = calcular_metricas(jogos_casa)
    fora = calcular_metricas(jogos_fora)
    global_ = calcular_metricas(jogos_time)

    # Estrutura final
    estatisticas_time = {
        "Categoria": [
            "Média de gols marcados por jogo",
            "Média de gols sofridos por jogo",
            "Média de gols marcados + sofridos",
            "Jogos sem sofrer gols",
            "Jogos sem marcar gols",
            "Jogos com Mais de 2,5 Gols",
            "Jogos com Menos de 2,5 Gols"
        ],
        "Casa": casa,
        "Fora": fora,
        "Global": global_,
    }

    return pd.DataFrame(estatisticas_time)

def calcular_estatisticas_adicionais(df, team_name, side):
    # Filtrar jogos do time
    jogos_time = df[(df['Home'] == team_name) | (df['Away'] == team_name)].copy()

    # Considerar apenas os últimos 10 jogos (ordenados por data)
    jogos_time = jogos_time.sort_values(by='Date', ascending=False).head(10)

    # Adicionar colunas auxiliares
    jogos_time['Abre_Marcador'] = jogos_time.apply(
        lambda row: (row['Home'] == team_name and row['Goals_H_FT'] > 0) or 
                    (row['Away'] == team_name and row['Goals_A_FT'] > 0), axis=1)
    jogos_time['Vence_Intervalo'] = jogos_time.apply(
        lambda row: (row['Home'] == team_name and row['Goals_H_HT'] > row['Goals_A_HT']) or 
                    (row['Away'] == team_name and row['Goals_A_HT'] > row['Goals_H_HT']), axis=1)
    jogos_time['Vence_Final'] = jogos_time.apply(
        lambda row: (row['Home'] == team_name and row['Goals_H_FT'] > row['Goals_A_FT']) or 
                    (row['Away'] == team_name and row['Goals_A_FT'] > row['Goals_H_FT']), axis=1)
    jogos_time['Reviravolta'] = jogos_time.apply(
        lambda row: ((row['Home'] == team_name and row['Goals_A_HT'] > row['Goals_H_HT'] and row['Goals_H_FT'] > row['Goals_A_FT']) or
                     (row['Away'] == team_name and row['Goals_H_HT'] > row['Goals_A_HT'] and row['Goals_A_FT'] > row['Goals_H_FT'])), axis=1)

    # Separar jogos em casa
    jogos_side = jogos_time[jogos_time[side] == team_name]

    # Função auxiliar para calcular as estatísticas adicionais
    def calcular_adicionais(jogos, total_jogos):
        if total_jogos == 0:
            return ["0 em 0 (0%)"] * 4

        abre_marcador = jogos['Abre_Marcador'].sum()
        vence_intervalo = jogos['Vence_Intervalo'].sum()
        vence_final = jogos['Vence_Final'].sum()
        reviravoltas = jogos['Reviravolta'].sum()

        return [
            f"{abre_marcador} em {total_jogos} ({round((abre_marcador / total_jogos) * 100)}%)",
            f"{vence_intervalo} em {total_jogos} ({round((vence_intervalo / total_jogos) * 100)}%)",
            f"{vence_final} em {total_jogos} ({round((vence_final / total_jogos) * 100)}%)",
            f"{reviravoltas} em {total_jogos} ({round((reviravoltas / total_jogos) * 100)}%)"
        ]

    # Calcular estatísticas    
    global_ = calcular_adicionais(jogos_time, len(jogos_time))
    side_data = calcular_adicionais(jogos_side, len(jogos_side))
    side_label = side.replace("Home","Casa").replace("Away","Fora")

    # Estrutura final
    estatisticas_adicionais_time = {
        "Categoria": [
            "Abre marcador (qualquer altura)",
            "Está a vencer ao intervalo",
            "Vence no final",
            "Reviravoltas"
        ],
        side_label: side_data,
        "Global": global_,
    }

    return pd.DataFrame(estatisticas_adicionais_time)

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
        st.info("Sem jogos.")

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
        st.info("Sem jogos.")

def aba_ult10(df_hist, team, side):
    df = df_hist.loc[
        (team == df_hist[side]), 
        ['Date','Season','Home','Away','Goals_H_HT','Goals_A_HT','Goals_H_FT','Goals_A_FT','Odd_H_FT','Odd_D_FT','Odd_A_FT','Odd_Over25_FT','Odd_BTTS_Yes']
    ].sort_values(by="Date", ascending=False).head(10)
    
    if len(df) > 0:
        print_dataframe(df)
    else:
        st.info("Sem jogos.")

def aba_ponto_de_saida_punter(df_hist, team, side, score):

    df = df_hist.loc[
        (df_hist[side] == team) & 
        ((df_hist['Season'] == get_current_season()) | (df_hist['Season'] == get_last_season()))
    ]
    jogos_analisados = len(df)

    if score == 'Goleada_H':
        filter = ((df_hist['Goals_H_FT'] >= 4) & (df_hist['Goals_H_FT'] > df_hist['Goals_A_FT']))
    elif score == 'Goleada_A':
        filter = ((df_hist['Goals_A_FT'] >= 4) & (df_hist['Goals_A_FT'] > df_hist['Goals_H_FT']))
    else:
        filter = (score.replace("x","-") == df_hist['Resultado_FT'])

    df = df.loc[
        filter, 
        ['Date','Season','Home','Away','Goals_H_HT','Goals_A_HT','Goals_H_FT','Goals_A_FT','Odd_H_FT','Odd_D_FT','Odd_A_FT','Odd_Over25_FT','Odd_BTTS_Yes']
    ].sort_values(by="Date", ascending=False)
    
    if len(df) > 0:
        print_dataframe(df)
    else:
        st.write(f"Não houve jogos anteriores do {team} terminados em {score}")

    st.write("Ponto de Saída: ")
    st.write(f"Jogos Analisados: {jogos_analisados}")

def aba_ponto_de_saida_trader(df_hist, team, side, score):

    df = df_hist.loc[
        (df_hist[side] == team) & 
        ((df_hist['Season'] == get_current_season()) | (df_hist['Season'] == get_last_season()))
    ]
    jogos_analisados = len(df)

    if score == 'Goleada_H':
        filter = ((df_hist['Goals_H_FT'] >= 4) & (df_hist['Goals_H_FT'] > df_hist['Goals_A_FT']))
    elif score == 'Goleada_A':
        filter = ((df_hist['Goals_A_FT'] >= 4) & (df_hist['Goals_A_FT'] > df_hist['Goals_H_FT']))
    else:
        filter = (score.replace("x","-") == df_hist['Resultado_75'])

    df = df.loc[
        filter, 
        ['Date','Season','Home','Away','Goals_H_HT','Goals_A_HT','Goals_H_FT','Goals_A_FT','Odd_H_FT','Odd_D_FT','Odd_A_FT','Odd_Over25_FT','Odd_BTTS_Yes']
    ].sort_values(by="Date", ascending=False)
    
    if len(df) > 0:
        print_dataframe(df)
    else:
        st.write(f"Não houve jogos anteriores do {team} que estavam em {score} no minuto 75")

    st.write("Ponto de Saída: ")
    st.write(f"Jogos Analisados: {jogos_analisados}")

def aba_ponto_de_revisao_ht(df_hist, team, side, score):

    df = df_hist.loc[
        (df_hist[side] == team) & 
        ((df_hist['Season'] == get_current_season()) | (df_hist['Season'] == get_last_season()))
    ]
    jogos_analisados = len(df)

    if score == 'Goleada_H':
        filter = ((df_hist['Goals_H_FT'] >= 4) & (df_hist['Goals_H_FT'] > df_hist['Goals_A_FT']))
    elif score == 'Goleada_A':
        filter = ((df_hist['Goals_A_FT'] >= 4) & (df_hist['Goals_A_FT'] > df_hist['Goals_H_FT']))
    else:
        filter = (score.replace("x","-") == df_hist['Resultado_HT'])

    df = df.loc[
        filter, 
        ['Date','Season','Home','Away','Goals_H_HT','Goals_A_HT','Goals_H_FT','Goals_A_FT','Odd_H_FT','Odd_D_FT','Odd_A_FT','Odd_Over25_FT','Odd_BTTS_Yes']
    ].sort_values(by="Date", ascending=False)
    
    if len(df) > 0:
        print_dataframe(df)
    else:
        st.write(f"Não houve jogos anteriores do {team} no intervalo em {score}")

    st.write("Ponto de Saída: ")
    st.write(f"Jogos Analisados: {jogos_analisados}")

def aba_confrontodireto(df_hist, home, away):
    filter = (df_hist["Home"].isin([home, away])) & (df_hist["Away"].isin([home, away]))
    df = df_hist.loc[
        filter, 
        ['Date','Season','Home','Away','Goals_H_HT','Goals_A_HT','Goals_H_FT','Goals_A_FT','Odd_H_FT','Odd_D_FT','Odd_A_FT','Odd_Over25_FT','Odd_BTTS_Yes']
    ].sort_values(by="Date", ascending=False)
    
    if len(df) > 0:
        print_dataframe(df)
    else:
        st.info("Sem jogos.")

def aba_back_home(df_hist, team, side):
    dict = {}
    df = df_hist.loc[
        (df_hist[side] == team) & 
        ((df_hist['Season'] == get_current_season()) | (df_hist['Season'] == get_last_season()))
    ]
    dict['Jogos analisados'] = len(df)

    filter = (df['Goals_H_FT'] > df['Goals_A_FT'])

    df['Profit_Back_Home'] = -1    
    df.loc[filter, 'Profit_Back_Home'] = round(df['Odd_H_FT']-1, 2)

    dict['Profit Acumulado'] = f"{str(round(df['Profit_Back_Home'].sum(), 2))} unidades"

    df = df.loc[filter]
    dict[f'Jogos vencidos pelo {team}'] = len(df)

    dict['Winrate'] = f"{round((dict[f'Jogos vencidos pelo {team}'] / dict['Jogos analisados']) * 100, 2)}%" if dict['Jogos analisados'] > 0 else "0.0%"

    if len(df) > 0:
        st.write(f"Jogos analisados: {dict['Jogos analisados']} — Jogos vencidos pelo {team}: {dict[f'Jogos vencidos pelo {team}']} — Winrate: {dict['Winrate']} — Profit Acumulado: {dict['Profit Acumulado']}")
        print_dataframe(df[['League','Season','Date','Home','Away','Odd_H_FT','Odd_D_FT','Odd_A_FT','Goals_H_FT','Goals_A_FT','Profit_Back_Home']])
    else:
        st.info("Sem jogos.")

def aba_back_draw(df_hist, team, side):
    dict = {}
    df = df_hist.loc[
        (df_hist[side] == team) & 
        ((df_hist['Season'] == get_current_season()) | (df_hist['Season'] == get_last_season()))
    ]
    dict['Jogos analisados'] = len(df)

    filter = (df['Goals_H_FT'] == df['Goals_A_FT'])

    df['Profit_Back_Draw'] = -1    
    df.loc[filter, 'Profit_Back_Draw'] = round(df['Odd_D_FT']-1, 2)

    dict['Profit Acumulado'] = f"{str(round(df['Profit_Back_Draw'].sum(), 2))} unidades"

    df = df.loc[filter]
    dict[f'Jogos empatados pelo {team}'] = len(df)

    dict['Winrate'] = f"{round((dict[f'Jogos empatados pelo {team}'] / dict['Jogos analisados']) * 100, 2)}%" if dict['Jogos analisados'] > 0 else "0.0%"

    if len(df) > 0:
        st.write(f"Jogos analisados: {dict['Jogos analisados']} — Jogos empatados pelo {team}: {dict[f'Jogos empatados pelo {team}']} — Winrate: {dict['Winrate']} — Profit Acumulado: {dict['Profit Acumulado']}")
        print_dataframe(df[['League','Season','Date','Home','Away','Odd_H_FT','Odd_D_FT','Odd_A_FT','Goals_H_FT','Goals_A_FT','Profit_Back_Draw']])
    else:
        st.info("Sem jogos.")

def aba_back_away(df_hist, team, side):
    dict = {}
    df = df_hist.loc[
        (df_hist[side] == team) & 
        ((df_hist['Season'] == get_current_season()) | (df_hist['Season'] == get_last_season()))
    ]
    dict['Jogos analisados'] = len(df)

    filter = (df['Goals_H_FT'] < df['Goals_A_FT'])

    df['Profit_Back_Away'] = -1    
    df.loc[filter, 'Profit_Back_Away'] = round(df['Odd_A_FT']-1, 2)

    dict['Profit Acumulado'] = f"{str(round(df['Profit_Back_Away'].sum(), 2))} unidades"

    df = df.loc[filter]
    dict[f'Jogos perdidos pelo {team}'] = len(df)

    dict['Winrate'] = f"{round((dict[f'Jogos perdidos pelo {team}'] / dict['Jogos analisados']) * 100, 2)}%" if dict['Jogos analisados'] > 0 else "0.0%"

    if len(df) > 0:
        st.write(f"Jogos analisados: {dict['Jogos analisados']} — Jogos perdidos pelo {team}: {dict[f'Jogos perdidos pelo {team}']} — Winrate: {dict['Winrate']} — Profit Acumulado: {dict['Profit Acumulado']}")
        print_dataframe(df[['League','Season','Date','Home','Away','Odd_H_FT','Odd_D_FT','Odd_A_FT','Goals_H_FT','Goals_A_FT','Profit_Back_Away']])
    else:
        st.info("Sem jogos.")

def aba_lay_home(df_hist, team, side):
    dict = {}
    df = df_hist.loc[
        (df_hist[side] == team) & 
        ((df_hist['Season'] == get_current_season()) | (df_hist['Season'] == get_last_season()))
    ]
    dict['Jogos analisados'] = len(df)

    filter = (df['Goals_H_FT'] <= df['Goals_A_FT'])

    df['Profit_Back_Home'] = -1    
    df.loc[filter, 'Profit_Back_Home'] = round(df['Odd_DC_X2']-1, 2)

    dict['Profit Acumulado'] = f"{str(round(df['Profit_Back_Home'].sum(), 2))} unidades"

    df = df.loc[filter]
    dict[f'Jogos não vencidos pelo {team}'] = len(df)

    dict['Winrate'] = f"{round((dict[f'Jogos não vencidos pelo {team}'] / dict['Jogos analisados']) * 100, 2)}%" if dict['Jogos analisados'] > 0 else "0.0%"

    if len(df) > 0:
        st.write(f"Jogos analisados: {dict['Jogos analisados']} — Jogos não vencidos pelo {team}: {dict[f'Jogos não vencidos pelo {team}']} — Winrate: {dict['Winrate']} — Profit Acumulado: {dict['Profit Acumulado']}")
        print_dataframe(df[['League','Season','Date','Home','Away','Odd_DC_1X','Odd_DC_12','Odd_DC_X2','Goals_H_FT','Goals_A_FT','Profit_Back_Home']])
    else:
        st.info("Sem jogos.")

def aba_lay_draw(df_hist, team, side):
    dict = {}
    df = df_hist.loc[
        (df_hist[side] == team) & 
        ((df_hist['Season'] == get_current_season()) | (df_hist['Season'] == get_last_season()))
    ]
    dict['Jogos analisados'] = len(df)

    filter = (df['Goals_H_FT'] != df['Goals_A_FT'])

    df['Profit_Back_Draw'] = -1    
    df.loc[filter, 'Profit_Back_Draw'] = round(df['Odd_DC_12']-1, 2)

    dict['Profit Acumulado'] = f"{str(round(df['Profit_Back_Draw'].sum(), 2))} unidades"

    df = df.loc[filter]
    dict[f'Jogos não empatados pelo {team}'] = len(df)

    dict['Winrate'] = f"{round((dict[f'Jogos não empatados pelo {team}'] / dict['Jogos analisados']) * 100, 2)}%" if dict['Jogos analisados'] > 0 else "0.0%"

    if len(df) > 0:
        st.write(f"Jogos analisados: {dict['Jogos analisados']} — Jogos não empatados pelo {team}: {dict[f'Jogos não empatados pelo {team}']} — Winrate: {dict['Winrate']} — Profit Acumulado: {dict['Profit Acumulado']}")
        print_dataframe(df[['League','Season','Date','Home','Away','Odd_DC_1X','Odd_DC_12','Odd_DC_X2','Goals_H_FT','Goals_A_FT','Profit_Back_Draw']])
    else:
        st.info("Sem jogos.")

def aba_lay_away(df_hist, team, side):
    dict = {}
    df = df_hist.loc[
        (df_hist[side] == team) & 
        ((df_hist['Season'] == get_current_season()) | (df_hist['Season'] == get_last_season()))
    ]
    dict['Jogos analisados'] = len(df)

    filter = (df['Goals_H_FT'] >= df['Goals_A_FT'])

    df['Profit_Back_Away'] = -1    
    df.loc[filter, 'Profit_Back_Away'] = round(df['Odd_DC_1X']-1, 2)

    dict['Profit Acumulado'] = f"{str(round(df['Profit_Back_Away'].sum(), 2))} unidades"

    df = df.loc[filter]
    dict[f'Jogos não vencidos pelo Adversário do {team}'] = len(df)

    dict['Winrate'] = f"{round((dict[f'Jogos não vencidos pelo Adversário do {team}'] / dict['Jogos analisados']) * 100, 2)}%" if dict['Jogos analisados'] > 0 else "0.0%"

    if len(df) > 0:
        st.write(f"Jogos analisados: {dict['Jogos analisados']} — Jogos não vencidos pelo Adversário do {team}: {dict[f'Jogos não vencidos pelo Adversário do {team}']} — Winrate: {dict['Winrate']} — Profit Acumulado: {dict['Profit Acumulado']}")
        print_dataframe(df[['League','Season','Date','Home','Away','Odd_DC_1X','Odd_DC_12','Odd_DC_X2','Goals_H_FT','Goals_A_FT','Profit_Back_Away']])
    else:
        st.info("Sem jogos.")

def resultados_singulares(df_hist, team, side):

    df = df_hist.loc[
        (df_hist[side] == team) & 
        ((df_hist['Season'] == get_current_season()) | (df_hist['Season'] == get_last_season()))
    ]

    # Lista de resultados possíveis
    resultados_possiveis = [
        f"{h}x{a}" for h in range(4) for a in range(4)
    ] + ["Goleada_H", "Goleada_A"]

    # Extrair resultados finais
    resultados_ocorridos = []
    for _, row in df.iterrows():
        placar = f"{row['Goals_H_FT']}x{row['Goals_A_FT']}"
        resultados_ocorridos.append(placar)
        
        # Verificar goleadas
        if row['Goals_H_FT'] >= 4 and row['Goals_H_FT'] > row['Goals_A_FT']:
            resultados_ocorridos.append("Goleada_H")
        elif row['Goals_A_FT'] >= 4 and row['Goals_A_FT'] > row['Goals_H_FT']:
            resultados_ocorridos.append("Goleada_A")

    # Identificar resultados ausentes
    resultados_ausentes = set(resultados_possiveis) - set(resultados_ocorridos)

    # Classificar resultados ausentes como singulares
    resultados_singulares = [f"O Placar {r} é SINGULAR" for r in resultados_ausentes]

    for resultado in resultados_singulares:
        st.write(resultado)

def analise_ocorrencia_placar(df_hist, home, away, score):

    df_home = df_hist.loc[
        (df_hist["Home"] == home) & 
        ((df_hist['Season'] == get_current_season()) | (df_hist['Season'] == get_last_season()))
    ]

    df_away = df_hist.loc[
        (df_hist["Away"] == away) & 
        ((df_hist['Season'] == get_current_season()) | (df_hist['Season'] == get_last_season()))
    ]

    df_confronto = df_hist.loc[
        (df_hist["Home"] == home) & (df_hist["Away"] == away) &
        ((df_hist['Season'] == get_current_season()) | (df_hist['Season'] == get_last_season()))
    ]

    if score == 'Goleada_H':
        filter = ((df_hist['Goals_H_FT'] >= 4) & (df_hist['Goals_H_FT'] > df_hist['Goals_A_FT']))
    elif score == 'Goleada_A':
        filter = ((df_hist['Goals_A_FT'] >= 4) & (df_hist['Goals_A_FT'] > df_hist['Goals_H_FT']))
    else:
        filter = (score.replace("x","-") == df_hist['Resultado_FT'])

    # Calcular ocorrências para o Home
    total_jogos_home = len(df_home)
    ocorrencias_home = df_home[filter].shape[0]

    # Calcular ocorrências para o Away
    total_jogos_away = len(df_home)
    ocorrencias_away = df_away[filter].shape[0]

    # Calcular ocorrências totais (confronto)
    total_jogos_confronto = len(df_home)
    ocorrencias_confronto = df_confronto[filter].shape[0]

    # Calcular porcentagens
    porcentagem_home = (ocorrencias_home / total_jogos_home) * 100 if total_jogos_home > 0 else 0
    porcentagem_away = (ocorrencias_away / total_jogos_away) * 100 if total_jogos_away > 0 else 0
    porcentagem_total = (ocorrencias_confronto / total_jogos_confronto) * 100 if total_jogos_confronto > 0 else 0

    # Retornar resultados formatados
    st.write(f"Placar {score} com {porcentagem_home:.2f} % de ocorrência para o Home (Pesquisa desde 2021)\n")
    st.write(f"Placar {score} com {porcentagem_away:.2f} % de ocorrência para o Away (Pesquisa desde 2021)\n")
    st.write(f"Placar {score} com {porcentagem_total:.2f} % de ocorrência para o Confronto (Pesquisa desde 2021)")

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

def rename_leagues(df):

    df.replace('ARGENTINA - 1','ARGENTINA - PRIMERA DIVISIÓN', inplace=True)
    df.replace('AUSTRIA - 2','AUSTRIA - 2. LIGA', inplace=True)
    df.replace('AUSTRIA - 1','AUSTRIA - BUNDESLIGA', inplace=True)
    df.replace('BELGIUM - 1','BELGIUM - PRO LEAGUE', inplace=True)
    df.replace('BRAZIL - 1','BRAZIL - SERIE A', inplace=True)
    df.replace('BRAZIL - 2','BRAZIL - SERIE B', inplace=True)
    df.replace('BULGARIA - 1','BULGARIA - FIRST LEAGUE', inplace=True)
    df.replace('CHILE - 1','CHILE - PRIMERA DIVISIÓN', inplace=True)
    df.replace('CHINA - 1','CHINA - CHINESE SUPER LEAGUE', inplace=True)
    df.replace('CROATIA - 1','CROATIA - PRVA HNL', inplace=True)
    df.replace('CZECH - 1','CZECH - REPUBLIC FIRST LEAGUE', inplace=True)
    df.replace('DENMARK - 1','DENMARK - SUPERLIGA', inplace=True)
    df.replace('EGYPT - 1','EGYPT - EGYPTIAN PREMIER LEAGUE', inplace=True)
    df.replace('ENGLAND - 2','ENGLAND - CHAMPIONSHIP', inplace=True)
    df.replace('ENGLAND - 3','ENGLAND - EFL LEAGUE ONE', inplace=True)
    df.replace('ENGLAND - 4','ENGLAND - EFL LEAGUE TWO', inplace=True)
    df.replace('ENGLAND - 1','ENGLAND - PREMIER LEAGUE', inplace=True)
    df.replace('ESTONIA - 1','ESTONIA - MEISTRILIIGA', inplace=True)
    df.replace('FINLAND - 1','FINLAND - VEIKKAUSLIIGA', inplace=True)
    df.replace('FRANCE - 1','FRANCE - LIGUE 1', inplace=True)
    df.replace('FRANCE - 2','FRANCE - LIGUE 2', inplace=True)
    df.replace('GERMANY - 2','GERMANY - 2. BUNDESLIGA', inplace=True)
    df.replace('GERMANY - 1','GERMANY - BUNDESLIGA', inplace=True)
    df.replace('GREECE - 1','GREECE - SUPER LEAGUE', inplace=True)
    df.replace('ICELAND - 1','ICELAND - ÚRVALSDEILD', inplace=True)
    df.replace('ITALY - 1','ITALY - SERIE A', inplace=True)
    df.replace('ITALY - 2','ITALY - SERIE B', inplace=True)
    df.replace('JAPAN - 1','JAPAN - J1 LEAGUE', inplace=True)
    df.replace('JAPAN - 2','JAPAN - J2 LEAGUE', inplace=True)
    df.replace('NETHERLANDS - 2','NETHERLANDS - EERSTE DIVISIE', inplace=True)
    df.replace('NETHERLANDS - 1','NETHERLANDS - EREDIVISIE', inplace=True)
    df.replace('NORWAY - 1','NORWAY - ELITESERIEN', inplace=True)
    df.replace('NORWAY - 2','NORWAY - FIRST DIVISION', inplace=True)
    df.replace('PARAGUAY - 1','PARAGUAY - DIVISION PROFESIONAL', inplace=True)
    df.replace('POLAND - 1','POLAND - EKSTRAKLASA', inplace=True)
    df.replace('PORTUGAL - 1','PORTUGAL - LIGA NOS', inplace=True)
    df.replace('PORTUGAL - 2','PORTUGAL - LIGAPRO', inplace=True)
    df.replace('REPUBLIC - OF IRELAND 1','REPUBLIC - OF IRELAND PREMIER DIVISION', inplace=True)
    df.replace('ROMANIA - 1','ROMANIA - LIGA I', inplace=True)
    df.replace('SCOTLAND - 1','SCOTLAND - PREMIERSHIP', inplace=True)
    df.replace('SERBIA - 1','SERBIA - SUPERLIGA', inplace=True)
    df.replace('SLOVAKIA - 1','SLOVAKIA - SUPER LIGA', inplace=True)
    df.replace('SLOVENIA - 2','SLOVENIA - PRVALIGA', inplace=True)
    df.replace('SOUTH - KOREA 1','SOUTH - KOREA K LEAGUE 1', inplace=True)
    df.replace('SOUTH - KOREA 2','SOUTH - KOREA K LEAGUE 2', inplace=True)
    df.replace('SPAIN - 1','SPAIN - LA LIGA', inplace=True)
    df.replace('SPAIN - 2','SPAIN - SEGUNDA DIVISIÓN', inplace=True)
    df.replace('SWEDEN - 1','SWEDEN - ALLSVENSKAN', inplace=True)
    df.replace('SWEDEN - 2','SWEDEN - SUPERETTAN', inplace=True)
    df.replace('SWITZERLAND - 2','SWITZERLAND - CHALLENGE LEAGUE', inplace=True)
    df.replace('SWITZERLAND - 1','SWITZERLAND - SUPER LEAGUE', inplace=True)
    df.replace('TURKEY - 1','TURKEY - SÜPER LIG', inplace=True)
    df.replace('URUGUAY - 1','URUGUAY - PRIMERA DIVISIÓN', inplace=True)
    df.replace('USA - 1','USA - MLS', inplace=True)
    df.replace('WALES - 1','WALES - WELSH PREMIER LEAGUE', inplace=True)
