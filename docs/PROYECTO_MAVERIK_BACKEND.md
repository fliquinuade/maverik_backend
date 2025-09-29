## Resumen del proyecto

Maverik Backend es una API REST construida con FastAPI que expone funcionalidades para el registro y autenticación de usuarios y para gestionar sesiones de asesoría financiera asistida por un servicio de recuperación de información (RAG) y, opcionalmente, un servicio de optimización de portafolios.

El objetivo es ofrecer un backend que: 1) almacene perfiles de usuario y sus preferencias financieras, 2) gestione sesiones de asesoría con historial de chat, 3) delegue la generación de respuestas al servicio RAG y 4) cuando aplique, solicite a un servicio de optimización un portafolio preliminar.

## Tecnologías principales

- Python 3.12
- FastAPI (servidor web / router / validación)
- SQLAlchemy 2.x (ORM)
- Alembic (migraciones)
- PostgreSQL (BD relacional; driver: `pg8000`)
- Pydantic / pydantic-settings (config y schemas)
- python-paseto (PASETO v4) para tokens
- requests (llamadas a servicios externos)
- Mangum (adaptador para AWS Lambda)

Dependencias están en `requirements.txt` y el proyecto usa `pyproject.toml`.

## Estructura del repositorio (relevante)

- `maverik_backend/`
  - `api.py` : definición de endpoints y dependencias (FastAPI).
  - `settings.py` : carga de configuración desde `.env` a Pydantic `Settings`.
  - `core/`
    - `database.py` : creación de engine y session factory.
    - `models.py` : modelos SQLAlchemy (usuarios, sesiones, catálogos, detalles de chat).
    - `schemas.py` : Pydantic schemas usados por endpoints y servicios.
    - `services.py` : lógica de negocio, armado de prompts, llamadas al servicio RAG y al optimizador.
    - `smtp.py` : helpers para enviar email (API o SMTP).
  - `utils/`
    - `auth.py` : helpers de PASETO (firmar, verificar, bearer auth).
- `alembic/` : scripts de migración; `versions/` contiene la migración que crea las tablas base.
- `deployments/backend.Dockerfile` : imagen para ejecutar la app.
- `docker-compose.yml` : define servicios `db` (Postgres) y `backend`.
- `.env` : valores de configuración por entorno (DB, endpoints externos, SMTP, etc.).

## Qué hace y cómo funciona (flujo típico)

1. Un cliente crea una cuenta con `POST /user/signup`. El backend genera una clave temporal, persiste el usuario y manda un email con credenciales.
2. El usuario hace `POST /user/login` con (email, clave). Si coincide en DB, el servidor devuelve un token PASETO (Bearer token).
3. Con token válido, el usuario puede crear una sesión de asesoría `POST /copilot/sessions`. Se guarda la sesión con sus metadatos.
4. Para iniciar o continuar el chat, el cliente llama `POST /copilot/sessions/{session_id}`. El backend:
   - recupera perfil del usuario (desde la DB) y prepara `userProfile` y `chatHistory`.
   - envía un JSON al servicio RAG (configurado en `rag_service_url`).
   - si es la primera interacción y hay respuesta, opcionalmente pide a `portfolio_optimization_url` un portafolio según el perfil de riesgo y lo concatena al output.
   - persiste el detalle (input/output) en `sesion_asesoria_detalle`.

## Endpoints disponibles (resumen)

- `GET /` — ping básico.
- `POST /user/signup` — crear usuario. Body: `UsuarioCrearRequest`.
- `POST /user/login` — login, devuelve token. Body: `UsuarioLogin`.
- `POST /copilot/sessions` — crear sesión de asesoría. Requiere Authorization Bearer PASETO.
- `POST /copilot/sessions/{session_id}` — enviar/continuar chat en sesión; envía al RAG y guarda detalle. Requiere auth.
- `GET /copilot/sessions/{session_id}` — obtener historial de detalles de una sesión. Requiere auth.

Los shapes de requests/responses están en `core/schemas.py`.

## Servicios externos y dependencias

- Servicio RAG (`rag_service_url`): se espera un endpoint `POST /api/chat` que reciba `{userProfile, chatHistory, input}` y responda un `response` de texto.
- Servicio de optimización de portafolio (`portfolio_optimization_url`): se llama a `/portfolio/generate/{risk_profile}` y debe devolver JSON con `assets` y `weights` para anexar al mensaje.
- SMTP/API de email (`smtp_api_url`, `smtp_api_key`, `mail_sender_*`) para enviar el correo de bienvenida.
- Base de datos Postgres (servicio `db` en docker-compose). En el contenedor `backend`, el host DB esperado es `db:5432`.

## Variables de configuración importantes (.env)

- db_name, db_schema, db_username, db_password, db_host, db_port
- rag_service_url
- portfolio_optimization_url
- frontend_url
- smtp_api_url, smtp_api_key, mail_sender_name, mail_sender_address

El `alembic/env.py` del repo está preparado para leer la configuración desde `settings.load_config()` por lo que es preferible mantener estos valores en `.env` y no hardcodear credenciales en `alembic.ini`.

## Migraciones

- Alembic está presente (`alembic/versions/0b2e5472511d_create_usuario_tables.py`) y crea las tablas y contenido base.
- Para ejecutar migraciones asegúrate de tener un `alembic.ini` en la raíz con `script_location = alembic` o generar uno con `alembic init` dentro del contenedor.
- Desde Docker Compose, dentro del contenedor `backend` la DB es accesible como `db:5432`. Si ejecutas desde host Windows con compose mapeado, el puerto puede ser distinto (p. ej. `5433` en tu `docker-compose.yml` local) y la URL de alembic debe apuntar a `localhost:5433` si corres alembic en host.

## Consideraciones y recomendaciones para desarrollo futuro

1. Seguridad de contraseñas: hoy las claves se almacenan en texto plano en la DB y se envían por email. Cambiar a hashing seguro (bcrypt/argon2) y flujo de creación de contraseña (signup → email verificación → set password) es prioritario.
2. Gestión de secretos: mover `secret_key` de PASETO y otros secretos fuera del repo y usar variables de entorno o un vault.
3. Token y expiración: el PASETO ya incluye campo `expires`; validar y rotar keys según ciclo.
4. Endpoint `/health`: el `Dockerfile` usa un healthcheck HTTP; agregar `GET /health` que valide DB y dependencias mejorará despliegue.
5. Tests: agregar tests unitarios e integración (pytest + factory fixtures + base de datos en memoria o testcontainers).
6. Autorización/permiso: hoy el token solo identifica usuario; agregar validaciones para asegurar que el usuario solicitante sea el dueño de la sesión (evitar acceso cruzado).
7. Manejo de errores y timeouts: proteger las llamadas a RAG/optimizer con timeouts, reintentos y circuit breaker si es necesario.
8. Hashing/rotación de claves PASETO y manejo de claves en entorno productivo.
9. Validación y sanitización del contenido de `rag_service` antes de persistirlo.
10. Documentación y OpenAPI: FastAPI ya expone `/docs` y `/openapi.json`; mantener y completar schemas y tipos.

## Cómo ejecutar (resumen rápido)

Con Docker Compose (preferido):

1. Crea un `.env` en la raíz (ejemplo ya incluido en repo). Asegurate `db_password` y otros valores.
2. Levanta:

```bat
docker compose up --build
```

3. Ejecuta migraciones desde el contenedor (opcional si las aplicás al arranque):

```bat
docker compose exec backend alembic upgrade head
```

Local (sin Docker):

```bat
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn maverik_backend.api:app --host 0.0.0.0 --port 8082
```

Nota: cuando ejecutes `alembic upgrade head` verifica que exista `alembic.ini` en la raíz. El `alembic/env.py` del repo ya construye la URL leyendo `settings.load_config()` (lee `.env`), por lo que si trabajas desde host puedes apuntar a `localhost:<puerto_mapeado>` según tu `docker-compose.yml`.

## Próximos pasos sugeridos (priorizados)

1. Reemplazar almacenamiento de contraseñas por hashing y flujo de set-password.
2. Añadir `/health` y revisiones básicas de dependencias (DB, RAG, optimizer).
3. Tests automáticos básicos (registro/login, creación sesión, persistencia de detalle).
4. Agregar validaciones de ownership en endpoints de sesiones.
5. Mejorar manejo de errores en `services.enviar_chat_al_rag` (timeouts, logs, fallback cuando RAG falla).

---

Archivo generado automáticamente: `docs/ARCHITECTURE.md` — Úsalo como guía para continuar el desarrollo.
