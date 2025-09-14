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
ENV DISCORD_TOKEN=OTA0MDY2MTc2MDk3ODQ5NDM0.GuSI43.brM8ArOyPI5lAmXw0wWNuoo8j-actmX6GT00_s
ENV SPOTIPY_CLIENT_ID=dba006a65be04444aa7e47f445cf27ca
ENV SPOTIPY_CLIENT_SECRET=54d00fbdf26f44149f3d2ec0f08473bb
ENV SPOTIPY_REDIRECT_URI=https://localhost:8882338/callback12323

# ===== Comando para rodar o bot =====
CMD ["python", "bot.py"]
