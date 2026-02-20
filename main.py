import streamlit as st

st.set_page_config(page_title="Família Marques AI", page_icon="🏠")
st.title("🏠 Família Marques AI")
st.subheader("Bem-vindos ao nosso projeto!")

if st.button('Ativar Comemoração!'):
    st.balloons()
    st.success("O site está online, Santiago! 🎉")import streamlit as st
from io import BytesIO
import time

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Família Marques AI", page_icon="🛡️", layout="wide")

# Estilo Dark Mode Personalizado
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #2e7d32; color: white; transition: 0.3s; }
    .stButton>button:hover { background-color: #1b5e20; border: 1px solid white; }
    .stTextInput>div>div>input { background-color: #262730; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DADOS EM MEMÓRIA ---
if "contas" not in st.session_state:
    st.session_state.contas = {
        "Santiago Marques": {"pass": "1234", "nivel": 110},
        "Pai": {"pass": "familia", "nivel": 3},
        "Mãe": {"pass": "familia", "nivel": 3}
    }

if "mural" not in st.session_state:
    st.session_state.mural = "Bem-vindos ao novo sistema da Família Marques! 🚀"

# --- LÓGICA DE LOGIN ---
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🛡️ Família Marques AI")
    st.subheader("Entrada no Sistema")
    
    nomes_disponiveis = list(st.session_state.contas.keys())
    nome = st.selectbox("Quem és?", nomes_disponiveis + ["+ Criar Nova Conta"])

    if nome == "+ Criar Nova Conta":
        novo_nome = st.text_input("Escolhe o teu nome de utilizador:")
        nova_pass = st.text_input("Escolhe a tua password:", type="password")
        if st.button("Finalizar Registo"):
            if novo_nome and nova_pass:
                st.session_state.contas[novo_nome] = {"pass": nova_pass, "nivel": 1}
                st.success("Conta criada! Seleciona agora o teu nome na lista e entra.")
            else:
                st.error("Preenche todos os campos!")
    else:
        password = st.text_input("Password:", type="password")
        if st.button("Entrar no Painel"):
            if password == st.session_state.contas[nome]["pass"]:
                st.session_state.logado = True
                st.session_state.user = nome
                st.session_state.nivel = st.session_state.contas[nome]["nivel"]
                st.rerun()
            else:
                st.error("Password incorreta. Tenta novamente.")

else:
    # --- INTERFACE PRINCIPAL ---
    
    # Mural (Fixo no topo)
    st.info(f"📌 **MURAL DA FAMÍLIA:** {st.session_state.mural}")

    # Menu Lateral
    with st.sidebar:
        st.title(f"👤 {st.session_state.user}")
        st.write(f"Nível de Acesso: **{st.session_state.nivel}**")
        st.divider()
        
        menu = st.radio("Navegação:", ["💬 Chat Privado", "📚 Modo Estudo", "🖼️ Gerador de QR Code"])
        
        if st.session_state.nivel == 110:
            st.divider()
            if st.button("⚙️ GESTÃO DO SISTEMA"):
                st.session_state.pagina = "admin"
                st.rerun()
        
        if st.button("Sair"):
            st.session_state.logado = False
            st.rerun()

    # --- PÁGINAS ---
    
    # Se carregou no botão de admin, muda a página
    if "pagina" in st.session_state and st.session_state.pagina == "admin":
        st.subheader("⚙️ Painel do Administrador (Santiago)")
        
        # Editar Mural
        novo_texto_mural = st.text_area("Atualizar Mural da Família:", value=st.session_state.mural)
        if st.button("Atualizar Mural para Todos"):
            st.session_state.mural = novo_texto_mural
            st.success("Mural atualizado!")
        
        st.divider()
        st.write("📊 **Utilizadores e Permissões**")
        for user, dados in st.session_state.contas.items():
            col1, col2 = st.columns([2, 1])
            col1.write(f"**{user}** (Nível {dados['nivel']})")
            if col2.button(f"Subir Nível", key=f"btn_{user}"):
                st.session_state.contas[user]["nivel"] += 1
                st.rerun()
        
        if st.button("Voltar ao Chat"):
            del st.session_state.pagina
            st.rerun()

    elif menu == "💬 Chat Privado":
        st.subheader("💬 Chat Privado com IA")
        
        # Histórico de Chat Privado
        if "historico" not in st.session_state:
            st.session_state.historico = []

        for msg in st.session_state.historico:
            st.chat_message(msg["role"]).write(msg["content"])

        prompt = st.chat_input("Como posso ajudar a família hoje?")
        if prompt:
            st.session_state.historico.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            
            # Resposta simulada (Até ligares a API Key no Secrets)
            resposta = f"Olá {st.session_state.user}! Estou a processar o teu pedido..."
            
            st.session_state.historico.append({"role": "assistant", "content": resposta})
            st.chat_message("assistant").write(resposta)

    elif menu == "📚 Modo Estudo":
        st.subheader("🚀 Foco e Estudo")
        materia = st.text_input("O que vais estudar agora?", placeholder="Ex: Programação, Matemática...")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⏱️ Iniciar Temporizador (25 min)"):
                st.toast(f"Foco iniciado em {materia}!")
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.1) # Simulação rápida
                    progress_bar.progress(i + 1)
                st.success("Sessão de estudo terminada! Hora de uma pausa.")
        with c2:
            if st.button("📝 Criar Questionário"):
                st.write(f"Vou gerar 3 perguntas sobre {materia} para te testar...")

    elif menu == "🖼️ Gerador de QR Code":
        if st.session_state.nivel >= 3:
            st.subheader("🖼️ Criar QR Code Rápido")
            link = st.text_input("Cola aqui o link ou texto:")
            if st.button("Gerar Imagem"):
                if link:
                    qr = qrcode.make(link)
                    buf = BytesIO()
                    qr.save(buf)
                    st.image(buf, caption="QR Code Gerado com Sucesso!")
                else:
                    st.warning("Insere um link primeiro.")
        else:
            st.error("🔒 Função Bloqueada. Precisas de Nível 3 (Pede ao Santiago!).")
