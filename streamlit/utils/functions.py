import streamlit as st
import pandas as pd
import ast
from datetime import datetime, timedelta

def get_current_season():
    SEASON = '2024/2025'
    return SEASON

def get_last_season():
    SEASON = '2023/2024'
    return SEASON

def get_today():
    now = datetime.now()
    adjusted_time = now - timedelta(hours=3)
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

@st.cache_data
def load_daymatches(dt):
    df = pd.read_csv(f"https://github.com/futpythontrader/YouTube/blob/main/Jogos_do_Dia/FootyStats/Jogos_do_Dia_FootyStats_{dt}.csv?raw=true")
    df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
    df["Formatted_Datetime"] = df["Datetime"].dt.strftime("%d/%m/%Y %H:%M")
    df["Confronto"] = df["Time"] + " - " + df["Home"] + " vs. " + df["Away"]
    return df

@st.cache_data
def load_histmatches(dt=None):

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
    if dt: df = df.loc[(df["Date"] < pd.to_datetime(dt))]
    df["Formatted_Date"] = df["Date"].dt.strftime("%d/%m/%Y")
    df["Resultado_FT"] = df["Goals_H_FT"].astype(str) + "-" + df["Goals_A_FT"].astype(str)
    df["Primeiro_Gol"] = df.apply(first_goal_string, axis=1)
    #df['Placar'] = f"{str(df['Goals_H_FT'])}x{str(df['Goals_A_FT'])}"
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

    return df_gols.melt(id_vars='Intervalo', var_name='Tipo de Gol', value_name='Quantidade')

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