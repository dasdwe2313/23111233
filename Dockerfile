# ===== Base =====
FROM python:3.11-slim

# ===== Variáveis de ambiente =====
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ===== Diretório de trabalho =====
WORKDIR /app

# ===== Instalar dependências do sistema =====
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# ===== Copiar arquivos =====
COPY . /app

# ===== Atualizar pip e instalar dependências Python =====
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ===== Comando para rodar o bot =====
CMD ["python", "bot.py"]
