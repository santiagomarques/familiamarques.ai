import streamlit as st

# 1. Configuração da Página e Estilo Visual (CSS)
st.set_page_config(page_title="Família Marques AI", page_icon="🏠", layout="wide")

# Aqui é onde a magia acontece para não ficar "uma merda"
st.markdown("""
    <style>
    /* Mudar o fundo de todo o site */
    .stApp {
        background: linear-gradient(to right, #1e3c72, #2a5298);
        color: white;
    }
    
    /* Estilo do Título */
    h1 {
        color: #00d2ff;
        font-family: 'Helvetica Neue', sans-serif;
        text-align: center;
        text-shadow: 2px 2px 4px #000000;
    }

    /* Estilo das caixas de texto */
    .stMarkdown {
        font-size: 1.2rem;
        text-align: center;
    }

    /* Botão personalizado */
    .stButton>button {
        background-color: #00d2ff;
        color: white;
        border-radius: 50px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #fff;
        color: #1e3c72;
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Conteúdo do Site
st.title("🏠 Família Marques AI")
st.markdown("### O nosso portal inteligente e exclusivo")

st.write("---")

# Criar colunas para organizar melhor
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.info("Bem-vindos! Este site foi criado pelo Santiago para unir a tecnologia e a nossa família.")
    
    nome = st.text_input("Como te chamas, membro da família?")
    if nome:
        st.write(f"Olá, **{nome}**! É bom ver-te por aqui hoje.")

st.write("---")

# Botão de Celebração
if st.button('✨ LANÇAR CELEBRAÇÃO DA FAMÍLIA!'):
    st.balloons()
    st.snow()
    st.success("A Família Marques é a melhor! 🎉")
