from utils.functions import *
from utils.filters import *

def main_page(fonte_dados):

    if st.secrets['ENV'] == 'dev':
        st.info("Ambiente de Desenvolvimento. Branch: dev")

    st.title("Futapp v0.2")
    st.header("⚽ Jogos sem resultado")

    # Init

    df_matches = load_daymatches(None, 'Betfair')
    df_matches["Goals_H_FT"] = pd.to_numeric(df_matches["Goals_H_FT"], errors="coerce")
    df_matches = df_matches[(df_matches['Goals_H_FT'].isna()) | (df_matches['Goals_H_FT'] < 0)]

    if df_matches.empty:
        st.info(f"Os dados não estão disponíveis.")

    else:
        # Dataframe
        df_matches_columns = ['League','Rodada','Time','Home','Away','Resultado','Goals_H_Minutes','Goals_A_Minutes','Odd_H_FT','Odd_D_FT','Odd_A_FT','Odd_Over25_FT','Odd_Under25_FT','Odd_BTTS_Yes','Odd_BTTS_No','Odd_CS_0x1_Lay','Odd_CS_0x2_Lay','Odd_CS_0x3_Lay','XG_Total_Pre','XG_Home_Pre','XG_Away_Pre','Odd_DC_1X','Odd_DC_12','Odd_DC_X2']
       
        match_selected = st.dataframe(
            df_matches[df_matches_columns]
            , on_select="rerun"
            , selection_mode="single-row"
            , use_container_width=True
            , hide_index=True
        )
        st.write(f"Última atualização no Codebuild: {last_refresh_daymatches()}")
        st.write(f"Quantidade de jogos: {len(df_matches)}")