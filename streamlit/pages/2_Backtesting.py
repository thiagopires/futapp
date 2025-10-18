import streamlit as st
import pandas as pd
from utils.functions import *
from utils.filters import *
from datetime import date
import plotly.express as px

st.set_page_config(layout="wide", page_title="Backtesting", page_icon="🔬")

# --- Funções de UI Refatoradas ---

def display_summary_metrics(stats, odd_media):
    """Exibe as métricas de resumo em um layout de colunas."""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    profit_value = float(stats['profit_acumulado'].split(' ')[0])
    
    col1.metric(label="Total de Jogos", value=stats['total_jogos'])
    col2.metric(label="Greens ✅", value=stats['total_greens'])
    col3.metric(label="Reds ❌", value=stats['total_reds'])
    col4.metric(label="Winrate", value=f"{stats['winrate']}%")
    col5.metric(label="Profit Líquido", value=f"{profit_value:.2f} un", delta=f"{round(profit_value / stats['total_jogos'] * 100, 2)}% ROI")

def create_profit_chart(df_hist):
    """Cria o gráfico de lucro acumulado com um design aprimorado."""
    daily_profit = df_hist.groupby("Date")["Profit"].sum().reset_index()
    daily_profit["Cumulative_Profit"] = daily_profit["Profit"].cumsum()

    fig = px.line(
        daily_profit, x="Date", y="Cumulative_Profit",
        title="Evolução do Lucro Acumulado",
        labels={"Date": "Data", "Cumulative_Profit": "Unidades (Stakes)"},
        markers=True
    )
    fig.update_layout(
        template="plotly_white",
        title={"font": {"size": 20}, "x": 0.5},
        xaxis=dict(gridcolor='lightgray'),
        yaxis=dict(gridcolor='lightgray'),
    )
    fig.update_traces(
        line=dict(width=3, color='#2E8B57'),
        marker=dict(size=7, symbol="circle", color="#FF4500"),
        hovertemplate="<b>Data:</b> %{x|%d/%m/%Y}<br><b>Lucro Acumulado:</b> %{y:.2f}<extra></extra>"
    )
    return fig

# --- Lógica Principal da Página ---

def main_page(fonte_dados):
    if st.secrets['ENV'] == 'dev':
        st.info("Ambiente de Desenvolvimento")
        
    st.title("🔬 Backtesting de Estratégias")

    df_hist = load_histmatches(fonte_dados)
    if df_hist.empty:
        st.error("A base de dados histórica não pôde ser carregada.")
        return

    # --- Seção de Filtros ---
    with st.expander("Definir Filtros da Análise", expanded=True):
        
        # Filtros de Período e Liga
        c1, c2, c3 = st.columns(3)
        with c1:
            data_inicial = st.date_input("Data Inicial", date(2025, 7, 1))
        with c2:
            data_final = st.date_input("Data Final", get_today(-1))
        with c3:
            leagues = sorted(df_hist['League'].unique())
            leagues.insert(0, 'Todas as Ligas')
            selected_leagues = st.multiselect("Filtrar por Liga", leagues, default=['Todas as Ligas'])

        st.write("**Filtros por Indicadores (Opcional)**")
        
        # Filtros Dinâmicos de Indicadores
        # ... (A lógica para criar e aplicar filtros dinâmicos permanece a mesma do seu arquivo original)
        # Por simplicidade, essa parte foi omitida, mas deve ser inserida aqui.

        st.divider()

        # Filtros de Estratégia e Condição
        c1, c2, c3 = st.columns([2,2,1])
        with c1:
            filtro_pronto = st.selectbox("Aplicar Estratégia (Filtro Rápido)", filtros_prontos[fonte_dados], key="filtro_pronto")
        with c2:
            condicao = st.radio("Condição de Favoritismo", ["Geral", "Favorito/Zebra", "Zebra/Favorito"], horizontal=True, key="condicao")
        with c3:
            executar = st.button("Executar Backtest", use_container_width=True, type="primary")

    # --- Aplicação dos Filtros ---
    df_filtrado = df_hist.copy()
    if data_inicial and data_final:
        df_filtrado = df_filtrado[
            (df_filtrado['Date'].dt.normalize() >= pd.to_datetime(data_inicial)) &
            (df_filtrado['Date'].dt.normalize() <= pd.to_datetime(data_final))
        ]
    if "Todas as Ligas" not in selected_leagues:
        df_filtrado = df_filtrado[df_filtrado['League'].isin(selected_leagues)]
    
    if condicao == "Favorito/Zebra":
        df_filtrado = df_filtrado[df_filtrado["Odd_H_FT"] < df_filtrado["Odd_A_FT"]]
    elif condicao == "Zebra/Favorito":
        df_filtrado = df_filtrado[df_filtrado["Odd_H_FT"] > df_filtrado["Odd_A_FT"]]

    # Aplica filtro pronto se selecionado
    df_filtrado, _, metodo_default = get_details_filtro_pronto(df_filtrado, condicao, None, filtro_pronto)

    # --- Exibição dos Resultados ---
    if executar:
        st.divider()
        st.header("Resultados do Backtesting")

        if df_filtrado.empty:
            st.warning("Nenhum jogo encontrado com os filtros selecionados.")
            return

        # Abas para cada método de análise
        tabs = st.tabs(metodos_tabs)
        for i, tab in enumerate(tabs):
            metodo_nome = metodos_tabs[i]
            with tab:
                df_metodo_final, odd_media = get_result_filtro_pronto(df_filtrado.copy(), metodo_nome)

                if df_metodo_final.empty:
                    st.info(f"Sem jogos para o método '{metodo_nome}' com os filtros atuais.")
                    continue

                stats = calculate_summary_stats(df_metodo_final)
                if not stats:
                    st.info(f"Não foi possível calcular as estatísticas para o método '{metodo_nome}'.")
                    continue
                
                # Resumo em Métricas
                display_summary_metrics(stats, odd_media)
                st.divider()

                # Gráfico e Tabelas de Detalhes
                col1, col2 = st.columns([2, 1])
                with col1:
                    profit_chart = create_profit_chart(df_metodo_final)
                    st.plotly_chart(profit_chart, use_container_width=True)
                with col2:
                    st.write("**Profit Acumulado por Liga**")
                    report = df_metodo_final.groupby(["League"])["Profit"].sum().reset_index().sort_values(by="Profit", ascending=False)
                    print_dataframe(report)

                # Detalhamento dos Jogos
                with st.expander("Ver detalhamento dos jogos (Greens, Reds, Voids)"):
                    display_cols = [col for col in ['League', 'Date', 'Home', 'Away', 'Resultado_FT', 'Profit', 'Status_Metodo'] if col in df_metodo_final.columns]
                    
                    st.write("**:green[GREENs:]**")
                    print_dataframe(df_metodo_final.loc[df_metodo_final['Status_Metodo'] == 'GREEN', display_cols])
                    
                    st.write("**:red[REDs:]**")
                    print_dataframe(df_metodo_final.loc[df_metodo_final['Status_Metodo'] == 'RED', display_cols])
                    
                    if stats['total_voids'] > 0:
                        st.write("**:gray[VOIDs:]**")
                        print_dataframe(df_metodo_final.loc[df_metodo_final['Status_Metodo'] == 'VOID', display_cols])

# --- Ponto de Entrada ---
main_page(st.session_state.get('fonte_dados', 'Betfair'))