import streamlit as st
from pymongo import MongoClient
import pandas as pd

def main_page():

    if st.secrets['ENV'] == 'dev':
        st.info("Ambiente de Desenvolvimento. Branch: dev")

    st.title("Futapp v0.3")
    st.caption("desenvolvido por thiago pires")
    st.header("🚀 Sistema de Ciclos - Trade Esportivo")

    # Init
    # 1. Conexão com MongoDB (Substitua pela sua URI)
    mongodb_host, mongodb_username, mongodb_password, mongodb_appName = st.secrets['mongodb'].values()
    connectionString = f"mongodb+srv://{mongodb_username}:{mongodb_password}@{mongodb_host}/?retryWrites=true&w=majority&appName={mongodb_appName}"
    client = MongoClient(connectionString)
    db = client.futdb
    ciclos_coll = db.ciclos

    # Sidebar para criar novo ciclo
    with st.sidebar:
        st.header("Novo Ciclo")
        valor_inicial = st.number_input("Valor Inicial (R$)", min_value=1.0, value=100.0)
        meta_odds = st.number_input("Odd Média", min_value=1.01, value=1.50)
        
        if st.button("Iniciar Novo Ciclo"):
            novo_ciclo = {
                "status": "ativo",
                "valor_atual": valor_inicial,
                "historico": [],
                "progresso": 0
            }
            ciclos_coll.insert_one(novo_ciclo)
            st.success("Ciclo iniciado!")

    # 2. Exibição do Ciclo Ativo
    ciclo_atual = ciclos_coll.find_one({"status": "ativo"})

    if ciclo_atual:
        st.subheader(f"Ciclo em Andamento - Banca Atual: R$ {ciclo_atual['valor_atual']:.2f}")
        
        col1, col2 = st.columns(2)
        with col1:
            odd_entrada = st.number_input("Odd da Entrada", min_value=1.01, value=1.50)
        with col2:
            resultado = st.selectbox("Resultado", ["Pendente", "Green", "Red"])

        if st.button("Registrar Entrada"):
            if resultado == "Green":
                novo_valor = ciclo_atual['valor_atual'] * odd_entrada
                lucro = novo_valor - ciclo_atual['valor_atual']
                
                ciclos_coll.update_one(
                    {"_id": ciclo_atual["_id"]},
                    {
                        "$set": {"valor_atual": novo_valor},
                        "$push": {"historico": {"odd": odd_entrada, "resultado": "Green", "lucro": lucro}}
                    }
                )
                st.balloons()
                st.rerun()
            elif resultado == "Red":
                st.error("Ciclo Quebrado! Reinicie a gestão.")
                ciclos_coll.update_one({"_id": ciclo_atual["_id"]}, {"$set": {"status": "encerrado"}})
                st.rerun()

        # Exibir Tabela de Histórico
        if ciclo_atual["historico"]:
            df = pd.DataFrame(ciclo_atual["historico"])
            st.table(df)
    else:
        st.info("Nenhum ciclo ativo. Use a barra lateral para começar.")