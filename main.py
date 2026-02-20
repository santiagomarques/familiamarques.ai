import streamlit as st
import google.generativeai as genai

# 1. Configuração Visual
st.set_page_config(page_title="Família Marques AI", page_icon="🤖", layout="centered")

# Estilo para ficar mais bonito
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #ff4b4b; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 Família Marques AI")
st.write("---")

# 2. Menu Lateral (Sidebar)
with st.sidebar:
    st.header("⚙️ Definições")
    api_key = st.text_input("Insere a tua Google API Key:", type="password")
    st.info("Precisas da chave para a IA responder!")

# 3. Área do Chat Inteligente
st.subheader("💬 Conversa com a nossa IA")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensagens antigas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input do utilizador
if prompt := st.chat_input("Diz algo à família..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Lógica da IA (Gemini)
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error("Erro na IA. Verifica a tua chave!")
    else:
        st.warning("⚠️ Por favor, coloca a tua API Key no menu lateral para eu poder responder.")

# 4. Rodapé Especial
st.write("---")
if st.button('✨ Lançar Balões de Celebração!'):
    st.balloons()
