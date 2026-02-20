import streamlit as st
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Família Marques AI", page_icon="⚡", layout="wide")

# --- ESTILO HACKER 2026 (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;500&display=swap');
    
    .stApp {
        background-color: #050505;
        color: #00ff41;
        font-family: 'Fira Code', monospace;
    }
    
    /* Login Box */
    .login-box {
        border: 2px solid #00ff41;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 0 20px #00ff41;
        background: rgba(0, 20, 0, 0.9);
    }
    
    /* Sidebar Personalizada */
    section[data-testid="stSidebar"] {
        background-color: #000c00 !important;
        border-right: 1px solid #00ff41;
    }

    /* Botões Hacker */
    .stButton>button {
        border: 1px solid #00ff41 !important;
        background: transparent !important;
        color: #00ff41 !important;
        transition: 0.3s;
        text-transform: uppercase;
        width: 100%;
    }
    .stButton>button:hover {
        background: #00ff41 !important;
        color: black !important;
        box-shadow: 0 0 15px #00ff41;
    }

    /* Mural */
    .mural {
        border: 1px dashed #00ff41;
        padding: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DADOS VOLÁTIL (Em memória) ---
if "users" not in st.session_state:
    st.session_state.users = {
        "Santiago Marques": {"pin": "1234", "level": "Jarvis", "bday": "2000-01-01", "loc": "Portugal"}
    }
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "mural_msg" not in st.session_state:
    st.session_state.mural_msg = "Bem-vindos ao Protocolo Família Marques 2026."
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#050505"

# --- LÓGICA DE LOGIN ---
if not st.session_state.logged_in:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.title("🔐 ACESSO AO SISTEMA")
        
        mode = st.radio("Escolha:", ["Entrar", "Novo Registo"], horizontal=True)
        
        nome = st.text_input("NOME:")
        pin = st.text_input("PIN:", type="password")
        
        if mode == "Novo Registo":
            bday = st.date_input("ANIVERSÁRIO:")
            loc = st.selectbox("LOCALIZAÇÃO:", ["Portugal", "Brasil"])
            foto = st.file_uploader("FOTO PERFIL:")
            
        if st.button("EXECUTAR LOGIN"):
            if mode == "Entrar":
                if nome in st.session_state.users and st.session_state.users[nome]["pin"] == pin:
                    st.session_state.logged_in = True
                    st.session_state.current_user = nome
                    st.rerun()
                else:
                    st.error("PIN INVÁLIDO OU UTILIZADOR INEXISTENTE")
            else:
                st.session_state.users[nome] = {"pin": pin, "level": "Básico", "bday": str(bday), "loc": loc}
                st.success("CONTA CRIADA. FAÇA LOGIN.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- INTERFACE PRINCIPAL ---
else:
    user_data = st.session_state.users[st.session_state.current_user]
    is_admin = user_data["level"] == "Jarvis"

    # --- SIDEBAR (Histórico e Níveis) ---
    with st.sidebar:
        st.header("📂 HISTÓRICO")
        st.write("---")
        st.caption("Logs de conversas antigas...")
        
        if is_admin:
            st.write("---")
            st.header("⚡ ADMIN: JARVIS")
            if st.checkbox("VER BASE DE DADOS"):
                st.write(st.session_state.users)
            
            new_mural = st.text_input("EDITAR MURAL:")
            if st.button("ATUALIZAR"):
                st.session_state.mural_msg = new_mural

    # --- CABEÇALHO E INFO DIREITA ---
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        st.markdown(f"**NÍVEL:** `{user_data['level']}`")
    with c2:
        st.markdown(f"<div class='mural'> {st.session_state.mural_msg} </div>", unsafe_allow_html=True)
    with c3:
        st.write(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
        st.write(f"⏰ {datetime.now().strftime('%H:%M')}")
        if st.button("🌦️ CLIMA"):
            st.write("Céu Limpo | 22°C")
            st.caption("Próximos dias: Sol constante")

    # --- ANIVERSÁRIO ---
    today = datetime.now().strftime('%m-%d')
    if user_data['bday'][5:] == today:
        st.balloons()
        st.success(f"🎂 FELIZ ANIVERSÁRIO, {st.session_state.current_user}!")

    # --- MODOS ---
    modo = st.selectbox("MODO DE OPERAÇÃO:", ["Fast 1.5", "Expert 4.0", "Shopping", "Study Focus"])

    # --- ÁREA DE CHAT ---
    chat_container = st.container()
    
    with chat_container:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.write(m["content"])

    # --- MODO SHOPPING ---
    if modo == "Shopping":
        st.warning("🛒 MODO COMPRAS ATIVO")
        item = st.text_input("O QUE QUERES COMPRAR?")
        if item:
            moeda = "€" if user_data["loc"] == "Portugal" else "R$"
            st.markdown(f"**RESULTADOS PARA:** {item}")
            # Simulação de pesquisa
            col_p, col_v, col_l = st.columns(3)
            col_p.write(f"Produto: {item} Pro")
            col_v.write(f"Preço: {moeda} 499.00")
            col_l.write("[LINK DA LOJA](https://google.com)")
            st.write("---")
            st.write(f"**TOTAL DA SESSÃO:** {moeda} 499.00")

    # --- INPUT DE IA ---
    prompt = st.chat_input("Insira comando ou peça imagem...")
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Lógica de mudar fundo se falar em imagem
        if "imagem" in prompt.lower() or "carro" in prompt.lower():
            st.session_state.bg_color = "#001a1a" # Muda tom do fundo
            
        # Resposta simulada (Para não depender de API paga agora)
        response = f"Protocolo {modo} ativo. Percebo que estás focado. Aqui está a análise de: {prompt}"
        
        if "imagem" in prompt.lower():
            response = "🎨 IMAGEM GERADA: [Espaço reservado para imagem da IA]"
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    # --- MODO ESTUDO ---
    if modo == "Study Focus":
        st.info("📚 MODO FOCO: Notificações silenciadas. IA em modo explicativo.")
