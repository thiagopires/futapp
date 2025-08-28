from utils.functions import *
from utils.filters import *

def main_page(fonte_dados):

    if st.secrets['ENV'] == 'dev':
        st.info("Ambiente de Desenvolvimento. Branch: dev")

    st.title("Futapp v0.2")
    st.header("⚽ Jogos sem resultado")

    # Init

    df_matches = load_daymatches(None, 'Betfair')
    df_matches['Filtro'] = ('{Date: ' + df_matches['Date'].astype(str) + ', Time: ' + df_matches['Time'].astype(str) + '}')
    df_matches["Goals_H_FT"] = pd.to_numeric(df_matches["Goals_H_FT"], errors="coerce")
    df_matches = df_matches[(((df_matches['Goals_H_FT'].isna()) | (df_matches['Goals_H_FT'] < 0)) & (df_matches['Date'] < datetime.now().strftime('%Y-%m-%d')))]

    if df_matches.empty:
        st.info(f"Os dados não estão disponíveis.")

    else:
        # Dataframe
        df_matches_columns = ['Event_ID','League','Filtro','Home','Away','Status','Resultado','Goals_H_Minutes','Goals_A_Minutes']
       
        match_selected = st.dataframe(
            df_matches[df_matches_columns]
            , on_select="rerun"
            , selection_mode="single-row"
            , use_container_width=True
            , hide_index=True
        )
        st.write(f"Última atualização no Codebuild: {last_refresh_daymatches()}")
        st.write(f"Quantidade de jogos: {len(df_matches)}")