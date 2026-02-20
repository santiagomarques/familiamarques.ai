import streamlit as st
import datetime
import random
import base64
from PIL import Image, ImageDraw
import io
import requests  # Para APIs externas, como clima e compras (usuário precisa de chaves API)
import os
import json

# Configurações iniciais
APP_TITLE = "Família Marques AI - Hacker Family 2026"
OWNER_NAME = "Santiago Marques"
OWNER_PIN = "1234"  # Mude para um PIN real e seguro!
DATA_FILE = "family_data.json"  # Arquivo para armazenar dados da família

# Carregar ou criar dados da família
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        family_data = json.load(f)
else:
    family_data = {
        "users": {},
        "levels": {},
        "admin": OWNER_NAME,
        "mural": []  # Para inquéritos ou frases inspiradoras
    }
    family_data["users"][OWNER_NAME] = {"pin": OWNER_PIN, "photo": None, "birthday": None}
    family_data["levels"][OWNER_NAME] = "Jarvis"
    with open(DATA_FILE, "w") as f:
        json.dump(family_data, f)

# Função para gerar imagem simples do zero (ex: carro básico com Pillow)
def generate_image(description):
    img = Image.new('RGB', (300, 200), color='white')
    draw = ImageDraw.Draw(img)
    if "carro" in description.lower():
        # Desenho simples de um carro
        draw.rectangle([50, 100, 250, 150], fill='blue')  # Corpo
        draw.ellipse([60, 140, 100, 180], fill='black')  # Roda esquerda
        draw.ellipse([200, 140, 240, 180], fill='black')  # Roda direita
    # Salvar em buffer para base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

# Função para obter clima (use sua chave OpenWeatherMap)
def get_weather(city="Lisboa"):  # Mude para localização padrão
    api_key = "SUA_CHAVE_OPENWEATHER"  # Coloque sua chave aqui
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=pt"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return f"Clima agora: {data['weather'][0]['description']}, {data['main']['temp']}°C"
    return "Erro ao obter clima"

# Função para previsão (simplificada)
def get_forecast(city="Lisboa"):
    return "Previsão: Amanhã ensolarado, 20°C; Depois chuva, 15°C"  # Use API real para mais detalhes

# Função para pesquisa de compras (simulada com web search placeholder)
def search_product(product, currency="EUR"):  # EUR para Portugal, BRL para Brasil
    # Simule pesquisa; use Google Shopping API ou similar na vida real
    products = [
        {"name": product, "price": f"10 {currency}", "link": "https://exemplo.com"},
        {"name": product, "price": f"15 {currency}", "link": "https://exemplo.com"}
    ]
    return products

# Função para IA simples (placeholder para GPT-like; integre OpenAI API)
def ai_response(user_input, mode, context):
    if "cria uma imagem" in user_input.lower():
        desc = user_input.split("de")[-1].strip()
        img = generate_image(desc)
        return f"Aqui está a imagem gerada: <img src='{img}' alt='Imagem gerada'>", "background-carro"  # Muda fundo
    elif mode == "shopping":
        product = user_input.split("quero")[-1].strip()
        currency = "EUR" if "portugal" in context else "BRL"
        products = search_product(product, currency)
        return f"Opções: {products[0]['name']} - {products[0]['price']} [Comprar]({products[0]['link']})", None
    elif mode == "study":
        return f"Foco no estudo: Resposta detalhada sobre {user_input}", None
    else:
        return f"Resposta da IA: {user_input} processado em modo {mode}", None

# Interface principal
st.set_page_config(page_title=APP_TITLE, layout="wide")

# Estilo hacker 2026: Verde em preto
st.markdown("""
    <style>
    .stApp { background-color: black; color: lime; font-family: 'Courier New', monospace; }
    .sidebar .sidebar-content { background-color: #111; }
    button { background-color: #222; color: lime; border: 1px solid lime; }
    </style>
""", unsafe_allow_html=True)

# Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.mode = "fast"
    st.session_state.cart = []
    st.session_state.conversations = []
    st.session_state.current_convo = []

st.title(APP_TITLE)

if not st.session_state.logged_in:
    st.subheader("Login - Primeira Vez? Crie sua conta!")
    name = st.text_input("Nome (Primeiro Nome)")
    pin = st.text_input("PIN (4 dígitos)", type="password")
    photo = st.file_uploader("Foto de Perfil (opcional)", type=["jpg", "png"])
    birthday = st.date_input("Data de Aniversário")
    
    if st.button("Entrar / Criar"):
        if name in family_data["users"]:
            if family_data["users"][name]["pin"] == pin:
                st.session_state.logged_in = True
                st.session_state.user = name
                st.session_state.level = family_data["levels"].get(name, "Básico")
                # Checar aniversário
                today = datetime.date.today()
                if birthday.month == today.month and birthday.day == today.day:
                    st.balloons()
                    st.success(f"Feliz Aniversário, {name}!")
            else:
                st.error("PIN errado!")
        else:
            # Novo usuário (só família, mas sem verificação extra)
            family_data["users"][name] = {"pin": pin, "photo": photo.name if photo else None, "birthday": str(birthday)}
            family_data["levels"][name] = "Básico"
            with open(DATA_FILE, "w") as f:
                json.dump(family_data, f)
            st.session_state.logged_in = True
            st.session_state.user = name
            st.session_state.level = "Básico"
            # Explicação na primeira vez
            st.info("""
            Bem-vindo à Família Marques AI!
            - Esquerda: Histórico de conversas.
            - Barra: Falar com IA, upload imagens (pede permissão).
            - Direita: Hora, data, clima (clique para previsão).
            - Modos: Fast (rápido), Expert (detalhado), Shopping (compras), Study (estudo focado).
            - Admin (só Santiago): Controle níveis, ver PINs, mural.
            - Fundo muda com contexto (ex: imagem de carro).
            - Níveis ocultos: Só admin sabe.
            """)

else:
    user = st.session_state.user
    level = st.session_state.level
    is_admin = user == OWNER_NAME
    
    # Layout: Colunas
    left, center, right = st.columns([1, 3, 1])
    
    with left:
        st.subheader("Histórico de Conversas")
        for i, convo in enumerate(st.session_state.conversations):
            if st.button(f"Conversa {i+1}"):
                st.session_state.current_convo = convo
        if st.button("Nova Conversa"):
            st.session_state.conversations.append(st.session_state.current_convo)
            st.session_state.current_convo = []
    
    with right:
        st.subheader("Info")
        st.write(f"Hora: {datetime.datetime.now().strftime('%H:%M')}")
        st.write(f"Dia: {datetime.date.today()}")
        weather = get_weather()
        if st.button(weather):
            st.write(get_forecast())
        if is_admin:
            st.subheader("Admin")
            for u in family_data["users"]:
                st.write(f"{u}: PIN {family_data['users'][u]['pin']}, Nível {family_data['levels'].get(u, 'Básico')}")
            new_level_user = st.text_input("Atribuir Nível a Usuário")
            new_level = st.text_input("Novo Nível")
            if st.button("Atribuir"):
                family_data["levels"][new_level_user] = new_level
                with open(DATA_FILE, "w") as f:
                    json.dump(family_data, f)
            # Mural
            mural_msg = st.text_area("Postar no Mural (inquérido ou frase)")
            if st.button("Postar"):
                family_data["mural"].append(mural_msg)
                with open(DATA_FILE, "w") as f:
                    json.dump(family_data, f)
    
    with center:
        st.subheader(f"Bem-vindo, {user}! Nível: {level if is_admin else 'Oculto'}")
        
        # Mural da família
        st.subheader("Mural da Família")
        for msg in family_data["mural"]:
            st.write(msg)
        
        # Modos
        mode = st.selectbox("Modo", ["Fast", "Expert", "Shopping", "Study"])
        st.session_state.mode = mode
        
        # Chat
        for msg in st.session_state.current_convo:
            st.write(msg)
        
        user_input = st.text_input("Fale com a IA:")
        if st.button("Enviar"):
            response, bg_change = ai_response(user_input, mode, "portugal")  # Detecte localização
            st.session_state.current_convo.append(f"Você: {user_input}")
            st.session_state.current_convo.append(f"IA: {response}")
            if bg_change:
                st.markdown(f"<style>.stApp {{ background-image: url('url_de_fundo_{bg_change}.jpg'); }}</style>", unsafe_allow_html=True)
        
        # Upload imagens
        upload = st.file_uploader("Upload Imagem (Galeria/Drive)", type=["jpg", "png"])
        if upload:
            st.image(upload)
        
        # Carrinho no modo shopping
        if mode == "Shopping" and st.session_state.cart:
            total = sum(float(p["price"].split()[0]) for p in st.session_state.cart)
            st.write(f"Total: {total} EUR/BRL")
            for item in st.session_state.cart:
                st.write(f"{item['name']} - {item['price']} [Link]({item['link']})")

# Detectar "sentimento" na escrita (simples: se tem ! ou maiúsculas)
def detect_sentiment(text):
    if "!" in text or text.isupper():
        return "Energético!"
    return "Calmo."

# Exemplo de uso no response: response += f" (Sentimento: {detect_sentiment(user_input)})"
