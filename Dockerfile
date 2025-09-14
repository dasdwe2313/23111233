# ===== Dockerfile =====
FROM python:3.11-slim

# ===== Variáveis de ambiente =====
ENV PYTHONUNBUFFERED=1 \
    DISCORD_TOKEN="" \
    SPOTIPY_CLIENT_ID="" \
    SPOTIPY_CLIENT_SECRET="" \
    SPOTIPY_REDIRECT_URI=""

# ===== Atualizar e instalar dependências =====
RUN apt-get update && \
    apt-get install -y ffmpeg curl git && \
    apt-get clean

# ===== Diretório do app =====
WORKDIR /app

# ===== Copiar arquivos =====
COPY requirements.txt .
COPY bot.py .

# ===== Instalar pacotes Python =====
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# ===== Comando para rodar o bot =====
CMD ["python", "bot.py"]
