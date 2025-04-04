from utils.functions import *
from utils.filters import *

def main_page(fonte_dados):

    if st.secrets['ENV'] == 'dev':
        st.info("Ambiente de Desenvolvimento. Branch: dev")

    st.title("Futapp v0.2")
    st.header("⚽ Análise Away")

    # Init

    data_analise = st.date_input("Data da Análise", get_today())
    df_matches = load_daymatches(data_analise, fonte_dados)
    df_hist = load_histmatches(fonte_dados)


    st.divider()


    if df_matches.empty:
        st.info(f"Os dados para {data_analise} não estão disponíveis.")    

    else:
        st.subheader("Filtro de Odds")

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.number_input("Odd_H_Min", value=1.10, min_value=1.10, max_value=1000.00, key="odd_h_min")
            st.number_input("Odd_H_Max", value=1000.00, min_value=1.10, max_value=1000.00, key="odd_h_max")
        with col2:
            st.number_input("Odd_D_Min", value=1.10, min_value=1.10, max_value=1000.00, key="odd_d_min")
            st.number_input("Odd_D_Max", value=1000.00, min_value=1.10, max_value=1000.00, key="odd_d_max")
        with col3:
            st.number_input("Odd_A_Min", value=1.10, min_value=1.10, max_value=1000.00, key="odd_a_min")
            st.number_input("Odd_A_Max", value=1000.00, min_value=1.10, max_value=1000.00, key="odd_a_max")
        with col4:
            st.number_input("Odd_Over25_FT_Min", value=1.10, min_value=1.10, max_value=1000.00, key="odd_over25_ft_min")
            st.number_input("Odd_Over25_FT_Max", value=1000.00, min_value=1.10, max_value=1000.00, key="odd_over25_ft_max")
        with col5:
            st.number_input("Odd_BTTS_Min", value=1.10, min_value=1.10, max_value=1000.00, key="odd_btts_min")
            st.number_input("Odd_BTTS_Max", value=1000.00, min_value=1.10, max_value=1000.00, key="odd_btts_max")


        st.divider()


        st.subheader("Jogos que atendem a esses filtros")

        df_matches = df_matches.loc[
            (df_matches["Odd_H_FT"] >= st.session_state.odd_h_min) &
            (df_matches["Odd_H_FT"] <= st.session_state.odd_h_max) &

            (df_matches["Odd_D_FT"] >= st.session_state.odd_d_min) &
            (df_matches["Odd_D_FT"] <= st.session_state.odd_d_max) &

            (df_matches["Odd_A_FT"] >= st.session_state.odd_a_min) &
            (df_matches["Odd_A_FT"] <= st.session_state.odd_a_max) &

            (df_matches["Odd_Over25_FT"] >= st.session_state.odd_over25_ft_min) &
            (df_matches["Odd_Over25_FT"] <= st.session_state.odd_over25_ft_max) &

            (df_matches["Odd_BTTS_Yes"] >= st.session_state.odd_btts_min) &
            (df_matches["Odd_BTTS_Yes"] <= st.session_state.odd_btts_max)
        ]

        print_dataframe(df_matches[['League','Rodada','Time','Home','Away','Odd_H_FT','Odd_D_FT','Odd_A_FT','Odd_Over05_HT','Odd_Over15_FT','Odd_Over25_FT','Odd_BTTS_Yes']])


        st.divider()


        st.subheader("Selecione o Visitante e o Placar para a análise")
        
        if len(df_matches) > 0:
            colb1, colb2 = st.columns(2)
            with colb1:
                visitante = st.selectbox("Escolha o Visitante", df_matches['Away'])
            with colb2:
                placar = st.selectbox("Escolha o Placar", ['0x0','0x1','0x2','0x3','1x0','1x1','1x2','1x3','2x0','2x1','2x2','2x3','3x0','3x1','3x2','3x3','Goleada_H','Goleada_A'])

            df_match_selected = df_matches.loc[(df_matches['Away'] == visitante)]


            st.divider()


            st.session_state['active_button'] = ""

            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            # with col1:
            #     if st.button("Profit Acumulado", use_container_width=True):
            #         st.session_state['active_button'] = "Profit Acumulado"
            with col2:
                if st.button("Ponto de Saída Punter", use_container_width=True):
                    st.session_state['active_button'] = "Ponto de Saída Punter"
            #     st.button("Ocorrências Gerais", use_container_width=True)
            with col3:
                if st.button("Ponto de Saída Trader", use_container_width=True):
                    st.session_state['active_button'] = "Ponto de Saída Trader"
                if st.button("Ponto de Revisão HT", use_container_width=True):
                    st.session_state['active_button'] = "Ponto de Revisão HT"
            with col4:
                if st.button("Últimos 10 jogos", use_container_width=True):
                    st.session_state['active_button'] = "Últimos 10 jogos"
                if st.button("Confronto Direto", use_container_width=True):
                    st.session_state['active_button'] = "Confronto Direto"
            # with col5:
            #     st.button("Temporada Atual", use_container_width=True)
            #     st.button("Temporada Anterior", use_container_width=True)
            with col6:
                if st.button("Match Odds - Back", use_container_width=True):
                    st.session_state['active_button'] = "Match Odds - Back"
                if st.button("Match Odds - Lay", use_container_width=True):
                    st.session_state['active_button'] = "Match Odds - Lay"
            with col7:
                if st.button("Over 2.5 FT / BTTS", use_container_width=True):
                    st.session_state['active_button'] = "Over 2.5 FT / BTTS"
                if st.button("Placares Singulares", use_container_width=True):
                    st.session_state['active_button'] = "Placares Singulares"
                    
            
            st.divider()


            if len(df_match_selected) > 0:

                mandante = df_match_selected.iloc[0]["Home"]

                if st.session_state['active_button'] == "Over 2.5 FT / BTTS":
                            
                    st.write(f"**Over 2.5 FT nos jogos do {visitante}**")
                    st.write(f"**Jogos anteriores do {visitante} que bateram o Over 2.5 FT**")    
                    aba_over25(df_hist, visitante, "Away")

                    st.write(f"**BTTS nos jogos do {visitante}**")
                    st.write(f"**Jogos anteriores do {visitante} que bateram o BTTS**")
                    aba_btts(df_hist, visitante, "Away")

                elif st.session_state['active_button'] == "Últimos 10 jogos":

                    st.write(f"**Últimos 10 jogos do {mandante} como Mandante**")
                    aba_ult10(df_hist, mandante, "Home")

                    st.write(f"**Últimos 10 jogos do {visitante} como Visitante**")
                    aba_ult10(df_hist, visitante, "Away")

                elif st.session_state['active_button'] == "Confronto Direto":
                    st.write(f"**Confronto direto - Temporadas passadas**")
                    aba_confrontodireto(df_hist, visitante, visitante)

                elif st.session_state['active_button'] == "Match Odds - Back":
                    st.write(f"**Back Home (Apostar no {visitante})**")
                    aba_back_home(df_hist, visitante, "Away")

                    st.write(f"**Back Draw (Apostar no Empate nos jogos do {visitante})**")
                    aba_back_draw(df_hist, visitante, "Away")

                    st.write(f"**Back Away (Apostar no Adversário do {visitante})**")
                    aba_back_away(df_hist, visitante, "Away")

                elif st.session_state['active_button'] == "Match Odds - Lay":
                    st.write(f"**Lay Home (Apostar contra o {visitante})**")
                    aba_lay_home(df_hist, visitante, "Away")

                    st.write(f"**Lay Draw (Apostar cintra o Empate nos jogos do {visitante})**")
                    aba_lay_draw(df_hist, visitante, "Away")

                    st.write(f"**Lay Away (Apostar contra o Adversário do {visitante})**")
                    aba_lay_away(df_hist, visitante, "Away")
                    
                elif st.session_state['active_button'] == "Ponto de Revisão HT":
                    
                    st.write(f"**Jogos anteriores do {visitante} que terminaram em {placar} no HT.**")
                    aba_ponto_de_revisao_ht(df_hist, visitante, "Away", placar)

                elif st.session_state['active_button'] == "Ponto de Saída Trader":
                    
                    st.write(f"**Jogos anteriores do {visitante} que estavam em {placar} no minuto 75.**")
                    aba_ponto_de_saida_trader(df_hist, visitante, "Away", placar)
                
                elif st.session_state['active_button'] == "Placares Singulares":
                    
                    st.write(f"**Singulares**")
                    st.write(f"**Resultados que não ocorreram para o {visitante} nas últimas temporadas**")
                    resultados_singulares(df_hist, visitante, "Away")
                    
                    st.write(f"**Análise de Ocorrência dos Placares**")
                    analise_ocorrencia_placar(df_hist, mandante, visitante, placar)

                elif any(item == st.session_state['active_button'] for item in ["", "Ponto de Saída Punter"]):
                # elif st.session_state['active_button'] == "Ponto de Saída Punter":
        
                    st.write(f"**Jogos anteriores do {visitante} terminados em {placar}.**")
                    aba_ponto_de_saida_punter(df_hist, visitante, "Away", placar)

# if "logged_in" not in st.session_state:
#     st.session_state["logged_in"] = False

# if st.session_state["logged_in"]:
#     display_sidebar('block')
#     main_page()
# else:
#     login_page()