import streamlit as st

# --- Lógica de Cálculo (Separada da UI) ---
# Nenhuma alteração necessária aqui.
def calcular_cashout_back_lay(odd_back, stake_back, odd_lay):
    """Calcula o cashout para uma aposta Back/Lay."""
    if odd_lay <= 1.0:
        return None
    
    stake_lay = (stake_back * odd_back) / odd_lay
    lucro_perda = stake_lay - stake_back
    
    return {
        "stake_necessaria": stake_lay,
        "lucro_perda": lucro_perda
    }

def calcular_cashout_lay_back(odd_lay, responsabilidade_lay, odd_back):
    """Calcula o cashout para uma aposta Lay/Back."""
    if odd_lay <= 1.0 or odd_back <= 1.0:
        return None

    stake_lay = responsabilidade_lay / (odd_lay - 1)
    stake_back = (stake_lay * odd_lay) / odd_back
    lucro_perda = (stake_back * (odd_back - 1)) - responsabilidade_lay
    
    return {
        "stake_necessaria": stake_back,
        "lucro_perda": lucro_perda
    }

# --- Interface Principal (CORRIGIDA) ---

def main_page():

    if st.secrets.get('ENV') == 'dev':
        st.info("Ambiente de Desenvolvimento. Branch: dev")

    st.title("Futapp v0.3")
    st.caption("desenvolvido por thiago pires")
    st.header("⚽ Calculadora de Trading")

    with st.expander("📘 Como usar a calculadora?"):
        st.markdown("""
        Esta ferramenta calcula o valor que você precisa apostar para garantir um lucro (ou minimizar uma perda) antes do final de um evento.

        - **Aba Back/Lay**: Use quando você fez uma aposta **a favor** de um resultado (`Back`) e quer fechá-la com uma aposta **contra** (`Lay`).
        - **Aba Lay/Back**: Use quando você fez uma aposta **contra** um resultado (`Lay`) e quer fechá-la com uma aposta **a favor** (`Back`).
        """)

    aba = st.radio(
        "Selecione o tipo de operação:",
        ["Back/Lay", "Lay/Back"],
        key="active_tab",
        horizontal=True
    )

    col_entrada, col_resultado = st.columns(2, gap="large")

    # --- Coluna de Entrada de Dados ---
    with col_entrada:
        with st.form(key="calculadora_form"):
            if aba == "Back/Lay":
                st.subheader("Sua aposta inicial (Back)")
                st.number_input("Odd Back", min_value=1.01, step=0.01, format="%.2f", key="bl_odd_back")
                st.number_input("Stake Back (R$)", min_value=0.01, step=1.00, format="%.2f", key="bl_stake_back")
                
                st.subheader("Fechamento da aposta (Lay)")
                st.number_input("Odd Lay de Fechamento", min_value=1.01, step=0.01, format="%.2f", key="bl_odd_lay")

            elif aba == "Lay/Back":
                st.subheader("Sua aposta inicial (Lay)")
                st.number_input("Odd Lay", min_value=1.01, step=0.01, format="%.2f", key="lb_odd_lay")
                st.number_input("Sua Responsabilidade (R$)", min_value=0.01, step=1.00, format="%.2f", key="lb_responsabilidade_lay")
                
                st.subheader("Fechamento da aposta (Back)")
                st.number_input("Odd Back de Fechamento", min_value=1.01, step=0.01, format="%.2f", key="lb_odd_back")

            submitted = st.form_submit_button("Calcular Cashout")

    # --- Coluna de Resultados (CORRIGIDA) ---
    with col_resultado:
        st.subheader("Resultado do Cashout")
        
        if submitted:
            resultado = None
            label_stake = ""

            if aba == "Back/Lay":
                # CORREÇÃO: Usar st.session_state para obter os valores dos inputs.
                resultado = calcular_cashout_back_lay(
                    st.session_state.bl_odd_back, 
                    st.session_state.bl_stake_back, 
                    st.session_state.bl_odd_lay
                )
                label_stake = "Stake de Lay necessária:"
                
            elif aba == "Lay/Back":
                # CORREÇÃO: Usar st.session_state para obter os valores dos inputs.
                resultado = calcular_cashout_lay_back(
                    st.session_state.lb_odd_lay, 
                    st.session_state.lb_responsabilidade_lay, 
                    st.session_state.lb_odd_back
                )
                label_stake = "Stake de Back necessária:"

            if resultado:
                lucro_perda = resultado['lucro_perda']
                
                st.metric(label=label_stake, value=f"R$ {resultado['stake_necessaria']:.2f}")
                st.metric(
                    label="Lucro / Prejuízo Garantido:",
                    value=f"R$ {lucro_perda:.2f}",
                    delta=f"{lucro_perda:.2f}"
                )
            else:
                st.error("Verifique os valores inseridos. Odds devem ser maiores que 1.0.")
        else:
            st.info("Preencha os dados da aposta e clique em 'Calcular' para ver o resultado.")