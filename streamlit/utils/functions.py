import streamlit as st
import pandas as pd
import ast
import telebot
import requests
import time
import urllib
import io
from datetime import datetime, timedelta

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

def rename_columns_betfair(df):
    df = df[df["League"].isin(get_betfair_leagues())]
    df = df.rename(columns=lambda col: col.removesuffix('_Back'))
    df = df.rename(columns={
        'Goals_H': 'Goals_H_FT',
        'Goals_A': 'Goals_A_FT',
        'Goals_Min_H': 'Goals_H_Minutes',
        'Goals_Min_A': 'Goals_A_Minutes',
        'Odd_H': 'Odd_H_FT',
        'Odd_A': 'Odd_A_FT',
        'Odd_D': 'Odd_D_FT',
        'Odd_H_Lay': 'Odd_H_FT_Lay',
        'Odd_A_Lay': 'Odd_A_FT_Lay',
        'Odd_D_Lay': 'Odd_D_FT_Lay',
    })

    return df

def load_content_api_github(file_path):
    headers = {"Authorization": f"token {st.secrets["github"]["TOKEN"]}"}
    url = f'https://api.github.com/repos/{st.secrets["github"]["OWNER"]}/{st.secrets["github"]["REPO"]}/contents/{file_path}'
    response = requests.get(url, headers=headers)
    content = requests.get(response.json()['download_url'], headers=headers).content

    return io.BytesIO(content)

def load_daymatches(dt, source):
    try:
        if source == 'Betfair':            
            file = load_content_api_github(f"Jogos_do_Dia/Betfair/Jogos_do_Dia_Betfair_Back_Lay_{dt}.csv")
            df = pd.read_csv(file)
            rename_leagues(df)
            rename_teams(df)
            df = rename_columns_betfair(df)
            # print_dataframe(df)

        elif source == 'FootyStats':
            df = pd.read_csv(f"https://github.com/futpythontrader/YouTube/blob/main/Jogos_do_Dia/FootyStats/Jogos_do_Dia_FootyStats_{dt}.csv?raw=true")
            rename_leagues(df)

        # df['League'] = df['League'].str.replace(' ', ' - ', 1).str.upper()
        df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
        df["Formatted_Datetime"] = df["Datetime"].dt.strftime("%d/%m/%Y %H:%M")
        df["Confronto"] = df["Time"] + " - " + df["Home"] + " vs. " + df["Away"]

        df['Probabilidade_H_FT'] = round((1 / df['Odd_H_FT']),2)
        df['Probabilidade_D_FT'] = round((1 / df['Odd_D_FT']),2)
        df['Probabilidade_A_FT'] = round((1 / df['Odd_A_FT']),2)

        df['CV_HDA_FT'] = round((df[['Odd_H_FT','Odd_D_FT','Odd_A_FT']].std(ddof=0, axis=1) / df[['Odd_H_FT','Odd_D_FT','Odd_A_FT']].mean(axis=1)),2)

        if source == 'Betfair':
            df['Season'] = ''
            df['Rodada'] = 0
            df['XG_Total_Pre'] = 1
            df['XG_Home_Pre'] = 1
            df['XG_Away_Pre'] = 1
            df["Diff_XG_Home_Away_Pre"] = 1
            df["Odd_DC_1X"] = df["Odd_A_FT_Lay"]
            df["Odd_DC_12"] = df["Odd_D_FT_Lay"]
            df["Odd_DC_X2"] = df["Odd_H_FT_Lay"]            
        elif source == 'FootyStats':
            df["Diff_XG_Home_Away_Pre"] = df['XG_Home_Pre'] - df['XG_Away_Pre']

        return df

    except urllib.error.HTTPError as e:
        return pd.DataFrame()  # Retorna um DataFrame vazio para evitar erro na aplicação

@st.cache_data
def betfair_load_histmatches():
    file = load_content_api_github("Bases_de_Dados/Betfair/Base_de_Dados_Betfair_Exchange_Back_Lay.csv")
    df = pd.read_csv(file)
    rename_leagues(df)
    df = rename_columns_betfair(df)
    return df

@st.cache_data
def footystats_load_histmatches():
    file = "https://github.com/futpythontrader/YouTube/blob/main/Bases_de_Dados/FootyStats/Base_de_Dados_FootyStats_(2022_2025).csv?raw=true"
    return pd.read_csv(file)

@st.cache_data
def load_histmatches(source):

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
        # gols_home = [int(minuto.split('+')[0]) for minuto in eval(row['Goals_H_Minutes']) if int(minuto.split('+')[0]) <= minute]
        # gols_away = [int(minuto.split('+')[0]) for minuto in eval(row['Goals_A_Minutes']) if int(minuto.split('+')[0]) <= minute]
        gols_home = [int(str(minuto).split('+')[0]) for minuto in eval(row['Goals_H_Minutes']) if int(str(minuto).split('+')[0]) <= minute]
        gols_away = [int(str(minuto).split('+')[0]) for minuto in eval(row['Goals_A_Minutes']) if int(str(minuto).split('+')[0]) <= minute]

        # Contar os gols marcados até o minuto x
        gols_home = len(gols_home)
        gols_away = len(gols_away)

        return f"{gols_home}-{gols_away}"

    try:
        if source == 'Betfair':            
            df = betfair_load_histmatches()
        elif source == 'FootyStats':
            df = footystats_load_histmatches()
        
        # df['League'] = df['League'].str.replace(' ', ' - ', 1).str.upper()
        rename_leagues(df)
        
        if source == 'FootyStats':
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
        
        if source == 'Betfair':
            df['Season'] = ''
            df['Rodada'] = 0
            df['XG_Total_Pre'] = 1
            df['XG_Home_Pre'] = 1
            df['XG_Away_Pre'] = 1
            df["Diff_XG_Home_Away_Pre"] = 1
            df["Odd_DC_1X"] = df["Odd_A_FT_Lay"]
            df["Odd_DC_12"] = df["Odd_D_FT_Lay"]
            df["Odd_DC_X2"] = df["Odd_H_FT_Lay"]
        elif source == 'FootyStats':
            df["Diff_XG_Home_Away_Pre"] = df['XG_Home_Pre'] - df['XG_Away_Pre']  

        return df
    
    except urllib.error.HTTPError as e:
        return pd.DataFrame()  # Retorna um DataFrame vazio para evitar erro na aplicação

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

    # FootyStats
    df.replace('ARGENTINA 1','ARGENTINA - PRIMERA DIVISIÓN', inplace=True)
    df.replace('AUSTRALIA 1','AUSTRALIA - A-LEAGUE', inplace=True)
    df.replace('AUSTRIA 2','AUSTRIA - 2. LIGA', inplace=True)
    df.replace('AUSTRIA 1','AUSTRIA - BUNDESLIGA', inplace=True)
    df.replace('BELGIUM 1','BELGIUM - PRO LEAGUE', inplace=True)
    df.replace('BRAZIL 1','BRAZIL - SERIE A', inplace=True)
    df.replace('BRAZIL 2','BRAZIL - SERIE B', inplace=True)
    df.replace('BULGARIA 1','BULGARIA - FIRST LEAGUE', inplace=True)
    df.replace('CHILE 1','CHILE - PRIMERA DIVISIÓN', inplace=True)
    df.replace('CHINA 1','CHINA - CHINESE SUPER LEAGUE', inplace=True)
    df.replace('CONFERENCE LEAGUE','EUROPA CONFERENCE LEAGUE', inplace=True)
    df.replace('CROATIA 1','CROATIA - PRVA HNL', inplace=True)
    df.replace('CZECH 1','CZECH - REPUBLIC FIRST LEAGUE', inplace=True)
    df.replace('DENMARK 1','DENMARK - SUPERLIGA', inplace=True)
    df.replace('EGYPT 1','EGYPT - EGYPTIAN PREMIER LEAGUE', inplace=True)
    df.replace('ENGLAND 2','ENGLAND - CHAMPIONSHIP', inplace=True)
    df.replace('ENGLAND 3','ENGLAND - EFL LEAGUE ONE', inplace=True)
    df.replace('ENGLAND 4','ENGLAND - EFL LEAGUE TWO', inplace=True)
    df.replace('ENGLAND 1','ENGLAND - PREMIER LEAGUE', inplace=True)
    df.replace('ESTONIA 1','ESTONIA - MEISTRILIIGA', inplace=True)
    df.replace('FINLAND 1','FINLAND - VEIKKAUSLIIGA', inplace=True)
    df.replace('FRANCE 1','FRANCE - LIGUE 1', inplace=True)
    df.replace('FRANCE 2','FRANCE - LIGUE 2', inplace=True)
    df.replace('GERMANY 2','GERMANY - 2. BUNDESLIGA', inplace=True)
    df.replace('GERMANY 1','GERMANY - BUNDESLIGA', inplace=True)
    df.replace('GREECE 1','GREECE - SUPER LEAGUE', inplace=True)
    df.replace('ICELAND 1','ICELAND - ÚRVALSDEILD', inplace=True)
    df.replace('ITALY 1','ITALY - SERIE A', inplace=True)
    df.replace('ITALY 2','ITALY - SERIE B', inplace=True)
    df.replace('JAPAN 1','JAPAN - J1 LEAGUE', inplace=True)
    df.replace('JAPAN 2','JAPAN - J2 LEAGUE', inplace=True)
    df.replace('MEXICO 1','MEXICO - LIGA MX', inplace=True)
    df.replace('NETHERLANDS 2','NETHERLANDS - EERSTE DIVISIE', inplace=True)
    df.replace('NETHERLANDS 1','NETHERLANDS - EREDIVISIE', inplace=True)
    df.replace('NORWAY 1','NORWAY - ELITESERIEN', inplace=True)
    df.replace('NORWAY 2','NORWAY - FIRST DIVISION', inplace=True)
    df.replace('PARAGUAY 1','PARAGUAY - DIVISION PROFESIONAL', inplace=True)
    df.replace('POLAND 1','POLAND - EKSTRAKLASA', inplace=True)
    df.replace('PORTUGAL 1','PORTUGAL - LIGA NOS', inplace=True)
    df.replace('PORTUGAL 2','PORTUGAL - LIGAPRO', inplace=True)
    df.replace('REPUBLIC OF IRELAND 1','REPUBLIC OF IRELAND - PREMIER DIVISION', inplace=True)
    df.replace('ROMANIA 1','ROMANIA - LIGA I', inplace=True)
    df.replace('SAUDI ARABIA 1','SAUDI ARABIA - SAUDI PROFESSION', inplace=True)
    df.replace('SCOTLAND 1','SCOTLAND - PREMIERSHIP', inplace=True)
    df.replace('SERBIA 1','SERBIA - SUPERLIGA', inplace=True)
    df.replace('SLOVAKIA 1','SLOVAKIA - SUPER LIGA', inplace=True)
    df.replace('SLOVENIA 2','SLOVENIA - PRVALIGA', inplace=True)
    df.replace('SOUTH KOREA 1','SOUTH KOREA - K LEAGUE 1', inplace=True)
    df.replace('SOUTH KOREA 2','SOUTH KOREA - K LEAGUE 2', inplace=True)
    df.replace('SPAIN 1','SPAIN - LA LIGA', inplace=True)
    df.replace('SPAIN 2','SPAIN - SEGUNDA DIVISIÓN', inplace=True)
    df.replace('SWEDEN 1','SWEDEN - ALLSVENSKAN', inplace=True)
    df.replace('SWEDEN 2','SWEDEN - SUPERETTAN', inplace=True)
    df.replace('SWITZERLAND 2','SWITZERLAND - CHALLENGE LEAGUE', inplace=True)
    df.replace('SWITZERLAND 1','SWITZERLAND - SUPER LEAGUE', inplace=True)
    df.replace('TURKEY 1','TURKEY - SÜPER LIG', inplace=True)
    df.replace('URUGUAY 1','URUGUAY - PRIMERA DIVISIÓN', inplace=True)
    df.replace('USA 1','USA - MLS', inplace=True)
    df.replace('WALES 1','WALES - WELSH PREMIER LEAGUE', inplace=True)

    # Betfair
    df.replace('Argentinian Primera Division','ARGENTINA - PRIMERA DIVISIÓN', inplace=True)
    df.replace('Australian A-League Men','AUSTRALIA - A-LEAGUE', inplace=True)
    df.replace('Belgian First Division A','BELGIUM - PRO LEAGUE', inplace=True)
    df.replace('Brazilian Serie A','BRAZIL - SERIE A', inplace=True)
    df.replace('Brazilian Serie B','BRAZIL - SERIE B', inplace=True)
    df.replace('Danish Superliga','DENMARK - SUPERLIGA', inplace=True)
    df.replace('Egyptian Premier','EGYPT - EGYPTIAN PREMIER LEAGUE', inplace=True)
    df.replace('English Championship','ENGLAND - CHAMPIONSHIP', inplace=True)
    df.replace('English League 1','ENGLAND - EFL LEAGUE ONE', inplace=True)
    df.replace('English League 2','ENGLAND - EFL LEAGUE TWO', inplace=True)
    df.replace('English Premier League','ENGLAND - PREMIER LEAGUE', inplace=True)
    df.replace('UEFA Champions League','EUROPA CHAMPIONS LEAGUE', inplace=True)
    df.replace('UEFA Europa Conference League','EUROPA CONFERENCE LEAGUE', inplace=True)
    df.replace('UEFA Europa League','EUROPA LEAGUE', inplace=True)
    df.replace('French Ligue 1','FRANCE - LIGUE 1', inplace=True)
    df.replace('French Ligue 2','FRANCE - LIGUE 2', inplace=True)
    df.replace('German Bundesliga 2','GERMANY - 2. BUNDESLIGA', inplace=True)
    df.replace('German Bundesliga','GERMANY - BUNDESLIGA', inplace=True)
    df.replace('Italian Serie A','ITALY - SERIE A', inplace=True)
    df.replace('Italian Serie B','ITALY - SERIE B', inplace=True)
    df.replace('Japanese J League','JAPAN - J1 LEAGUE', inplace=True)
    df.replace('Mexican Liga MX','MEXICO - LIGA MX', inplace=True)
    df.replace('Dutch Eerste Divisie','NETHERLANDS - EERSTE DIVISIE', inplace=True)
    df.replace('Dutch Eredivisie','NETHERLANDS - EREDIVISIE', inplace=True)
    df.replace('Norwegian Eliteserien','NORWAY - ELITESERIEN', inplace=True)
    df.replace('Portuguese Primeira Liga','PORTUGAL - LIGA NOS', inplace=True)
    df.replace('Romanian Liga I','ROMANIA - LIGA I', inplace=True)
    df.replace('Saudi Professional League','SAUDI ARABIA - SAUDI PROFESSION', inplace=True)
    df.replace('Scottish Premiership','SCOTLAND - PREMIERSHIP', inplace=True)
    df.replace('Spanish La Liga','SPAIN - LA LIGA', inplace=True)
    df.replace('Spanish Segunda Division','SPAIN - SEGUNDA DIVISIÓN', inplace=True)
    df.replace('Turkish Super League','TURKEY - SÜPER LIG', inplace=True)
    df.replace('US Major League Soccer','USA - MLS', inplace=True)


    # df.replace('Spanish Primera Division RFEF Group 1','SPAIN - PRIMERA RFEF', inplace=True)
    # df.replace('Argentinian Copa de la Liga Profesional','ARGENTINA - COPA DE LA LIGA PROFESIONAL', inplace=True)
    # df.replace('Argentinian Primera Division','ARGENTINA - LIGA PROFESIONAL', inplace=True)
    # # df.replace('Argentinian Primera Division','ARGENTINA - TORNEO BETANO', inplace=True)
    # df.replace('Armenian Premier League','ARMENIA - PREMIER LEAGUE', inplace=True)
    # df.replace('Australian A-League Men','AUSTRALIA - A-LEAGUE', inplace=True)
    # df.replace('Austrian Bundesliga', 'AUSTRIA - BUNDESLIGA',inplace=True)
    # df.replace('Austrian Erste Liga','AUSTRIA - 2. LIGA', inplace=True)
    # df.replace('Belgian First Division B','BELGIUM - CHALLENGER PRO LEAGUE', inplace=True)
    # df.replace('Belgian First Division A','BELGIUM - JUPILER PRO LEAGUE', inplace=True)
    # df.replace('Bolivian Liga de Futbol Profesional','BOLIVIA - DIVISION PROFESIONAL', inplace=True)
    # df.replace('Bosnian Premier League','BOSNIA AND HERZEGOVINA - PREMIJER LIGA BIH', inplace=True)
    # df.replace('Brazilian Serie A','BRAZIL - SERIE A', inplace=True)
    # df.replace('Brazilian Serie B','BRAZIL - SERIE B', inplace=True)
    # df.replace('Brazilian Serie C','BRAZIL - SERIE C', inplace=True)
    # df.replace('Brazilian Serie D','BRAZIL - SERIE D', inplace=True)
    # df.replace('BRAZIL - COPA DO BRASIL','BRAZIL - COPA DO BRASIL', inplace=True)
    # df.replace('Bulgarian A League','BULGARIA - PARVA LIGA', inplace=True)
    # df.replace('Chilean Primera Division','CHILE - PRIMERA DIVISION', inplace=True)
    # df.replace('Chinese Super League','CHINA - SUPER LEAGUE', inplace=True)
    # df.replace('Colombian Primera A','COLOMBIA - PRIMERA A', inplace=True)
    # df.replace('Croatian 1 HNL','CROATIA - HNL', inplace=True)
    # df.replace('Croatian 2 HNL','CROATIA - PRVA NL', inplace=True)
    # df.replace('Cypriot 1st Division','CYPRUS - CYTA CHAMPIONSHIP', inplace=True)
    # df.replace('Czech 1 Liga','CZECH REPUBLIC - FORTUNA:LIGA', inplace=True)
    # df.replace('Danish 1st Division','DENMARK - 1ST DIVISION', inplace=True)
    # df.replace('Danish Superliga','DENMARK - SUPERLIGA', inplace=True)
    # df.replace('Ecuadorian Serie A','ECUADOR - LIGA PRO', inplace=True)
    # df.replace('Egyptian Premier','EGYPT - PREMIER LEAGUE', inplace=True)
    # df.replace('English Championship','ENGLAND - CHAMPIONSHIP', inplace=True)
    # df.replace('English League 1','ENGLAND - LEAGUE ONE', inplace=True)
    # df.replace('English League 2','ENGLAND - LEAGUE TWO', inplace=True)
    # df.replace('English National League','ENGLAND - NATIONAL LEAGUE', inplace=True)
    # df.replace('English Premier League','ENGLAND - PREMIER LEAGUE', inplace=True)
    # df.replace('English FA Cup','ENGLAND - FA CUP', inplace=True)
    # df.replace('Estonian Esiliiga','ESTONIA - ESILIIGA', inplace=True)
    # df.replace('Estonian Premier League','ESTONIA - MEISTRILIIGA', inplace=True)
    # df.replace('UEFA Champions League','EUROPA CHAMPIONS LEAGUE', inplace=True)
    # df.replace('UEFA Europa Conference League','EUROPA CONFERENCE LEAGUE', inplace=True)
    # df.replace('UEFA Europa League','EUROPA LEAGUE', inplace=True)
    # df.replace('Finnish Veikkausliiga','FINLAND - VEIKKAUSLIIGA', inplace=True)
    # df.replace('Finnish Ykkonen','FINLAND - YKKONEN', inplace=True)
    # df.replace('French Ligue 1','FRANCE - LIGUE 1', inplace=True)
    # df.replace('French Ligue 2','FRANCE - LIGUE 2', inplace=True)
    # df.replace('French National','FRANCE - NATIONAL', inplace=True)
    # df.replace('German Bundesliga 2','GERMANY - 2. BUNDESLIGA', inplace=True)
    # df.replace('German 3 Liga','GERMANY - 3. LIGA', inplace=True)
    # df.replace('German Bundesliga','GERMANY - BUNDESLIGA', inplace=True)
    # df.replace('Greek Super League','GREECE - SUPER LEAGUE', inplace=True)
    # df.replace('Hungarian NB I','HUNGARY - OTP BANK LIGA', inplace=True)
    # #df.replace('????','ICELAND - BESTA DEILD KARLA', inplace=True)
    # df.replace('Icelandic 1 Deild','ICELAND - LENGJUDEILDIN', inplace=True)
    # df.replace('Irish Division 1','IRELAND - DIVISION 1', inplace=True)
    # df.replace('Irish Premier Division','IRELAND - PREMIER DIVISION', inplace=True)
    # df.replace('Israeli Premier League',"ISRAEL - LIGAT HA'AL", inplace=True)
    # df.replace('Italian Serie A','ITALY - SERIE A', inplace=True)
    # df.replace('Italian Serie B','ITALY - SERIE B', inplace=True)
    # df.replace('Italian Serie C','ITALY - SERIE C', inplace=True)
    # df.replace('Italian Serie D','ITALY - SERIE D', inplace=True)
    # df.replace('Japanese J League','JAPAN - J1 LEAGUE', inplace=True)
    # df.replace('Japanese J League 2','JAPAN - J2 LEAGUE', inplace=True)
    # df.replace('Mexican Liga MX','MEXICO - LIGA MX', inplace=True)
    # df.replace('Dutch Eerste Divisie','NETHERLANDS - EERSTE DIVISIE', inplace=True)
    # df.replace('Dutch Eredivisie','NETHERLANDS - EREDIVISIE', inplace=True)
    # df.replace('Northern Irish Championship','NORTHERN IRELAND - NIFL CHAMPIO', inplace=True)
    # df.replace('Northern Irish Premiership','NORTHERN IRELAND - NIFL PREMIER', inplace=True)
    # df.replace('Norwegian Eliteserien','NORWAY - ELITESERIEN', inplace=True)
    # df.replace('Norwegian 1st Division','NORWAY - OBOS-LIGAEN', inplace=True)
    # df.replace('Paraguayan Division Profesional','PARAGUAY - PRIMERA DIVISION', inplace=True)
    # df.replace('Peruvian Primera Division','PERU - LIGA 1', inplace=True)
    # df.replace('Polish I Liga','POLAND - DIVISION 1', inplace=True)
    # df.replace('Polish Ekstraklasa','POLAND - EKSTRAKLASA', inplace=True)
    # df.replace('Portuguese Primeira Liga','PORTUGAL - LIGA PORTUGAL', inplace=True)
    # df.replace('Portuguese Segunda Liga','PORTUGAL - LIGA PORTUGAL 2', inplace=True)
    # df.replace('Romanian Liga I','ROMANIA - LIGA 1', inplace=True)
    # df.replace('Romanian Liga II','ROMANIA - LIGA 2', inplace=True)
    # df.replace('Saudi Professional League','SAUDI ARABIA - SAUDI PROFESSION', inplace=True)
    # df.replace('Saudi 1st Division','SAUDI ARABIA - 1ST DIVISION', inplace=True)    
    # df.replace('Scottish Championship','SCOTLAND - CHAMPIONSHIP', inplace=True)
    # df.replace('Scottish League One','SCOTLAND - LEAGUE ONE', inplace=True)
    # df.replace('Scottish League Two','SCOTLAND - LEAGUE TWO', inplace=True)
    # df.replace('Scottish Premiership','SCOTLAND - PREMIERSHIP', inplace=True)
    # df.replace('Serbian First League','SERBIA - PRVA LIGA', inplace=True)
    # df.replace('Serbian Super League','SERBIA - SUPER LIGA', inplace=True)
    # df.replace('Slovakian Super League','SLOVAKIA - NIKE LIGA', inplace=True)
    # df.replace('Slovenian Premier League','SLOVENIA - PRVA LIGA', inplace=True)
    # df.replace('South African Premier Division','SOUTH AFRICA - PREMIER LEAGUE', inplace=True)
    # df.replace('CONMEBOL Copa Libertadores','SOUTH AMERICA - COPA LIBERTADOR', inplace=True)
    # df.replace('CONMEBOL Copa Sudamericana','SOUTH AMERICA - COPA SUDAMERICA', inplace=True)
    # df.replace('South Korean K League 1','SOUTH KOREA - K LEAGUE 1', inplace=True)
    # df.replace('South Korean K League 2','SOUTH KOREA - K LEAGUE 2', inplace=True)
    # df.replace('Spanish La Liga','SPAIN - LALIGA', inplace=True)
    # df.replace('Spanish Segunda Division','SPAIN - LALIGA2', inplace=True)
    # df.replace('Spanish Primera Division RFEF A','SPAIN - PRIMERA RFEF', inplace=True)
    # df.replace('Spanish Primera Division RFEF B','SPAIN - PRIMERA RFEF', inplace=True)
    # df.replace('Spanish Primera Division RFEF C','SPAIN - PRIMERA RFEF', inplace=True)
    # df.replace('Spanish Primera Division RFEF D','SPAIN - PRIMERA RFEF', inplace=True)
    # df.replace('Spanish Primera Division RFEF E','SPAIN - PRIMERA RFEF', inplace=True)
    # df.replace('Spanish Primera Division RFEF F','SPAIN - PRIMERA RFEF', inplace=True)
    # df.replace('Spanish Primera Division RFEF G','SPAIN - PRIMERA RFEF', inplace=True)
    # df.replace('Spanish Segunda RFEF - Group 1','SPAIN - SEGUNDA RFEF', inplace=True)
    # df.replace('Spanish Segunda RFEF - Group 2','SPAIN - SEGUNDA RFEF', inplace=True)
    # df.replace('Spanish Segunda RFEF - Group 3','SPAIN - SEGUNDA RFEF', inplace=True)
    # df.replace('Spanish Segunda RFEF - Group 4','SPAIN - SEGUNDA RFEF', inplace=True)
    # df.replace('Spanish Segunda RFEF - Group 5','SPAIN - SEGUNDA RFEF', inplace=True)
    # df.replace('Swedish Allsvenskan','SWEDEN - ALLSVENSKAN', inplace=True)
    # df.replace('Swedish Superettan','SWEDEN - SUPERETTAN', inplace=True)
    # df.replace('Swiss Challenge League','SWITZERLAND - CHALLENGE LEAGUE', inplace=True)
    # df.replace('Swiss Super League','SWITZERLAND - SUPER LEAGUE', inplace=True)
    # df.replace('Todas as Ligas','Todas as Ligas', inplace=True)
    # df.replace('Turkish 1 Lig','TURKEY - 1. LIG', inplace=True)
    # df.replace('Turkish Super League','TURKEY - SUPER LIG', inplace=True)
    # df.replace('Ukrainian Premier League','UKRAINE - PREMIER LEAGUE', inplace=True)
    # df.replace('Uruguayan Primera Division','URUGUAY - PRIMERA DIVISION', inplace=True)
    # df.replace('US Major League Soccer','USA - MLS', inplace=True)
    # df.replace('Venezuelan Primera Division','VENEZUELA - LIGA FUTVE', inplace=True)
    # df.replace('Welsh Premiership','WALES - CYMRU PREMIER', inplace=True)
    # df.replace('Lithuanian A Lyga','LITHUANIA - A LYGA', inplace=True)

def rename_teams(df):

    df.replace("Cerro Porteno","Cerro Porteno", inplace=True)
    df.replace("Melilla UD","Melilla", inplace=True)
    df.replace("Almeria II","Almeria B", inplace=True)
    df.replace("CE Andratx","Andratx", inplace=True)
    df.replace("Juventud Torremolinos","Torremolinos", inplace=True)
    df.replace("Villarreal B","Villarreal B", inplace=True)
    df.replace("Juventus B","Juventus U23", inplace=True)
    df.replace("Cesena","Cesena", inplace=True)
    df.replace("Catanzaro","Catanzaro", inplace=True) 
    df.replace("Boston Utd","Boston Utd", inplace=True)
    df.replace("Barnet","Barnet", inplace=True)
    df.replace("Konyaspor","Konyaspor", inplace=True)
    df.replace("Sparta Prague","Sparta Prague", inplace=True)
    # df.replace("Kfum Oslo","KFUM Oslo", inplace=True)
    df.replace("Haugesund","Haugesund", inplace=True)
    df.replace("Racing de Ferrol","Racing Club Ferrol", inplace=True)
    df.replace("Huesca","Huesca", inplace=True)
    df.replace("Heerenveen","Heerenveen", inplace=True)
    df.replace("Sturm Graz","Sturm Graz", inplace=True)
    df.replace("SK Sturm Graz II","Sturm Graz (Am)", inplace=True)
    df.replace("Kristiansund","Kristiansund", inplace=True)
    df.replace("Portsmouth","Portsmouth", inplace=True)
    df.replace("Blackburn","Blackburn", inplace=True)
    df.replace("Willem II","Willem II", inplace=True)
    df.replace("Haras El Hodood", "Haras El Hodood",inplace=True)
    df.replace("AC Milan B", "AC Milan U23",inplace=True)
    df.replace("Real Zaragoza II","Zaragoza B", inplace=True)
    df.replace("Zaragoza","Zaragoza", inplace=True)
    df.replace("Bodrum Belediyesi Bodrumspor","Bodrumspor", inplace=True)
    df.replace("Goztepe","Goztepe", inplace=True)
    df.replace("Centro Atletico Fenix","Fenix", inplace=True)
    df.replace("Grasshoppers Zurich","Grasshoppers", inplace=True)
    df.replace("Amorebieta","Amorebieta", inplace=True)
    df.replace("Varazdin","Varazdin", inplace=True)
    df.replace('La Equidad','La Equidad', inplace=True)
    df.replace("Tenerife B","Tenerife B", inplace=True)
    df.replace("River Plate","River Plate", inplace=True)
    df.replace("AVS Futebol SAD","AVS", inplace=True)
    df.replace("Western Sydney Wanderers","WS Wanderers", inplace=True)
    df.replace('07 Vestur', '07 Vestur Sorvagur', inplace=True)
    df.replace('Once Municipal', '11 Deportivo', inplace=True)
    df.replace('12 de Junio de Villa Hayes', '12 de Junio', inplace=True)
    df.replace('1 Dezembro', '1º Dezembro', inplace=True)
    df.replace('Club Sportivo 2 de Mayo', '2 de Mayo', inplace=True)
    df.replace('9 de J Rafaela', '9 de Julio Rafaela', inplace=True)
    df.replace('Audax Italiano', 'A. Italiano', inplace=True)
    df.replace('Austria Klagenfurt', 'A. Klagenfurt', inplace=True)
    df.replace('SC Austria Lustenau', 'A. Lustenau', inplace=True)
    df.replace('SV Austria Salzburg', 'A. Salzburg', inplace=True)
    df.replace('ABC RN', 'ABC', inplace=True)
    df.replace('CD Aguila', 'AD Aguila', inplace=True)
    df.replace('Fafe', 'AD Fafe', inplace=True)
    df.replace('Santos de Guapiles', 'AD Santos', inplace=True)
    df.replace('AD Sao Caetano U20', 'AD Sao Caetano do Sul U20', inplace=True)
    df.replace('Asociacion Deportiva T', 'AD Tarma', inplace=True)
    df.replace('Club ADA Jaén', 'ADA Jaen', inplace=True)
    df.replace('Altos', 'AE Altos', inplace=True)
    df.replace('AEK Athens', 'AEK Athens FC', inplace=True)
    df.replace('Telford', 'AFC Telford', inplace=True)
    df.replace('APR FC', 'APR', inplace=True)
    df.replace('Roma', 'AS Roma', inplace=True)
    df.replace('Asa AL', 'ASA', inplace=True)
    df.replace('ASEEV GO', 'ASEEV', inplace=True)
    df.replace('Voitsberg', 'ASK Voitsberg', inplace=True)
    df.replace('Rainbow FC', 'ASOS Rainbow AC', inplace=True)
    df.replace('Asco Atsv Wolfsberg', 'ATSV Wolfsberger', inplace=True)
    df.replace('Az Alkmaar', 'AZ Alkmaar', inplace=True)
    df.replace('AaB', 'Aalborg', inplace=True)
    df.replace('Aalesunds', 'Aalesund', inplace=True)
    df.replace('Aalesund II', 'Aalesund 2', inplace=True)
    df.replace('AGF', 'Aarhus', inplace=True)
    df.replace('Abo Qair Semads', 'Abu Qir Semad', inplace=True)
    df.replace('Academico de Viseu', 'Academico Viseu', inplace=True)
    df.replace('Academico de Viseu U23', 'Academico Viseu U23', inplace=True)
    df.replace('AD Aserri', 'Ad Aserri', inplace=True)
    df.replace('AD San Carlos', 'Ad San Carlos', inplace=True)
    df.replace('Adanaspor', 'Adanaspor AS', inplace=True)
    df.replace('CS Afumati', 'Afumati', inplace=True)
    df.replace('SC Aguai U20', 'Aguai U20', inplace=True)
    df.replace('Aguia de Maraba', 'Aguia De Maraba', inplace=True)
    df.replace('CD Aguila', 'Aguila', inplace=True)
    df.replace('Aguilas Doradas', 'Aguilas', inplace=True)
    # df.replace('Aguilas', 'Aguilas FC', inplace=True)
    df.replace('Rot-Weiss Ahlen', 'Ahlen', inplace=True)
    df.replace('IA Akranes', 'Akranes', inplace=True)
    df.replace('FK Aktobe', 'Aktobe', inplace=True)
    df.replace('Al Ahli Amman', 'Al Ahli', inplace=True)
    df.replace('Al Ahli (QAT)', 'Al Ahli Doha', inplace=True)
    df.replace('Al Ahli', 'Al Ahli SC', inplace=True)
    df.replace('Al Ahly Cairo', 'Al Ahly', inplace=True)
    df.replace('El Alominiom', 'Al Aluminium', inplace=True)
    df.replace('Al-Ettifaq', 'Al Ettifaq', inplace=True)
    df.replace('Al-Fujairah FC', 'Al Fujairah', inplace=True)
    df.replace('Al-Hilal', 'Al Hilal', inplace=True)
    df.replace('Al-Ittihad', 'Al Ittihad', inplace=True)
    df.replace('Al-Ittihad', 'Al Ittihad (EGY)', inplace=True)
    df.replace('Al-Jazeera', 'Al Jazeera Amman', inplace=True)
    df.replace('Kuwait SC', 'Al Kuwait', inplace=True)
    df.replace('Al-Masry', 'Al Masry', inplace=True)
    df.replace('Al Nasr (UAE)', 'Al Nasr', inplace=True)
    df.replace('Al-Qadsia', 'Al Qadisiya', inplace=True)
    df.replace('Al Salmiyah', 'Al Salmiya', inplace=True)
    df.replace('Al-Shabab (KSA)', 'Al Shabab', inplace=True)
    df.replace('Al Tadhamon', 'Al Tadamon', inplace=True)
    df.replace('Hay Al Wadi', 'Al Wadi', inplace=True)
    df.replace('Al-Duhail SC', 'Al-Duhail', inplace=True)
    df.replace('Al Fahaheel FC', 'Al-Fahaheel', inplace=True)
    df.replace('Al Faisaly SC', 'Al-Faisaly Amman', inplace=True)
    df.replace('Al Hilal Omdurman', 'Al-Hilal Omdurman', inplace=True)
    # df.replace('Al Ittihad (EGY)', 'Al-Ittihad', inplace=True)
    df.replace('Alagoinhas AC', 'Alagoinhas', inplace=True)
    df.replace('Ld Alajuelense', 'Alajuelense', inplace=True)
    df.replace('Aland United (W)', 'Aland Utd (W)', inplace=True)
    df.replace('Al Nasar (KUW)', 'Alaves (W)', inplace=True)
    df.replace('Albinoleffe', 'AlbinoLeffe', inplace=True)
    df.replace('Albion FC', 'Albion', inplace=True)
    df.replace('Albion', 'Albion Rovers', inplace=True)
    df.replace('Albirex Niigata (SIN)', 'Albirex Niigata', inplace=True)
    df.replace('Albirex Niigata', 'Albirex Niigata (SIN)', inplace=True)
    df.replace('ASD Alcione', 'Alcione Milano', inplace=True)
    df.replace('Alebrijes De Oaxaca', 'Alebrijes Oaxaca', inplace=True)
    df.replace('FCM Alexandria', 'Alexandria', inplace=True)
    df.replace('Alfreton Town', 'Alfreton', inplace=True)
    df.replace('Alianza Petrolera', 'Alianza', inplace=True)
    df.replace('Alianza Atletico', 'Alianza Atl.', inplace=True)
    df.replace('Alianza FC (SLV)', 'Alianza FC', inplace=True)
    df.replace('Alianza Universidad', 'Alianza Huanuco', inplace=True)
    df.replace('Alianza FC (Pan)', 'Alianza Petrolera', inplace=True)
    df.replace('Almagro BA', 'Almagro', inplace=True)
    df.replace('NK Aluminij', 'Aluminij', inplace=True)
    df.replace('Amazonas FC', 'Amazonas', inplace=True)
    df.replace('Club Sportivo Ameliano', 'Ameliano', inplace=True)
    df.replace('America de Cali S.A', 'America De Cali', inplace=True)
    df.replace('Ammanford AFC', 'Ammanford', inplace=True)
    df.replace('SKU Amstetten', 'Amstetten', inplace=True)
    df.replace('Anapolis GO', 'Anapolis', inplace=True)
    df.replace('Anderlecht B', 'Anderlecht U23', inplace=True)
    df.replace('Indija', 'Andijan', inplace=True)
    df.replace('Andorra CF', 'Andorra', inplace=True)
    df.replace('Angelholms', 'Angelholm', inplace=True)
    df.replace('Angostura FC', 'Angostura', inplace=True)
    df.replace('Ansan Greeners FC', 'Ansan Greeners', inplace=True)
    df.replace('SPVGG Ansbach', 'Ansbach', inplace=True)
    df.replace('Antequera CF', 'Antequera', inplace=True)
    df.replace('Antigua GFC', 'Antigua', inplace=True)
    df.replace('PFA Antioquia FC', 'Antioquia', inplace=True)
    df.replace('Deportes Antofagasta (W)', 'Antofagasta (W)', inplace=True)
    df.replace('FC Anyang', 'Anyang', inplace=True)
    df.replace('Aparecidense Go', 'Aparecidense', inplace=True)
    df.replace('Apollon Limassol', 'Apollon', inplace=True)
    df.replace('Al Mokawloon', 'Arab Contractors', inplace=True)
    df.replace('FC Ararat Yerevan', 'Ararat Yerevan', inplace=True)
    df.replace('Ararat Armenia', 'Ararat-Armenia', inplace=True)
    df.replace('Araz Nakhchivan PFK', 'Araz', inplace=True)
    df.replace('FC Arbaer', 'Arbaer', inplace=True)
    df.replace('Argentino Monte Maiz', 'Argentino MM', inplace=True)
    df.replace('CA Argentino de Rosario', 'Argentino de Rosario', inplace=True)
    df.replace('Argentinos Juniors', 'Argentinos Jrs', inplace=True)
    df.replace('Argentinos Juniors (Res)', 'Argentinos Jrs 2', inplace=True)
    df.replace('Ariana FC', 'Ariana', inplace=True)
    df.replace('DJK Arminia Klosterhardt', 'Arminia Klosterhardt', inplace=True)
    df.replace('Arsenal de Sarandi', 'Arsenal Sarandi', inplace=True)
    df.replace('FK Arsenal Tivat', 'Arsenal Tivat', inplace=True)
    df.replace('Fernandez Vial', 'Arturo Fernandez Vial', inplace=True)
    df.replace('Aryan Club', 'Aryan', inplace=True)
    df.replace('Arzignanochiampo', 'Arzignano', inplace=True)
    df.replace('Chungnam Asan', 'Asan', inplace=True)
    df.replace('Asane Fotball II', 'Asane 2', inplace=True)
    df.replace('Viktoria Aschaffenburg', 'Aschaffenburg', inplace=True)
    df.replace('Assiden IF', 'Assiden', inplace=True)
    df.replace('BK Astrio', 'Astrio', inplace=True)
    df.replace('Aswan FC', 'Aswan SC', inplace=True)
    df.replace('Atalanta B', 'Atalanta U23', inplace=True)
    df.replace('Athletic Bilbao', 'Ath Bilbao', inplace=True)
    df.replace('Kallithea', 'Athens Kallithea', inplace=True)
    df.replace('Atherton Collieries AFC', 'Atherton', inplace=True)
    df.replace('Athletic Club MG U20', 'Athletic Club U20', inplace=True)
    df.replace('Atletico Paranaense U20', 'Athletico-PR U20', inplace=True)
    df.replace('Athlone Town', 'Athlone', inplace=True)
    df.replace('Athlone Town (W)', 'Athlone WFC (W)', inplace=True)
    df.replace('Atletico Madrid', 'Atl. Madrid', inplace=True)
    df.replace('Atletico Madrid (W)', 'Atl. Madrid (W)', inplace=True)
    df.replace('Club Atletico Morelia', 'Atl. Morelia', inplace=True)
    df.replace('Atletico Nacional Medellin', 'Atl. Nacional', inplace=True)
    df.replace('Atletico Ottawa', 'Atl. Ottawa', inplace=True)
    df.replace('Atletico Rafaela', 'Atl. Rafaela', inplace=True)
    df.replace('Atletico San Luis', 'Atl. San Luis', inplace=True)
    df.replace('Atletico San Luis (W)', 'Atl. San Luis (W)', inplace=True)
    df.replace('Atl Tucuman', 'Atl. Tucuman', inplace=True)
    df.replace('Atletico Tucuman (Res)', 'Atl. Tucuman 2', inplace=True)
    df.replace('Atlantico FC', 'Atlantico', inplace=True)
    df.replace('Atlantis FC/Akatemia', 'Atlantis 2', inplace=True)
    df.replace('CA Atlas', 'Atlas', inplace=True)
    df.replace('FC Atlas (W)', 'Atlas (W)', inplace=True)
    df.replace('CA Atlanta', 'Atletico Atlanta', inplace=True)
    df.replace('Atletico FC Cali', 'Atletico F.C.', inplace=True)
    df.replace('Atletico Goianiense U20', 'Atletico GO U20', inplace=True)
    df.replace('Atletico Paranaense U20', 'Atletico Goianiense U20', inplace=True)
    df.replace('Atletico Sanluqueno CF', 'Atletico La Cruz', inplace=True)
    df.replace('Club Atletico La Paz', 'Atletico La Paz', inplace=True)
    df.replace('Club Atletico Pantoja', 'Atletico Pantoja', inplace=True)
    df.replace('FC Atletico Cearense', 'Atletico-CE', inplace=True)
    df.replace('Atletico MG', 'Atletico-MG', inplace=True)
    df.replace('Atletico MG U20', 'Atletico-MG U20', inplace=True)
    df.replace('FK Atmosfera', 'Atmosfera', inplace=True)
    df.replace('FK Atyrau', 'Atyrau', inplace=True)
    df.replace('TSV Aubstadt', 'Aubstadt', inplace=True)
    df.replace('FK Auda', 'Auda', inplace=True)
    df.replace('Audax Rio', 'Audax RJ', inplace=True)
    df.replace('Dundalk U20', 'Audax RJ U20', inplace=True)
    df.replace('Erzgebirge', 'Aue', inplace=True)
    df.replace('Dundalk', 'Augnablik', inplace=True)
    df.replace('FC Augsburg U19', 'Augsburg U19', inplace=True)
    df.replace('Austria Wien (A)', 'Austria Vienna (Am)', inplace=True)
    df.replace('CS Avantul Periam', 'Avantul Periam', inplace=True)
    df.replace('Esporte Clube Avenida', 'Avenida', inplace=True)
    df.replace('Aviles Stadium CF', 'Aviles Stadium', inplace=True)
    df.replace('Fukuoka', 'Avispa Fukuoka', inplace=True)
    df.replace('Avro FC', 'Avro', inplace=True)
    df.replace('Ayeyawady United', 'Ayeyawady', inplace=True)
    df.replace('AZ Alkmaar', 'Az Alkmaar', inplace=True)
    df.replace('Azuriz FC U20', 'Azuriz U20', inplace=True)
    df.replace('Mgladbach', 'B. Monchengladbach', inplace=True)
    df.replace('Mgladbach (W)', 'B. Monchengladbach (W)', inplace=True)
    df.replace('Mgladbach II', 'B. Monchengladbach II', inplace=True)
    df.replace('B93 Copenhagen', 'B.93', inplace=True)
    df.replace('B36 Torshavn II', 'B36 Torshavn 2', inplace=True)
    df.replace('Be1 NFA', 'BE1 NFA', inplace=True)
    df.replace('BFF Academy FC', 'BFF Academy U19', inplace=True)
    df.replace('Frem', 'BK Frem', inplace=True)
    df.replace('Belenenses', 'BSAD', inplace=True)
    df.replace('BSS Sporting Club', 'BSS Sporting', inplace=True)
    df.replace('Bts Neustadt', 'BTS Neustadt', inplace=True)
    df.replace('FC Blau Weiss Linz', 'BW Linz', inplace=True)
    df.replace('DJK Blau-Weis Mintard', 'BW Mintard', inplace=True)
    df.replace('FK Babrungas', 'Babrungas', inplace=True)
    df.replace('Fc Baden', 'Baden', inplace=True)
    df.replace('Baerum', 'Baerum Sportsklubb', inplace=True)
    df.replace('EC Bahia (W)', 'Bahia (W)', inplace=True)
    df.replace('Bahia EC U20', 'Bahia U20', inplace=True)
    df.replace('Bahia De Feira BA', 'Bahia de Feira', inplace=True)
    df.replace('Bahlinger SC', 'Bahlinger', inplace=True)
    df.replace('Baladeyet Al-Mahalla', 'Baladiyat El Mahalla', inplace=True)
    df.replace('FBK Balkan', 'Balkan', inplace=True)
    df.replace('Ballyfermot United FC', 'Ballyfermot', inplace=True)
    df.replace('CSF Balti', 'Balti', inplace=True)
    df.replace('Balzan FC', 'Balzan', inplace=True)
    df.replace('FC Eintracht Bamberg', 'Bamberg', inplace=True)
    df.replace('CA Banfield (W)', 'Banfield (W)', inplace=True)
    df.replace('CA Banfield (Res)', 'Banfield 2', inplace=True)
    df.replace('FK Banga Gargzdu', 'Banga', inplace=True)
    df.replace('FK Banga II', 'Banga 2', inplace=True)
    df.replace('Bangor', 'Bangor FC', inplace=True)
    df.replace('Dukla Banska Bystrica', 'Banska Bystrica', inplace=True)
    df.replace('Barcelona (Ecu)', 'Barcelona (ECU)', inplace=True)
    df.replace('Barcelona (ECU)', 'Barcelona SC', inplace=True)
    df.replace('BVV Barendrecht', 'Barendrecht', inplace=True)
    df.replace('SSD Bari', 'Bari', inplace=True)
    df.replace('PS Barito Putera', 'Barito Putera', inplace=True)
    df.replace('Barra SC U20', 'Barra FC U20', inplace=True)
    df.replace('Barracas Central (Res)', 'Barracas Central 2', inplace=True)
    df.replace('Barretos SP', 'Barretos EC', inplace=True)
    df.replace('Barry Town Utd', 'Barry', inplace=True)
    df.replace('FC Basel', 'Basel', inplace=True)
    df.replace('Bassano Virtus', 'Bassano', inplace=True)
    df.replace('Bath City', 'Bath', inplace=True)
    df.replace('SF Baumberg', 'Baumberg', inplace=True)
    df.replace('Leverkusen', 'Bayer Leverkusen', inplace=True)
    df.replace('Leverkusen (W)', 'Bayer Leverkusen (W)', inplace=True)
    df.replace('Bayern Munich II', 'Bayern II', inplace=True)
    df.replace('Bradford', 'Bedford', inplace=True)
    df.replace('KFCO Beerschot Wilrijk', 'Beerschot VA', inplace=True)
    df.replace('Beijing Tech FC', 'Beijing Technology', inplace=True)
    df.replace('SC Beira Mar Aveiro', 'Beira Mar', inplace=True)
    df.replace('CA Belgrano (W)', 'Belgrano (W)', inplace=True)
    df.replace('Belgrano (Res)', 'Belgrano 2', inplace=True)
    df.replace('SK Benesov', 'Benesov', inplace=True)
    df.replace('Bengaluru', 'Bengaluru FC', inplace=True)
    df.replace('AD Berazategui', 'Berazategui', inplace=True)
    df.replace('Bergantinos CF', 'Bergantinos', inplace=True)
    df.replace('Beroe Stara Za', 'Beroe', inplace=True)
    df.replace('Betim Futebol U20', 'Betim U20', inplace=True)
    df.replace('Bhawanipore FC', 'Bhawanipore', inplace=True)
    df.replace('Sportivo Atenas', 'Biblioteca Atenas', inplace=True)
    df.replace('Biel Bienne', 'Biel', inplace=True)
    df.replace('BTS Rekord B-B', 'Bielsko-Biala', inplace=True)
    df.replace('Bylis Ballsh', 'Big Bullets', inplace=True)
    df.replace('Billericay Town', 'Billericay', inplace=True)
    df.replace('FC Bilovec', 'Bilovec', inplace=True)
    df.replace('Binfield Fc', 'Binfield', inplace=True)
    df.replace('SK Bischofshofen', 'Bischofshofen', inplace=True)
    df.replace('FK Blansko', 'Blansko', inplace=True)
    df.replace('Blaublitz Akita', 'Blaublitz', inplace=True)
    df.replace('Blauw Geel 38', 'Blauw Geel', inplace=True)
    df.replace('Svg Bleiburg', 'Bleiburg', inplace=True)
    df.replace('Blektini Stargard', 'Blekitni Stargard', inplace=True)
    df.replace('Blooming Santa Cruz', 'Blooming', inplace=True)
    df.replace('Blumenau Esporte Clube', 'Blumenau', inplace=True)
    df.replace('Boca Jrs (Res)', 'Boca Juniors 2', inplace=True)
    df.replace("Boca Juniors","Boca Juniors", inplace=True)
    df.replace('FC Bocholt', 'Bocholt', inplace=True)
    df.replace('VfL Bochum U19', 'Bochum U19', inplace=True)
    df.replace('Bodens', 'Boden', inplace=True)
    df.replace('Bodo Glimt', 'Bodo/Glimt', inplace=True)
    df.replace('Bohemians 1905', 'Bohemians', inplace=True)
    df.replace('Bohemians (W)', 'Bohemians WFC (W)', inplace=True)
    df.replace('TJ Tatran Bohunice', 'Bohunice', inplace=True)
    df.replace('FK Bokelj', 'Bokelj', inplace=True)
    df.replace('Sioni Bolnisi', 'Bolnisi', inplace=True)
    df.replace('Bonita Banana SC', 'Bonita Banana', inplace=True)
    df.replace('Bonner SC', 'Bonner', inplace=True)
    df.replace('Bonnyrigg', 'Bonnyrigg Rose', inplace=True)
    df.replace('Pusamania Borneo FC', 'Borneo', inplace=True)
    df.replace('Boston U20', 'Boston City U20', inplace=True)
    df.replace('Botafogo FR', 'Botafogo RJ', inplace=True)
    df.replace('Botafogo FR U20', 'Botafogo U20', inplace=True)
    df.replace('Bourg-en-Bresse', 'Bourg en Bresse', inplace=True)
    df.replace('TUS Bovinghausen 04', 'Bovinghausen', inplace=True)
    df.replace('Bala Town', 'Bala', inplace=True)
    df.replace('Bracknell Town Fc', 'Bracknell', inplace=True)
    df.replace('Bradford', 'Bradford City', inplace=True)
    df.replace('Sporting Braga U23', 'Braga U23', inplace=True)
    df.replace('Bragantino SP', 'Bragantino', inplace=True)
    df.replace('IK Brage', 'Brage', inplace=True)
    df.replace('Brann II', 'Brann 2', inplace=True)
    df.replace('NK Bravo', 'Bravo', inplace=True)
    df.replace('Bray Wanderers', 'Bray', inplace=True)
    df.replace('NAC Breda', 'NAC Breda', inplace=True)
    df.replace('Grindavik (W)', 'Breidablik (W)', inplace=True)
    df.replace('Bremer SV', 'Bremer', inplace=True)
    df.replace('Brightlingsea Regent', 'Brightlingsea', inplace=True)
    df.replace('Boston River', 'Bristol Rovers', inplace=True)
    df.replace('FC Zbrojovka Brno', 'Brno', inplace=True)
    df.replace('Bromsgrove Sporting FC', 'Bromsgrove', inplace=True)
    df.replace('Brown de Adrogue', 'Brown Adrogue', inplace=True)
    df.replace('SC Bruhl St Gallen', 'Bruhl', inplace=True)
    df.replace('FC Bruenninghausen', 'Brunninghausen', inplace=True)
    df.replace('Brusque FC', 'Brusque', inplace=True)
    df.replace('Brusque FC U20', 'Brusque U20', inplace=True)
    df.replace('Stal Brzeg', 'Brzeg', inplace=True)
    df.replace('Atletico Bucaramanga', 'Bucaramanga', inplace=True)
    df.replace('FC Buderich', 'Buderich', inplace=True)
    df.replace('Fk Buducnost Podgorica', 'Buducnost', inplace=True)
    df.replace('Burgos', 'Burgos CF', inplace=True)
    df.replace('Buriram Utd', 'Buriram', inplace=True)
    df.replace('Burton Albion', 'Burton', inplace=True)
    df.replace('Busan IPark', 'Busan', inplace=True)
    df.replace('Busan Transportation Corp', 'Busan Kyotong', inplace=True)
    df.replace('Atlante', 'CA Atlanta', inplace=True)
    df.replace('Atlas', 'CA Atlas', inplace=True)
    df.replace('Cerro', 'CA Cerro', inplace=True)
    df.replace('Estudiantes de Caseros', 'CA Estudiantes', inplace=True)
    df.replace('IA Akranes (W)', 'CA Estudiantes (W)', inplace=True)
    df.replace('Atletico Independiente', 'CA Independiente', inplace=True)
    df.replace('Atletico Mitre', 'CA Mitre', inplace=True)
    df.replace('Sporting San Miguelito', 'CA San Miguel', inplace=True)
    df.replace('Extremadura UD', 'CD Extremadura', inplace=True)
    df.replace('Club Deportes Santa Cruz', 'CD Santa Cruz', inplace=True)
    df.replace('Talavera CF', 'CF Talavera', inplace=True)
    df.replace('Petrolero', 'CI Petrolero', inplace=True)
    df.replace('ACS Dumbravita', 'CSC Dumbravita', inplace=True)
    df.replace('CSD Rangers Talca', 'CSD Rangers', inplace=True)
    df.replace('Clube Sociedade Esportiva', 'CSE', inplace=True)
    df.replace('CS Kosarom Pascani', 'CSM Pascani', inplace=True)
    df.replace('CSM Scolar Resita', 'CSM Resita', inplace=True)
    df.replace('CSR Espanol BA', 'CSR Espanol', inplace=True)
    df.replace('CD Cacahuatique', 'Cacahuatique', inplace=True)
    df.replace('Cadiz', 'Cadiz CF', inplace=True)
    df.replace('Cadiz B', 'Cadiz CF B', inplace=True)
    df.replace('Caernarfon Town', 'Caernarfon', inplace=True)
    df.replace('UTC Cajamarca', 'Cajamarca', inplace=True)
    df.replace('CD Calahorra', 'Calahorra', inplace=True)
    df.replace('Calcutta Police Club', 'Calcutta Police', inplace=True)
    df.replace('Caldas SC', 'Caldas', inplace=True)
    df.replace('ASD Calcio Caldiero Terme', 'Caldiero Terme', inplace=True)
    df.replace('Cambuur Leeuwarden', 'Cambuur', inplace=True)
    df.replace('Nuovo Campobasso', 'Campobasso', inplace=True)
    df.replace('Cancun FC', 'Cancun', inplace=True)
    df.replace('Cangzhou Mighty Lions', 'Cangzhou', inplace=True)
    df.replace('Canvey Island', 'Canvey', inplace=True)
    df.replace('Cape Town CIty F.C.', 'Cape Town City', inplace=True)
    df.replace('Capital-TO', 'Capital FC', inplace=True)
    df.replace('Capo FC', 'Capo', inplace=True)
    df.replace('Carabobo FC', 'Carabobo', inplace=True)
    df.replace('AD Cariari Pococi', 'Cariari Pococi', inplace=True)
    df.replace('C Stein', 'Carlos Stein', inplace=True)
    df.replace('Ad Carmelita', 'Carmelita', inplace=True)
    df.replace('Carshalton Athletic FC', 'Carshalton', inplace=True)
    df.replace('Real Cartagena', 'Cartagena', inplace=True)
    df.replace('Cs Cartagines', 'Cartagines', inplace=True)
    df.replace('Cascavel PR', 'Cascavel', inplace=True)
    df.replace('CD Castellon', 'Castellon', inplace=True)
    df.replace('Caucaia EC', 'Caucaia', inplace=True)
    df.replace('Cavese 1919', 'Cavese', inplace=True)
    df.replace('Ceara SC Fortaleza', 'Ceara', inplace=True)
    df.replace('Ceara SC U20', 'Ceara U20', inplace=True)
    df.replace('Ceilandia Esporte Clube', 'Ceilandia', inplace=True)
    df.replace('NK Celje', 'Celje', inplace=True)
    df.replace('CSD Central Ballester', 'Central Ballester', inplace=True)
    df.replace('Central Cordoba (SdE)', 'Central Cordoba', inplace=True)
    df.replace('Central Cordoba SdE (Res)', 'Central Cordoba 2', inplace=True)
    df.replace('CA Central Nort', 'Central Norte', inplace=True)
    df.replace('Central Valley Fuego FC', 'Central Valley Fuego', inplace=True)
    df.replace('Central Valley Fuego F', 'Central Valley Fuego FC', inplace=True)
    df.replace('Centro Oeste SAF', 'Centro Oeste', inplace=True)
    df.replace('Cercle Brugge', 'Cercle Brugge KSV', inplace=True)
    df.replace('C-Osaka', 'Cerezo Osaka', inplace=True)
    df.replace('Cerro Largo FC', 'Cerro Largo', inplace=True)
    df.replace('Universidad Cesar Vallejo', 'Cesar Vallejo', inplace=True)
    df.replace('Moravsky Krumlov', 'Cesky Krumlov', inplace=True)
    df.replace('AD Ceuta FC', 'Ceuta B', inplace=True)
    df.replace('Chacarita', 'Chacarita Juniors', inplace=True)
    df.replace('Chacaritas SC', 'Chacaritas', inplace=True)
    df.replace('Changwon City', 'Changwon', inplace=True)
    df.replace('Chapecoense', 'Chapecoense-SC', inplace=True)
    df.replace('Charleston Battery', 'Charleston', inplace=True)
    df.replace('Charlotte FC', 'Charlotte', inplace=True)
    df.replace('Charlotte Independence', 'Charlotte Independ.', inplace=True)
    df.replace('Chatham Town', 'Chatham', inplace=True)
    df.replace('Chattanooga Red Wolves SC', 'Chattanooga Red Wolves', inplace=True)
    df.replace('Cavese 1919', 'Chaves U19', inplace=True)
    df.replace('Chennaiyin FC', 'Chennaiyin', inplace=True)
    df.replace('Cheongju FC', 'Cheongju', inplace=True)
    df.replace('Chernomorets Odesa', 'Ch. Odesa', inplace=True)
    df.replace('Chesham Utd', 'Chesham', inplace=True)
    df.replace('JL Chiangmai United', 'Chiangmai Utd', inplace=True)
    df.replace('Jef Utd Chiba', 'Chiba', inplace=True)
    df.replace('Boyaca Chico', 'Chico', inplace=True)
    df.replace('FK Chlumec', 'Chlumec nad Cidlinou', inplace=True)
    df.replace('Chojniczanka Chojnice', 'Chojniczanka', inplace=True)
    df.replace('MFK Chrudim', 'Chrudim', inplace=True)
    df.replace('Cianorte PR', 'Cianorte', inplace=True)
    df.replace('Cibao FC', 'Cibao', inplace=True)
    df.replace('FC Cincinnati II', 'Cincinnati 2', inplace=True)
    df.replace('Club Cipolletti', 'Cipolletti', inplace=True)
    df.replace('Circulo Deportivo Otamendi', 'Circulo Deportivo', inplace=True)
    df.replace('Ciudad de Bolivar', 'Ciudad Bolivar', inplace=True)
    df.replace('TSV Victoria Clarholz', 'Clarholz', inplace=True)
    df.replace('CA Claypole', 'Claypole', inplace=True)
    df.replace('CA Guemes', 'Club A. Guemes', inplace=True)
    df.replace('CF America', 'Club America', inplace=True)
    df.replace('CF America (W)', 'Club America (W)', inplace=True)
    df.replace('CA Colegiales', 'Club Atletico Colegiales', inplace=True)
    df.replace('Club Brugge', 'Club Brugge KV', inplace=True)
    df.replace('Leon', 'Club Leon', inplace=True)
    df.replace('Club Leon FC (W)', 'Club Leon (W)', inplace=True)
    df.replace('Club Mutual Crucero del Norte', 'Club Mutual Crucero del No', inplace=True)
    df.replace('Sportivo Trinidense', 'Club Sportivo Trinidense', inplace=True)
    df.replace('Tijuana', 'Club Tijuana', inplace=True)
    df.replace('Cobreloa Calama', 'Cobreloa', inplace=True)
    df.replace('Cockhill Celtic', 'Cockhill', inplace=True)
    df.replace('A.D. Cofutpa', 'Cofutpa', inplace=True)
    df.replace('Coimbra EC U20', 'Coimbra U20', inplace=True)
    df.replace('Colchester United U21', 'Colchester U21', inplace=True)
    df.replace('Club Atletico Colegiales', 'Colegiales', inplace=True)
    df.replace('Colo Colo BA', 'Colo C.', inplace=True)
    df.replace('Colo Colo (W)', 'Colo-Colo (W)', inplace=True)
    df.replace('Colon FC', 'Colon', inplace=True)
    df.replace('Colon', 'Colon Santa Fe', inplace=True)
    df.replace('Colorado', 'Colorado Rapids', inplace=True)
    df.replace('Colorado Rapids II', 'Colorado Rapids 2', inplace=True)
    df.replace('Colorado Springs Switchbacks FC', 'Colorado Springs', inplace=True)
    df.replace('Colorado Springs Switchba', 'Colorado Springs Switchbacks FC', inplace=True)
    df.replace('Columbus', 'Columbus Crew', inplace=True)
    df.replace('Columbus Crew II', 'Columbus Crew 2', inplace=True)
    df.replace('Comerciantes FC', 'Comerciantes', inplace=True)
    df.replace('SD Compostela', 'Compostela', inplace=True)
    df.replace('Concon National FC', 'Concon National', inplace=True)
    df.replace('Concordia Chiajna', 'Concordia', inplace=True)
    df.replace('Concordia Chiajna', 'Concordia CA', inplace=True)
    df.replace('Contagem EC U20', 'Contagem U20', inplace=True)
    df.replace('CSyD Cooper', 'Cooper', inplace=True)
    df.replace('Deportes Copiapo', 'Copiapo', inplace=True)
    df.replace('Coquimbo Unido', 'Coquimbo', inplace=True)
    df.replace('Coquimbo Unido (W)', 'Coquimbo (W)', inplace=True)
    df.replace('Coria CF', 'Coria C.F.', inplace=True)
    df.replace('Correcaminos UAT', 'Correcaminos', inplace=True)
    df.replace('Coruxo', 'Coruxo FC', inplace=True)
    df.replace('FC Cosmos Koblenz', 'Cosmos Koblenz', inplace=True)
    df.replace('Costa Rica EC', 'Costa Rica', inplace=True)
    df.replace('Cracovia Krakow', 'Cracovia', inplace=True)
    df.replace('Crawley Town', 'Crawley', inplace=True)
    df.replace('Bray Wanderers U20', 'Cray Wanderers', inplace=True)
    df.replace('US Cremonese', 'Cremonese', inplace=True)
    df.replace('Croydon Athletic', 'Croydon Ath.', inplace=True)
    df.replace('Club Mutual Crucero del No', 'Crucero del Norte', inplace=True)
    df.replace('Cruzeiro MG', 'Cruzeiro', inplace=True)
    df.replace('Cruzeiro de Arapiraca', 'Cruzeiro Arapiraca', inplace=True)
    df.replace('Crvena Zvezda', 'Crvena zvezda', inplace=True)
    df.replace('CS Cartagines', 'Cs Cartagines', inplace=True)
    df.replace('Csikszereda', 'Csikszereda M. Ciuc', inplace=True)
    df.replace('Cucuta Deportivo', 'Cucuta', inplace=True)
    df.replace('Cuiaba EC U20', 'Cuiaba U20', inplace=True)
    df.replace('Leonesa', 'Cultural Leonesa', inplace=True)
    df.replace('Cumbaya FC', 'Cumbaya', inplace=True)
    df.replace('Gualan FC', 'Cumbaya FC', inplace=True)
    df.replace('Cuniburo FC', 'Cuniburo', inplace=True)
    df.replace('Cusco FC', 'Cusco', inplace=True)
    df.replace('SSD Cynthialbalonga', 'Cynthialbalonga', inplace=True)
    df.replace('MKS Czarni Polaniec', 'Czarni Polaniec', inplace=True)
    df.replace('Deportes Concepcion', 'D. Concepcion', inplace=True)
    df.replace('Puerto Montt', 'D. Puerto Montt', inplace=True)
    df.replace('Dinamo Zagreb', 'D. Zagreb', inplace=True)
    df.replace('DC Utd', 'DC United', inplace=True)
    df.replace('Brunei DPMM FC', 'DPMM', inplace=True)
    df.replace('Diosgyori', 'DVTK', inplace=True)
    df.replace('Diosgyori VTK (W)', 'DVTK (W)', inplace=True)
    df.replace('Daegu FC', 'Daegu', inplace=True)
    df.replace('Daegu FC (Res)', 'Daegu 2', inplace=True)
    df.replace('Daegu Fc', 'Daegu FC', inplace=True)
    df.replace('Daejeon Citizen', 'Daejeon', inplace=True)
    df.replace('Daejeon Korail FC', 'Daejeon Korail', inplace=True)
    df.replace('Dag and Red', 'Dag & Red', inplace=True)
    df.replace('Daga United FC', 'Daga United', inplace=True)
    df.replace('Dagon FC', 'Dagon', inplace=True)
    df.replace('Dagon Port FC', 'Dagon Port', inplace=True)
    df.replace('FK Dainava Alytus', 'Dainava Alytus', inplace=True)
    df.replace('Dalian Kun City FC', 'Dalian Kuncheng', inplace=True)
    df.replace('Dalian Yifang', 'Dalian Pro', inplace=True)
    df.replace('Dalkurd FF', 'Dalkurd', inplace=True)
    df.replace('SV Darmstadt', 'Darmstadt', inplace=True)
    df.replace('SV Darmstadt 98 U19', 'Darmstadt U19', inplace=True)
    df.replace('Debreceni VSC', 'Debrecen', inplace=True)
    df.replace('FK Decic', 'Decic', inplace=True)
    df.replace('Club Defensores de P', 'Def. Pronunciamiento', inplace=True)
    df.replace('Defensores de Belgrano', 'Def. de Belgrano', inplace=True)
    df.replace('CD Cambaceres', 'Def. de Cambaceres', inplace=True)
    df.replace('Defensa y Justicia (Res)', 'Defensa y Justicia 2', inplace=True)
    df.replace('Defensor Sporting', 'Defensor Sp.', inplace=True)
    df.replace('Def Belgrano VR', 'Defensores Belgrano VR', inplace=True)
    df.replace('Comerciantes Unidos', 'Defensores Unidos', inplace=True)
    df.replace('FC Deisenhofen', 'Deisenhofen', inplace=True)
    df.replace('Democrata FC', 'Democrata SL', inplace=True)
    df.replace('ADO Den Haag', 'Den Haag', inplace=True)
    df.replace('FCV Dender', 'Dender', inplace=True)
    df.replace('Deportivo Cali', 'Dep. Cali', inplace=True)
    df.replace('Deportivo Cuenca', 'Dep. Cuenca', inplace=True)
    df.replace('Deportivo La Coruna II', 'Dep. Fabril', inplace=True)
    df.replace('Deportivo', 'Dep. La Coruna', inplace=True)
    df.replace('Deportivo La Coruna (W)', 'Dep. La Coruna (W)', inplace=True)
    df.replace('Linares', 'Dep. Linares', inplace=True)
    df.replace('Deportivo Merlo', 'Dep. Merlo', inplace=True)
    df.replace('Deportivo Municipal', 'Dep. Municipal', inplace=True)
    df.replace('Once Municipal', 'Dep. Municipal (W)', inplace=True)
    df.replace('Deportivo Pasto', 'Dep. Pasto', inplace=True)
    df.replace('Deportivo Riestra', 'Dep. Riestra', inplace=True)
    df.replace('Deportivo Santo Domingo', 'Dep. Santo Domingo', inplace=True)
    df.replace('Deportivo Tachira', 'Dep. Tachira', inplace=True)
    df.replace('Deportes Rengo Unido', 'Deportes Rengo', inplace=True)
    df.replace('Tolima', 'Deportes Tolima', inplace=True)
    df.replace('Achuapa FC', 'Deportivo Achuapa', inplace=True)
    df.replace('Camioneros', 'Deportivo Camioneros', inplace=True)
    df.replace('CD Maipu', 'Deportivo Maipu', inplace=True)
    df.replace('Deportivo Ocotal', 'Deportivo Mixco', inplace=True)
    df.replace('Deportivo Maldonado', 'Deportivo Moron', inplace=True)
    df.replace('CSD Muniz', 'Deportivo Muniz', inplace=True)
    df.replace('CA Deportivo Paraguayo', 'Deportivo Paraguayo', inplace=True)
    df.replace('Deportivo Riestra (Res)', 'Deportivo Riestra 2', inplace=True)
    df.replace('Deportivo Mictlan', 'Deportivo Rincon', inplace=True)
    df.replace('Deportivo San Pedro', 'Deportivo Santani', inplace=True)
    df.replace('CD Universitario', 'Deportivo Universitario', inplace=True)
    df.replace('Desp Brasil P LTDA U20', 'Desportivo U20', inplace=True)
    df.replace('Detroit City FC', 'Detroit', inplace=True)
    df.replace('Deutsch Mithlinger', 'Deutschlandsberger', inplace=True)
    df.replace('FC Differdange 03', 'Differdange', inplace=True)
    df.replace('Dinamo Bucharest', 'Din. Bucuresti', inplace=True)
    df.replace('Dinamo Minsk', 'Din. Minsk', inplace=True)
    df.replace('Dinamo Tbilisi (Res)', 'Dinamo Tbilisi 2', inplace=True)
    df.replace('Diriangen FC', 'Diriangen', inplace=True)
    df.replace('Djurgardens', 'Djurgarden', inplace=True)
    df.replace('Djurgardens IF DFF (W)', 'Djurgarden (W)', inplace=True)
    df.replace('CS Dock Sud', 'Dock Sud', inplace=True)
    df.replace('SSD Dolomiti Bellunesi', 'Dolomiti Bellunesi', inplace=True)
    df.replace('SV Donau Klagenfurt', 'Donau Klagenfurt', inplace=True)
    df.replace('SR Donaufeld', 'Donaufeld Wien', inplace=True)
    df.replace('FC Dordrecht', 'Dordrecht', inplace=True)
    df.replace('Dorking Wanderers', 'Dorking', inplace=True)
    df.replace('Fc Dornbirn', 'Dornbirn', inplace=True)
    df.replace('SK Senco Doubravka', 'Doubravka', inplace=True)
    df.replace('CA Douglas Haig', 'Douglas Haig', inplace=True)
    df.replace('Dorados', 'Dourados U20', inplace=True)
    df.replace('CD Dragon', 'Dragon', inplace=True)
    df.replace('ASV Drassburg', 'Drassburg', inplace=True)
    df.replace('KF Drita', 'Drita', inplace=True)
    df.replace('Drochtersen-Assel', 'Drochtersen/Assel', inplace=True)
    df.replace('Gualan FC', 'Dublanc FC', inplace=True)
    df.replace('FK Dubocica', 'Dubocica', inplace=True)
    df.replace('NK Dubrava Zagreb', 'Dubrava', inplace=True)
    df.replace('F91 Dudelange', 'Dudelange', inplace=True)
    df.replace('MSV Duisburg U19', 'Duisburg U19', inplace=True)
    df.replace('FK Dukla Praha U19', 'Dukla Prague U19', inplace=True)
    df.replace('Dunajska Streda', 'Dun. Streda', inplace=True)
    df.replace('Dundee', 'Dundee FC', inplace=True)
    df.replace('Dundee B', 'Dundee FC B', inplace=True)
    df.replace('Dundee United B', 'Dundee Utd B', inplace=True)
    df.replace('FC Duren', 'Duren', inplace=True)
    df.replace('Fortuna Dusseldorf', 'Dusseldorf', inplace=True)
    df.replace('Dynamo Kiev', 'Dyn. Kyiv', inplace=True)
    df.replace('SK Dynamo Ceske B', 'Dynamo Dresden', inplace=True)
    df.replace('FC Dziugas', 'Dziugas Telsiai', inplace=True)
    df.replace('EC Sao Jose Porto Alegre', 'EC Sao Jose', inplace=True)
    df.replace('El Nacional', 'EL Nacional', inplace=True)
    df.replace('EVV Echt', 'EVV', inplace=True)
    df.replace('SC East Bengal (Res)', 'East Bengal 2', inplace=True)
    df.replace('E Stirling', 'East Stirlingshire', inplace=True)
    df.replace('Eastbourne', 'Eastbourne Boro', inplace=True)
    df.replace('Eastern Railway S.C', 'Eastern Railway', inplace=True)
    df.replace('Ebbsfleet Utd', 'Ebbsfleet', inplace=True)
    df.replace('VV Eemdijk', 'Eemdijk', inplace=True)
    df.replace('Germania E-L', 'Egestorf-Langreder', inplace=True)
    df.replace('Egnatia Rrogozhine', 'Egnatia', inplace=True)
    df.replace('SD Eibar (W)', 'Eibar (W)', inplace=True)
    df.replace('Eidsvold Turn', 'Eidsvold TF', inplace=True)
    df.replace('FC Eilenburg', 'Eilenburg', inplace=True)
    df.replace('FC Eindhoven', 'Eindhoven FC', inplace=True)
    df.replace('FC Einheit Rudolstadt', 'Einheit Rudolstadt', inplace=True)
    df.replace('Eint Frankfurt II', 'Eintracht Frankfurt II', inplace=True)
    df.replace('SV Eintracht Hohkeppel', 'Eintracht Hohkeppel', inplace=True)
    df.replace('FC Eintracht Rheine', 'Eintracht Rheine', inplace=True)
    df.replace('SD Ejea', 'Ejea', inplace=True)
    df.replace('EIF', 'Ekenas', inplace=True)
    df.replace('FK Ekibastuz', 'Ekibastuz', inplace=True)
    df.replace('El Geish', 'El Gaish', inplace=True)
    df.replace('El Gounah', 'El Gouna', inplace=True)
    df.replace('Ismaily', 'El Ismaily', inplace=True)
    df.replace('Club Atletico el Linqueno', 'El Linqueno', inplace=True)
    df.replace('El Paso Locomotive FC', 'El Paso', inplace=True)
    df.replace('Club El Porvenir (BA)', 'El Porvenir', inplace=True)
    df.replace('Elche', 'Elche', inplace=True)
    df.replace('Elgin City FC', 'Elgin City', inplace=True)
    df.replace('SC Eltersdorf', 'Eltersdorf', inplace=True)
    df.replace('FC Elva', 'Elva', inplace=True)
    df.replace('Kickers Emden', 'Emden', inplace=True)
    df.replace('FV Engers 07', 'Engers', inplace=True)
    df.replace('TUS Ennepetal', 'Ennepetal', inplace=True)
    df.replace('ENPPI', 'Enppi', inplace=True)
    df.replace('FC Epicentr Dunaivtsi', 'Epitsentr', inplace=True)
    df.replace('Rot-Weiss Erfurt', 'Erfurt', inplace=True)
    df.replace('FC Rot Weiss Erfurt U19', 'Erfurt U19', inplace=True)
    df.replace('SV Erlbach', 'Erlbach', inplace=True)
    df.replace('Erokspor A.S', 'Erokspor', inplace=True)
    df.replace('UM Escobedo', 'Escobedo', inplace=True)
    df.replace('Escorpiones FC', 'Escorpiones', inplace=True)
    df.replace('Esporte Clube Futgol U20', 'Esporte Clube Avenida', inplace=True)
    df.replace('TSV Essingen', 'Essingen', inplace=True)
    df.replace('Real Esteli FC', 'Esteli', inplace=True)
    df.replace('Estoril Praia', 'Estoril', inplace=True)
    df.replace('GD Estoril Praia U23', 'Estoril U23', inplace=True)
    df.replace('CD Estradense', 'Estradense', inplace=True)
    df.replace('Club Football Estrela', 'Estrela', inplace=True)
    df.replace('CS Estudiantes San Luis', 'Estudiantes', inplace=True)
    df.replace('Estudiantes', 'Estudiantes L.P.', inplace=True)
    df.replace('Estudiantes de Merida', 'Estudiantes Merida', inplace=True)
    df.replace('Estudiantes Rio ', 'Estudiantes Rio Cuarto', inplace=True)
    df.replace('Etoile Carouge', 'Etoile-Carouge', inplace=True)
    df.replace('Excursionistas(W)', 'Excursionistas (W)', inplace=True)
    df.replace('Fremad Amager', 'F. Amager', inplace=True)
    df.replace('CD Fas', 'FAS', inplace=True)
    df.replace('Melgar', 'FBC Melgar', inplace=True)
    df.replace('Homburg', 'FC 08 Homburg', inplace=True)
    df.replace('Arges Pitesti', 'FC Arges', inplace=True)
    df.replace('KF Ballkani', 'FC Ballkani', inplace=True)
    df.replace('Bihor Oradea', 'FC Bihor', inplace=True)
    df.replace('Botosani', 'FC Botosani', inplace=True)
    df.replace('FC Cartagena', 'FC Cartagena SAD', inplace=True)
    df.replace('Emmen', 'FC Emmen', inplace=True)
    df.replace('Gandzasar FC II', 'FC Gandzasar', inplace=True)
    df.replace('FC Gareji', 'FC Gareji Sagarejo', inplace=True)
    df.replace('FC Halifax Town', 'FC Halifax', inplace=True)
    df.replace('Hermannstadt', 'FC Hermannstadt', inplace=True)
    df.replace('FC Arbaer', 'FC Karbach', inplace=True)
    df.replace('FC Koln', 'FC Koln', inplace=True)
    df.replace('Johvi FC Lokomotiv', 'FC Lokomotivi Tbilisi', inplace=True)
    df.replace('1. FC Monheim', 'FC Monheim', inplace=True)
    df.replace('Porto', 'FC Porto', inplace=True)
    df.replace('Porto B', 'FC Porto B', inplace=True)
    df.replace('Pucioasa', 'FC Pucioasa', inplace=True)
    df.replace('Rapid Bucharest', 'FC Rapid Bucuresti', inplace=True)
    df.replace('CSD Tellioz', 'FC Telavi', inplace=True)
    df.replace('Tulsa Roughnecks FC', 'FC Tulsa', inplace=True)
    df.replace('FC Utd Manchester', 'FC United', inplace=True)
    df.replace('FK Banga II', 'FK Babrungas', inplace=True)
    df.replace('Arsenal Ceska Lipa', 'FK Ceska Lipa', inplace=True)
    df.replace('MFK Frydek-Mistek', 'FK Frydek-Mistek', inplace=True)
    df.replace('KFK Kopavogur', 'FK Komarov', inplace=True)
    df.replace('Liepajas Metalurgs', 'FK Liepaja', inplace=True)
    df.replace('Minija Kretinga', 'FK Minija', inplace=True)
    df.replace('Panevezys', 'FK Panevezys', inplace=True)
    df.replace('FK Panevezys II', 'FK Panevezys 2', inplace=True)
    df.replace('Pardubice', 'FK Pardubice', inplace=True)
    df.replace('FC Pardubice U19', 'FK Pardubice U19', inplace=True)
    df.replace('Sarajevo', 'FK Sarajevo', inplace=True)
    df.replace('Vozdovac', 'FK Vozdovac', inplace=True)
    df.replace('Zorya', 'FK Zorya Luhansk', inplace=True)
    df.replace('FS Metta', 'FS Metta/Lu', inplace=True)
    df.replace('Falcon FC', 'Falcon', inplace=True)
    df.replace('FC Floresti', 'Falesti', inplace=True)
    df.replace('Falkenbergs', 'Falkenberg', inplace=True)
    df.replace('Falu FK', 'Falu', inplace=True)
    df.replace('Flandria', 'Fana', inplace=True)
    df.replace('Farnborough FC', 'Farnborough', inplace=True)
    df.replace('Farsley Celtic', 'Farsley', inplace=True)
    df.replace('Favoritner AC', 'Favoritner', inplace=True)
    df.replace('MOL Vidi', 'Fehervar FC', inplace=True)
    df.replace('CA Fenix', 'Fenix', inplace=True)
    df.replace('Feralpisalo', 'FeralpiSalo', inplace=True)
    df.replace('Ferro Carril Oeste', 'Ferro', inplace=True)
    df.replace('Club Ferro Carril Oeste (W)', 'Ferro (W)', inplace=True)
    df.replace('Ferro Carril Oeste GP', 'Ferro Carril Oeste', inplace=True)
    df.replace('Ferroviaria DE U20', 'Ferroviaria U20', inplace=True)
    df.replace('TESTE', 'Finland U17 (W)', inplace=True)
    df.replace('First Vienna Fc 1894', 'First Vienna', inplace=True)
    df.replace('FK Buducnost Podgorica', 'Fk Buducnost Podgorica', inplace=True)
    df.replace('Flamengo', 'Flamengo RJ', inplace=True)
    df.replace('Flamengo U20', 'Flamengo RJ U20', inplace=True)
    df.replace('Fleetwood Town', 'Fleetwood', inplace=True)
    df.replace('Floy Flekkeroy', 'Flekkeroy', inplace=True)
    df.replace('Tallinna FC Flora', 'Flora', inplace=True)
    df.replace('Flora Tallinn II', 'Flora U21', inplace=True)
    df.replace('FC Floresti', 'Floresti', inplace=True)
    df.replace('Folkestone Invicta', 'Folkestone', inplace=True)
    df.replace('Forfar', 'Forfar Athletic', inplace=True)
    df.replace('Fortaleza FC U20', 'Fortaleza U20', inplace=True)
    df.replace('Fortuna Dusseldorf U19', 'Fortuna Dusseldorf', inplace=True)
    df.replace('SV Fortuna Regensburg', 'Fortuna Regensburg', inplace=True)
    df.replace('BK Forward', 'Forward', inplace=True)
    df.replace('Forward Madison FC', 'Forward Madison', inplace=True)
    df.replace('Dongguan Guanlian', 'Foshan Nanshi', inplace=True)
    df.replace('AA Francana', 'Francana', inplace=True)
    df.replace('Fredrikstad II', 'Fredrikstad 2', inplace=True)
    df.replace('SGV Freiberg', 'Freiberg', inplace=True)
    df.replace('SC Freiburg U19', 'Freiburg U19', inplace=True)
    df.replace('Frenstat Pod Radhostem', 'Frenstat p. R.', inplace=True)
    df.replace('Frydlant Nad Ostravici', 'Frydlant n. O.', inplace=True)
    df.replace('Fujieda Myfc', 'Fujieda MYFC', inplace=True)
    df.replace('Fujieda MYFC', 'Fujieda Myfc', inplace=True)
    df.replace('TSV Lehnerz', 'Fulda-Lehnerz', inplace=True)
    df.replace('Greuther Furth II', 'Furth II', inplace=True)
    df.replace('FC Futura', 'Futura', inplace=True)
    df.replace('Fylkir Reykjavik (W)', 'Fylkir (W)', inplace=True)
    df.replace('Go Ahead Eagles', 'G.A. Eagles', inplace=True)
    df.replace('GBK', 'GBK Kokkola', inplace=True)
    df.replace('Gks Jastrzebie', 'GKS Jastrzebie', inplace=True)
    df.replace('Gosk Gabela', 'GOSK Gabela', inplace=True)
    df.replace('CD Gualberto Villarroel', 'GV San Jose', inplace=True)
    df.replace('Tottori', 'Gainare Tottori', inplace=True)
    df.replace('Galway Utd', 'Galway', inplace=True)
    df.replace('Galway WFC (W)', 'Galway United (W)', inplace=True)
    df.replace('G-Osaka', 'Gamba Osaka', inplace=True)
    df.replace('Gangneung City', 'Gangneung', inplace=True)
    df.replace('Shaoxing Shangyu Pterosaur', 'Ganzhou Ruishi', inplace=True)
    df.replace('Garliava Kaunas', 'Garliava', inplace=True)
    df.replace('IK Gauthiod', 'Gauthiod', inplace=True)
    df.replace('DJK Gebenbach', 'Gebenbach', inplace=True)
    df.replace('Club General Caballero JLM', 'General Caballero', inplace=True)
    df.replace('Club General Caballero JLM', 'General Caballero JLM', inplace=True)
    df.replace('CD General Velasquez', 'General Velasquez', inplace=True)
    df.replace('Genesis Huracan', 'Genesis', inplace=True)
    df.replace('Racing Genk B', 'Genk U23', inplace=True)
    df.replace('George Telegraph SC', 'George Telegrapher', inplace=True)
    df.replace('Ratingen SV Germania', 'Germania Ratingen', inplace=True)
    df.replace('Grotta (W)', 'Germany (W)', inplace=True)
    df.replace('CA Germinal', 'Germinal', inplace=True)
    df.replace('Geylang International', 'Geylang', inplace=True)
    df.replace('PAS Giannina', 'Giannina', inplace=True)
    df.replace('FC Giessen', 'Giessen', inplace=True)
    df.replace('FC Gifu', 'Gifu', inplace=True)
    df.replace('Sporting Gijon', 'Gijon', inplace=True)
    df.replace('Sporting Gijon B', 'Gijon B', inplace=True)
    df.replace('Gimhae City', 'Gimhae', inplace=True)
    df.replace('Gimnasia Conc del Uruguay', 'Gimnasia E.R.', inplace=True)
    df.replace('Gimnasia La Plata', 'Gimnasia L.P.', inplace=True)
    df.replace('Gimnasia La Plata (Res)', 'Gimnasia L.P. 2', inplace=True)
    df.replace('Club Gimnasia y Tiro', 'Gimnasia y Tiro', inplace=True)
    df.replace('RS Gimnastica', 'Gimnastic', inplace=True)
    df.replace('Gimnastica Segoviana CF', 'Gimnastica Segoviana', inplace=True)
    df.replace('Gimpo Citizen', 'Gimpo FC', inplace=True)
    df.replace('Kitakyushu', 'Giravanz Kitakyushu', inplace=True)
    df.replace('FC Giugliano', 'Giugliano', inplace=True)
    df.replace('Grotta (W)', 'Glentoran (W)', inplace=True)
    df.replace('Globo FC RN', 'Globo', inplace=True)
    df.replace('SV Gloggnitz', 'Gloggnitz', inplace=True)
    df.replace('FC Goa', 'Goa', inplace=True)
    df.replace('Goczalkowice-Zdroj', 'Goczalkowice Zdroj', inplace=True)
    df.replace('LKS Goczalkowice-Zdroj', 'Goczalkowice-Zdroj', inplace=True)
    df.replace('Godoy Cruz (Res)', 'Godoy Cruz 2', inplace=True)
    df.replace('SV Gonsenheim', 'Gonsenheim', inplace=True)
    df.replace('Goppinger SV', 'Goppinger', inplace=True)
    df.replace('HNK Gorica', 'Gorica', inplace=True)
    df.replace('Gornik Leczna (W)', 'Gornik Leczna', inplace=True)
    df.replace('KS Gornik Zabrze II', 'Gornik Zabrze II', inplace=True)
    df.replace('GOSK Gabela', 'Gosk Gabela', inplace=True)
    df.replace('IFK Goteborg', 'Goteborg', inplace=True)
    df.replace('Gottne IF', 'Gottne', inplace=True)
    df.replace('De Graafschap', 'De Graafschap', inplace=True)
    df.replace('Granada', 'Granada CF', inplace=True)
    df.replace('FC Grand-Saconnex', 'Grand-Saconnex', inplace=True)
    df.replace('Grasshoppers Zurich', 'Grasshoppers', inplace=True)
    df.replace('Atletico Grau', 'Grau', inplace=True)
    df.replace('Municipal Grecia', 'Grecia', inplace=True)
    df.replace('Greenville Triumph SC', 'Greenville', inplace=True)
    df.replace('Greifswalder SV 04', 'Greifswald', inplace=True)
    df.replace('Gremio Novorizo U20', 'Gremio Novorizontino U20', inplace=True)
    df.replace('Gremio FBPA U20', 'Gremio U20', inplace=True)
    df.replace('SC Grobina', 'Grobina', inplace=True)
    df.replace('SV Grodig', 'Grodig', inplace=True)
    df.replace('Pogon Grodzisk Mazowiecki', 'Grodzisk M.', inplace=True)
    df.replace('FC Groningen', 'Groningen', inplace=True)
    df.replace('Grorud IL', 'Grorud', inplace=True)
    df.replace('SG Sonnenhof', 'Grossaspach', inplace=True)
    df.replace('TSV Grunwald', 'Grunwald', inplace=True)
    df.replace('Gryf Slupsk SA', 'Gryf Slupsk', inplace=True)
    df.replace('Guadalajara Chivas', 'Guadalajara Chivas', inplace=True)
    df.replace('Guadalajara', 'Guadalajara', inplace=True)
    df.replace('Guadalajara (W)', 'Guadalajara Chivas (W)', inplace=True)
    df.replace('Guadalupe FC', 'Guadalupe', inplace=True)
    df.replace('Guairena', 'Guairena FC', inplace=True)
    df.replace('Gualaceo SC', 'Gualaceo', inplace=True)
    df.replace('AD Guanacasteca', 'Guanacasteca', inplace=True)
    df.replace('Guangdong GZ-Power FC', 'Guangdong GZ-Power', inplace=True)
    df.replace('Guangxi Baoyun', 'Guangxi Pingguo Haliao', inplace=True)
    df.replace('Guarani SP U20', 'Guarani U20', inplace=True)
    df.replace('FSV Gutersloh 2009 (W)', 'Gutersloh (W)', inplace=True)
    df.replace('Gutierrez', 'Gutierrez Mendoza', inplace=True)
    df.replace('GH & NP', 'Gyeongju Hydro & Nucle', inplace=True)
    df.replace('Gyeongju Hydro & NP', 'Gyeongju KHNP', inplace=True)
    df.replace('Gyori', 'Gyor', inplace=True)
    df.replace('Gzira United FC', 'Gzira', inplace=True)
    df.replace('H & W Welders', 'H&W Welders', inplace=True)
    df.replace('Hapoel Beer Sheva', 'H. Beer Sheva', inplace=True)
    df.replace('Ironi R Has', 'H. Ironi Rishon', inplace=True)
    df.replace('MSK Povazska Bystrica', 'HA Banska Bystrica', inplace=True)
    df.replace('SV HBC', 'HBC', inplace=True)
    df.replace('HJK Helsinki', 'HJK', inplace=True)
    df.replace('HJK Helsinki (W)', 'HJK (W)', inplace=True)
    df.replace('HJS Akatemia', 'HJS', inplace=True)
    df.replace('Hjs Akatemia', 'HJS Akatemia', inplace=True)
    df.replace('Laanemaa Haapsalu', 'Haapsalu', inplace=True)
    df.replace('Hainan Star', 'Haikou Mingcheng', inplace=True)
    df.replace('Halesowen Town', 'Halesowen', inplace=True)
    df.replace('VFL Halle', 'Halle', inplace=True)
    df.replace('BSV Halle-Ammendorf', 'Halle-Ammendorf', inplace=True)
    df.replace('Hallescher FC', 'Hallescher', inplace=True)
    df.replace('Halmstads', 'Halmstad', inplace=True)
    df.replace('HamKam 2', 'Ham-Kam 2', inplace=True)
    df.replace('Ham-Kam', 'HamKam', inplace=True)
    df.replace('Hamburg II', 'Hamburger SV II', inplace=True)
    df.replace('Hampton and Richmond', 'Hampton & Richmond', inplace=True)
    df.replace('Hamrun Spartans FC', 'Hamrun', inplace=True)
    df.replace('SpVgg Hankofen-Hailing', 'Hankofen-Hailing', inplace=True)
    df.replace('Hannover 96 U19', 'Hannover U19', inplace=True)
    df.replace('FC Hansa Rostock U19', 'Hansa Rostock U19', inplace=True)
    df.replace('Hanthawaddy United FC', 'Hantharwady Utd', inplace=True)
    df.replace('Hapoel Eran Hadera', 'Hapoel Hadera', inplace=True)
    df.replace('Harborough Town', 'Harborough', inplace=True)
    df.replace('HHC Hardenberg', 'Hardenberg', inplace=True)
    df.replace('TuRa Harksheide', 'Harksheide', inplace=True)
    df.replace('Harrogate Town', 'Harrogate', inplace=True)
    df.replace('Hartford Athletic FC', 'Hartford Athletic', inplace=True)
    df.replace('Havant and W', 'Havant & (W)', inplace=True)
    df.replace('Haverfordwest County', 'Haverfordwest', inplace=True)
    df.replace('MFK Havirov', 'Havirov', inplace=True)
    df.replace('Slovan Havlickuv Brod', 'Havlickuv Brod', inplace=True)
    df.replace('Hearts FC II', 'Hearts B', inplace=True)
    df.replace('Hegelmann Litauen', 'Hegelmann', inplace=True)
    df.replace('Hegelmann Litauen B', 'Hegelmann Litauen 2', inplace=True)
    df.replace('FC Heidenheim', 'Heidenheim', inplace=True)
    df.replace('Heilongjiang Lava Spring', 'Heilongjiang Ice City', inplace=True)
    df.replace('HIK Hellerup', 'Hellerup', inplace=True)
    df.replace('Helmond Sport', 'Helmond', inplace=True)
    df.replace('Helsingborgs', 'Helsingborg', inplace=True)
    df.replace('FC Helsingor', 'Helsingor', inplace=True)
    df.replace('JS Hercules', 'Hercules', inplace=True)
    df.replace('Cs Herediano', 'Herediano', inplace=True)
    df.replace('Hereford FC', 'Hereford', inplace=True)
    df.replace('Herrera FC', 'Herrera', inplace=True)
    df.replace('Hertford Town FC', 'Hertford', inplace=True)
    df.replace('FC Hertha 03 Zehlendorf', 'Hertha Zehlendorf', inplace=True)
    df.replace('Swift Hesperange', 'Hesperange', inplace=True)
    df.replace('VfB 03 Hilden', 'Hilden', inplace=True)
    df.replace('Hillerod Fodbold', 'Hillerod', inplace=True)
    df.replace('Hastings United', 'Hills United', inplace=True)
    df.replace('TJ Unie Hlubina', 'Hlubina', inplace=True)
    df.replace('RSM Hodonin', 'Hodonin', inplace=True)
    df.replace('TSG Hoffenheim U19', 'Hoffenheim U19', inplace=True)
    df.replace('VfB Hohenems', 'Hohenems', inplace=True)
    df.replace('SV Hohenlimburg 1910', 'Hohenlimburg', inplace=True)
    df.replace('Sapporo', 'Hokkaido Consadole Sapporo', inplace=True)
    df.replace('Holzheimer SG', 'Holzheimer', inplace=True)
    df.replace('Honka Akatemia', 'Honka', inplace=True)
    df.replace('FC Honka (W)', 'Honka (W)', inplace=True)
    df.replace('SV Horn', 'Horn', inplace=True)
    df.replace('FK Bestrent Horna Krupa', 'Horna Krupa', inplace=True)
    df.replace('SK Horovice', 'Horovice', inplace=True)
    df.replace('AC Horsens', 'Horsens', inplace=True)
    df.replace('US Hostert', 'Hostert', inplace=True)
    df.replace('Sokol Hostoun', 'Hostoun', inplace=True)
    df.replace('Hottur', 'Hottur / Huginn', inplace=True)
    df.replace('Hougang Utd', 'Hougang', inplace=True)
    df.replace('Houston Dynamo II', 'Houston Dynamo 2', inplace=True)
    df.replace('TJ Slovan Hradek nad Nisou', 'Hradek nad Nisou', inplace=True)
    df.replace('SK Hrebec', 'Hrebec', inplace=True)
    df.replace('Hubei Chufeng Heli', 'Hubei Istar', inplace=True)
    df.replace('Hudiksvalls FF', 'Hudiksvall', inplace=True)
    df.replace('Atletico Huila', 'Huila', inplace=True)
    df.replace('Humaita AC', 'Humaita', inplace=True)
    df.replace('AFC Humpolec', 'Humpolec', inplace=True)
    df.replace('Hunan Billows FC', 'Hunan Billows', inplace=True)
    df.replace('FC Hunedoara', 'Hunedoara', inplace=True)
    df.replace('Genesis Huracan', 'Huracan', inplace=True)
    df.replace('CA Huracan (W)', 'Huracan (W)', inplace=True)
    df.replace('FC Hurth', 'Hurth', inplace=True)
    df.replace('Hvidovre', 'Hvidovre IF', inplace=True)
    df.replace('Hviti Riddarinn', 'Hviti', inplace=True)
    df.replace('Hwaseong FC', 'Hwaseong', inplace=True)
    df.replace('Brommapojkarna (W)', 'IF Brommapojkarna (W)', inplace=True)
    df.replace('Skovde', 'IFK Skovde', inplace=True)
    df.replace('Ijsselmeervogels', 'IJsselmeervogels', inplace=True)
    df.replace('FK IMT Novi Beograd', 'IMT Novi Beograd', inplace=True)
    df.replace('FC Iberia 1999', 'Iberia 1999', inplace=True)
    df.replace('United Sports Club', 'Ibis Sport Club', inplace=True)
    df.replace('Ibrachina FC U20', 'Ibrachina U20', inplace=True)
    df.replace('FK Igman Konjic', 'Igman K.', inplace=True)
    df.replace('AD Iguatu', 'Iguatu', inplace=True)
    df.replace('Ilkeston FC', 'Ilkeston', inplace=True)
    df.replace('IBV (W)', 'Ilves (W)', inplace=True)
    df.replace('Tampereen Ilves II', 'Ilves 2', inplace=True)
    df.replace('Ilves Kissat', 'Ilves-Kissat', inplace=True)
    df.replace('FC Imabari', 'Imabari', inplace=True)
    df.replace('ACS Inainte Modelu', 'Inainte Modelu', inplace=True)
    df.replace('Incheon Utd', 'Incheon', inplace=True)
    df.replace('Independiente Juniors', 'Ind. Juniors', inplace=True)
    df.replace('Ind Medellin', 'Ind. Medellin', inplace=True)
    df.replace('Independiente Rivadavia', 'Ind. Rivadavia', inplace=True)
    df.replace('Indep Rivadavia (Res)', 'Ind. Rivadavia 2', inplace=True)
    df.replace('Independiente (Ecu)', 'Ind. del Valle', inplace=True)
    df.replace('CA Independiente', 'Independiente', inplace=True)
    df.replace('CA Independiente (W)', 'Independiente (W)', inplace=True)
    df.replace('Atletico Independiente', 'Independiente FBC', inplace=True)
    df.replace('Petrolero', 'Independiente Petrolero', inplace=True)
    df.replace('Inhulets Petrove', 'Inhulets', inplace=True)
    df.replace('Inter Club Escaldes', 'Inter Escaldes', inplace=True)
    df.replace('Inter Miami CF', 'Inter Miami', inplace=True)
    df.replace('Internacional de Palmira', 'Inter Palmira', inplace=True)
    df.replace('Universidad San Carlos', 'Inter San Carlos', inplace=True)
    df.replace('FC Inter', 'Inter Turku', inplace=True)
    df.replace('FC Inter 2', 'Inter Turku 2', inplace=True)
    df.replace('CD Hermanos Colmenarez', 'Inter de Barinas', inplace=True)
    df.replace('Inter Limeira', 'Inter de Limeira', inplace=True)
    df.replace('Inter Limeira U20', 'Internacional de Limeira U20', inplace=True)
    df.replace('Inverness CT', 'Inverness', inplace=True)
    df.replace('Ipatinga FC', 'Ipatinga', inplace=True)
    df.replace('Ipatinga FC U20', 'Ipatinga U20', inplace=True)
    df.replace('Ipora EC', 'Ipora', inplace=True)
    df.replace('Ipswich', 'Ipswich', inplace=True)
    df.replace('Hapoel Rishon Lezion', 'Ironi R Has', inplace=True)
    df.replace('Irvine Zeta FC', 'Irvine Zeta', inplace=True)
    df.replace('Ishoj IF', 'Ishoj', inplace=True)
    df.replace('FC Ismaning', 'Ismaning', inplace=True)
    df.replace('Istanbulspor', 'Istanbulspor AS', inplace=True)
    df.replace('NK Istra', 'Istra 1961', inplace=True)
    df.replace('Itabuna BA', 'Itabuna', inplace=True)
    df.replace('Ituano FC U20', 'Ituano U20', inplace=True)
    df.replace('CA Ituzaingo', 'Ituzaingo', inplace=True)
    df.replace('Iwaki SC', 'Iwaki', inplace=True)
    df.replace('CD Izarra', 'Izarra', inplace=True)
    df.replace('JJK', 'JJK Jyvaskyla', inplace=True)
    df.replace('JPS', 'JPS Jyvaskyla', inplace=True)
    df.replace('JaPS/47', 'JaPS 2', inplace=True)
    df.replace('FK Jablonec', 'Jablonec', inplace=True)
    df.replace('Jacuipense BA', 'Jacuipense', inplace=True)
    df.replace('Jagiellonia Bialystock', 'Jagiellonia', inplace=True)
    df.replace('Jamshedpur FC', 'Jamshedpur', inplace=True)
    df.replace('FC Jarfalla', 'Jarfalla', inplace=True)
    df.replace('FK Javor Ivanjica', 'Javor', inplace=True)
    df.replace('FC Jazz', 'Jazz Pori', inplace=True)
    df.replace('SSV Jeddeloh', 'Jeddeloh', inplace=True)
    df.replace('Rudar Prijedor', 'Jedinstvo', inplace=True)
    df.replace('FK Jedinstvo Ub', 'Jedinstvo U.', inplace=True)
    df.replace('FK Jelgava', 'Jelgava', inplace=True)
    df.replace('Carl Zeiss Jena', 'Jena', inplace=True)
    df.replace('Jeonbuk Motors', 'Jeonbuk', inplace=True)
    df.replace('Jeonnam Dragons', 'Jeonnam', inplace=True)
    df.replace('Fk Jezero', 'Jezero', inplace=True)
    df.replace('Jiangxi Dark Horse Junior', 'Jiangxi Dark Horse', inplace=True)
    df.replace('Jiangxi Liansheng', 'Jiangxi Lushan', inplace=True)
    df.replace('Vysocina Jihlava', 'Jihlava', inplace=True)
    df.replace('FC Vysocina Jihlava U19', 'Jihlava U19', inplace=True)
    df.replace('Johor Darul Takzim', 'Johor DT', inplace=True)
    df.replace('Jong AZ Alkmaar', 'Jong AZ', inplace=True)
    df.replace('Jong Ajax Amsterdam', 'Jong Ajax', inplace=True)
    df.replace('Jong PSV Eindhoven', 'Jong PSV', inplace=True)
    df.replace('Jong FC Utrecht', 'Jong Utrecht', inplace=True)
    df.replace('Jonkopings Sodra', 'Jonkoping', inplace=True)
    df.replace('Jose Bonifacio U20', 'Jose Bonifacio EC U20', inplace=True)
    df.replace('Juan Pablo II College', 'Juan Pablo II', inplace=True)
    df.replace('FC Juarez', 'Juarez', inplace=True)
    df.replace('FC Juarez (W)', 'Juarez (W)', inplace=True)
    df.replace('Juazeirense BA', 'Juazeirense', inplace=True)
    df.replace('VFL Juchen-Garzwei', 'Juchen-Garzweiler', inplace=True)
    df.replace('Junior FC Barranquilla', 'Junior', inplace=True)
    df.replace('Junior FC Barranquilla', 'Junior FC Barranquilla', inplace=True)
    df.replace('Juventud De Las Piedras', 'Juventud', inplace=True)
    df.replace('C J Antoniana', 'Juventud Antoniana', inplace=True)
    df.replace('Juventud Unida San Miguel', 'Juventud Unida S. M.', inplace=True)
    df.replace('Team K League', 'K-League Stars', inplace=True)
    df.replace('Lierse', 'K. Lierse S.K.', inplace=True)
    df.replace('FK Gostivar', 'KF Gostivar', inplace=True)
    df.replace('Fjardabyggd', 'KFA', inplace=True)
    df.replace('KFG', 'KFG Gardabaer', inplace=True)
    df.replace('KFUM Oslo', 'KFUM Oslo', inplace=True)
    df.replace('KPV', 'KPV Kokkola', inplace=True)
    df.replace('Wieczysta Krakow', 'KS Wieczysta Krakow', inplace=True)
    df.replace('Yellow-Red Mechelen', 'KV Mechelen', inplace=True)
    df.replace('UN Kaerjeng 97', 'Kaerjeng', inplace=True)
    df.replace('FK Kaisar', 'Kaisar Kyzylorda', inplace=True)
    df.replace('Kalighat MS', 'Kalighat', inplace=True)
    df.replace('Nomme Kalju', 'Kalju', inplace=True)
    df.replace('Kalmar FF', 'Kalmar', inplace=True)
    df.replace('SC Kalsdorf', 'Kalsdorf', inplace=True)
    df.replace('Kamatamare Sanuki', 'Kamatamare', inplace=True)
    df.replace('Kapaz Ganja', 'Kapaz', inplace=True)
    df.replace('KSV 1919', 'Kapfenberg', inplace=True)
    df.replace('FC Karbach', 'Karbach', inplace=True)
    df.replace('Karlbergs BK', 'Karlbergs', inplace=True)
    df.replace('Karlsruhe', 'Karlsruher SC', inplace=True)
    df.replace('IF Karlstad', 'Karlstad', inplace=True)
    df.replace('Drogheda United U20', 'Karonga United', inplace=True)
    df.replace('Karpaty', 'Karpaty Lviv', inplace=True)
    df.replace('MFK Karvina', 'Karvina', inplace=True)
    df.replace('MFK Karvina B', 'Karvina B', inplace=True)
    df.replace('Kasetsart FC', 'Kasetsart', inplace=True)
    df.replace('Kashiwa', 'Kashima', inplace=True)
    df.replace('Kashima', 'Kashima Antlers', inplace=True)
    df.replace('Kashiwa', 'Kashiwa Reysol', inplace=True)
    df.replace('Hessen Kassel', 'Kassel', inplace=True)
    df.replace('FK Kauno Zalgiris', 'Kauno Zalgiris', inplace=True)
    df.replace('FK Kauno Zalgiris 2', 'Kauno Zalgiris 2', inplace=True)
    df.replace('Kawasaki', 'Kawasaki Frontale', inplace=True)
    df.replace('Kazincbarcika', 'Kazincbarcikai', inplace=True)
    df.replace('Kazma Sc', 'Kazma SC', inplace=True)
    df.replace('Kecskemeti', 'Kecskemeti TE', inplace=True)
    df.replace('Klaksvikar Itrottarfelag', 'Klaksvik', inplace=True)
    df.replace('Kelantan United', 'Kelantan DNFC', inplace=True)
    df.replace('Kerry FC', 'Kerry', inplace=True)
    df.replace('PKK-U', 'Keski-Uusimaa', inplace=True)
    df.replace('Kettering Town FC', 'Kettering', inplace=True)
    df.replace('Khan Tengry', 'Khan Tengri', inplace=True)
    df.replace('Kidderpore SC', 'Kidderpore', inplace=True)
    df.replace('FC Kiffen', 'Kiffen', inplace=True)
    df.replace('Kilbarrack United', 'Kilbarrack Utd', inplace=True)
    df.replace('CA Kimberley', 'Kimberley', inplace=True)
    df.replace('Kings Lynn', 'King’s Lynn', inplace=True)
    df.replace('Hapoel Kiryat Shmona', 'Kiryat Shmona', inplace=True)
    df.replace('Kitchee SC', 'Kitchee', inplace=True)
    df.replace('FC Kitzbuhel', 'Kitzbuhel', inplace=True)
    df.replace('Klubi-04', 'Klubi 04', inplace=True)
    df.replace('Mks Kluczbork', 'Kluczbork', inplace=True)
    df.replace('HB Koge', 'Koge', inplace=True)
    df.replace('Kolding IF (W)', 'KoldingQ (W)', inplace=True)
    df.replace('FC Kolkheti Poti', 'Kolkheti 1913', inplace=True)
    df.replace('1. FC Koln (W)', 'Koln (W)', inplace=True)
    df.replace('FC Koln II', 'Koln II', inplace=True)
    df.replace('FC Koln U19', 'Koln U19', inplace=True)
    df.replace('Kolos Kovalyovka', 'Kolos Kovalivka', inplace=True)
    df.replace('Slavoj Kolovec', 'Kolovec', inplace=True)
    df.replace('Kolubara Lazarevac', 'Kolubara', inplace=True)
    df.replace('KFC Komarno', 'Komarno', inplace=True)
    df.replace('IK Kongahalla', 'Kongahalla', inplace=True)
    df.replace('Kongsvinger II', 'Kongsvinger 2', inplace=True)
    df.replace('TuS Blau-Weis Konigsdorf', 'Konigsdorf', inplace=True)
    df.replace('HK Kopavogur', 'Kopavogur', inplace=True)
    df.replace('TSV Kornburg', 'Kornburg', inplace=True)
    df.replace('Korneuburg ASC', 'Korneuburg', inplace=True)
    df.replace('FC Kosice', 'Kosice', inplace=True)
    df.replace('TSV Kottern', 'Kottern-St. Mang', inplace=True)
    df.replace('Kozarmisleny', 'Kozarmisleny SE', inplace=True)
    df.replace('Kremser SC', 'Kremser', inplace=True)
    df.replace('Kristianstads', 'Kristianstad', inplace=True)
    df.replace('Kristiansund BK II', 'Kristiansund 2', inplace=True)
    df.replace('FK Krnov', 'Krnov', inplace=True)
    df.replace('H Slavia Kromeriz', 'Kromeriz', inplace=True)
    df.replace('Levski Krumovgrad', 'Krumovgrad', inplace=True)
    df.replace('Kryvbas Krivyi Rih', 'Kryvbas', inplace=True)
    df.replace('KuPs (W)', 'KuPS (W)', inplace=True)
    df.replace('Kuala Lumpur', 'Kuala Lumpur City', inplace=True)
    df.replace('Kuching FA', 'Kuching City FC', inplace=True)
    df.replace('Kungsangens IF', 'Kungsangen', inplace=True)
    df.replace('FC Kuressaare II', 'Kuressaare U21', inplace=True)
    df.replace('FC Kurim', 'Kurim', inplace=True)
    df.replace('Thespakusatsu Gunma', 'Kusatsu', inplace=True)
    df.replace('FK Kyzyl-Zhar', 'Kyzylzhar', inplace=True)
    df.replace('Tatran Lip Mikulas', 'L. Mikulas', inplace=True)
    df.replace('LR Vicenza Virtus', 'L.R. Vicenza', inplace=True)
    df.replace('SPG Lask Amateure', 'LASK', inplace=True)
    df.replace('LDU', 'LDU Quito', inplace=True)
    df.replace('LA Fiorita', 'La Fiorita', inplace=True)
    df.replace('Deportivo La Guaira', 'La Guaira', inplace=True)
    df.replace('La Luz FC', 'La Luz', inplace=True)
    df.replace('Landstraber AC Inter', 'Lac Inter', inplace=True)
    df.replace('Deportivo Laferrere', 'Laferrere', inplace=True)
    df.replace('SV Lafnitz', 'Lafnitz', inplace=True)
    df.replace('Reipas', 'Lahden Reipas', inplace=True)
    df.replace('Lancaster City', 'Lancaster', inplace=True)
    df.replace('FC Grand-Lancy', 'Lancy', inplace=True)
    df.replace('TSV Landsberg', 'Landsberg', inplace=True)
    df.replace('Landvetter IS', 'Landvetter', inplace=True)
    df.replace('UP Langreo', 'Langreo', inplace=True)
    df.replace('CA Lanus (Res)', 'Lanus 2', inplace=True)
    df.replace('Tj Sokol Lanzhot', 'Lanzhot', inplace=True)
    df.replace('CD Laredo', 'Laredo', inplace=True)
    df.replace('Las Vegas Lights FC', 'Las Vegas Lights', inplace=True)
    df.replace('Lausanne Sport II', 'Lausanne II', inplace=True)
    df.replace('Stade Lausanne-Ouchy', 'Lausanne Ouchy', inplace=True)
    df.replace('Lautaro de Buin', 'Lautaro', inplace=True)
    df.replace('LD Alajuelense', 'Ld Alajuelense', inplace=True)
    df.replace('Leandro N Alem', 'Leandro N. Alem', inplace=True)
    df.replace('KKS Lech Poznan II', 'Lech Poznan II', inplace=True)
    df.replace('Gornik Leczna', 'Leczna', inplace=True)
    df.replace('CD Leganes II', 'Leganes B', inplace=True)
    df.replace('Legia Warsaw', 'Legia', inplace=True)
    df.replace('FC Legia Warsaw II', 'Legia II', inplace=True)
    df.replace('FC Legnago', 'Legnago Salus', inplace=True)
    df.replace('Miedz Legnica', 'Legnica', inplace=True)
    df.replace('Leiknir R', 'Leiknir', inplace=True)
    df.replace('Lentigione Calcio', 'Lentigione', inplace=True)
    df.replace('DSV Leoben', 'Leoben', inplace=True)
    df.replace('SV Leobendorf', 'Leobendorf', inplace=True)
    df.replace('Leones FC', 'Leones', inplace=True)
    df.replace('CD Leones del Norte', 'Leones del Norte', inplace=True)
    df.replace('Oud-Heverlee Leuven', 'Leuven', inplace=True)
    df.replace('Oud-Heverlee Leuven (W)', 'Leuven (W)', inplace=True)
    df.replace('FCI Tallinn', 'Levadia', inplace=True)
    df.replace('Levadia Tallinn II', 'Levadia U21', inplace=True)
    df.replace('Treaty United U20', 'Levante U20', inplace=True)
    df.replace('PFC Levski Sofia', 'Levski Sofia', inplace=True)
    df.replace('Lexington SC', 'Lexington', inplace=True)
    df.replace('Shenyang Urban FC', 'Liaoning Tieren', inplace=True)
    df.replace('Slovan Liberec', 'Liberec', inplace=True)
    df.replace('AD Municipal Liberia', 'Liberia', inplace=True)
    df.replace('Libertad FC', 'Libertad', inplace=True)
    df.replace('Libertad', 'Libertad Asuncion', inplace=True)
    df.replace('FC Libertad Gran Mamoré', 'Libertad Gran Mamore', inplace=True)
    df.replace('Lichtenberg 47', 'Lichtenberg', inplace=True)
    df.replace('Lidkopings FK', 'Lidkoping', inplace=True)
    df.replace('FC Liefering', 'Liefering', inplace=True)
    df.replace('Lillestrom SK 2', 'Lillestrom 2', inplace=True)
    df.replace('Deportes Limache', 'Limache', inplace=True)
    df.replace('Limavady United', 'Limavady', inplace=True)
    df.replace('Linares Deportivo', 'Linares', inplace=True)
    df.replace('CSD Liniers de Ciudad Evita', 'Liniers', inplace=True)
    df.replace('Home Utd', 'Lion City', inplace=True)
    df.replace('SV Lippstadt', 'Lippstadt', inplace=True)
    df.replace('Lisburn (W)', 'Lisburn Ladies (W)', inplace=True)
    df.replace('Liverpool Montevideo', 'Liverpool M.', inplace=True)
    df.replace('Livyi Bereh', 'Livyi Bereg', inplace=True)
    df.replace('Deportivo Llacuabamba', 'Llacuabamba', inplace=True)
    df.replace('Llanelli Town', 'Llanelli', inplace=True)
    df.replace('Llaneros FC', 'Llaneros', inplace=True)
    df.replace('Barry Town Utd', 'Llantwit Major', inplace=True)
    df.replace('FC Lokomotivi Tbilisi', 'Loco. Tbilisi', inplace=True)
    df.replace('IF Lodde', 'Lodde', inplace=True)
    df.replace('TuS BW Lohne', 'Lohne', inplace=True)
    df.replace('Lokomotiv Plovdiv', 'Lok. Plovdiv', inplace=True)
    df.replace('Lokomotiv Sofia', 'Lok. Sofia', inplace=True)
    df.replace('FK Olimpik Tashkent', 'Lok. Tashkent', inplace=True)
    df.replace('Lokomotiva', 'Lok. Zagreb', inplace=True)
    df.replace('SC Lokeren-Temse', 'Lokeren-Temse', inplace=True)
    df.replace('Lokomotiva Zvolen', 'Lokomotiv Oslo', inplace=True)
    df.replace('Lokomotiv Leipzig', 'Lokomotive Leipzig', inplace=True)
    df.replace('Lommel', 'Lommel SK', inplace=True)
    df.replace('Long Eaton United', 'Long Eaton', inplace=True)
    df.replace('LA Galaxy', 'Los Angeles Galaxy', inplace=True)
    df.replace('CD Los Chankas', 'Los Chankas', inplace=True)
    df.replace('Sportfreunde Lotte', 'Lotte', inplace=True)
    df.replace('Loudoun United FC', 'Loudoun', inplace=True)
    df.replace('Louisville FC', 'Louisville City', inplace=True)
    df.replace('VFB Lubeck II', 'Lubeck II', inplace=True)
    df.replace('MFK Stara Lubovna', 'Lubovna', inplace=True)
    df.replace('FSV 63 Luckenwalde', 'Luckenwalde', inplace=True)
    df.replace('Lucksta IF', 'Lucksta', inplace=True)
    df.replace('FC Lugano II', 'Lugano II', inplace=True)
    df.replace('CD Luis Angel Firpo', 'Luis Angel Firpo', inplace=True)
    df.replace('Lunds BK', 'Lunds', inplace=True)
    df.replace('Lusitania Futebol Clube', 'Lusitania FC', inplace=True)
    df.replace('MFk Skalica', 'MFK Skalica', inplace=True)
    df.replace('MVV Maastricht', 'Maastricht', inplace=True)
    df.replace('Maccabi Bnei Reiyne', 'Maccabi Bnei Raina', inplace=True)
    df.replace('Maccabi Kabilio Jaffa', 'Maccabi Jaffa', inplace=True)
    df.replace('Maccabi Haifa', 'Maccabi Kabilio Jaffa', inplace=True)
    df.replace('Hapoel Petah Tikva', 'Maccabi Petach Tikva', inplace=True)
    df.replace('Maccabi Petach Tikva', 'Maccabi Petah Tikva', inplace=True)
    df.replace('FC Machida', 'Machida', inplace=True)
    df.replace('Macva Sabac', 'Macva', inplace=True)
    df.replace('Madla', 'Madla IL', inplace=True)
    df.replace('Madura Utd', 'Madura United', inplace=True)
    df.replace('FC Magdeburg', 'Magdeburg', inplace=True)
    df.replace('FCB Magpies', 'Magpies', inplace=True)
    df.replace('Mahar United FC', 'Mahar United', inplace=True)
    df.replace('Mahasarakham Sam Bai Tao FC', 'Mahasarakham', inplace=True)
    df.replace('Maidstone Utd', 'Maidstone', inplace=True)
    df.replace('Malaga CF II', 'Malaga B', inplace=True)
    df.replace('Deportivo Maldonado', 'Maldonado', inplace=True)
    df.replace('Manaura Esporte Clube', 'Manauara', inplace=True)
    df.replace('Imbabura Sporting Club', 'Manaura Esporte Clube', inplace=True)
    df.replace('Manaus FC', 'Manaus', inplace=True)
    df.replace('Man City', 'Manchester City', inplace=True)
    df.replace('Man City U21', 'Manchester City U21', inplace=True)
    df.replace('Man Utd', 'Manchester Utd', inplace=True)
    df.replace('Waldhof Mannheim', 'Mannheim', inplace=True)
    df.replace('Manta FC', 'Manta', inplace=True)
    df.replace('Maracana CE', 'Maracana', inplace=True)
    df.replace('CD Marathon', 'Marathon', inplace=True)
    df.replace('CD Marchamalo', 'Marchamalo', inplace=True)
    df.replace('SC Mannsdorf', 'Marchfeld', inplace=True)
    df.replace('Marcílio Dias U20', 'Marcilio Dias U20', inplace=True)
    df.replace('Viktoria Marianske Lazne', 'Marianske Lazne', inplace=True)
    df.replace('NK Maribor', 'Maribor', inplace=True)
    df.replace('IFK Mariehamn', 'Mariehamn', inplace=True)
    df.replace('Marignane-Gignac', 'Marignane GCB', inplace=True)
    df.replace('Marine FC', 'Marine', inplace=True)
    df.replace('Maringa', 'Maringa FC', inplace=True)
    df.replace('Marino Luanco', 'Marino de Luanco', inplace=True)
    df.replace('Club Martin Ledesma', 'Martin Ledesma', inplace=True)
    df.replace('Matlock Town', 'Matlock', inplace=True)
    df.replace('Mazatlan FC(W)', 'Mazatlan FC (W)', inplace=True)
    df.replace('TSV Meerbusch U19', 'Meerbusch U19', inplace=True)
    df.replace('Sv Meerssen', 'Meerssen', inplace=True)
    df.replace('Deportes Melipilla', 'Melipilla', inplace=True)
    df.replace('FC Memmingen', 'Memmingen', inplace=True)
    df.replace('Memphis 901 FC', 'Memphis', inplace=True)
    df.replace('SV Meppen', 'Meppen', inplace=True)
    df.replace('SV Meppen U19', 'Meppen U19', inplace=True)
    df.replace('Club Mercedes', 'Mercedes', inplace=True)
    df.replace('Metropolitan Police', 'Met. Police', inplace=True)
    df.replace('FC Metaloglobus Bucuresti', 'Metaloglobus Bucharest', inplace=True)
    df.replace('CF Metalurgistul Cugir', 'Metalurgistul Cugir', inplace=True)
    df.replace('AD Isidro Metapan', 'Metapan', inplace=True)
    df.replace('FS Metta/Lu', 'Metta', inplace=True)
    df.replace('FC Meyrin', 'Meyrin', inplace=True)
    df.replace('Zemplin', 'Michalovce', inplace=True)
    df.replace('Mickleover Sports', 'Mickleover', inplace=True)
    df.replace('FC Midland', 'Midland', inplace=True)
    df.replace('MP', 'Mikkeli', inplace=True)
    df.replace('FC Milsami-Ursidos', 'Milsami', inplace=True)
    df.replace('FC Minaj', 'Minaj', inplace=True)
    df.replace('SFC Minerva', 'Minerva', inplace=True)
    df.replace('Minnesota United FC II', 'Minnesota 2', inplace=True)
    df.replace('Minnesota Utd', 'Minnesota United', inplace=True)
    df.replace('CS Mioveni', 'Mioveni', inplace=True)
    df.replace('Miramar Misiones', 'Miramar', inplace=True)
    df.replace('Mjondalen IF II', 'Mjondalen 2', inplace=True)
    df.replace('Mladost Lucani', 'Mladost', inplace=True)
    df.replace('FK Mladost Novi Sad', 'Mladost GAT', inplace=True)
    df.replace('Moca FC', 'Moca', inplace=True)
    df.replace('Future FC', 'Modern Sport', inplace=True)
    df.replace('Mohammedan SC', 'Mohammedan', inplace=True)
    df.replace('Mohun Bagan Super Giants', 'Mohun Bagan', inplace=True)
    df.replace('Mokpo City', 'Mokpo', inplace=True)
    df.replace('Molde II', 'Molde 2', inplace=True)
    df.replace('FC Mondercange', 'Mondercange', inplace=True)
    df.replace('Yamagata', 'Montedio Yamagata', inplace=True)
    df.replace('Monterey Bay FC', 'Monterey Bay', inplace=True)
    df.replace('Torque', 'Montevideo City', inplace=True)
    df.replace('AC Monza', 'Monza', inplace=True)
    df.replace('Cesar Vallejo Moquegua', 'Moquegua', inplace=True)
    df.replace('FK Mornar', 'Mornar Bar', inplace=True)
    df.replace('CD Mosconia', 'Mosconia', inplace=True)
    df.replace('CD Motagua', 'Motagua', inplace=True)
    df.replace('Moto Clube', 'Moto Club', inplace=True)
    df.replace('LKP Motor Lublin', 'Motor Lublin', inplace=True)
    df.replace('SPG Motz/Silz', 'Motz/Silz', inplace=True)
    df.replace('1860 Munich', 'Munich 1860', inplace=True)
    df.replace('1860 Munich II', 'Munich 1860 II', inplace=True)
    df.replace('1860 Munich U19', 'Munich 1860 U19', inplace=True)
    df.replace('CSD Municipal', 'Municipal', inplace=True)
    df.replace('CD Municipal Limeno', 'Municipal Limeno', inplace=True)
    df.replace('ART Municipal Jalapa', 'Municipal Santa Ana', inplace=True)
    df.replace('Real Murcia', 'Murcia', inplace=True)
    df.replace('Myawady FC', 'Myawady', inplace=True)
    df.replace('Rainbow FC', 'NBP Rainbow AC', inplace=True)
    df.replace('NK Slovenska Bistrica', 'NK Bistrica', inplace=True)
    df.replace('Krka', 'NK Krka', inplace=True)
    df.replace('Nacional (Uru)', 'Nacional', inplace=True)
    df.replace('CD Nacional Funchal', 'Nacional (Uru)', inplace=True)
    df.replace('Nacional (Par)', 'Nacional Asuncion', inplace=True)
    df.replace('Nacional AM', 'Nacional-AM', inplace=True)
    df.replace('Nafta Lendava', 'Nafta', inplace=True)
    df.replace('Nagaworld FC', 'NagaWorld', inplace=True)
    df.replace('Nagano Parceiro', 'Nagano', inplace=True)
    df.replace('Nagoya', 'Nagoya Grampus', inplace=True)
    df.replace('Nanjing Fengfan', 'Nanjing City', inplace=True)
    df.replace('Haimen Codion', 'Nantong Haimen', inplace=True)
    df.replace('Nantong Zhiyun F.C', 'Nantong Zhiyun', inplace=True)
    df.replace('FK Napredak', 'Napredak', inplace=True)
    df.replace('Trans Narva', 'Narva', inplace=True)
    df.replace('National Bank', 'National Bank Egypt', inplace=True)
    df.replace('Nautico PE', 'Nautico', inplace=True)
    df.replace('Naxxar Lions', 'Naxxar', inplace=True)
    df.replace('Club Necaxa (W)', 'Necaxa (W)', inplace=True)
    df.replace('Neftchi Baku', 'Neftci Baku', inplace=True)
    df.replace('Neman Grodno', 'Neman', inplace=True)
    df.replace('FC Neptunas Klaipeda', 'Neptunas', inplace=True)
    df.replace('FK Neratovice-Byskovice', 'Neratovice', inplace=True)
    df.replace('Maccabi Netanya', 'Netanya', inplace=True)
    df.replace('SC Neusiedl am See', 'Neusiedl', inplace=True)
    df.replace('TSG Neustrelitz', 'Neustrelitz', inplace=True)
    df.replace('FK Nevezis', 'Nevezis Kedainiai', inplace=True)
    df.replace('New England', 'New England Revolution', inplace=True)
    df.replace('New Mexico United', 'New Mexico', inplace=True)
    df.replace('New York Red Bulls II', 'New York Red Bulls 2', inplace=True)
    df.replace('Newcastle U21', 'Newcastle Utd U21', inplace=True)
    df.replace('Newells', 'Newells Old Boys', inplace=True)
    df.replace('Newells Old Boys (Res)', 'Newells Old Boys 2', inplace=True)
    df.replace('Newport County', 'Newport', inplace=True)
    df.replace('Progres Niedercorn', 'Niedercorn', inplace=True)
    df.replace('NEC Nijmegen', 'Nijmegen', inplace=True)
    df.replace('Niki Volou', 'Niki Volos', inplace=True)
    df.replace('FC Noah', 'Noah', inplace=True)
    df.replace('Nomme Kalju II', 'Nomme Kalju U21', inplace=True)
    df.replace('Nongbua Pitchaya FC', 'Nong Bua Pitchaya', inplace=True)
    df.replace('United IK Nordic', 'Nordic United', inplace=True)
    df.replace('TSV Nordlingen', 'Nordlingen', inplace=True)
    df.replace('FC Nordsjaelland', 'Nordsjaelland', inplace=True)
    df.replace('FC Nordsjaelland (W)', 'Nordsjaelland (W)', inplace=True)
    df.replace('Normannia Schwabisch Gmund', 'Normannia Gmund', inplace=True)
    df.replace('Norrby IF', 'Norrby', inplace=True)
    df.replace('North Carolina FC', 'North Carolina', inplace=True)
    df.replace('North East United FC', 'North East Utd', inplace=True)
    df.replace('North Texas SC', 'North Texas', inplace=True)
    df.replace('Northern Colorado FC', 'Northern Colorado', inplace=True)
    df.replace('Nosaby IF', 'Nosaby', inplace=True)
    df.replace('FC Nottingen', 'Nottingen', inplace=True)
    df.replace('Nottm Forest', 'Nottingham', inplace=True)
    df.replace('Nova Iguacu FC U20', 'Nova Iguacu U20', inplace=True)
    df.replace('FK Novi Pazar', 'Novi Pazar', inplace=True)
    df.replace('Gremio Novorizontino U20', 'Novorizontino U20', inplace=True)
    df.replace('Club Nueve de Octubre', 'Nueve de Octubre', inplace=True)
    df.replace('1. FC Nurnberg U19', 'Nurnberg U19', inplace=True)
    df.replace('Nykobing FC', 'Nykobing', inplace=True)
    df.replace('Olimpija', 'O. Ljubljana', inplace=True)
    df.replace('Charleroi-Marchienne', 'OC Charleroi', inplace=True)
    df.replace('OFI', 'OFI Crete', inplace=True)
    df.replace('OLS', 'OLS Oulu', inplace=True)
    df.replace('Rot-Weiss Oberhausen', 'Oberhausen', inplace=True)
    df.replace('Odds BK', 'Odd', inplace=True)
    df.replace('OB', 'Odense', inplace=True)
    df.replace('Kickers Offenbach', 'Offenbach', inplace=True)
    df.replace('Conaree United', 'Ogre United', inplace=True)
    df.replace('Oita', 'Oita Trinita', inplace=True)
    df.replace('Olimpia Grudziadz', 'Ol. Grudziadz', inplace=True)
    df.replace('Vikingur Olafsvik', 'Olafsvik', inplace=True)
    df.replace('Oldenburger SV', 'Oldenburger', inplace=True)
    df.replace('Olimpo', 'Olimpia', inplace=True)
    df.replace('Olimpia', 'Olimpia Asuncion', inplace=True)
    df.replace('ACS Olimpic Zarnesti', 'Olimpic Zarnesti', inplace=True)
    df.replace('Oliveirense', 'Oliveirense', inplace=True)
    df.replace('Olympiakos', 'Olympiacos Piraeus', inplace=True)
    df.replace('BK Olympic', 'Olympic', inplace=True)
    df.replace('Omiya', 'Omiya Ardija', inplace=True)
    df.replace('Omonia FC Aradippou', 'Omonia Aradippou', inplace=True)
    df.replace('Onsala BK', 'Onsala', inplace=True)
    df.replace('SFC Opava', 'Opava', inplace=True)
    df.replace('Operario PR', 'Operario', inplace=True)
    df.replace('CE Operario Varzea-Grandense', 'Operario VG', inplace=True)
    df.replace('Orange County Blues', 'Orange County SC', inplace=True)
    df.replace('FC Ordabasy', 'Ordabasy', inplace=True)
    df.replace('KIF Orebro Dff (W)', 'Orebro (W)', inplace=True)
    df.replace('Orebro Syrianska', 'Orebro Syr.', inplace=True)
    df.replace('Orense Sporting Club', 'Orense', inplace=True)
    df.replace('Club Oriental de La Paz', 'Oriental', inplace=True)
    df.replace('Orihuela CF', 'Orihuela', inplace=True)
    df.replace('Orlando Pirates (SA)', 'Orlando Pirates', inplace=True)
    df.replace('Orn Horten', 'Orn', inplace=True)
    df.replace('CF Os Belenenses', 'Os Belenenses', inplace=True)
    df.replace('FC Osaka', 'Osaka', inplace=True)
    df.replace('CA Osasuna II', 'Osasuna B', inplace=True)
    df.replace('Oskarshamns AIK', 'Oskarshamn', inplace=True)
    df.replace('FC Oss', 'Oss', inplace=True)
    df.replace('Osters', 'Oster', inplace=True)
    df.replace('IFK Osterakers FK', 'Osteraker IFK', inplace=True)
    df.replace('Osterlen FF', 'Osterlen', inplace=True)
    df.replace('Ostersunds FK', 'Ostersund', inplace=True)
    df.replace('Banik Ostrava', 'Ostrava', inplace=True)
    df.replace('Banik Ostrava B', 'Ostrava B', inplace=True)
    df.replace('Otelul Galati', 'Otelul', inplace=True)
    df.replace('FK Otrant', 'Otrant', inplace=True)
    df.replace('UD Ourense', 'Ourense CF', inplace=True)
    df.replace('Pallo-Iirot', 'P-Iirot Rauma', inplace=True)
    df.replace('Pas Giannina', 'PAS Giannina', inplace=True)
    df.replace('PDRM', 'PDRM FC', inplace=True)
    df.replace('PK 35', 'PK-35', inplace=True)
    df.replace('PK-35 RY Helsinki (W)', 'PK-35 Helsinki (W)', inplace=True)
    df.replace('Pacajus EC', 'Pacajus', inplace=True)
    df.replace('Pacific', 'Pacific FC', inplace=True)
    df.replace('SC Paderborn 07 II', 'Paderborn II', inplace=True)
    df.replace('Paide Linnameeskond', 'Paide', inplace=True)
    df.replace('Paide Linnameeskond II', 'Paide Linnameeskond U21', inplace=True)
    df.replace('Paks', 'Paks II', inplace=True)
    df.replace('Atletico Palmaflor Vinto', 'Palmaflor', inplace=True)
    df.replace('SE Palmeiras', 'Palmeiras', inplace=True)
    df.replace('USC Paloma', 'Paloma', inplace=True)
    df.replace('SK Pama', 'Pama', inplace=True)
    df.replace('MSV Pampow', 'Pampow', inplace=True)
    df.replace('Panaitolikos', 'Panetolikos', inplace=True)
    df.replace('Paphos FC', 'Paphos', inplace=True)
    df.replace('FC Paradiso', 'Paradiso', inplace=True)
    df.replace('Enosis Neon Paralimni', 'Paralimni', inplace=True)
    df.replace('Paris St-G', 'PSG', inplace=True)
    df.replace('SV Pars Neu-Isenburg', 'Pars Neu-Isenburg', inplace=True)
    df.replace('Partick', 'Partick Thistle', inplace=True)
    df.replace('Partizan Belgrade', 'Partizan', inplace=True)
    df.replace('Partizani Tirana', 'Partizani', inplace=True)
    df.replace('BG Pathumthani United', 'Pathum United', inplace=True)
    df.replace('Boyaca Patriotas', 'Patriotas', inplace=True)
    df.replace('Boyaca Patriotas', 'Patriotas U20', inplace=True)
    df.replace('Patro Eisden Maasmechelen', 'Patro Eisden', inplace=True)
    df.replace('CA Patrocinense', 'Patrocinense', inplace=True)
    df.replace('Pau', 'Pau FC', inplace=True)
    df.replace('FC Paulesti', 'Paulesti', inplace=True)
    df.replace('Paysandu', 'Paysandu PA', inplace=True)
    df.replace('Peamount United (W)', 'Peamount (W)', inplace=True)
    df.replace('CSC Peciu Nou', 'Peciu Nou', inplace=True)
    df.replace('Peerless SC', 'Peerless', inplace=True)
    df.replace('Pelikan Lowicz', 'Pelikan', inplace=True)
    df.replace('Pelister Bitola', 'Pelister', inplace=True)
    df.replace('Penarol', 'Pena', inplace=True)
    df.replace('Pulau Pinang', 'Penang', inplace=True)
    df.replace('Deportivo Pereira', 'Pereira', inplace=True)
    df.replace('Sparta Petegem', 'Petegem', inplace=True)
    df.replace('Peterborough Sports FC', 'Peterborough Sports', inplace=True)
    df.replace('CS Petrocub', 'Petrocub', inplace=True)
    df.replace('Petrolina PE', 'Petrolina', inplace=True)
    df.replace('ACS Petrolul 52', 'Petrolul', inplace=True)
    df.replace('OFK Petrovac', 'Petrovac', inplace=True)
    df.replace('TJ Petrvald na Morave', 'Petrvald na Morave', inplace=True)
    df.replace('FC Petrzalka', 'Petrzalka', inplace=True)
    df.replace('FC Petrzalka (W)', 'Petrzalka (W)', inplace=True)
    df.replace('Pevidem SC', 'Pevidem', inplace=True)
    df.replace('TSG Pfeddersheim', 'Pfeddersheim', inplace=True)
    df.replace('1. CfR Pforzheim', 'Pforzheim', inplace=True)
    df.replace('Pharco FC', 'Pharco', inplace=True)
    df.replace('Philadelphia', 'Philadelphia Union', inplace=True)
    df.replace('Phnom Penh', 'Phnom Penh Crown', inplace=True)
    df.replace('Phoenix Rising FC', 'Phoenix Rising', inplace=True)
    df.replace('Phoenix Rising F', 'Phoenix Rising FC', inplace=True)
    df.replace('FC Phonix Lubeck', 'Phonix Lubeck', inplace=True)
    df.replace('US Pianese', 'Pianese', inplace=True)
    df.replace('XV De Piracicaba', 'Piracicaba', inplace=True)
    df.replace('XV de Piracicaba U20', 'Piracicaba U20', inplace=True)
    df.replace('Pittsburgh Riverhounds', 'Pittsburgh', inplace=True)
    df.replace('CA Platense', 'Platense', inplace=True)
    df.replace('Atl Platense (Res)', 'Platense 2', inplace=True)
    df.replace('Platense Zacatecoluca', 'Platense Municipal', inplace=True)
    df.replace('VFC Plauen', 'Plauen', inplace=True)
    df.replace('Pocheon FC', 'Pocheon', inplace=True)
    df.replace('Podbeskidzie B-B', 'Podbeskidzie', inplace=True)
    df.replace('Pohang Steelers', 'Pohang', inplace=True)
    df.replace('Spartak Police nad Metuji', 'Police nad Metuji', inplace=True)
    df.replace('Gornik Polkowice', 'Polkowice', inplace=True)
    df.replace('Pontefract Collieries', 'Pontefract', inplace=True)
    df.replace('Pontevedra CF', 'Pontevedra', inplace=True)
    df.replace('Portimonense SC U23', 'Portimonense U23', inplace=True)
    df.replace('Portland Timbers II', 'Portland Timbers 2', inplace=True)
    df.replace('Port FC', 'Porto SC', inplace=True)
    df.replace('Porto Velho EC', 'Porto Velho', inplace=True)
    df.replace('Portuguesa FC', 'Portuguesa', inplace=True)
    df.replace('Portuguesa FC', 'Portuguesa RJ U20', inplace=True)
    df.replace('AA Portuguesa S U20', 'Portuguesa Santista U20', inplace=True)
    df.replace('Nk Posusje', 'Posusje', inplace=True)
    df.replace('Potiguar', 'Potiguar de Mossoró', inplace=True)
    df.replace('Costa Del Este', 'Potros del Este', inplace=True)
    df.replace('Potters Bar Town', 'Potters Bar', inplace=True)
    df.replace('MSK Povazska Bystrica', 'Povazska Bystrica', inplace=True)
    df.replace('Sexy Poxyt', 'Poxyt', inplace=True)
    df.replace('Tatran Presov', 'Presov', inplace=True)
    df.replace('Preussen Munster ll', 'Preussen Munster 2', inplace=True)
    df.replace('Rudar Prijedor', 'Prijedor', inplace=True)
    df.replace('NK Primorje', 'Primorje', inplace=True)
    df.replace('Princesa Dos Solimoes', 'Princesa do Solimoes', inplace=True)
    df.replace('SSD Pro Sesto', 'Pro Sesto', inplace=True)
    df.replace('Acs Progresul Fundulea', 'Progresul Fundulea', inplace=True)
    df.replace('Provincial Osorno', 'Provincial', inplace=True)
    df.replace('Provincial Ovalle FC', 'Provincial Ovalle', inplace=True)
    df.replace('Provincial Osorno', 'Provincial Ovalle FC', inplace=True)
    df.replace('Znicz Pruszkow', 'Pruszkow', inplace=True)
    df.replace('FK Puchov', 'Puchov', inplace=True)
    df.replace('Puebla FC (W)', 'Puebla (W)', inplace=True)
    df.replace('CA Puerto Nuevo', 'Puerto Nuevo', inplace=True)
    df.replace('Puntarenas F.C.', 'Puntarenas FC', inplace=True)
    df.replace('Puskas Akademia', 'Puskas Academy', inplace=True)
    df.replace('Puszcza Niepolomice', 'Puszcza', inplace=True)
    df.replace('FC Van Yerevan', 'Pyunik Yerevan 2', inplace=True)
    df.replace('Qarabag FK', 'Qarabag', inplace=True)
    df.replace('Qingdao Jonoon', 'Qingdao Hainiu', inplace=True)
    df.replace('Qingdao Youth Island', 'Qingdao West Coast', inplace=True)
    df.replace('Quanzhou Yaxin', 'Quanzhou Yassin', inplace=True)
    df.replace('Queens University', 'Queens Univ.', inplace=True)
    df.replace('Qviding FIF', 'Qviding', inplace=True)
    df.replace('Oviedo', 'R. Oviedo', inplace=True)
    df.replace('Real Oviedo II', 'R. Oviedo B', inplace=True)
    df.replace('Resovia Rzeszow', 'R. Rzeszow', inplace=True)
    df.replace('Real Union', 'R. Union', inplace=True)
    df.replace('Red Bull Bragantino U20', 'RB Bragantino U20', inplace=True)
    df.replace('FC Liege', 'RFC Liege', inplace=True)
    df.replace('Rigas Futbola Skola', 'RFS', inplace=True)
    df.replace('Anderlecht (W)', 'RSC Anderlecht (W)', inplace=True)
    df.replace('SV Eintracht 1949', 'RSV Eintracht', inplace=True)
    df.replace('RTC FC', 'RTC', inplace=True)
    df.replace('Rot-Weiss Essen', 'RW Essen', inplace=True)
    df.replace('Rot Weiss Essen U19', 'RW Essen U19', inplace=True)
    df.replace('SG Rot-Weiss Frankfurt 01', 'RW Frankfurt', inplace=True)
    df.replace('SV Rot-Weiss Walldorf', 'RW Walldorf', inplace=True)
    df.replace('Racing (W)', 'Racing Club (W)', inplace=True)
    df.replace('Racing Club (Res)', 'Racing Club 2', inplace=True)
    df.replace('Club Cordoba', 'Racing Cordoba', inplace=True)
    df.replace('Racing Club (Uru)', 'Racing Montevideo', inplace=True)
    df.replace('Radcliffe Borough', 'Radcliffe', inplace=True)
    df.replace('FK Radnicki 1923', 'Radnicki 1923', inplace=True)
    df.replace('FK Radnicki Sremska', 'Radnicki S. Mitrovica', inplace=True)
    df.replace('Radnik Surdulica', 'Radnik', inplace=True)
    df.replace('NK Radomlje', 'Radomlje', inplace=True)
    df.replace('Railway Athletic FC', 'Railway', inplace=True)
    df.replace('TSV Rain/Lech', 'Rain/Lech', inplace=True)
    df.replace('Rakhine Utd', 'Rakhine United', inplace=True)
    df.replace('Rakow Czestochowa', 'Rakow', inplace=True)
    df.replace('Randers', 'Randers FC', inplace=True)
    df.replace('Rangers', 'Rangers', inplace=True)
    df.replace('Ranheim IL', 'Ranheim', inplace=True)
    df.replace('Rapperswil-Jona', 'Rapperswil', inplace=True)
    df.replace('Optik Rathenow', 'Rathenow', inplace=True)
    df.replace('Rathfriland Rangers', 'Rathfriland', inplace=True)
    df.replace('Real Avila CF', 'Real Avila', inplace=True)
    df.replace('Real Soacha Cundinamarca FC', 'Real Cundinamarca', inplace=True)
    df.replace('Real Madrid Castilla', 'Real Madrid B', inplace=True)
    df.replace('Real Monarchs SLC', 'Real Monarchs', inplace=True)
    df.replace('Real Pilar FC', 'Real Pilar', inplace=True)
    df.replace('Deportes Recoleta', 'Recoleta', inplace=True)
    df.replace('ACS Recolta Gheorghe Doja', 'Recolta Gh. Doja', inplace=True)
    df.replace('Red Bull Bragantino U', 'Red Bull Bragantino U20', inplace=True)
    df.replace('Referencia FC U20', 'Referencia U20', inplace=True)
    df.replace('Jahn Regensburg', 'Regensburg', inplace=True)
    df.replace('Jahn Regensburg II', 'Regensburg II', inplace=True)
    df.replace('SVG Reichenau', 'Reichenau', inplace=True)
    df.replace('CA Rentistas', 'Rentistas', inplace=True)
    df.replace('Resistencia SC', 'Resistencia', inplace=True)
    df.replace('Retro FC Brasil', 'Retro', inplace=True)
    df.replace('SC Retz', 'Retz', inplace=True)
    df.replace('Reynir Sandgeroi', 'Reynir', inplace=True)
    df.replace('Rhode Island FC', 'Rhode Island', inplace=True)
    df.replace('SV Ried', 'Ried', inplace=True)
    df.replace('FK Riga', 'Riga FC', inplace=True)
    df.replace('FC Rijnvogels', 'Rijnvogels', inplace=True)
    df.replace('Ringsted IF', 'Ringsted', inplace=True)
    df.replace('Rio Ave FC U23', 'Rio Ave U23', inplace=True)
    df.replace('Rio Branco-Acre', 'Rio Branco', inplace=True)
    df.replace('Rio Grande Valley FC', 'Rio Grande', inplace=True)
    df.replace('CA River Plate BA (Res)', 'River Plate 2', inplace=True)
    df.replace('River Atletico Clube', 'River-PI', inplace=True)
    df.replace('Rochdale', 'Rochedale', inplace=True)
    df.replace('Roda JC', 'Roda', inplace=True)
    df.replace('SV Rodinghausen', 'Rodinghausen', inplace=True)
    df.replace('FC Rokycany', 'Rokycany', inplace=True)
    df.replace('Roma City FC', 'Roma City', inplace=True)
    df.replace('Rosario Central (Res)', 'Rosario Central 2', inplace=True)
    df.replace('Rosenborg BK (W)', 'Rosenborg (W)', inplace=True)
    df.replace('Rosenborg BK 2', 'Rosenborg 2', inplace=True)
    df.replace('Ross Co', 'Ross County', inplace=True)
    df.replace('SC Rothis', 'Rothis', inplace=True)
    df.replace('RoPS', 'Rovaniemi', inplace=True)
    df.replace('Union St Gilloise', 'Royale Union SG', inplace=True)
    df.replace('Rukh Vynnyky', 'Rukh Lviv', inplace=True)
    df.replace('FC Rustavi', 'Rustavi', inplace=True)
    df.replace('Jiskra Rymarov', 'Rymarov', inplace=True)
    df.replace('FC Ryukyu', 'Ryukyu', inplace=True)
    df.replace('C. Springs', 'S. Morning', inplace=True)
    df.replace('Santiago Morning (W)', 'S. Morning (W)', inplace=True)
    df.replace('Stal Rzeszow', 'S. Rzeszow', inplace=True)
    df.replace('Santiago Wanderers', 'S. Wanderers', inplace=True)
    df.replace('Stal Stalowa Wola', 'S. Wola', inplace=True)
    df.replace('San Antonio FC', 'SA Bulo Bulo', inplace=True)
    df.replace('FC Ashdod', 'SC Ashdod', inplace=True)
    df.replace('Farense', 'SC Farense', inplace=True)
    df.replace('Farense U23', 'SC Farense U23', inplace=True)
    df.replace('Feyenoord', 'Feyenoord', inplace=True)
    df.replace('SC Lusitania Dos Acores', 'SC Lusitania', inplace=True)
    df.replace('SC Lusitania Dos Acores U19', 'SC Lusitania U19', inplace=True)
    df.replace('St Veit/Glan', 'SC St. Veit', inplace=True)
    df.replace('SD Family FC', 'SD Family', inplace=True)
    df.replace('SER Caxias do Sul', 'SER Caxias', inplace=True)
    df.replace('Dynamo Dresden', 'SG Dynamo Dresden', inplace=True)
    df.replace('Wattenscheid', 'SG Wattenscheid', inplace=True)
    df.replace('SJK 2', 'SJK Akatemia', inplace=True)
    df.replace('Gjovik-Lyn', 'SK Gjovik-Lyn', inplace=True)
    df.replace('Rapid Vienna', 'SK Rapid', inplace=True)
    df.replace('Heimstetten', 'SKU Amstetten', inplace=True)
    df.replace('S.L. Benfica (W)', 'SL Benfica (W)', inplace=True)
    df.replace('Velbert', 'SSVg Velbert', inplace=True)
    df.replace('TSV Kottern', 'SV Horn', inplace=True)
    df.replace('Trans Narva', 'SV Transvaal', inplace=True)
    df.replace('Schwarz Weiss Essen', 'SW Essen', inplace=True)
    df.replace('Pinzgau Saalfelden', 'Saalfelden', inplace=True)
    df.replace('Sabah FA', 'Sabah', inplace=True)
    df.replace('FC Sabah', 'Sabah Baku', inplace=True)
    df.replace('Tosu', 'Sagan Tosu', inplace=True)
    df.replace('Bnei Sakhnin', 'Sakhnin', inplace=True)
    df.replace('Salford City', 'Salford', inplace=True)
    df.replace('Salisbury City', 'Salisbury Utd.', inplace=True)
    df.replace('Red Bull Salzburg', 'Salzburg', inplace=True)
    df.replace('Samgurali Tskaltubo', 'Samgurali', inplace=True)
    df.replace('Sampaio Correa FC', 'Sampaio Correa', inplace=True)
    df.replace('Samtse FC', 'Samtse', inplace=True)
    df.replace('Samut Prakan', 'Samut Prakan City', inplace=True)
    df.replace('San Antonio FC', 'San Antonio', inplace=True)
    df.replace('San Benito FC', 'San Antonio FC', inplace=True)
    df.replace('CSD San Antonio Unido', 'San Antonio Unido', inplace=True)
    df.replace('Sao Bento U20', 'San Benito FC', inplace=True)
    df.replace('Ad San Carlos', 'San Carlos', inplace=True)
    df.replace('San Diego Loyal SC', 'San Diego Loyal', inplace=True)
    df.replace('Union San Felipe', 'San Felipe', inplace=True)
    df.replace('San Fernando CD', 'San Fernando', inplace=True)
    df.replace('San Francisco FC', 'San Francisco', inplace=True)
    df.replace('San Lorenzo Almagro (W)', 'San Lorenzo (W)', inplace=True)
    df.replace('San Lorenzo (Res)', 'San Lorenzo 2', inplace=True)
    df.replace('San Luis FC Women', 'San Luis (W)', inplace=True)
    df.replace('San Martin de Burzaco', 'San Martin Burzaco', inplace=True)
    df.replace('CSG San M Formosa', 'San Martin Formosa', inplace=True)
    df.replace('San Martin de Mendoza', 'San Martin Mendoza', inplace=True)
    df.replace('San Martin de San Juan', 'San Martin S.J.', inplace=True)
    df.replace('San Martin de Tucuman', 'San Martin T.', inplace=True)
    df.replace('San Martin De San Juan', 'San Martin de San Juan', inplace=True)
    df.replace('CA San Miguel', 'San Miguel', inplace=True)
    df.replace('SS Reyes', 'San Sebastian Reyes', inplace=True)
    df.replace('Sandecja Nowy Sacz', 'Sandecja Nowy S.', inplace=True)
    df.replace('SV Sandhausen', 'Sandhausen', inplace=True)
    df.replace('Sandnes Ulf', 'Sandnes', inplace=True)
    df.replace('Sandvikens', 'Sandviken', inplace=True)
    df.replace('Sandvikens AIK FK', 'Sandvikens AIK', inplace=True)
    df.replace('Hiroshima', 'Sanfrecce Hiroshima', inplace=True)
    df.replace('Sangiuliano City Nova', 'Sangiuliano City', inplace=True)
    df.replace('Atletico Sanluqueno CF', 'Sanluqueno', inplace=True)
    df.replace('UE Sant Andreu', 'Sant Andreu', inplace=True)
    df.replace('Municipal Santa Ana', 'Santa Ana', inplace=True)
    df.replace('Club Real Santa Cruz', 'Santa Cruz', inplace=True)
    df.replace('Santa Cruz RN', 'Santa Cruz de Natal', inplace=True)
    df.replace('EC Santo Andre U20', 'Santo Andre U20', inplace=True)
    df.replace('Santos De Guapiles', 'Santos de Guapiles', inplace=True)
    df.replace('San Benito FC', 'Sao Bento U20', inplace=True)
    df.replace('AD Sao Caetano do Sul U20', 'Sao Caetano U20', inplace=True)
    df.replace('San Marcos', 'Sao Carlos', inplace=True)
    df.replace('Sao Francisco AC', 'Sao Francisco FC', inplace=True)
    df.replace('Sao Jose EC SP', 'Sao Jose EC', inplace=True)
    df.replace('Independente FSJ', 'Sao Joseense', inplace=True)
    df.replace('Sao Raimundo', 'Sao Raimundo RR', inplace=True)
    df.replace('Deportivo Saprissa', 'Saprissa', inplace=True)
    df.replace('Sarmiento de Junin', 'Sarmiento Junin', inplace=True)
    df.replace('CA Sarmiento (Res)', 'Sarmiento Junin 2', inplace=True)
    df.replace('Sarmiento de Resistenc', 'Sarmiento Resistencia', inplace=True)
    df.replace('Atletico Sarmiento', 'Sarmiento de La Banda', inplace=True)
    df.replace('Sarmiento de Resistencia', 'Sarmiento de Resistenc', inplace=True)
    df.replace('Sarpsborg', 'Sarpsborg 08', inplace=True)
    df.replace('Savedalens', 'Savedalen', inplace=True)
    df.replace('Scarborough Athletic', 'Scarborough', inplace=True)
    df.replace('Schalding-Heining', 'Schalding', inplace=True)
    df.replace('Schalke 04', 'Schalke', inplace=True)
    df.replace('Schalke 04 II', 'Schalke II', inplace=True)
    df.replace('FC Schalke U19', 'Schalke U19', inplace=True)
    df.replace('SpVg Schonnebeck', 'Schonnebeck', inplace=True)
    df.replace('TSV Schott Mainz U19', 'Schott Mainz U19', inplace=True)
    df.replace('TSV Schwaben Augsburg', 'Schwaben Augsburg', inplace=True)
    df.replace('SC Schwaz', 'Schwaz', inplace=True)
    df.replace('SV Schwechat', 'Schwechat', inplace=True)
    df.replace('Sekhukhune United', 'Sekhukhune', inplace=True)
    df.replace('Selangor FA', 'Selangor', inplace=True)
    df.replace('CSC 1599 Selimbar', 'Selimbar', inplace=True)
    df.replace('Seongnam FC', 'Seongnam', inplace=True)
    df.replace('FC Seoul', 'Seoul', inplace=True)
    df.replace('Seoul E-Land FC', 'Seoul E-Land', inplace=True)
    df.replace('Seoul E-Land FC', 'Seoul E.', inplace=True)
    df.replace('ACS Sepsi OSK', 'Sepsi Sf. Gheorghe', inplace=True)
    df.replace('Septemvri', 'Septemvri Sofia', inplace=True)
    df.replace('Sestao River', 'Sestao', inplace=True)
    df.replace('USD Sestri Levante 1919', 'Sestri Levante', inplace=True)
    df.replace('NK Sesvete', 'Sesvete', inplace=True)
    df.replace('Sevilla B', 'Sevilla FC B', inplace=True)
    df.replace('Shaanxi Union FC', 'Shaanxi Union', inplace=True)
    df.replace('Shakhtar', 'Shakhtar Donetsk', inplace=True)
    df.replace('Shamakhi FK', 'Shamakhi', inplace=True)
    df.replace('Shan United', 'Shan Utd', inplace=True)
    df.replace('Shandong Huangming (W)', 'Shandong SL (W)', inplace=True)
    df.replace('Shanghai Jiading', 'Shanghai Jiading Huilong', inplace=True)
    df.replace('Shanghai Port FC', 'Shanghai Port', inplace=True)
    df.replace('Sheff Utd', 'Sheffield Utd', inplace=True)
    df.replace('Sheff Wed', 'Sheffield Wed', inplace=True)
    df.replace('Shenzhen FC', 'Shenzhen', inplace=True)
    df.replace('Shenzhen Juniors FC', 'Shenzhen Juniors', inplace=True)
    df.replace('Sichuan Jiuniu FC', 'Shenzhen Xinpengcheng', inplace=True)
    df.replace('Shepshed Dynamo', 'Shepshed', inplace=True)
    df.replace('Hebei KungFu', 'Shijiazhuang Gongfu', inplace=True)
    df.replace('Shimizu', 'Shimizu S-Pulse', inplace=True)
    df.replace('Shonan', 'Shonan Bellmare', inplace=True)
    df.replace('FK Siauliai II', 'Siauliai 2', inplace=True)
    df.replace('Fk Siauliai', 'Siauliai FA', inplace=True)
    df.replace('FC Sion II', 'Sion II', inplace=True)
    df.replace('Fortuna Sittard', 'Sittard', inplace=True)
    df.replace('MFK Skalica', 'Skalica', inplace=True)
    df.replace('Unia Skierniewice', 'Skierniewice', inplace=True)
    df.replace('Skovde Aik', 'Skovde AIK', inplace=True)
    df.replace('Skra Czestochowa', 'Skra', inplace=True)
    df.replace('IA Akranes (W)', 'Skra (W)', inplace=True)
    df.replace('SK Slany', 'Slany', inplace=True)
    df.replace('Slavia Praha B', 'Slavia Prague B', inplace=True)
    df.replace('Sliema Wanderers FC', 'Sliema', inplace=True)
    df.replace('FK Sloboda Point', 'Sloboda', inplace=True)
    df.replace('Slough Town', 'Slough', inplace=True)
    df.replace('Selfoss (W)', 'Slovacko (W)', inplace=True)
    df.replace('Slovan Bratislava II', 'Slovan Bratislava B', inplace=True)
    df.replace('Slovan Ljublana', 'Slovan Ljubljana', inplace=True)
    df.replace('Skeid U19', 'Slovenia U19', inplace=True)
    df.replace('Fk Smederevo', 'Smederevo', inplace=True)
    df.replace('Social Atletico T (W)', 'Social Atletico Television (W)', inplace=True)
    df.replace('TJ Sokol Zivanice', 'Sokol Radnice', inplace=True)
    df.replace('Sol De Mayo', 'Sol de Mayo', inplace=True)
    df.replace('Sollentuna FF', 'Sollentuna', inplace=True)
    df.replace('SonderjyskE', 'Sonderjyske', inplace=True)
    df.replace('Sondrio Calcio', 'Sondrio', inplace=True)
    df.replace('SV Sonsbeck', 'Sonsbeck', inplace=True)
    df.replace('Sotra SK', 'Sotra', inplace=True)
    df.replace('Sousa EC', 'Sousa', inplace=True)
    df.replace('Sportivo Luqueno', 'Sp. Luqueno', inplace=True)
    df.replace('FK Spartak', 'Sp. Subotica', inplace=True)
    df.replace('Bayreuth', 'SpVgg Bayreuth', inplace=True)
    df.replace('Spalding Utd', 'Spalding United', inplace=True)
    df.replace('FC Spartak Trnava (W)', 'Sparta Prague (W)', inplace=True)
    df.replace('CSF Spartanii', 'Spartans', inplace=True)
    df.replace('VFB Speldorf', 'Speldorf', inplace=True)
    df.replace('SC Spelle Venhaus', 'Spelle-Venhaus', inplace=True)
    df.replace('Spennymoor Town', 'Spennymoor', inplace=True)
    df.replace('Spjelkavik IL', 'Spjelkavik', inplace=True)
    df.replace('Spokane Velocity FC', 'Spokane Velocity', inplace=True)
    df.replace('Sport Boys (Per)', 'Sport Boys', inplace=True)
    df.replace('Sporting Lisbon', 'Sporting CP', inplace=True)
    df.replace('Sporting Lisbon B', 'Sporting CP B', inplace=True)
    df.replace('Sporting Lisbon U23', 'Sporting CP U23', inplace=True)
    df.replace('Kansas City', 'Sporting Kansas City', inplace=True)
    df.replace('Sporting San Miguelito', 'Sporting Kansas City II', inplace=True)
    df.replace('CS Sporting Liesti', 'Sporting Liesti', inplace=True)
    df.replace('Sporting San Jose FC', 'Sporting San Jose', inplace=True)
    df.replace('SAC Las Par', 'Sportivo AC Las Parejas', inplace=True)
    df.replace('SportivoAtenas', 'Sportivo Atenas', inplace=True)
    df.replace('Sportivo AC Las Parejas', 'Sportivo Las Parejas', inplace=True)
    df.replace('Club Sportivo Trinidense', 'Sportivo Trinidense', inplace=True)
    df.replace('Sportlust 46', 'Sportlust', inplace=True)
    df.replace('Union AC Mauer', 'Sportunion Mauer', inplace=True)
    df.replace('Sprint Jeloy', 'Sprint-Jeloy', inplace=True)
    df.replace('Pahang', 'Sri Pahang', inplace=True)
    df.replace('St Albans', 'St. Albans', inplace=True)
    df.replace('St Gallen', 'St. Gallen', inplace=True)
    df.replace('Standard', 'St. Liege', inplace=True)
    df.replace('St Louis City SC', 'St. Louis City', inplace=True)
    df.replace('Saint Louis City II', 'St. Louis City 2', inplace=True)
    df.replace('St Mirren', 'St. Mirren', inplace=True)
    df.replace('St Mirren B', 'St. Mirren B', inplace=True)
    df.replace('St Patricks', 'St. Patricks', inplace=True)
    df.replace('St Pauli', 'St. Pauli', inplace=True)
    df.replace('FC St. Pauli U19', 'St. Pauli U19', inplace=True)
    df.replace('St Polten', 'St. Polten', inplace=True)
    df.replace('SKN St. Polten (W)', 'St. Polten (W)', inplace=True)
    df.replace('Sint Truiden', 'St. Truiden', inplace=True)
    df.replace('Stourbridge', 'Stalybridge', inplace=True)
    df.replace('Southport', 'Staphorst', inplace=True)
    df.replace('CSA Steaua Bucuresti', 'Steaua Bucuresti', inplace=True)
    df.replace('SV Steinbach', 'Steinbach Haiger', inplace=True)
    df.replace('Stellenbosch FC', 'Stellenbosch', inplace=True)
    df.replace('Stenungsunds IF', 'Stenungsunds', inplace=True)
    df.replace('SFC Stern', 'Stern', inplace=True)
    df.replace('SK Steti', 'Steti', inplace=True)
    df.replace('Stjordals-Blink', 'Stjordals Blink', inplace=True)
    df.replace('FC Stockholm Internazionale', 'Stockholm Internazionale', inplace=True)
    df.replace('Stockport', 'Stockport County', inplace=True)
    df.replace('IFK Stocksund', 'Stocksund', inplace=True)
    df.replace('Stalybridge', 'Stourbridge', inplace=True)
    df.replace('FC Strani', 'Strani', inplace=True)
    df.replace('EB Streymur', 'Streymur', inplace=True)
    df.replace('SV Stripfing/Weiden', 'Stripfing', inplace=True)
    df.replace('Stromsgodset II', 'Stromsgodset 2', inplace=True)
    df.replace('SV Stuttgarter Kickers', 'Stutt. Kickers', inplace=True)
    df.replace('zzzStuttgart Kickers U19', 'Stuttgarter Kickers U19', inplace=True)
    df.replace('CD Subiza', 'Subiza', inplace=True)
    df.replace('ZFK Spartak Subotica (W)', 'Subotica (W)', inplace=True)
    df.replace('IA Sud America', 'Sud America', inplace=True)
    df.replace('FK Suduva', 'Suduva', inplace=True)
    df.replace('Vctoria Sulejowek', 'Sulejowek', inplace=True)
    df.replace('FK Sumqayit', 'Sumqayit', inplace=True)
    df.replace('FK Sutjeska', 'Sutjeska', inplace=True)
    df.replace('Sutton Utd', 'Sutton', inplace=True)
    df.replace('St. Peters FC', 'Svaty Peter', inplace=True)
    df.replace('Swit Skolwin', 'Swit Szczecin', inplace=True)
    df.replace('Tennis Borussia Berlin', 'TB Berlin', inplace=True)
    df.replace('The New Saints', 'TNS', inplace=True)
    df.replace('TS Galaxy FC', 'TS Galaxy', inplace=True)
    df.replace('FK Backa Topola', 'TSC', inplace=True)
    df.replace('Tabasalu JK', 'Tabasalu', inplace=True)
    df.replace('MAS Taborsko', 'Taborsko', inplace=True)
    df.replace('Taby FK', 'Taby', inplace=True)
    df.replace('Tacuary Asuncion', 'Tacuary', inplace=True)
    df.replace('Taichung Futuro FC', 'Taichung', inplace=True)
    df.replace('Taipei City Tatung', 'Taipei Vikings', inplace=True)
    df.replace('Talleres (RE)', 'Talleres', inplace=True)
    df.replace('Talleres', 'Talleres Cordoba', inplace=True)
    df.replace('Tall de Cordoba (Res)', 'Talleres Cordoba 2', inplace=True)
    df.replace('Tallinna Kalev II', 'Tallinna Kalev U21', inplace=True)
    df.replace('Tammeka Tartu', 'Tammeka', inplace=True)
    df.replace('JK Tammeka Tartu II', 'Tammeka Tartu (W)', inplace=True)
    df.replace('Tampa Bay Rowdies', 'Tampa Bay', inplace=True)
    df.replace('Tampines Rovers', 'Tampines', inplace=True)
    df.replace('Tamworth FC', 'Tamworth', inplace=True)
    df.replace('Tanjong Pagar United', 'Tanjong Pagar', inplace=True)
    df.replace('CA Tarazona', 'Tarazona', inplace=True)
    df.replace('AFC Odorheiu Secuiesc', 'Targu Secuiesc', inplace=True)
    df.replace('JK Welco Elekter', 'Tartu Welco', inplace=True)
    df.replace('FC Tatabanya', 'Tatabanya', inplace=True)
    df.replace('Taunton Town', 'Taunton', inplace=True)
    df.replace('Tauro FC', 'Tauro', inplace=True)
    df.replace('Carabobo FC', 'Tauro FC', inplace=True)
    df.replace('Team TG FF', 'Team TG', inplace=True)
    df.replace('Tecnico Universitario', 'Tecnico U.', inplace=True)
    df.replace('FC Telavi', 'Telavi', inplace=True)
    df.replace('SC Telstar', 'Telstar', inplace=True)
    df.replace('CA Temperley', 'Temperley', inplace=True)
    df.replace('Tensung FC', 'Tensung', inplace=True)
    df.replace('CD Tepatitlan De Morelos', 'Tepatitlan de Morelos', inplace=True)
    df.replace('FK Teplice B', 'Teplice B', inplace=True)
    df.replace('Nieciecza', 'Termalica B-B.', inplace=True)
    df.replace('CD Teruel', 'Teruel', inplace=True)
    df.replace('Teutonia 05 Ottensen', 'Teutonia Ottensen', inplace=True)
    df.replace('Thisted', 'Thisted FC', inplace=True)
    df.replace('Thitsar Arman FC', 'Thitsar Arman', inplace=True)
    df.replace('Thor', 'Thor Akureyri', inplace=True)
    df.replace('Three Bridges Fc', 'Three Bridges', inplace=True)
    df.replace('Throttur Reykjavik (W)', 'Throttur (W)', inplace=True)
    df.replace('FC Thun II', 'Thun II', inplace=True)
    df.replace('Tianjin Jinmen Tiger FC', 'Tianjin Jinmen Tiger', inplace=True)
    df.replace('Tigre (Res)', 'Tigre 2', inplace=True)
    df.replace('Tigres FC Zipaquira', 'Tigres', inplace=True)
    df.replace('Tiller IL', 'Tiller', inplace=True)
    df.replace('WSG Wattens', 'Tirol', inplace=True)
    df.replace('Tiszafuredi VSE', 'Tiszafuredi', inplace=True)
    df.replace('Tiverton Town', 'Tiverton', inplace=True)
    df.replace('Tlaxcala F.C', 'Tlaxcala', inplace=True)
    df.replace('Tobol Kostanay', 'Tobol', inplace=True)
    df.replace('SV Todesfelde 1928', 'Todesfelde', inplace=True)
    df.replace('B68 Toftir', 'Toftir', inplace=True)
    df.replace('UD Tomares', 'Tomares UD', inplace=True)
    df.replace('Real Tomayapo', 'Tomayapo', inplace=True)
    df.replace('Tombense MG', 'Tombense', inplace=True)
    df.replace('Tonbridge Angels', 'Tonbridge', inplace=True)
    df.replace('IK Tord', 'Tord', inplace=True)
    df.replace('Tormenta FC', 'Tormenta', inplace=True)
    df.replace('Tormenta FC', 'Toronto FC II', inplace=True)
    df.replace('SC Uniao Torreense U23', 'Torreense U23', inplace=True)
    df.replace('Sassari Torres', 'Torres', inplace=True)
    df.replace('Taiwan PC FC', 'Town FC', inplace=True)
    df.replace('Trafford FC', 'Trafford', inplace=True)
    df.replace('FCM TQS Traiskirchen', 'Traiskirchen', inplace=True)
    df.replace('ATSV Erlangen', 'Tranent', inplace=True)
    df.replace('TransINVEST Vilnius', 'Transinvest', inplace=True)
    df.replace('Transport United FC', 'Transport United', inplace=True)
    df.replace('CD Trasandino', 'Trasandino', inplace=True)
    df.replace('FK Trayal Krusevac', 'Trayal Krusevac', inplace=True)
    df.replace('Treaty United (W)', 'Treaty Utd (W)', inplace=True)
    df.replace('Trelleborgs', 'Trelleborg', inplace=True)
    df.replace('Trem AP', 'Trem', inplace=True)
    df.replace('FK AS Trencin (W)', 'Trencin (W)', inplace=True)
    df.replace('A.C. Trento S.C.S.D.', 'Trento', inplace=True)
    df.replace('AC Tres Coracoes U20', 'Tres Coracoes U20', inplace=True)
    df.replace('Treze', 'Treze PB', inplace=True)
    df.replace('Spartak Trnava', 'Trnava', inplace=True)
    df.replace('CD Trofense', 'Trofense', inplace=True)
    df.replace('FC Trollhattan', 'Trollhattan', inplace=True)
    df.replace('ESTAC Troyes', 'Troyes', inplace=True)
    df.replace('Truro City', 'Truro', inplace=True)
    df.replace('Tsirang FC', 'Tsirang', inplace=True)
    df.replace('TUS Koblenz', 'TuS Koblenz', inplace=True)
    df.replace('CA Tubarao', 'Tubarao', inplace=True)
    df.replace('FK Tukums 2000', 'Tukums 2000', inplace=True)
    df.replace('Tulevik Viljandi', 'Tulevik', inplace=True)
    df.replace('Tuna Luso PA', 'Tuna Luso', inplace=True)
    df.replace('SV Turkgucu-Ataspor', 'Turkgucu Munchen', inplace=True)
    df.replace('Turkspor Dortmund 2000', 'Turkspor Dortmund', inplace=True)
    df.replace('Pencin Turnov', 'Turnov', inplace=True)
    df.replace('Tusker FC', 'Tusker', inplace=True)
    df.replace('Tvaakers', 'Tvaaker', inplace=True)
    df.replace('FC Twente', 'Twente', inplace=True)
    df.replace('GKS Tychy', 'Tychy', inplace=True)
    df.replace('FC U Craiova 1948', 'U Craiova 1948', inplace=True)
    df.replace('Univ Catolica (Ecu)', 'U. Catolica', inplace=True)
    df.replace('Universidad Catolica (W', 'U. Catolica (W)', inplace=True)
    df.replace('Universitatea Cluj', 'U. Cluj', inplace=True)
    df.replace('Universidad de Chile', 'U. De Chile', inplace=True)
    df.replace('Universidad de Chile (W)', 'U. De Chile (W)', inplace=True)
    df.replace('Universidad de Concepcion', 'U. De Concepcion', inplace=True)
    df.replace('U de Concepcion (W)', 'U. De Concepcion (W)', inplace=True)
    df.replace('Union Espanola', 'U. Espanola', inplace=True)
    df.replace('Union Magdalena', 'U. Magdalena', inplace=True)
    df.replace('Universitario de Deportes', 'U. de Deportes', inplace=True)
    df.replace('Tigres', 'U.A.N.L.- Tigres', inplace=True)
    df.replace('Pumas UNAM', 'U.N.A.M.- Pumas', inplace=True)
    df.replace('Pumas UNAM (W)', 'U.N.A.M.- Pumas (W)', inplace=True)
    df.replace('Uai Urquiza', 'UAI Urquiza', inplace=True)
    df.replace('UCD', 'UC Dublin', inplace=True)
    df.replace('Ibiza Eivissa', 'UD Ibiza', inplace=True)
    df.replace('Una Strassen', 'UNA Strassen', inplace=True)
    df.replace('UNAN Managua', 'UNAN-Managua', inplace=True)
    df.replace('Up Langreo', 'UP Langreo', inplace=True)
    df.replace('Lobos UPNFM', 'UPNFM', inplace=True)
    df.replace('UAI Urquiza', 'Uai Urquiza', inplace=True)
    df.replace('CSK Uhersky Brod', 'Uhersky Brod', inplace=True)
    df.replace('Ullensaker Kisa', 'Ull/Kisa', inplace=True)
    df.replace('SSV Ulm', 'Ulm', inplace=True)
    df.replace('SSV Ulm 1846 U19', 'Ulm U19', inplace=True)
    df.replace('Ulsan Citizen FC', 'Ulsan Citizen', inplace=True)
    df.replace('Ulsan Hyundai Horang-i', 'Ulsan HD', inplace=True)
    df.replace('Ulsan Hyundai Horang-i', 'Ulsan Hyundai', inplace=True)
    df.replace('Everton', 'Everton', inplace=True)
    df.replace('Zamora FC', 'Umea FC', inplace=True)
    df.replace('Umm Salal', 'Umm-Salal', inplace=True)
    df.replace('Uniao EC Rondonopolis', 'Uniao Rondonopolis', inplace=True)
    df.replace('Uniao Suzano AC U20', 'Uniao Suzano U20', inplace=True)
    df.replace('1. FC Union Berlin U19', 'Union Berlin U19', inplace=True)
    df.replace('Union Clodiense Chioggia', 'Union Clodiense', inplace=True)
    df.replace('Rochefort', 'Union Rochefortoise', inplace=True)
    df.replace('CA Union de Sunchales', 'Union Sunchales', inplace=True)
    df.replace('UT Petenge', 'Union Titus Petange', inplace=True)
    df.replace('Union Santa Fe', 'Union de Santa Fe', inplace=True)
    df.replace('CA Union Santa Fe (Res)', 'Union de Santa Fe 2', inplace=True)
    df.replace('ACS Unirea Branistea', 'Unirea Branistea', inplace=True)
    df.replace('ASA Unirea Ungheni', 'Unirea Ungheni', inplace=True)
    df.replace('We United FC', 'United City', inplace=True)
    df.replace('United Sports Club', 'United SC', inplace=True)
    df.replace('Univ Catolica (Chile)', 'Univ Catolica (Ecu)', inplace=True)
    df.replace('Universitatea Craiova', 'Univ. Craiova', inplace=True)
    df.replace('CS Universitar din Alba I', 'Univ. din Alba Iulia', inplace=True)
    df.replace('Universidad de Venezuela', 'Universidad Central', inplace=True)
    df.replace('Universidad Cesar Vall', 'Universidad Cesar Vallejo', inplace=True)
    df.replace('Universidad Guadalajara', 'Universidad de Chile', inplace=True)
    df.replace('Univ de Chile (W)', 'Universidad de Chile (W)', inplace=True)
    df.replace('SPVGG Unterhaching II', 'Unterhaching II', inplace=True)
    df.replace('FC Urartu', 'Urartu', inplace=True)
    df.replace('Urawa', 'Urawa Reds', inplace=True)
    df.replace('SV Urk', 'Urk', inplace=True)
    df.replace('Uruguay Montevideo FC', 'Uruguay Montevideo', inplace=True)
    df.replace('Cuba U20', 'Uruguay U20', inplace=True)
    df.replace('Usti Nad Labem', 'Usti nad Labem', inplace=True)
    df.replace('Utebo CF', 'Utebo FC', inplace=True)
    df.replace('FC Utrecht', 'Utrecht', inplace=True)
    df.replace('Utsiktens', 'Utsikten', inplace=True)
    df.replace('Nagasaki', 'V-Varen Nagasaki', inplace=True)
    df.replace('Vard Haugesund', 'V. Haugesund', inplace=True)
    df.replace('VSK Aarhus FC', 'VSK Aarhus', inplace=True)
    df.replace('FCV', 'Vaajakoski', inplace=True)
    df.replace('FC Vaduz', 'Vaduz', inplace=True)
    df.replace('Vaengir Jupiters', 'Vaengirs', inplace=True)
    df.replace('TJ Valasske Mezirici', 'Valasske Mezirici', inplace=True)
    df.replace('Valerenga II', 'Valerenga 2', inplace=True)
    df.replace('Valladolid B', 'Valladolid Promesas', inplace=True)
    df.replace('Valmieras FK', 'Valmiera', inplace=True)
    df.replace('Valur Reykjavik (W)', 'Valur (W)', inplace=True)
    df.replace('Fram Reykavik (W)', 'Valur Reykjavik (W)', inplace=True)
    df.replace('Vancouver Whitecaps II', 'Vancouver Whitecaps 2', inplace=True)
    df.replace('Vanraure Hachinohe', 'Vanraure', inplace=True)
    df.replace('Varbergs BoIS', 'Varberg', inplace=True)
    df.replace('Vardar Skopje', 'Vardar', inplace=True)
    df.replace('CD Vargas Torres', 'Vargas Torres', inplace=True)
    df.replace('Kari', 'Varzim', inplace=True)
    df.replace('Vasalunds IF', 'Vasalund', inplace=True)
    df.replace('Vasco da Gama', 'Vasco', inplace=True)
    df.replace('V√§xj√∂ DFF (W)', 'Vaxjo DFF (W)', inplace=True)
    df.replace('ACS Vedita Colonesti MS', 'Vedita Colonesti', inplace=True)
    df.replace('Sendai', 'Vegalta Sendai', inplace=True)
    df.replace('SK Slavia Vejprnice', 'Vejprnice', inplace=True)
    df.replace('Fk Velez Mostar', 'Velez Mostar', inplace=True)
    df.replace('Velez Sarsfield (Res)', 'Velez Sarsfield 2', inplace=True)
    df.replace('Velo Clube Rioclarense U20', 'Velo Clube U20', inplace=True)
    df.replace('Venados FC', 'Venados', inplace=True)
    df.replace('Vendsyssel FF', 'Vendsyssel', inplace=True)
    df.replace('VVV Venlo', 'Venlo', inplace=True)
    df.replace('Ventura County FC', 'Ventura County', inplace=True)
    df.replace('Veraguas FC', 'Veraguas', inplace=True)
    df.replace('Verdal IL', 'Verdal', inplace=True)
    df.replace('Tokyo-V', 'Verdy', inplace=True)
    df.replace('Veres Rivne', 'Veres-Rivne', inplace=True)
    df.replace('Versailles 78 FC', 'Versailles', inplace=True)
    df.replace('IBV', 'Vestmannaeyjar', inplace=True)
    df.replace('IF Vestri', 'Vestri', inplace=True)
    df.replace('FC Vevey', 'Vevey', inplace=True)
    df.replace('VFB Oldenburg', 'VfB Oldenburg', inplace=True)
    df.replace('VfL 07 Bremen', 'VfL Bremen', inplace=True)
    df.replace('CD Victoria', 'Victoria', inplace=True)
    df.replace('Victoriano Arenas', 'Victoriano A.', inplace=True)
    df.replace('ACS Viitorul Tg Jiu', 'Viitorul Tg. Jiu', inplace=True)
    df.replace('Viking FK (W)', 'Viking (W)', inplace=True)
    df.replace('Viking FK II', 'Viking 2', inplace=True)
    df.replace('Vikingur Gota', 'Vikingur', inplace=True)
    df.replace('HK Vikingur (W)', 'Vikingur Reykjavik (W)', inplace=True)
    df.replace('CD Victoria', 'Viktoria', inplace=True)
    df.replace('Viktoria FC-Szombathely (W)', 'Viktoria (W)', inplace=True)
    df.replace('Vila Nova', 'Vila Nova FC', inplace=True)
    df.replace('Villefranche Beaujolais', 'Villefranche', inplace=True)
    df.replace('FC 08 Villingen', 'Villingen', inplace=True)
    df.replace('DJK Vilzing', 'Vilzing', inplace=True)
    df.replace('Vineta Wolin', 'Vineta W.', inplace=True)
    df.replace('SS Virtus', 'Virtus', inplace=True)
    df.replace('SS Virtus Verona 1921', 'Virtus Verona', inplace=True)
    df.replace('Visakha FC', 'Visakha', inplace=True)
    df.replace('Kobe', 'Vissel Kobe', inplace=True)
    df.replace('Vitesse Arnhem', 'Vitesse', inplace=True)
    df.replace('EC Vitoria Salvador', 'Vitoria', inplace=True)
    df.replace('Guimaraes', 'Vitoria Guimaraes', inplace=True)
    df.replace('FC Sellier & Bellot Vlasim', 'Vlasim', inplace=True)
    df.replace('NFC Volos', 'Volos', inplace=True)
    df.replace('Vorskla', 'Vorskla Poltava', inplace=True)
    df.replace('Sk Vorwarts Steyr', 'Vorwarts Steyr', inplace=True)
    df.replace('SC Vorwarts-Wacker 04', 'Vorwarts-Wacker', inplace=True)
    df.replace('SpVgg Vreden', 'Vreden', inplace=True)
    df.replace('FK Vrsac', 'Vrsac', inplace=True)
    df.replace('Tatran Vsechovice', 'Vsechovice', inplace=True)
    df.replace('SK Vysoke Myto', 'Vysoke Myto', inplace=True)
    df.replace('RKC Waalwijk', 'Waalwijk', inplace=True)
    df.replace('FC Astoria Walldorf', 'Walldorf', inplace=True)
    df.replace('SV Wallern', 'Wallern/St Marienkirchen', inplace=True)
    df.replace('SV Wals-Grunau', 'Wals-Grunau', inplace=True)
    df.replace('Wanderers (Uru)', 'Wanderers', inplace=True)
    df.replace('Zulte-Waregem', 'Waregem', inplace=True)
    df.replace('Kari', 'Wari', inplace=True)
    df.replace('Warrington Town', 'Warrington', inplace=True)
    df.replace('FC Wegberg-Beeck', 'Wegberg-Beeck', inplace=True)
    df.replace('Wehen Wiesbaden', 'Wehen', inplace=True)
    df.replace('SPVGG Weiden', 'Weiden', inplace=True)
    df.replace('Welling Utd', 'Welling', inplace=True)
    df.replace('Wexford F.C', 'Wexford', inplace=True)
    df.replace('KFC Wezel', 'Wezel Sport', inplace=True)
    df.replace('SC Wiedenbruck', 'Wiedenbruck', inplace=True)
    df.replace('Wiener SK', 'Wiener Sport-Club', inplace=True)
    df.replace('Wiener Victoria', 'Wiener Viktoria', inplace=True)
    df.replace('GKS Wikielec', 'Wikielec', inplace=True)
    df.replace('FC Wil', 'Wil', inplace=True)
    df.replace('SV Wilhelmshaven', 'Wilhelmshaven', inplace=True)
    df.replace('Jorge Wilstermann', 'Wilstermann', inplace=True)
    df.replace('Wingate and Finchley', 'Wingate & Finchley', inplace=True)
    df.replace('Wisla Krakow', 'Wisla', inplace=True)
    df.replace('FC Anker Wismar', 'Wismar', inplace=True)
    df.replace('Worksop Town', 'Worksop', inplace=True)
    df.replace('Wormatia Worms', 'Worms', inplace=True)
    df.replace('Wuppertaler', 'Wuppertal', inplace=True)
    df.replace('XV Jau U20', 'XV de Jau U20', inplace=True)
    df.replace('Neuchatel Xamax', 'Xamax', inplace=True)
    df.replace('Xerez', 'Xerez D.F.C.', inplace=True)
    df.replace('Xian Chongde Ronghai', 'Xian Ronghai', inplace=True)
    df.replace('Huehueteco Xinabajul', 'Xinabajul', inplace=True)
    df.replace('Yokohama SCC', 'YSCC', inplace=True)
    df.replace('CD Union Sur Yaiza', 'Yaiza', inplace=True)
    df.replace('Matsumoto', 'Yamaga', inplace=True)
    df.replace('Yangon United', 'Yangon Utd', inplace=True)
    df.replace('Yangpyeong FC', 'Yangpyeong', inplace=True)
    df.replace('Al Yarmouk', 'Yarmouk', inplace=True)
    df.replace('Yate Town FC', 'Yate Town', inplace=True)
    df.replace('Yeclano Deportivo', 'Yeclano', inplace=True)
    df.replace('Elimai FC  ', 'Yelimay Semey', inplace=True)
    df.replace('Yeoju FC', 'Yeoju Citizen', inplace=True)
    df.replace('Yokohama FM', 'Yokohama F. Marinos', inplace=True)
    df.replace('York9', 'York Utd', inplace=True)
    df.replace('Courts Young Lions', 'Young Lions', inplace=True)
    df.replace('Ypiranga RS', 'Ypiranga FC', inplace=True)
    df.replace('CSD Yupanqui', 'Yupanqui', inplace=True)
    df.replace('Yverdon Sport', 'Yverdon', inplace=True)
    df.replace('Zlate Moravce', 'Z. Moravce-Vrable', inplace=True)
    df.replace('ZED FC', 'ZED', inplace=True)
    df.replace('Mineros de Zacatecas', 'Zacatecas Mineros', inplace=True)
    df.replace('Zaglebie Lubin', 'Zaglebie', inplace=True)
    df.replace('Zaglebie Lubin II', 'Zaglebie II', inplace=True)
    df.replace('Zalaegerszeg', 'Zalaegerszegi', inplace=True)
    df.replace('VMFD Zalgiris', 'Zalgiris', inplace=True)
    # df.replace('Zamora FC', 'Zamora', inplace=True)
    df.replace('Zamora', 'Zamora', inplace=True)
    df.replace('FK Slavoj Zatec', 'Zatec', inplace=True)
    df.replace('Zawisza Bydgoszcz', 'Zawisza', inplace=True)
    df.replace('FC Zdas Zdar nad Sazavou', 'Zdar na Sazavou', inplace=True)
    df.replace('Mladost Zdralovi', 'Zdralovi', inplace=True)
    df.replace('Municipal Perez Zeledon', 'Zeledon', inplace=True)
    df.replace('Sokol Zeleznice', 'Zeleznice', inplace=True)
    df.replace('Zhejiang Hangzhou Xizi (W)', 'Zhejiang (W)', inplace=True)
    df.replace('Zhejiang Greentown', 'Zhejiang Professional', inplace=True)
    df.replace('Zhenys', 'Zhenis', inplace=True)
    df.replace('FC Zhetysu', 'Zhetysu Taldykorgan', inplace=True)
    df.replace('MSK Zilina II', 'Zilina B', inplace=True)
    df.replace('Fastav Zlin U19', 'Zlin U19', inplace=True)
    df.replace('Zlin', 'Zlinsko', inplace=True)
    df.replace('FC Zurich', 'Zurich', inplace=True)
    df.replace('FC Zurich II', 'Zurich II', inplace=True)
    df.replace('FC Zuzenhausen', 'Zuzenhausen', inplace=True)
    df.replace('Lokomotiva Zvolen', 'Zvolen', inplace=True)
    df.replace('FSV Zwickau', 'Zwickau', inplace=True)
    df.replace('PEC Zwolle', 'Zwolle', inplace=True)
    df.replace('Slovan Liberec B', 'Liberec B', inplace=True)
    df.replace('FK Jablonec B', 'Jablonec B', inplace=True)
    df.replace('Hradec Kralove', 'Hradec Kralove B', inplace=True)
    df.replace('Psis Semarang', 'PSIS Semarang', inplace=True)
    df.replace('Svay Rieng FC', 'Svay Rieng', inplace=True)
    df.replace('SP Falcons FC', 'Falcons', inplace=True)
    df.replace('Chainat Hornbill', 'Chainat', inplace=True)
    df.replace('Persebaya Surabaya', 'Persebaya', inplace=True)
    df.replace('Spartans WFC (W)', 'Spartans (W)', inplace=True)
    df.replace('Montrose FC (W)', 'Montrose (W)', inplace=True)
    df.replace('IFK Kumla', 'Kumla', inplace=True)
    df.replace('Nakhon Ratchasima', 'Nakhon Ratchasima FC', inplace=True)
    df.replace('BSC Young Boys II', 'Young Boys II', inplace=True)
    df.replace('Connahs Quay', 'Connahs Q.', inplace=True)
    df.replace('Union Luxembourg', 'Racing Luxembourg', inplace=True)
    df.replace('KF Shkupi', 'Shkupi', inplace=True)
    df.replace('SK Benatky nad Jizerou', 'Benatky n. Jiz.', inplace=True)
    df.replace('FC Shirak', 'FC Strani', inplace=True)
    df.replace('Deportivo Nueva Concepcion', 'Deportes Concepcion', inplace=True)
    df.replace('Fk Jedinstvo Bijelo Polje', 'FK Jedinstvo Ub', inplace=True)
    df.replace('Wanderers (Uru)', 'WS Wanderers U23', inplace=True)
    df.replace('Aurora Pro Patria 1919', 'Pro Patria', inplace=True)
    df.replace('Briton Ferry Llansawel', 'Briton Ferry', inplace=True)
    df.replace('Csakvar', 'Csakvari', inplace=True)
    df.replace('FC Ajka', 'Ajka', inplace=True)
    df.replace('Gimnasia de La Plata (W)', 'Gimnasia L.P. (W)', inplace=True)
    df.replace('FE Grama', 'Grama', inplace=True)
    df.replace('UE Vilassar de Mar', 'Vilassar de Mar', inplace=True)
    df.replace('Excursionistas (W)', 'Excursionistas(W)', inplace=True)
    df.replace('UNIVERSIDAD O&M', 'Universidad O&M', inplace=True)
    df.replace('CSG San Martin Formosa', 'CSG San M Formosa', inplace=True)
    df.replace('Estudiantes Rio Cuarto', 'Estudiantes Rio ', inplace=True)
    df.replace('AZ Picerno ASD', 'Picerno', inplace=True)
    df.replace('Everton De Vina', 'Everton', inplace=True)
    df.replace('CS Herediano', 'Cs Herediano', inplace=True)
    df.replace('Taipei Vikings', 'Taipei City Tatung', inplace=True)
    df.replace('Banik Most', 'Banik Most-Sous', inplace=True)
    df.replace('FK Dukla Praha B', 'Dukla Prague B', inplace=True)
    df.replace('Bali Utd Pusam', 'Bali United', inplace=True)
    df.replace('TJ Prestice', 'Trebatice', inplace=True)
    df.replace('Mgladbach U19', 'B. Monchengladbach U19', inplace=True)
    df.replace('Angkor Tiger FC', 'Angkor Tiger', inplace=True)
    df.replace('Pogon Tczew (W)', 'Tczew (W)', inplace=True)
    df.replace('Khangarid Klub', 'Khangarid', inplace=True)
    df.replace('Ayutthaya United', 'Ayutthaya Utd', inplace=True)
    df.replace('Pss Sleman', 'PSS Sleman', inplace=True)
    df.replace('Jonsereds IF', 'Jonsereds', inplace=True)
    df.replace('Muangthong Utd', 'Muang Thong Utd', inplace=True)
    df.replace('KuPS Kuopio (W)', 'KuPs (W)', inplace=True)
    df.replace('Honefoss BK Women', 'Honefoss (W)', inplace=True)
    df.replace('SV Sonsbeck', 'MSK Senec', inplace=True)
    df.replace('Polokwane City', 'Polokwane', inplace=True)
    df.replace('FC Wiltz 71', 'Wiltz', inplace=True)
    df.replace('Erzurum BB', 'Erzurumspor', inplace=True)
    df.replace('Ytterhogdals IK', 'Ytterhogdal', inplace=True)
    df.replace('FC Voska Sport', 'Voska Sport', inplace=True)
    df.replace('FK Sileks', 'Sileks', inplace=True)
    df.replace('SK Petrin Plzen', 'Petrin Plzen', inplace=True)
    df.replace('AEK Larnaca', 'AEL Larissa', inplace=True)
    df.replace('Penybont FC', 'Penybont', inplace=True)
    df.replace('BVSC Zuglo', 'BVSC-Zuglo', inplace=True)
    df.replace('Bekescsaba', 'Bekescsaba 1912', inplace=True)
    df.replace('Szeged 2011', 'Szeged', inplace=True)
    df.replace('SD Gernika Club', 'Gernika', inplace=True)
    df.replace('Saudi Arabia Women', 'Saudi Arabia (W)', inplace=True)
    df.replace('Taranto Sport', 'Taranto', inplace=True)
    df.replace('CA San Lorenzo de Almagro (W)', 'San Lorenzo Almagro (W)', inplace=True)
    df.replace('Gimnasia Conc del Urugu', 'Gimnasia Conc del Uruguay', inplace=True)
    df.replace('Atletico Sarmie', 'Atletico Sarmiento', inplace=True)
    df.replace('9deJulioRafaela', '9 de J Rafaela', inplace=True)
    df.replace('Circulo Deportivo Otamen', 'Circulo Deportivo Otamendi', inplace=True)
    df.replace('Team Altamura', 'Altamura', inplace=True)
    df.replace('CA Central Norte', 'CA Central Nort', inplace=True)
    df.replace('Arema Cronus', 'Arema FC', inplace=True)
    df.replace('Indija', 'FK Indjija', inplace=True)
    df.replace('Deportivo Carapegua', 'Sp. Carapegua', inplace=True)
    df.replace('Fortaleza EC', 'Fortaleza', inplace=True)
    df.replace('Guadalupe F.C', 'Guadalupe FC', inplace=True)
    df.replace('Dewa United FC', 'Dewa United', inplace=True)
    df.replace('SK Poltava', 'SC Poltava', inplace=True)
    df.replace('Fleetwood Town U21', 'Fleetwood U21', inplace=True)
    df.replace('Khonkaen United', 'Khonkaen Utd.', inplace=True)
    df.replace('Oleksandria', 'Oleksandriya', inplace=True)
    df.replace('Sheff Utd U21', 'Sheffield Utd U21', inplace=True)
    df.replace('Sarpsborg 08 FF II', 'Sarpsborg 08 2', inplace=True)
    df.replace('Gaziantep FK', 'Gaziantep', inplace=True)
    df.replace('Uni San Martin', 'U. San Martin', inplace=True)
    df.replace('Tigres (W)', 'U.A.N.L.- Tigres (W)', inplace=True)
    df.replace('CD Illescas', 'Illescas', inplace=True)
    df.replace('Al Gharafa', 'Al-Gharafa', inplace=True)
    df.replace('CD Caspe', 'Caspe', inplace=True)
    df.replace('Uniao Suzano AC', 'Uniao Suzano', inplace=True)
    # df.replace('Rangers', 'Carrick Rangers', inplace=True)
    df.replace('Coventry City U21', 'Coventry U21', inplace=True)
    df.replace('Wigan Athletic U21', 'Wigan U21', inplace=True)
    df.replace('Al Ahli', 'Al Ahli (UAE)', inplace=True)
    df.replace('Sokol Brozany', 'Brozany', inplace=True)
    df.replace('Skeid Fotball 2', 'Skeid 2', inplace=True)
    df.replace('Brandenburger SC Sud', 'Brandenburger', inplace=True)
    # df.replace('Central Cordoba', 'Central Cordoba (SdE)', inplace=True)
    df.replace('Bristol Rovers', 'Boston River', inplace=True)
    df.replace('Mirassol (Res)', 'Mirassol B', inplace=True)
    df.replace('CDA Navalcarnero', 'Navalcarnero', inplace=True)
    df.replace('Cardiff City U21', 'Cardiff U21', inplace=True)
    df.replace('Emami East Bengal FC', 'East Bengal', inplace=True)
    df.replace('FCM Baia Mare', 'Baia Mare', inplace=True)
    df.replace('ACS Kids Tampa Brasov', 'Kids Tampa Brasov', inplace=True)
    df.replace('CSM Ramnicu-Valcea', 'Ramnicu Valcea', inplace=True)
    df.replace('CSO Petrolul Potcoava', 'Petrolul Potcoava', inplace=True)
    df.replace('Gloria Popesti-Leordeni', 'Popesti Leordeni', inplace=True)
    df.replace('CSM Unirea Alba Iulia', 'Unirea Alba-Iulia', inplace=True)
    df.replace('CD Feirense U19', 'Feirense U19', inplace=True)
    df.replace('CD Mafra U19', 'Mafra U19', inplace=True)
    df.replace('FC Energie Cottbus U19', 'Cottbus U19', inplace=True)
    df.replace('FC Ingolstadt 04 U19', 'Ingolstadt U19', inplace=True)
    df.replace('Bayern Munich U19', 'Bayern U19', inplace=True)
    df.replace('SC Paderborn 07 U19', 'Paderborn U19', inplace=True)
    df.replace('Fortuna Dusseldorf U19', 'Dusseldorf U19', inplace=True)
    df.replace('St Jakob Ros', 'St. Jakob/Ros', inplace=True)
    df.replace('AC Torrellano', 'Torrellano', inplace=True)
    df.replace('CD Alaves B', 'Alaves B', inplace=True)
    df.replace('EC Taubate (W)', 'Taubate (W)', inplace=True)
    df.replace('St Pauli U19', 'Sao Paulo U20', inplace=True)
    df.replace('Comunicaciones', 'Comunicaciones B Aires', inplace=True)
    df.replace('Levante UD (W)', 'Levante (W)', inplace=True)
    df.replace('ASD Calcio Brusaporto', 'Brusaporto', inplace=True)
    df.replace('Sheff Wed U21', 'Sheffield Wed U21', inplace=True)
    df.replace('FC Zalau', 'CSM Zalau', inplace=True)
    df.replace('Gloria 2018 BN', 'Gloria 2018 Bistrita', inplace=True)
    df.replace('Dunarea Calarasi', 'Calarasi', inplace=True)
    df.replace('CS Tunari', 'Tunari', inplace=True)
    df.replace('Torreense Futebol U19', 'Torreense U19', inplace=True)
    df.replace('CF Os Belenenses U19', 'Belenenses U19', inplace=True)
    df.replace('SG Dynamo Dresden U19', 'Dresden U19', inplace=True)
    df.replace('Hertha BSC Berlin U19', 'Hertha U19', inplace=True)
    df.replace('SpVgg Unterhaching U19', 'Unterhaching U19', inplace=True)
    df.replace('Schalke U19', 'FC Schalke U19', inplace=True)
    df.replace('VST Volkermarkt', 'Volkermarkt', inplace=True)
    df.replace('Torrent CF', 'Torrent', inplace=True)
    df.replace('ATSV Erlangen', 'TSV Nordlingen', inplace=True)
    df.replace('FC Erzgebirge Aue U19', 'SC Freiburg U19', inplace=True)
    df.replace('Athletic Bilbao B', 'Ath Bilbao B', inplace=True)
    df.replace('AD Ceuta FC', 'Ceuta', inplace=True)
    df.replace('CD Lealtad', 'Lealtad', inplace=True)
    df.replace('Pinda SC (W)', 'Pinda Ferroviaria (W)', inplace=True)
    df.replace('Santos FC (W)', 'Santos (W)', inplace=True)
    df.replace('Huracan', 'Genesis Huracan', inplace=True)
    df.replace('CD Arnedo', 'Arnedo', inplace=True)
    df.replace('Sokol Kleczew', 'Kleczew', inplace=True)
    df.replace('Hapoel Tel Aviv', 'Hapoel Petah Tikva', inplace=True)
    df.replace('Sola FK', 'Sola', inplace=True)
    df.replace('Vikingur Reykjavik (W)', 'HK Vikingur (W)', inplace=True)
    df.replace('SC Ortmann', 'Ortmann', inplace=True)
    df.replace('Vikingur Reykjavik', 'KR Reykjavik', inplace=True)
    df.replace('TSV Karlburg', 'Karlburg', inplace=True)
    df.replace('SV Auersmacher', 'Auersmacher', inplace=True)
    df.replace('Lorca Deportiva CF', 'Lorca Deportiva', inplace=True)
    df.replace('Estudiantes de LP (Res)', 'Estudiantes L.P. 2', inplace=True)
    df.replace('RB Keflavik', 'Keflavik', inplace=True)
    df.replace('ACS Aro Muscelul C-Lung', 'Muscel', inplace=True)
    df.replace('FC Pyunik', 'Pyunik Yerevan', inplace=True)
    df.replace('Eisbachtaler Sportfreunde', 'Eisbachtal', inplace=True)
    df.replace('Instituto de Cordoba (Res)', 'Instituto 2', inplace=True)
    df.replace('One Knoxville SC', 'One Knoxville', inplace=True)
    df.replace('FC La Libertad', 'Libertad FC', inplace=True)
    df.replace('UD Santa Marta', 'Santa Marta Tormes', inplace=True)
    df.replace('Hull City U21', 'Hull U21', inplace=True)
    df.replace('Gandzasar Kapan', 'Gandzasar FC II', inplace=True)
    df.replace('Odisha', 'Odisha FC', inplace=True)
    df.replace('Vukovar', 'Vukovar 1991', inplace=True)
    # df.replace('Gorica', 'ND Gorica', inplace=True)
    df.replace('FC Bergerac', 'Bergerac', inplace=True)
    df.replace('Heiligenkreuz am Waasen', 'Heiligenkreuz', inplace=True)
    df.replace('AGF Aarhus (W)', 'Aarhus (W)', inplace=True)
    df.replace('Vendee Les Herbiers', 'Les Herbiers', inplace=True)
    df.replace('Aubagne FC', 'Aubagne', inplace=True)
    df.replace('Leeds United U21', 'Leeds U21', inplace=True)
    df.replace('KMSK Deinze U21', 'Deinze U21', inplace=True)
    df.replace('Al Arabi Kuwait', 'Al Arabi (QAT)', inplace=True)
    df.replace('Jataiense U20', 'Cesena U20', inplace=True)
    df.replace('Crusaders Strikers (W)', 'Crusaders (W)', inplace=True)
    df.replace('Breidablik (W)', 'Grindavik (W)', inplace=True)
    df.replace('Guarani (Par)', 'Guarani', inplace=True)
    df.replace('Carolina Core FC', 'Carolina Core', inplace=True)
    df.replace('Deportivo Cali (W)', 'Dep. Cali (W)', inplace=True)
    df.replace('ISI Dangkor Senchey FC', 'Dangkor', inplace=True)
    df.replace('AB', 'AB Copenhagen', inplace=True)
    df.replace('SV Tillmitsch', 'Tillmitsch', inplace=True)
    df.replace('Gobelins F.C.', 'Paris 13 Atl.', inplace=True)
    df.replace('Seraing', 'Seraing Utd', inplace=True)
    df.replace('KS Wiazownica', 'Wiazownica', inplace=True)
    df.replace('FC Wettswil-Bonstetten', 'Wettswil-Bonstetten', inplace=True)
    df.replace('FC Dardania Lausanne', 'Dardania Lausanne', inplace=True)
    df.replace('Stoke U21', 'Stoke City U21', inplace=True)
    df.replace('Man Utd U21', 'Manchester Utd U21', inplace=True)
    df.replace('AC Taverne', 'Taverne', inplace=True)
    df.replace('Westerlo (Res)', 'Westerlo U21', inplace=True)
    df.replace('Al Arabi Kuwait', 'Al Arabi', inplace=True)
    df.replace('Admira Wacker', 'Admira', inplace=True)
    df.replace('Flint Town United', 'Flint', inplace=True)
    df.replace('Taipei Play One (W)', 'Taipei Bravo (W)', inplace=True)
    df.replace('New Taipei Hang Yuen (W)', 'Hang Yuan (W)', inplace=True)
    df.replace('Hualian (W)', 'Hualien (W)', inplace=True)
    df.replace('Kanchanaburi FC', 'Kanchanaburi', inplace=True)
    df.replace('TSV Schott Mainz', 'Schott Mainz', inplace=True)
    df.replace('SV Sandhausen U19', 'Sandhausen U19', inplace=True)
    df.replace('Lampang FC', 'Lampang', inplace=True)
    df.replace('Chanthaburi FC', 'Chanthaburi', inplace=True)
    df.replace('Odense BK (W)', 'Odense Q (W)', inplace=True)
    df.replace('Asane Football (W)', 'Asane (W)', inplace=True)
    df.replace('KuPS Kuopio (W)', 'GKS Katowice (W)', inplace=True)
    df.replace('SC Villa', 'Villa', inplace=True)
    df.replace('Club F de la Mora', 'Fernando de la Mora', inplace=True)
    df.replace('Club Brugge B', 'Club Brugge (W)', inplace=True)
    df.replace('Spartans', 'Spartak II', inplace=True)
    df.replace('CA Mineiro (W)', 'Cruzeiro (W)', inplace=True)
    df.replace('CSD Rangers Talca', 'Cove Rangers', inplace=True)
    df.replace('Elimai FC', 'Elimai FC  ', inplace=True)
    df.replace('FC Suhareka', 'Suhareka', inplace=True)
    df.replace('El Kanemi Warriors', 'Olympia Warriors', inplace=True)
    df.replace("Racing de Ferrol","Ferrol", inplace=True)
    df.replace('Drava (Slovenia)', 'Moravska Slavia', inplace=True)
    df.replace('Cibalia Vinkovci', 'Cibalia', inplace=True)
    df.replace('HNK Orijent 1919', 'Orijent', inplace=True)
    df.replace('NK Bilje', 'Bilje', inplace=True)
    df.replace('FK BSK Banja Luka', 'BSK Banja Luka', inplace=True)
    df.replace('FC Mendrisio Stabio', 'Mendrisio', inplace=True)
    df.replace('Waasland-Beveren', 'Beveren', inplace=True)
    df.replace('Fluminense RJ (W)', 'Fluminense (W)', inplace=True)
    df.replace('CS Constantine', 'Constantine', inplace=True)
    df.replace('Molenbeek', 'Holbaek', inplace=True)
    df.replace('Deportivo Pereira', 'Deportivo Armenio', inplace=True)
    df.replace('CA Juventus', 'YF Juventus', inplace=True)
    df.replace('Portuguesa SP', 'Portuguesa FC', inplace=True)
    df.replace('GKS Jastrzebie', 'Gks Jastrzebie', inplace=True)
    df.replace('Kazma SC', 'Kazma Sc', inplace=True)
    df.replace('Ferroviaria(W)', 'Ferroviaria (W)', inplace=True)
    df.replace('Union de Touarga', 'Union Touarga', inplace=True)
    df.replace('Gremio FBPA (W)', 'Gremio FBPA U20', inplace=True)
    df.replace('Deportivo Mictlan', 'Deportivo Ocotal', inplace=True)
    df.replace('Kaohsiung Sunny Bank (W)', 'Kaohsiung (W)', inplace=True)
    df.replace('Inter Taoyuan (W)', 'Taoyuan Mars (W)', inplace=True)
    df.replace('Muscelul Campulung', 'Campulung', inplace=True)
    df.replace('Gyeongju Hydro', 'Gyeongju Hydro & NP', inplace=True)
    df.replace('APLG Gdansk (W)', 'Gdansk (W)', inplace=True)
    df.replace('Taichung Blue Whale (W)', 'Taichung Blue (W)', inplace=True)
    df.replace('Linkopings FC (W)', 'Linkoping (W)', inplace=True)
    df.replace('Phrae United', 'Orapa United', inplace=True)
    df.replace('PSIS Semarang', 'Psis Semarang', inplace=True)
    df.replace('Sindri', 'Sirius', inplace=True)
    df.replace('Jwaneng Galaxy FC', 'Jwaneng Galaxy', inplace=True)
    df.replace('Club Atletico Tembetary', 'Atl. Tembetary', inplace=True)
    df.replace('Carrick Rangers', 'Brora Rangers', inplace=True)
    df.replace('Brackley Town', 'Crawley Town', inplace=True)
    df.replace('Rushall Olympic', 'Rushall', inplace=True)
    df.replace('Al Aqaba', 'Aqaba', inplace=True)
    df.replace('KF Dukagjini', 'Dukagjini', inplace=True)
    df.replace('NK Tosk Tesanj', 'TOSK Tesanj', inplace=True)
    df.replace('CSD Tellioz', 'CD Castellon', inplace=True)
    df.replace('NK Croatia Zmijavci', 'Croatia Zmijavci', inplace=True)
    df.replace('NK Jadran Dekani', 'Jadran Dekani', inplace=True)
    df.replace('FK Romanija Pale', 'Romanija Pale', inplace=True)
    df.replace('Teungueth FC', 'Teungueth', inplace=True)
    df.replace('Melita FC', 'Melita', inplace=True)
    df.replace('Panserraikos', 'Panserraikos', inplace=True)
    df.replace('Red Bull Bragantino (W)', 'Bragantino (W)', inplace=True)
    df.replace('Police FC', 'Police', inplace=True)
    df.replace('Paola Hibernians FC', 'Hibernians', inplace=True)
    df.replace('Real Soacha Cundinamarc', 'Real Soacha Cundinamarca FC', inplace=True)
    df.replace('Universidad Guadalajara', 'Universidad San Carlos', inplace=True)
    df.replace('PFK Turan Tovuz', 'Turan', inplace=True)
    df.replace('CSD Tellioz', 'Zacapa', inplace=True)
    df.replace('Khaan Khuns Erchim', 'Khaan Khuns-Erchim', inplace=True)
    df.replace('SV Werder Bremen U19', 'Werder Bremen U19', inplace=True)
    df.replace('1. FSV Mainz 05 U19', 'Mainz U19', inplace=True)
    df.replace('FC Hennef 05 U19', 'Hennef U19', inplace=True)
    df.replace('Guangdong Haiyin (W)', 'Guangdong Meizhou (W)', inplace=True)
    df.replace('Eintracht Braunschweig U19', 'Braunschweig U19', inplace=True)
    df.replace('FC Erzgebirge Aue U19', 'FC Energie Cottbus U19', inplace=True)
    df.replace('Khoromkhon Klub', 'Khoromkhon', inplace=True)
    df.replace('Kickers Offenbach (W)', 'Offenbach (W)', inplace=True)
    df.replace('Kenya Police FC', 'Police FC', inplace=True)
    df.replace('St Pauli II', 'St. Pauli II', inplace=True)
    df.replace('Alingsas FC United (W)', 'Gwalia United (W)', inplace=True)
    df.replace('Vfv 06 Hildesheim', 'Hildesheim', inplace=True)
    df.replace('US Zilimadjou', 'Zilimadjou', inplace=True)
    df.replace('Zug 94', 'Zug', inplace=True)
    df.replace('Victoria United Limbe', 'Victoria United', inplace=True)
    df.replace('EB/Streymur', 'EB Streymur', inplace=True)
    df.replace('Keflavik', 'RB Keflavik', inplace=True)
    df.replace('FC Rodange', 'Rodange', inplace=True)
    df.replace('Zrinski Jurjevac', 'Zrinski Osjecko', inplace=True)
    df.replace('ACA FC', 'APR FC', inplace=True)
    df.replace('BSK Bijelo Brdo', 'Bijelo Brdo', inplace=True)
    df.replace('First Vienna FC 1894 (W)', 'First Vienna (W)', inplace=True)
    df.replace('KFC Komarno', 'NK Smartno', inplace=True)
    df.replace('CD Palencia', 'Palencia CA', inplace=True)
    df.replace('Juventud Unida Universitario', 'Juventud Unida San Miguel', inplace=True)
    df.replace('America MG (W)', 'America Mineiro (W)', inplace=True)
    df.replace('Imbabura Sporting Club', 'BSS Sporting Club', inplace=True)
    df.replace('Marsaxlokk FC', 'Marsaxlokk', inplace=True)
    df.replace('San Carlos FC', 'San Marcos', inplace=True)
    df.replace('Ciudad Nueva Santa Cruz', 'Ciudad Nueva SC', inplace=True)
    df.replace('Club Deportivo FATIC', 'Deportivo Cuenca', inplace=True)
    df.replace('Gualan FC', 'Guarda FC', inplace=True)
    df.replace('Orlando City II', 'Orlando City B', inplace=True)
    df.replace('Sporting Kansas City II', 'Sporting Khalsa (W)', inplace=True)
    df.replace('Kieler SV Holstein U19', 'Holstein Kiel U19', inplace=True)
    df.replace('Kickers Offenbach U19', 'Offenbach U19', inplace=True)
    df.replace('Brera Ilch FC', 'Brera Ilch', inplace=True)
    df.replace('Trat', 'Trat FC', inplace=True)
    df.replace('FC Ingolstadt (W)', 'Ingolstadt (W)', inplace=True)
    df.replace('USC Landhaus (W)', 'Sand (W)', inplace=True)
    df.replace('Sonderjyske', 'SonderjyskE', inplace=True)
    df.replace('Ethiopian Coffee', 'Ethiopia Bunna', inplace=True)
    df.replace('Enugu Rangers International', 'Enugu Rangers', inplace=True)
    df.replace('Botafogo FR (W)', 'Botafogo RJ (W)', inplace=True)
    df.replace('GimdeLaPla(W)', 'Gimnasia de La Plata (W)', inplace=True)
    df.replace('SC Internacional (W)', 'Internacional (W)', inplace=True)
    df.replace('Fola Esch', 'Fola', inplace=True)
    df.replace('NK Jarun', 'Jarun', inplace=True)
    df.replace('Dravinja Kostroj', 'Dravinja', inplace=True)
    df.replace('NK Dugopolje', 'Dugopolje', inplace=True)
    df.replace('NK Brinje Grosuplje', 'Grosuplje', inplace=True)
    df.replace('Klaksvikar Itrottarfelag', 'Skala Itrottarfelag', inplace=True)
    df.replace('SV Neulengbach (W)', 'Neulengbach (W)', inplace=True)
    df.replace('FK Velez Mostar', 'Fk Velez Mostar', inplace=True)
    df.replace('Deportivo Upala', 'Deportivo Aleman', inplace=True)
    df.replace('Radnicki Nis', 'Radnicki Zrenjanin', inplace=True)
    df.replace('Deportivo Rincon', 'Deportivo Mictlan', inplace=True)
    df.replace('CA Argentino de Rosari', 'CA Argentino de Rosario', inplace=True)
    df.replace('Independiente Chivilco', 'Independiente Chivilcoy', inplace=True)
    df.replace('New York City FC II', 'New York City II', inplace=True)
    df.replace('Atlanta United FC II', 'Atlanta United 2', inplace=True)
    df.replace('River Plate (Uru)', 'River Plate (Uru)', inplace=True)
    df.replace('Paro FC', 'Paro', inplace=True)
    df.replace('Port FC', 'Port MTI FC', inplace=True)
    df.replace('FK Navbahor Namangan', 'Navbahor Namangan', inplace=True)
    df.replace('KF Gjilani', 'Gjilani', inplace=True)
    df.replace('KF Laci', 'Laci', inplace=True)
    df.replace('FC Oberneuland', 'Oberneuland', inplace=True)
    df.replace('Nottingham Forest U21', 'Nottingham U21', inplace=True)
    df.replace('Club Deportivo San Luis', 'Club Sportivo Ameliano', inplace=True)
    df.replace('Bodo Glimt 2', 'Bodo/Glimt 2', inplace=True)
    df.replace('Vllaznia Shkoder', 'Vllaznia', inplace=True)
    df.replace('Deportivo Moron', 'Deportivo Maldonado', inplace=True)
    df.replace('Seoul City Amazones (W)', 'Seoul (W)', inplace=True)
    df.replace('Rayon Sports FC', 'Rayon Sport', inplace=True)
    df.replace('SCR Altach', 'Altach', inplace=True)

def get_betfair_leagues():
    return [
        'ARGENTINA - PRIMERA DIVISIÓN',
        'AUSTRALIA - A-LEAGUE',
        'BELGIUM - PRO LEAGUE',
        'BRAZIL - SERIE A',
        'BRAZIL - SERIE B',
        'DENMARK - SUPERLIGA',
        'EGYPT - EGYPTIAN PREMIER LEAGUE',
        'ENGLAND - CHAMPIONSHIP',
        'ENGLAND - EFL LEAGUE ONE',
        'ENGLAND - EFL LEAGUE TWO',
        'ENGLAND - PREMIER LEAGUE',
        'EUROPA CHAMPIONS LEAGUE',
        'EUROPA CONFERENCE LEAGUE',
        'EUROPA LEAGUE',
        'FRANCE - LIGUE 1',
        'FRANCE - LIGUE 2',
        'GERMANY - 2. BUNDESLIGA',
        'GERMANY - BUNDESLIGA',
        'ITALY - SERIE A',
        'ITALY - SERIE B',
        'JAPAN - J1 LEAGUE',
        'MEXICO - LIGA MX',
        'NETHERLANDS - EERSTE DIVISIE',
        'NETHERLANDS - EREDIVISIE',
        'NORWAY - ELITESERIEN',
        'PORTUGAL - LIGA NOS',
        'ROMANIA - LIGA I',
        'SAUDI ARABIA - SAUDI PROFESSION',
        'SCOTLAND - PREMIERSHIP',
        'SPAIN - LA LIGA',
        'SPAIN - SEGUNDA DIVISIÓN',
        'TURKEY - SÜPER LIG',
        'USA - MLS',
    ]