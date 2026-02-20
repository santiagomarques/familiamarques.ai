import streamlit as st
import datetime
import random
import base64
from PIL import Image, ImageDraw
import io
import requests  # Para APIs externas
import os
import json
from openai import OpenAI  # Para IA real
import streamlit.components.v1 as components  # Para JS custom
import hashlib
import hmac

# Configurações iniciais
APP_TITLE = "Família Marques AI - Hacker Family 2026"
OWNER_NAME = "Santiago Marques"
OWNER_PIN = "1234"  # Mude para um PIN real e seguro!
DATA_FILE = "family_data.json"  # Arquivo para armazenar dados
OPENAI_API_KEY = "SUA_CHAVE_OPENAI_AQUI"  # Coloque sua chave OpenAI
AMAZON_ACCESS_KEY = "SUA_AMAZON_ACCESS_KEY"  # Chave de acesso Amazon PA API
AMAZON_SECRET_KEY = "SUA_AMAZON_SECRET_KEY"  # Chave secreta Amazon PA API
AMAZON_ASSOCIATE_TAG = "SUA_ASSOCIATE_TAG"  # Tag de associado Amazon

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
    family_data["users"][OWNER_NAME] = {"pin": OWNER_PIN, "photo": None, "birthday": None, "location": "Portugal"}
    family_data["levels"][OWNER_NAME] = "Jarvis"
    with open(DATA_FILE, "w") as f:
        json.dump(family_data, f)

# Cliente OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Função para gerar imagem com DALL-E
def generate_image(description):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=description,
            n=1,
            size="1024x1024"
        )
        img_url = response.data[0].url
        return img_url
    except Exception as e:
        return f"Erro ao gerar imagem: {e}"

# Função para obter taxa de câmbio
def get_exchange_rate(from_curr, to_curr):
    url = f"https://api.exchangerate.host/convert?from={from_curr}&to={to_curr}&amount=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['result']
    return 1  # Fallback se erro

# Função para obter clima
def get_weather(city="Lisboa"):
    api_key = "SUA_CHAVE_OPENWEATHER"  # Coloque sua chave aqui
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=pt"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return f"Clima agora: {data['weather'][0]['description']}, {data['main']['temp']}°C"
    return "Erro ao obter clima"

# Função para previsão
def get_forecast(city="Lisboa"):
    return "Previsão: Amanhã ensolarado, 20°C; Depois chuva, 15°C"  # Use API real

# Função SigV4 para Amazon
def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def get_signature_key(key, date_stamp, region_name, service_name):
    k_date = sign(('AWS4' + key).encode('utf-8'), date_stamp)
    k_region = sign(k_date, region_name)
    k_service = sign(k_region, service_name)
    k_signing = sign(k_service, 'aws4_request')
    return k_signing

def search_amazon(product, host, region, marketplace, currency):
    method = 'POST'
    service = 'ProductAdvertisingAPI'
    endpoint = f'https://{host}/paapi5/searchitems'
    request_parameters = json.dumps({
        "Keywords": product,
        "Resources": [
            "ItemInfo.Title",
            "Offers.Listings.Price"
        ],
        "PartnerTag": AMAZON_ASSOCIATE_TAG,
        "PartnerType": "Associates",
        "Marketplace": marketplace
    })

    t = datetime.datetime.utcnow()
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')

    canonical_uri = '/paapi5/searchitems'
    canonical_query_string = ''
    canonical_headers = 'content-type:application/json; charset=utf-8\n' + 'host:' + host + '\n' + 'x-amz-date:' + amz_date + '\n' + 'x-amz-target:com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems\n'
    signed_headers = 'content-type;host;x-amz-date;x-amz-target'
    payload_hash = hashlib.sha256(request_parameters.encode('utf-8')).hexdigest()

    canonical_request = method + '\n' + canonical_uri + '\n' + canonical_query_string + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash

    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = date_stamp + '/' + region + '/' + service.lower() + '/' + 'aws4_request'
    string_to_sign = algorithm + '\n' +  amz_date + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()

    signing_key = get_signature_key(AMAZON_SECRET_KEY, date_stamp, region, service.lower())
    signature = hmac.new(signing_key, (string_to_sign.encode('utf-8')), hashlib.sha256).hexdigest()

    authorization_header = algorithm + ' ' + 'Credential=' + AMAZON_ACCESS_KEY + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Host': host,
        'X-Amz-Date': amz_date,
        'X-Amz-Target': 'com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems',
        'Authorization': authorization_header
    }

    r = requests.post(endpoint, data=request_parameters, headers=headers)
    if r.status_code == 200:
        data = r.json()
        items = data.get('SearchItemsResponse', {}).get('ItemsResult', {}).get('Items', [])
        products = []
        rate = get_exchange_rate("EUR" if "es" in marketplace else "BRL", currency)  # Ajuste se necessário
        for item in items:
            title = item.get('ItemInfo', {}).get('Title', {}).get('DisplayValue', 'N/A')
            price = item.get('Offers', {}).get('Listings', [{}])[0].get('Price', {}).get('Amount', 0)
            converted_price = price * rate
            link = item.get('DetailPageURL', '')
            products.append({
                "name": title,
                "price": f"{converted_price:.2f} {currency}",
                "link": link
            })
        return products
    return [{"name": "Erro", "price": "N/A", "link": ""}]

# Função para pesquisa de compras
def search_product(product, location="Portugal"):
    currency = "EUR" if location == "Portugal" else "BRL"
    if location == "Brasil":
        # Use Mercado Livre para Brasil
        site_id = "MLB"
        api_currency = "BRL"
        url = f"https://api.mercadolibre.com/sites/{site_id}/search?q={product}&sort=price_asc&limit=5"
        response = requests.get(url)
        if response.status_code != 200:
            return [{"name": "Erro", "price": "N/A", "link": ""}]
        data = response.json()
        products = []
        rate = get_exchange_rate(api_currency, currency) if currency != api_currency else 1
        for item in data.get('results', []):
            original_price = item['price']
            converted_price = original_price * rate
            products.append({
                "name": item['title'],
                "price": f"{converted_price:.2f} {currency}",
                "link": item['permalink']
            })
        return products
    else:
        # Use Amazon para Portugal
        host = "webservices.amazon.es"
        region = "eu-west-1"
        marketplace = "www.amazon.es"
        return search_amazon(product, host, region, marketplace, currency)

# Função para resposta da IA usando OpenAI
def ai_response(user_input, mode, context, location):
    # Detectar sentimento simples
    sentiment = detect_sentiment(user_input)
    system_prompt = f"Você é uma IA amigável para a família Marques. Modo: {mode}. Sentimento do usuário: {sentiment}. Localização: {location}. Responda de forma adaptada."
    
    if "cria uma imagem" in user_input.lower():
        desc = user_input.split("de")[-1].strip()
        img_url = generate_image(desc)
        bg_change = "background-image: url('{}');".format(img_url)  # Tenta mudar fundo
        return f"Aqui está a imagem gerada: ![Imagem]({img_url})", bg_change
    
    # Usar ChatGPT
    try:
        response = client.chat.completions.create(
            model="gpt-4o" if mode == "expert" else "gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content, None
    except Exception as e:
        return f"Erro na IA: {e}", None

# Detectar sentimento simples
def detect_sentiment(text):
    positive_words = ['bom', 'ótimo', 'feliz', 'amo', 'gosto']
    negative_words = ['ruim', 'triste', 'ódio', 'não gosto']
    score = sum(1 for word in positive_words if word in text.lower()) - sum(1 for word in negative_words if word in text.lower())
    if score > 0:
        return "Positivo - Respondendo animado!"
    elif score < 0:
        return "Negativo - Respondendo com empatia."
    else:
        return "Neutro."

# JS para localização
def get_location():
    components.html("""
    <script>
    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(showPosition);
        } else {
            parent.document.querySelector("#location").innerHTML = "Geolocalização não suportada.";
        }
    }
    function showPosition(position) {
        parent.document.querySelector("#location").innerHTML = "Latitude: " + position.coords.latitude + 
        "<br>Longitude: " + position.coords.longitude;
    }
    getLocation();
    </script>
    <p id="location">Obtendo localização...</p>
    """, height=100)

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
    st.session_state.location = "Portugal"

st.title(APP_TITLE)

if not st.session_state.logged_in:
    st.subheader("Login - Primeira Vez? Crie sua conta!")
    name = st.text_input("Nome (Primeiro Nome)")
    pin = st.text_input("PIN (4 dígitos)", type="password")
    photo = st.file_uploader("Foto de Perfil (opcional)", type=["jpg", "png"])
    birthday = st.date_input("Data de Aniversário")
    location = st.selectbox("Localização", ["Portugal", "Brasil"])
    
    if st.button("Entrar / Criar"):
        if name in family_data["users"]:
            if family_data["users"][name]["pin"] == pin:
                st.session_state.logged_in = True
                st.session_state.user = name
                st.session_state.level = family_data["levels"].get(name, "Básico")
                st.session_state.location = family_data["users"][name].get("location", "Portugal")
                # Checar aniversário
                today = datetime.date.today()
                if birthday.month == today.month and birthday.day == today.day:
                    st.balloons()
                    st.success(f"Feliz Aniversário, {name}!")
            else:
                st.error("PIN errado!")
        else:
            # Novo usuário
            family_data["users"][name] = {"pin": pin, "photo": photo.name if photo else None, "birthday": str(birthday), "location": location}
            family_data["levels"][name] = "Básico"
            with open(DATA_FILE, "w") as f:
                json.dump(family_data, f)
            st.session_state.logged_in = True
            st.session_state.user = name
            st.session_state.level = "Básico"
            st.session_state.location = location
            # Explicação na primeira vez
            st.info("""
            Bem-vindo à Família Marques AI!
            - Esquerda: Histórico de conversas.
            - Barra: Falar com IA, upload imagens (pede permissão do navegador).
            - Direita: Hora, data, clima (clique para previsão).
            - Modos: Fast (rápido), Expert (detalhado), Shopping (compras), Study (estudo focado).
            - Admin (só Santiago): Controle níveis, ver PINs, mural.
            - Fundo muda com contexto (ex: imagem de carro).
            - Níveis ocultos: Só admin sabe.
            - IA detecta sentimento e adapta resposta.
            - Modo Shopping integra Mercado Livre (Brasil) e Amazon (Portugal/Brasil).
            """)

else:
    user = st.session_state.user
    level = st.session_state.level
    is_admin = user == OWNER_NAME
    location = st.session_state.location
    currency = "EUR" if location == "Portugal" else "BRL"
    
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
        weather = get_weather("Lisboa" if location == "Portugal" else "São Paulo")
        if st.button(weather):
            st.write(get_forecast())
        get_location()  # Mostra localização
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
            mural_msg = st.text_area("Postar no Mural (inquérito ou frase)")
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
            response, bg_change = ai_response(user_input, mode, "família", location)
            st.session_state.current_convo.append(f"Você: {user_input}")
            st.session_state.current_convo.append(f"IA: {response}")
            if bg_change:
                st.markdown(f"<style>.stApp {{ {bg_change} background-size: cover; }}</style>", unsafe_allow_html=True)
        
        # Upload imagens
        upload = st.file_uploader("Upload Imagem (Galeria/Drive)", type=["jpg", "png"])
        if upload:
            st.image(upload)
        
        # Modo shopping: exibir produtos e adicionar ao carrinho
        if mode == "Shopping":
            if user_input and "quero" in user_input.lower():
                product = user_input.split("quero")[-1].strip()
                products = search_product(product, location)
                for p in products:
                    st.write(f"{p['name']} - {p['price']} [Comprar]({p['link']})")
                    if st.button(f"Adicionar {p['name']} ao carrinho"):
                        st.session_state.cart.append(p)
            if st.session_state.cart:
                # Calcular total na moeda do usuário
                total = sum(float(p["price"].split()[0]) for p in st.session_state.cart)
                st.write(f"Total: {total:.2f} {currency}")
                for item in st.session_state.cart:
                    st.write(f"{item['name']} - {item['price']} [Link]({item['link']})")
