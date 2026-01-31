import streamlit as st
from pymongo import MongoClient
import pandas as pd
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Ciclos Trade - Lay CS", layout="wide")

# Helper para formatar moeda em texto (Cards/Labels)
def format_brl(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def main_page():

    if st.secrets.get('ENV') == 'dev':
        st.info("Ambiente de Desenvolvimento. Branch: dev")

    st.title("Futapp v0.3")
    st.caption("desenvolvido por thiago pires")
    
    # Conexão MongoDB (Usando seus secrets)
    mongodb_host, mongodb_username, mongodb_password, mongodb_appName = st.secrets['mongodb'].values()
    connectionString = f"mongodb+srv://{mongodb_username}:{mongodb_password}@{mongodb_host}/?retryWrites=true&w=majority&appName={mongodb_appName}"
    client = MongoClient(connectionString)
    db = client.futdb
    ciclos_coll = db["ciclos"]

    # --- ORGANIZAÇÃO EM TABS ---
    tab_atual, tab_historico = st.tabs(["🛡️ Gestão de Ciclo Ativo", "📚 Ciclos Anteriores"])

    with tab_atual:
        # --- SEÇÃO 1: INICIALIZAÇÃO ---
        ciclo_ativo = ciclos_coll.find_one({"status": "ativo"})

        if not ciclo_ativo:
            with st.expander("🆕 Iniciar Novo Ciclo", expanded=True):
                col_ini1, col_ini2 = st.columns(2)
                resp_max = col_ini1.number_input("Responsabilidade Máxima do Ciclo (R$)", min_value=1.0, value=100.0)
                
                if st.button("Criar Ciclo"):
                    novo_ciclo = {
                        "status": "ativo",
                        "responsabilidade_inicial": resp_max,
                        "banca_atual": resp_max, 
                        "entradas": [],
                        "data_inicio": datetime.now()
                    }
                    ciclos_coll.insert_one(novo_ciclo)
                    st.rerun()

        # --- SEÇÃO 2: REGISTRO DE ENTRADA ---
        else:
            with st.container(border=True):
                st.subheader(f"Entrada Atual - Banca Disponível: {format_brl(ciclo_ativo['banca_atual'])}")
                
                # Campos solicitados
                c1, c2, c3 = st.columns(3)
                data_jogo = c1.date_input("DATA", datetime.now())
                jogo = c2.text_input("JOGO", placeholder="Ex: Real Madrid x City")
                liga = c3.text_input("LIGA", placeholder="Ex: Champions League")
                
                c4, c5, c6 = st.columns(3)
                entrada_desc = c4.text_input("ENTRADA", placeholder="Ex: Lay CS 0-0")
                odd_lay = c5.number_input("ODD LAY", min_value=1.01, step=0.1, value=5.0)
                
                # Cálculo Lay: Lucro = Responsabilidade / (Odd - 1)
                lucro_potencial = ciclo_ativo['banca_atual'] / (odd_lay - 1)
                c6.metric("Lucro Potencial (Green)", format_brl(lucro_potencial))

                res = st.radio("RESULTADO", ["Pendente", "✅ GREEN", "❌ RED"], horizontal=True)

                if st.button("Confirmar Registro"):
                    if res == "Pendente":
                        st.warning("Selecione Green ou Red para computar.")
                    else:
                        if res == "✅ GREEN":
                            novo_saldo = ciclo_ativo['banca_atual'] + lucro_potencial
                            status_ciclo = "ativo"
                        else:
                            novo_saldo = 0
                            status_ciclo = "encerrado"

                        nova_entrada = {
                            "data": str(data_jogo),
                            "jogo": jogo,
                            "liga": liga,
                            "entrada": entrada_desc,
                            "odd": odd_lay,
                            "resultado": res,
                            "lucro_obtido": lucro_potencial if res == "✅ GREEN" else -ciclo_ativo['banca_atual']
                        }

                        ciclos_coll.update_one(
                            {"_id": ciclo_ativo["_id"]},
                            {
                                "$set": {"banca_atual": novo_saldo, "status": status_ciclo},
                                "$push": {"entradas": nova_entrada}
                            }
                        )
                        st.rerun()

        # --- SEÇÃO 3: HISTÓRICO DO CICLO ATIVO ---
        if ciclo_ativo and ciclo_ativo["entradas"]:
            st.divider()
            st.subheader("📊 Itens do Ciclo Atual")
            df = pd.DataFrame(ciclo_ativo["entradas"])
            df = df[["data", "jogo", "liga", "entrada", "odd", "resultado", "lucro_obtido"]]
            
            st.dataframe(
                df, 
                use_container_width=True,
                hide_index=True,
                column_config={
                    "lucro_obtido": st.column_config.NumberColumn("Lucro", format="R$ %.2f"),
                    "odd": st.column_config.NumberColumn("Odd", format="%.2f")
                }
            )
            
            if st.button("Finalizar Ciclo (Sacar Lucro)"):
                ciclos_coll.update_one({"_id": ciclo_ativo["_id"]}, {"$set": {"status": "finalizado_sucesso"}})
                st.success("Lucro garantido! Ciclo arquivado.")
                st.rerun()

    # --- TAB 2: VISUALIZAR CICLOS ANTERIORES ---
    with tab_historico:
        st.subheader("📚 Histórico de Ciclos Encerrados")
        
        # Busca ciclos finalizados ou que deram red, ordenando pelo mais recente
        cursor_antigos = ciclos_coll.find({"status": {"$ne": "ativo"}}).sort("data_inicio", -1)
        ciclos_passados = list(cursor_antigos)
        
        if not ciclos_passados:
            st.info("Nenhum ciclo finalizado encontrado.")
        else:
            for ciclo in ciclos_passados:
                data_inicio = ciclo['data_inicio'].strftime('%d/%m/%Y')
                status_resumo = "✅ SUCESSO" if ciclo['status'] == "finalizado_sucesso" else "❌ RED"
                
                with st.expander(f"Ciclo {data_inicio} | Status: {status_resumo} | Saldo Final: {format_brl(ciclo['banca_atual'])}"):
                    if ciclo["entradas"]:
                        df_h = pd.DataFrame(ciclo["entradas"])
                        st.dataframe(
                            df_h[["data", "jogo", "liga", "entrada", "odd", "resultado", "lucro_obtido"]],
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "lucro_obtido": st.column_config.NumberColumn("Lucro", format="R$ %.2f")
                            }
                        )
                    else:
                        st.write("Ciclo sem entradas registradas.")