import streamlit as st

# 1. Configuração de Estilo (O que faz o site ficar BONITO)
st.set_page_config(page_title="Família Marques AI", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        background-image: radial-gradient(circle at 2px 2px, #1d2129 1px, transparent 0);
        background-size: 40px 40px;
        color: #ffffff;
    }
    .main-title {
        font-size: 50px;
        font-weight: bold;
        color: #00f2fe;
        text-align: center;
        text-shadow: 0 0 10px #00f2fe;
    }
    .stButton>button {
        background: linear-gradient(45deg, #00f2fe, #4facfe);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Título Impactante
st.markdown('<p class="main-title">🤖 Família Marques AI Portal</p>', unsafe_allow_html=True)
st.write("---")

# 3. Organização em Colunas
col1, col2 = st.columns([1, 1])

with col1:
    st.header("⚡ O Nosso Painel")
    st.info("Aqui vamos ligar a Inteligência Artificial e o nosso mural.")
    if st.button('🚀 Ativar Sistema'):
        st.balloons()
        st.success("SISTEMA MARQUES ONLINE!")

with col2:
    st.header("💬 Chat da Família")
    st.chat_input("Escreve aqui a tua ideia...")
    st.caption("Aguardando configuração da API Key do Google...")

st.write("---")
st.subheader("🖼️ Mural do Futuro")
# Aqui vai entrar a imagem que vou gerar para ti agora
