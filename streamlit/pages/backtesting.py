from utils.functions import *
from utils.filters import *
from utils.filters_func import *

from datetime import date
import plotly.express as px
import math

# --- Constantes ---
# Usar constantes torna o código mais fácil de manter.
COMMISSION = 2.8
STATUS_GREEN = 'GREEN'
STATUS_RED = 'RED'
STATUS_VOID = 'VOID'

# --- Funções Auxiliares ---

def calculate_summary_stats(df_hist):
    """Calcula e retorna as estatísticas resumidas do backtesting."""
    total_jogos = len(df_hist)
    if total_jogos == 0:
        return None

    total_greens = len(df_hist[df_hist['Status_Metodo'] == STATUS_GREEN])
    total_reds = len(df_hist[df_hist['Status_Metodo'] == STATUS_RED])
    total_voids = len(df_hist[df_hist['Status_Metodo'] == STATUS_VOID])
    
    winrate = round((total_greens + total_voids) / total_jogos * 100, 2)
    profit_acumulado = f"{str(round(df_hist['Profit'].sum(), 2))} unidades"

    return {
        "total_jogos": total_jogos,
        "total_greens": total_greens,
        "total_reds": total_reds,
        "total_voids": total_voids,
        "winrate": winrate,
        "profit_acumulado": profit_acumulado
    }

def create_profit_chart(df_hist):
    """Cria e retorna a figura do gráfico de lucro acumulado."""
    daily_profit = df_hist.groupby("Date")["Profit"].sum().reset_index()
    daily_profit["Cumulative_Profit"] = daily_profit["Profit"].cumsum()

    fig = px.line(
        daily_profit,
        x="Date",
        y="Cumulative_Profit",
        title="Evolução do Lucro Acumulado",
        labels={"Date": "Data", "Cumulative_Profit": "Unidades/Stakes"},
        markers=True
    )

    fig.update_layout(
        template="plotly_white",
        title={"text": "Evolução do Lucro Acumulado", "y": 0.9, "x": 0.5, "xanchor": "center", "yanchor": "top", "font": {"size": 24}},
        xaxis=dict(showgrid=True, gridcolor="lightgray"),
        yaxis=dict(showgrid=True, gridcolor="lightgray"),
        font=dict(family="Arial", size=14),
    )

    fig.update_traces(
        line=dict(width=2, color='#2E8B57'),
        marker=dict(size=8, symbol="circle", color="#FF4500"),
        hovertemplate="<b>Data:</b> %{x|%d/%m/%Y}<br><b>Lucro Acumulado:</b> %{y:.2f}<extra></extra>"
    )
    return fig

def display_reports(df_hist):
    """Exibe os relatórios de performance por liga e outros critérios."""
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Profit por Liga/Mês**")
        report_monthly = df_hist.groupby(["League", "Month_Year"])["Profit"].sum().reset_index()
        print_dataframe(report_monthly)

    with col2:
        st.write("**Profit acumulado por Liga**")
        report_league_profit = df_hist.groupby(["League"])["Profit"].sum().reset_index()
        report_league_profit = report_league_profit.sort_values(by="Profit", ascending=False)
        report_league_profit["Cumulative_Profit"] = report_league_profit["Profit"].cumsum()
        print_dataframe(report_league_profit)

    st.divider()

    col3, col4 = st.columns(2)
    with col3:
        st.write("**Resultado por Liga**")
        report_league_result = df_hist.groupby(["League", "Status_Metodo"]).size().unstack(fill_value=0).reset_index()
        for status in [STATUS_GREEN, STATUS_RED]:
            if status not in report_league_result.columns:
                report_league_result[status] = 0
        
        # Evitar divisão por zero
        total_bets = report_league_result[STATUS_GREEN] + report_league_result[STATUS_RED]
        report_league_result['Winrate'] = round((report_league_result[STATUS_GREEN] / total_bets.where(total_bets != 0, 1)) * 100, 2)
        print_dataframe(report_league_result)

    with col4:
        st.write("**Resultado por FX (Prob, CV) do MO**")
        report_fx = df_hist.groupby(["League", "FX_Probabilidade_A", "FX_CV_HDA", "Status_Metodo"], observed=True).size().unstack(fill_value=0).reset_index()
        for status in [STATUS_GREEN, STATUS_RED]:
            if status not in report_fx.columns:
                report_fx[status] = 0
        
        report_fx = report_fx[report_fx[STATUS_GREEN] + report_fx[STATUS_RED] > 0]
        # Evitar divisão por zero
        total_bets_fx = report_fx[STATUS_GREEN] + report_fx[STATUS_RED]
        report_fx['Winrate'] = round((report_fx[STATUS_GREEN] / total_bets_fx.where(total_bets_fx != 0, 1)) * 100, 2)
        print_dataframe(report_fx)

def display_details(df_hist, stats):
    # Exibição dos jogos detalhados
    df_columns = ['League','Rodada','Date','Time','Home','Away','Resultado_FT','Goals_H_Minutes','Goals_A_Minutes','Odd_H_FT','Odd_D_FT','Odd_A_FT','Odd_CS_0x1_Lay','Odd_CS_0x2_Lay','Odd_CS_0x3_Lay','Odd_CS_Goleada_A','Odd_Over05_FT','Odd_Over25_FT','Odd_Under05_FT','Odd_Under15_FT','Odd_Under25_FT','Odd_BTTS_Yes','Odd_BTTS_No','Odd_DC_1X','Odd_DC_12','Odd_DC_X2','XG_Total_Pre','XG_Home_Pre','XG_Away_Pre','Diff_XG_Home_Away_Pre','PPG_Home_Pre','PPG_Away_Pre','Primeiro_Gol','Status_Metodo','Profit','Probabilidade_H_FT','Probabilidade_D_FT','Probabilidade_A_FT','CV_HDA_FT']
    
    # Garantir que apenas colunas existentes sejam selecionadas
    display_cols = [col for col in df_columns if col in df_hist.columns]

    st.write("### Detalhamento dos Jogos")
    with st.expander("Clique para ver os **GREENs** ✅"):
        st.write(f"**:green[GREENs:]**")
        print_dataframe(df_hist.loc[df_hist['Status_Metodo'] == STATUS_GREEN, display_cols])
    
    with st.expander("Clique para ver os **REDs** ❌"):
        st.write(f"**:red[REDs:]**")
        print_dataframe(df_hist.loc[df_hist['Status_Metodo'] == STATUS_RED, display_cols])

    if stats['total_voids'] > 0:
        with st.expander("Clique para ver os **VOIDs** 🔄"):
            st.write(f"**:gray[VOIDs:]**")
            print_dataframe(df_hist.loc[df_hist['Status_Metodo'] == STATUS_VOID, display_cols])

# --- Função Principal ---

def generate_backtesting(pdf_hist, metodo):
    """
    Função principal que orquestra a geração e exibição dos resultados do backtesting.
    """
    df_hist, odd_media = get_result_filtro_pronto(pdf_hist, metodo)

    st.write("### Resultado do Backtesting")

    if df_hist.empty:
        st.info("Sem jogos para analisar com os filtros selecionados.")
        return

    stats = calculate_summary_stats(df_hist)
    if not stats:
        st.info("Sem jogos para analisar com os filtros selecionados.")
        return

    # str_voids = f"Voids: {stats['total_voids']}, " if stats['total_voids'] > 0 else ''
    # summary_text = (
    #     f"**Jogos:** {stats['total_jogos']} | "
    #     f"**Greens:** {stats['total_greens']} | "
    #     f"**Reds:** {stats['total_reds']} | "
    #     f"{str_voids}"
    #     f"**Winrate:** {stats['winrate']}% | "
    #     f"**Profit Líquido:** {stats['profit_acumulado']} | "
    #     f"**Comissão:** {COMMISSION}% | "
    #     f"**Odd Média:** {odd_media}"
    # )
    # st.markdown(summary_text)

    """Exibe as métricas de resumo em um layout de colunas."""
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    
    profit_value = float(stats['profit_acumulado'].split(' ')[0])
    
    col1.metric(label="Método", value=metodo, border=True)
    col2.metric(label="Jogos", value=stats['total_jogos'], border=True)
    col3.metric(label="Greens ✅", value=stats['total_greens'], border=True)
    col4.metric(label="Reds ❌", value=stats['total_reds'], border=True)
    col5.metric(label="Voids 🔄", value=stats['total_voids'], border=True)
    col6.metric(label="Winrate", value=f"{stats['winrate']}%", delta=f"Odd média: {odd_media}", delta_color="off", border=True)
    col7.metric(label="Profit Líquido", value=f"{profit_value:.2f} un", delta=f"{round(profit_value / stats['total_jogos'] * 100, 2)}% ROI", border=True)

    # Criação e exibição do gráfico
    profit_chart_fig = create_profit_chart(df_hist)
    # **A SOLUÇÃO:** Adicionar uma `key` única e descritiva.
    st.plotly_chart(profit_chart_fig, use_container_width=True, key=f"profit_chart_{metodo}")

    display_details(df_hist, stats)

    # Exibição dos relatórios em dataframes
    display_reports(df_hist)


def main_page(fonte_dados):

    if st.secrets['ENV'] == 'dev':
        st.info("Ambiente de Desenvolvimento. Branch: dev")

    st.title("Futapp v0.3")
    st.caption("desenvolvido por thiago pires")
    st.header("⚽ Backtesting")

    # fonte_dados = st.selectbox("Fonte de Dados", ['Betfair','FootyStats'])
    df_hist = load_histmatches(fonte_dados)

    indicadores = df_hist.columns

    operadores_opcoes = {
        "=": "Igual",
        ">": "Maior que",
        "<": "Menor que",
        ">=": "Maior ou igual",
        "<=": "Menor ou igual",
        "!=": "Diferente de"
    }
    operadores_formatados = [f"{descricao} ({simbolo})" for simbolo, descricao in operadores_opcoes.items()] 

    st.write("**Selecione o período**")

    col1, col2, col3 = st.columns(3)
    with col1: data_inicial = st.date_input("Data Inicial", date(2025, 7, 1))
    with col2: data_final = st.date_input("Data Final", get_today(-1))
    # with col3:
    #     seasons = sorted(df_hist['Season'].unique())
    #     seasons.insert(0, 'Todas as Temporadas')
    #     selected_seasons = st.multiselect("Filtrar por Temporada", seasons, [seasons[0]])


    st.divider()


    st.write("**Indicadores**")

    with st.expander("Clique para expandir:"):

        leagues = sorted(df_hist['League'].unique())
        leagues.insert(0, 'Todas as Ligas')
        selected_leagues = st.multiselect("Filtrar por Liga", leagues, [leagues[0]])
        # if not (not selected_seasons or "Todas as Temporadas" in selected_seasons):
        #     df_hist = df_hist[df_hist['Season'].isin(selected_seasons)]

        if data_inicial and data_final:
            df_hist = df_hist[
                (df_hist['Date'].dt.normalize() >= pd.to_datetime(data_inicial)) &
                (df_hist['Date'].dt.normalize() <= pd.to_datetime(data_final))
            ]

        if "Todas as Ligas" not in selected_leagues:
            df_hist = df_hist[df_hist['League'].isin(selected_leagues)]

        for i in range(1,9):
            cola, colb, colc, cold = st.columns(4)
            with cola: st.selectbox("Indicador", indicadores, key=f"indicador_{i}")
            with colb: st.selectbox("Tipo", ['Valor Absoluto', 'Valor Relativo'], key=f"tipo_{i}")
            with colc: st.selectbox("Operador", operadores_formatados, key=f"operador_{i}")
            with cold: st.text_input("Digite o valor ou Campo:", key=f"valor_{i}")

        col1, col2, col3 = st.columns(3)
        with col1:
            metodo = st.selectbox("Método", metodos)
        with col2:
            condicao = st.radio("Condição", ["Geral","Favorito/Zebra","Zebra/Favorito"], horizontal=True)
            if condicao == "Favorito/Zebra":
                df_hist = df_hist[(df_hist["Odd_H_FT"] < df_hist["Odd_A_FT"])]
            elif condicao == "Zebra/Favorito":
                df_hist = df_hist[(df_hist["Odd_H_FT"] > df_hist["Odd_A_FT"])]

        executar = st.button("Executar")
    
    string_indicadores = ""

    if executar:
        for i in range(1,9):
            indicador = st.session_state[f'indicador_{i}']
            tipo = st.session_state[f'tipo_{i}']
            operador_selecionado = st.session_state[f'operador_{i}']
            valor = st.session_state[f'valor_{i}']

            if valor != "":
                string_indicadores += f"{indicador} {operador_selecionado} {valor} | "

                if indicador != 'Primeiro_Gol_Marcador' and tipo != 'Valor Relativo':
                    valor = float(valor)

                if operador_selecionado == 'Igual (=)':
                    filter = (df_hist[indicador] == valor) if tipo == 'Valor Absoluto' else (df_hist[indicador] == df_hist[valor])
                if operador_selecionado == 'Maior que (>)':
                    filter = (df_hist[indicador] > valor) if tipo == 'Valor Absoluto' else (df_hist[indicador] > df_hist[valor])
                if operador_selecionado == 'Menor que (<)':
                    filter = (df_hist[indicador] < valor) if tipo == 'Valor Absoluto' else (df_hist[indicador] < df_hist[valor])
                if operador_selecionado == 'Maior ou igual (>=)':
                    filter = (df_hist[indicador] >= valor) if tipo == 'Valor Absoluto' else (df_hist[indicador] >= df_hist[valor])
                if operador_selecionado == 'Menor ou igual (<=)':
                    filter = (df_hist[indicador] <= valor) if tipo == 'Valor Absoluto' else (df_hist[indicador] <= df_hist[valor])
                if operador_selecionado == 'Diferente de (!=)':
                    filter = (df_hist[indicador] != valor) if tipo == 'Valor Absoluto' else (df_hist[indicador] != df_hist[valor])

                df_hist = df_hist[filter]

    st.caption(string_indicadores)


    st.divider()


    col1, _, _ = st.columns(3)
    with col1:
        filtro_pronto_selecionado = st.selectbox("Filtros Prontos", filtros_prontos[fonte_dados])

    st.divider()

    # ETAPA 1: Inicializar o estado na primeira execução
    # Guardamos o método ativo e também o último filtro/condição que foi usado para definir um default
    if 'active_method' not in st.session_state:
        st.session_state.active_method = metodos_tabs[0]
    if 'last_filter' not in st.session_state:
        st.session_state.last_filter = None
    if 'last_condicao' not in st.session_state:
        st.session_state.last_condicao = None

    # Esta lógica de exibição continua a mesma
    if filtro_pronto_selecionado != "Sem filtro" or executar:

        # ETAPA 2: Verificar se o contexto para o default mudou
        # Isso acontece se o filtro mudou, a condição mudou, ou o botão "Executar" foi pressionado
        # A variável 'executar' já captura a ação do botão principal
        contexto_mudou = (st.session_state.last_filter != filtro_pronto_selecionado) or \
                        (st.session_state.last_condicao != condicao)

        # ETAPA 3: ATUALIZAR O DEFAULT APENAS SE O CONTEXTO MUDOU
        if contexto_mudou or executar:
            _, _, metodo_default = get_details_filtro_pronto(
                df_hist.copy(),
                condicao,
                metodo,
                filtro_pronto_selecionado
            )

            # Atualizamos o método ativo e guardamos os novos valores de filtro/condição
            st.session_state.active_method = metodo_default
            st.session_state.last_filter = filtro_pronto_selecionado
            st.session_state.last_condicao = condicao

        # ETAPA 4: Renderizar os botões em duas linhas (lógica que você já tinha)
        midpoint = math.ceil(len(metodos_tabs) / 2)
        primeira_linha_metodos = metodos_tabs[:midpoint]
        segunda_linha_metodos = metodos_tabs[midpoint:]

        # Renderiza a PRIMEIRA linha de botões
        cols_linha1 = st.columns(len(primeira_linha_metodos))
        for i, metodo_nome in enumerate(primeira_linha_metodos):
            with cols_linha1[i]:
                button_type = "primary" if st.session_state.active_method == metodo_nome else "secondary"
                if st.button(metodo_nome, key=f"btn_{metodo_nome}", type=button_type, use_container_width=True):
                    # Se clicado, apenas atualiza o estado e deixa o Streamlit reexecutar
                    st.session_state.active_method = metodo_nome
                    st.rerun() # Garante a atualização visual imediata

        # Renderiza a SEGUNDA linha de botões
        if segunda_linha_metodos:
            cols_linha2 = st.columns(len(segunda_linha_metodos))
            for i, metodo_nome in enumerate(segunda_linha_metodos):
                with cols_linha2[i]:
                    button_type = "primary" if st.session_state.active_method == metodo_nome else "secondary"
                    if st.button(metodo_nome, key=f"btn_{metodo_nome}", type=button_type, use_container_width=True):
                        st.session_state.active_method = metodo_nome
                        st.rerun()

        # ETAPA 5: O resto do código usa o estado que agora está correto
        st.divider()
        metodo_escolhido = st.session_state.active_method

        pdf_hist_filtrado, _, _ = get_details_filtro_pronto(
            df_hist.copy(),
            condicao,
            metodo_escolhido,
            filtro_pronto_selecionado
        )

        generate_backtesting(pdf_hist_filtrado, metodo_escolhido)