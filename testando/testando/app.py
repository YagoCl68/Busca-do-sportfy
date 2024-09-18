from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from testando.schemas import Musica, Musicas
import base64
import requests
import random
import time

# Inicializando o FastAPI
app = FastAPI()

# Informações de autenticação do Spotify
client_id = "03d8c173d4dc4b2fadfc95c767e82645"
client_secret = "1fc63f29ccfd4a0e8d5769073a137964"

# URL para obter o token de acesso
token_url = "https://accounts.spotify.com/api/token"

# Codificar credenciais em Base64
credentials = f"{client_id}:{client_secret}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# Definir os parâmetros e cabeçalhos para obter o token
data = {
    'grant_type': 'client_credentials'
}
headers = {
    'Authorization': f'Basic {encoded_credentials}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Variáveis globais para armazenar o token e o tempo de expiração
access_token = None
token_expires_at = 0

# Configurar a pasta estática
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

@app.get("/", response_class=HTMLResponse)
def serve_html():
    try:
        with open("templates/index.html", encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content, media_type="text/html; charset=UTF-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar a página: {e}")

def get_access_token():
    global access_token, token_expires_at

    # Se o token já estiver definido e ainda não expirou, reutilize-o
    if access_token and time.time() < token_expires_at:
        return access_token

    # Caso contrário, faça uma nova solicitação para obter um novo token
    try:
        response = requests.post(token_url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        token_info = response.json()
        access_token = token_info['access_token']
        token_expires_at = time.time() + token_info['expires_in']
        return access_token
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter token do Spotify: {e}")

def get_with_retry(url, headers, params=None, max_retries=5):
    retries = 0
    while retries < max_retries:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:  # Too Many Requests
            wait_time = 2 ** retries  # Exponential backoff
            print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            retries += 1
        else:
            response.raise_for_status()
    raise HTTPException(status_code=429, detail="Rate limit exceeded after multiple retries.")

@app.get("/suggestions/")
def get_suggestions(q: str = Query(...)):
    try:
        access_token = get_access_token()
        search_headers = {
            'Authorization': f'Bearer {access_token}'
        }

        search_params = {
            'q': q,
            'type': 'track',
            'limit': 5  # Limitar as sugestões
        }
        search_url = "https://api.spotify.com/v1/search"
        response = requests.get(search_url, headers=search_headers, params=search_params)
        response.raise_for_status()

        search_results = response.json()
        tracks = search_results.get('tracks', {}).get('items', [])

        suggestions = [{'name': track['name']} for track in tracks]

        return {"suggestions": suggestions}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar sugestões: {e}")

@app.get("/search/", response_model=Musicas)
def buscar_musica(q: str = Query(None, description="Nome da música ou artista a ser buscado")):
    try:
        access_token = get_access_token()
        if not access_token:
            return Musicas(musicas=[])

        search_headers = {
            'Authorization': f'Bearer {access_token}'
        }

        results = []

        # Buscar por músicas
        search_params = {
            'q': f'track:"{q}"',
            'type': 'track',
            'limit': 20
        }
        search_url = "https://api.spotify.com/v1/search"
        search_results = get_with_retry(search_url, search_headers, search_params)

        tracks = search_results.get('tracks', {}).get('items', [])
        if tracks:
            results.extend([Musica(link=f"https://open.spotify.com/embed/track/{track['id']}") for track in tracks])

        # Buscar por artistas
        search_params = {
            'q': q,
            'type': 'artist',
            'limit': 5
        }
        artist_results = get_with_retry(search_url, search_headers, search_params)

        artists = artist_results.get('artists', {}).get('items', [])
        if artists:
            artist_id = artists[0]['id']
            tracks_params = {
                'limit': 20,
                'market': 'US'  # Mercado que deseja buscar (US, BR, etc.)
            }
            tracks_url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
            tracks_results = get_with_retry(tracks_url, search_headers, tracks_params)

            tracks = tracks_results.get('tracks', [])
            results.extend([Musica(link=f"https://open.spotify.com/embed/track/{track['id']}") for track in tracks])

        # Embaralhar a lista de resultados antes de retornar
        random.shuffle(results)
        return Musicas(musicas=results)

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar músicas/artistas: {e}")