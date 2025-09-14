# ===== Imagem base =====
FROM python:3.11-slim

# ===== Diretório de trabalho =====
WORKDIR /app

# ===== Copiar arquivos =====
COPY requirements.txt .
COPY bot.py .

# ===== Instalar dependências =====
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# ===== Variáveis de ambiente =====
ENV DISCORD_TOKEN=seu_token_aqui
ENV SPOTIPY_CLIENT_ID=seu_client_id
ENV SPOTIPY_CLIENT_SECRET=seu_client_secret
ENV SPOTIPY_REDIRECT_URI=seu_redirect_uri

# ===== Comando para rodar o bot =====
CMD ["python", "bot.py"]
