FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

# Dependencias del sistema:
# - libsodium: requerido por pysodium/PASETO (evita el problema en Windows)
# - curl: para healthcheck
# - build-essential: por si alguna wheel necesita compilar (uvloop/httptools en ARM, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsodium23 curl build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar deps primero (mejor cache)
COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

# Copiar el código
COPY . .

# Puerto app
EXPOSE 8082

# Variables por defecto (podés sobreescribir APP_MODULE en compose/.env)
ENV APP_MODULE=maverik_backend.api:app \
    APP_HOST=0.0.0.0 \
    APP_PORT=8082

# Healthcheck al endpoint /health
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD curl -fsS http://localhost:${APP_PORT}/health || exit 1

# Ejecutar en modo desarrollo con --reload
CMD ["sh", "-c", "python -m uvicorn $APP_MODULE --host $APP_HOST --port $APP_PORT --reload"]