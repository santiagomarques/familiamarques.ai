import streamlit as st
import google.generativeai as genai
from datetime import datetime
import time

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Família Marques AI", layout="wide")

# --- ESTILO HACKER FAMÍLIA 2026 (O Visual que pediste) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00ff41; font-family: 'Courier New', monospace; }
    .stTextInput>div>div>input { background-color: #050505 !important; color: #00ff41 !important; border: 1px solid #00ff41 !important; }
    .stButton>button { background-color: #003300; color: #00ff41; border: 1px solid #00ff41; border-radius: 0px; width: 100%; }
    .stButton>button:hover { background-color: #00ff41; color: #000; }
    .sidebar .sidebar-content { background-color: #050505; border-right: 1px solid #00ff41; }
    [data-testid="stMetricValue"] { color: #00ff41 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DADOS (Em Memória) ---
if "users" not in st.session_state:
    # Santiago já nasce como Jarvis
    st.session_state.users = {"Santiago Marques": {"pin": "2026", "level": "Jarvis", "loc": "Portugal", "bday": "2010-01-01"}}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "mural" not in st.session_state: st.session_state.mural = "Bem-vindos ao futuro. Protocolo Marques Ativo."
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "cart" not in st.session_state: st.session_state.cart = []

# --- SISTEMA DE LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🔐 FAMÍLIA MARQUES AI: LOGIN</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        modo_login = st.radio("Ação:", ["Entrar", "Novo Registo (1ª Vez)"])
        nome = st.text_input("NOME:")
        pin = st.text_input("PIN (4 dígitos):", type="password")
        
        if modo_login == "Novo Registo (1ª Vez)":
            loc = st.selectbox("LOCALIZAÇÃO:", ["Portugal", "Brasil"])
            bday = st.date_input("DATA DE ANIVERSÁRIO:")
            foto = st.file_uploader("FOTO DE PERFIL:")
            if st.button("CRIAR CONTA"):
                st.session_state.users[nome] = {"pin": pin, "level": "Membro", "loc": loc, "bday": str(bday)}
                st.success("Conta criada! Agora muda para 'Entrar'.")
        
        if st.button("EXECUTAR ACESSO"):
            if nome in st.session_state.users and st.session_state.users[nome]["pin"] == pin:
                st.session_state.logged_in = True
                st.session_state.user = nome
                st.rerun()
            else: st.error("ACESSO NEGADO: Dados incorretos.")

# --- PORTAL ATIVO ---
else:
    user = st.session_state.user
    u_data = st.session_state.users[user]
    is_jarvis = u_data["level"] == "Jarvis"

    # Verificação de Aniversário
    if datetime.now().strftime('%m-%d') in u_data["bday"]:
        st.balloons()
        st.toast(f"🎂 FELIZ ANIVERSÁRIO, {user.upper()}!")

    # --- SIDEBAR (HISTÓRICO E INFO) ---
    with st.sidebar:
        st.title("📂 SISTEMA")
        st.write(f"USER: {user}")
        st.write(f"NÍVEL: {u_data['level']}")
        st.write("---")
        st.subheader("📜 HISTÓRICO")
        for h in st.session_state.chat_history[-5:]: st.text(f"> {h[:20]}...")
        
        if is_jarvis:
            st.header("🛠️ PAINEL JARVIS")
            if st.checkbox("VER TODOS OS PINS"): st.write(st.session_state.users)
            novo_mural = st.text_input("EDITAR MURAL:")
            if st.button("POSTAR"): st.session_state.mural = novo_mural

    # --- LAYOUT PRINCIPAL ---
    c_left, c_right = st.columns([2, 1])

    with c_right:
        st.markdown(f"### 🕒 {datetime.now().strftime('%H:%M:%S')}")
        st.markdown(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
        if st.button("🌡️ CLIMA"): 
            st.write("Hoje: 22°C - Céu Limpo")
            st.write("Próximos 3 dias: ☀️ ☀️ ⛈️")
        
        st.markdown("---")
        st.markdown(f"### 📢 MURAL\n> {st.session_state.mural}")

    with c_left:
        modo = st.selectbox("MODO IA:", ["Fast 1.5", "Expert 4.0", "Shopping 🛒", "Study Focus 📚"])
        
        # Chat
        for m in st.session_state.chat_history:
            st.text(m)

        prompt = st.chat_input("Comando para a IA...")
        
        if prompt:
            st.session_state.chat_history.append(f"VOCÊ: {prompt}")
            
            # Resposta Dinâmica
            if modo == "Shopping 🛒":
                moeda = "€" if u_data["loc"] == "Portugal" else "R$"
                res = f"IA: Encontrei '{prompt}' pelo melhor preço de {moeda} 150.00 [LINK]"
                st.session_state.cart.append(150.00)
                st.write(f"**TOTAL CARRINHO:** {moeda} {sum(st.session_state.cart)}")
            elif "imagem" in prompt.lower() or "carro" in prompt.lower():
                res = "IA: Gerando imagem... [Fundo do site alterado para modo visual]"
                st.markdown("<style>.stApp { background-image: url('https://source.unsplash.com/random/1600x900/?tech'); background-size: cover; }</style>", unsafe_allow_html=True)
            else:
                res = f"IA ({modo}): Processando comando... Protocolo Marques em execução."
            
            st.session_state.chat_history.append(res)
            st.rerun()

    # Tutorial para a primeira vez
    if len(st.session_state.chat_history) < 2:
        st.info("💡 BEM-VINDO: No lado ESQUERDO falas com a IA. No lado DIREITO tens as horas e o mural do Santiago. Usa os MODOS para mudar a postura da IA.")
