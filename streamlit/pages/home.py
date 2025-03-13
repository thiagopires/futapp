from utils.functions import *
from utils.filters import *

def main_page():
    if st.secrets['ENV'] == 'dev':
        st.info("Ambiente de Desenvolvimento. Branch: dev")

    st.title("Futapp v0.2")

    st.write("Conteúdo protegido para usuários logados.")