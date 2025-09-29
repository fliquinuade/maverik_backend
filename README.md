# maverik_backend

## Configuración de ambiente:
Para configurar el ambiente:

- Instalar uv:

`curl -LsSf https://astral.sh/uv/install.sh | sh`

- Instalar Python 3.12:

`uv python install 3.12`

- Crear el ambiente virtual:

`uv venv --python 3.12`

- Instalar las dependencias:

`uv sync`

- Para levantar la API ejecuta:

`python -m uvicorn maverik_backend.api:app --host 0.0.0.0 --port 8082`
