import streamlit as st

st.set_page_config(layout="wide")

USERS = {
    "admin": "1234",
    "user": "abcd"
}

def authenticate(username, password):
    return USERS.get(username) == password

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Login")

    username = st.text_input("Usuário", value="admin", key="username")
    password = st.text_input("Senha", value="1234", type="password", key="password")
    login_button = st.button("Entrar")

    if login_button:
        if authenticate(username, password):
            st.session_state.authenticated = True
            st.success("Login realizado com sucesso!")
            st.info("Escolha um módulo no menu lateral.")
        else:
            st.error("Usuário ou senha incorretos.")
else:
    st.title("Página Principal")
    st.write("Você está autenticado!")

    # Botão para logout
    if st.button("Logout"):
        st.session_state.authenticated = False



# import streamlit as st

# st.set_page_config(layout="wide")

# st.title("Web App Football Data")

# st.write("Escolha um módulo na sidebar.")