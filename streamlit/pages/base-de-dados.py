import streamlit as st
import pandas as pd
from datetime import datetime, date

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

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

def print_dataframe(df, styled_df=None):
    if isinstance(styled_df, pd.io.formats.style.Styler):
        styled_df = styled_df.set_properties(**{'text-align': 'center'})
        styled_df = styled_df.set_table_styles([
            {'selector': 'th', 'props': [('text-align', 'center')]}
        ])
        st.dataframe(styled_df, height=len(df)*38, use_container_width=True, hide_index=True)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

def load_histmatches():
    df1 = pd.read_csv("https://github.com/futpythontrader/YouTube/blob/main/Bases_de_Dados/FootyStats/Base_de_Dados_FootyStats_(2022_2024).csv?raw=true")
    #df2 = pd.read_csv("https://github.com/futpythontrader/YouTube/blob/main/Bases_de_Dados/FootyStats/Base_de_Dados_FootyStats_(2006_2021).csv?raw=true")

    #df = pd.concat([df1, df2], ignore_index=True)
    df = df1

    df[["Date", "Time"]] = df["Date"].str.split(" ", expand=True)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Formatted_Date"] = df["Date"].dt.strftime("%d/%m/%Y")
    df["Resultado_FT"] = df["Goals_H_FT"].astype(str) + "-" + df["Goals_A_FT"].astype(str)
    df["Primeiro_Gol"] = df.apply(first_goal_string, axis=1)

    return df

st.set_page_config(layout="wide")

st.title("⚽ Base de dados")

### FootyStats ###

df_hist = load_histmatches()

col1, col2 = st.columns(2)
with col1:
  data_inicial = st.date_input("Data Inicial", date(2022, 2, 10))
with col2:
  data_final = st.date_input("Data Final", datetime.today())

leagues = sorted(df_hist['League'].unique())
leagues.insert(0, 'Todas as Ligas')

selected_leagues = st.multiselect(
    "Filtrar por Liga",
    leagues,
    [leagues[0]],
)

seasons = sorted(df_hist['Season'].unique())
seasons.insert(0, 'Todas as Temporadas')

selected_seasons = st.multiselect(
    "Filtrar por Temporada",
    seasons,
    [seasons[0]]
)

st.write(selected_leagues)
st.write(selected_seasons)

if not selected_leagues or "Todas as Ligas" in selected_leagues:
    # Não aplica filtro, retorna o DataFrame completo
    filtered_df = df_hist
else:
    # Filtra o DataFrame pelos valores selecionados
    filtered_df = df_hist[df_hist['Leagues'].isin(selected_leagues)]

print_dataframe(filtered_df)

### football-data.co.uk ###

# st.sidebar.header("Filtros")
# selected_league = st.sidebar.selectbox('Escolha uma liga', ['England','Germany','Italy','Spain','France'])
# selected_season = st.sidebar.selectbox('Escolha uma temporada', ['2024/2025','2023/2024','2022/2023','2021/2022','2020/2021'])

# def drop_reset_index(df):
#     df = df.dropna()
#     df = df.reset_index(drop=True)
#     df.index += 1
#     return df

# def load_data(league, season):

#   match league:
#     case 'England':
#       league = 'E0'
#     case 'Germany':
#       league = 'D1'
#     case 'Italy':
#       league = 'I1'
#     case 'Spain':
#       league = 'SP1'
#     case 'France':
#       league = 'F1'

#   url = f"https://www.football-data.co.uk/mmz4281/{season[2:4]}{season[7:9]}/{league}.csv"
#   data = pd.read_csv(url)
#   return data

# df = load_data(selected_league, selected_season)

# df = df[['Div','Date','Time','HomeTeam','AwayTeam','HTHG','HTAG','HTR','FTHG','FTAG','FTR',
# 'BFEH','BFED','BFEA','BFE>2.5','BFE<2.5','AHh','BFEAHH','BFEAHA']]

# df.columns = ['League','Date','Time','Home','Away','Goals_H_HT','Goals_A_HT','Result_HT','Goals_H_FT','Goals_A_FT','Result_FT',
# 'Odd_H_Open','Odd_D_Open','Odd_A_Open','Odd_Over25_Open','Odd_Under25_Open','Asian_Handicap_Open','Odd_AHH_Open','Odd_AHA_Open']

# df = drop_reset_index(df)

# st.subheader(f"Dataframe: {selected_league} - {selected_season}")

# st.dataframe(df)
