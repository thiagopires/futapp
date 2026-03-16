from utils.functions import *
from utils.filters import *
from utils.filters_func import *

def main_page(fonte_dados):

    if st.secrets['ENV'] == 'dev':
        st.info("Ambiente de Desenvolvimento. Branch: dev")

    st.title("Futapp v0.3")
    st.caption("desenvolvido por thiago pires")
    st.header("⚽ Filtros Prontos")

    # Init

    # fonte_dados = st.selectbox("Fonte de Dados", ['FootyStats','Betfair'])
    data_analise = st.date_input("Data da Análise", get_today())

    df_matches = load_daymatches(data_analise, fonte_dados)
    df_matches_columns = ['League','Rodada','Time','Home','Away','Resultado','Goals_H_Minutes','Goals_A_Minutes','Odd_H_FT','Odd_D_FT','Odd_A_FT','Odd_CS_0x1_Lay','Odd_CS_0x2_Lay','Odd_CS_0x3_Lay','Odd_CS_1x3_Lay','Odd_Over25_FT','Odd_Under25_FT','Odd_BTTS_Yes','Odd_BTTS_No','XG_Total_Pre','XG_Home_Pre','XG_Away_Pre','Odd_DC_1X','Odd_DC_12','Odd_DC_X2']

    if df_matches.empty:
        st.info(f"Os dados para {data_analise} não estão disponíveis.")

    else:

        for fp in filtros_prontos[fonte_dados].pop(0):
            print(fp)

            df_matches, condicao, metodo = get_details_filtro_pronto(df_matches, None, None, fp)

            if not df_matches.empty():
                st.subheader(fp)
                st.dataframe(
                    df_matches[df_matches_columns]
                    , on_select="rerun"
                    , selection_mode="single-row"
                    , width='stretch'
                    , hide_index=True
                )

            st.divider()
        
        st.write(f"Última atualização no AWS Codebuild: {last_refresh_daymatches()}")
        st.write(f"Quantidade de jogos: {len(df_matches)}")