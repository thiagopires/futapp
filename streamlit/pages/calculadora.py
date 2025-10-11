import streamlit as st

# --- Lógica de Cálculo (Separada da UI) ---
# MELHORIA: Mover os cálculos para funções dedicadas torna o código mais limpo.

def calcular_cashout_back_lay(odd_back, stake_back, odd_lay):
    """Calcula o cashout para uma aposta Back/Lay."""
    if odd_lay == 0: # Evita divisão por zero
        return None
    
    stake_lay = (stake_back * odd_back) / odd_lay
    lucro_perda = stake_lay - stake_back
    
    return {
        "stake_necessaria": stake_lay,
        "lucro_perda": lucro_perda
    }

def calcular_cashout_lay_back(odd_lay, responsabilidade_lay, odd_back):
    """Calcula o cashout para uma aposta Lay/Back."""
    if odd_lay <= 1 or odd_back == 0: # Evita divisões inválidas
        return None

    stake_lay = responsabilidade_lay / (odd_lay - 1)
    stake_back = (stake_lay * odd_lay) / odd_back
    lucro_perda = (stake_back * (odd_back - 1)) - responsabilidade_lay
    
    return {
        "stake_necessaria": stake_back,
        "lucro_perda": lucro_perda
    }

# --- Interface Principal ---

def main_page():

    if st.secrets.get('ENV') == 'dev':
        st.info("Ambiente de Desenvolvimento. Branch: dev")

    st.title("Futapp v0.3")
    st.caption("desenvolvido por thiago pires")
    st.header("⚽ Calculadora de Trading")

    # MELHORIA: Expander com instruções para ajudar o usuário.
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
        horizontal=True # MELHORIA: Deixa o rádio mais compacto.
    )

    col_entrada, col_resultado = st.columns(2, gap="large")

    # --- Coluna de Entrada de Dados ---
    with col_entrada:
        # MELHORIA: st.form melhora a UX ao evitar recálculos a cada alteração.
        # O cálculo só ocorre quando o botão é pressionado.
        with st.form(key="calculadora_form"):
            if aba == "Back/Lay":
                st.subheader("Sua aposta inicial (Back)")
                bl_odd_back = st.number_input("Odd Back", min_value=1.01, step=0.01, format="%.2f", key="bl_odd_back")
                bl_stake_back = st.number_input("Stake Back (€)", min_value=0.01, step=1.00, format="%.2f", key="bl_stake_back")
                
                st.subheader("Fechamento da aposta (Lay)")
                bl_odd_lay = st.number_input("Odd Lay de Fechamento", min_value=1.01, step=0.01, format="%.2f", key="bl_odd_lay")

            elif aba == "Lay/Back":
                st.subheader("Sua aposta inicial (Lay)")
                lb_odd_lay = st.number_input("Odd Lay", min_value=1.01, step=0.01, format="%.2f", key="lb_odd_lay")
                lb_responsabilidade_lay = st.number_input("Sua Responsabilidade (€)", min_value=0.01, step=1.00, format="%.2f", key="lb_responsabilidade_lay")
                
                st.subheader("Fechamento da aposta (Back)")
                lb_odd_back = st.number_input("Odd Back de Fechamento", min_value=1.01, step=0.01, format="%.2f", key="lb_odd_back")

            submitted = st.form_submit_button("Calcular Cashout")

    # --- Coluna de Resultados ---
    with col_resultado:
        st.subheader("Resultado do Cashout")
        
        # MELHORIA: A lógica de exibição é acionada apenas pelo botão do formulário.
        if submitted:
            resultado = None
            label_stake = ""

            if aba == "Back/Lay":
                resultado = calcular_cashout_back_lay(bl_odd_back, bl_stake_back, bl_odd_lay)
                label_stake = "Stake de Lay necessária:"
                
            elif aba == "Lay/Back":
                resultado = calcular_cashout_lay_back(lb_odd_lay, lb_responsabilidade_lay, lb_odd_back)
                label_stake = "Stake de Back necessária:"

            if resultado:
                lucro_perda = resultado['lucro_perda']
                delta_color = "normal" # cinza para 0
                if lucro_perda > 0:
                    delta_color = "inverse" # verde