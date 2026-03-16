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

    if df_matches.empty:
        st.info(f"Os dados para {data_analise} não estão disponíveis.")

    else:

        for fp in filtros_prontos[fonte_dados]:

            st.subheader(fp)
            df_matches, condicao, metodo = get_details_filtro_pronto(df_matches, None, None, fp)

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