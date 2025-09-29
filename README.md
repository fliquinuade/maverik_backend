# Maverik Backend

API REST construida con FastAPI que proporciona funcionalidades para el registro y autenticación de usuarios, y gestión de sesiones de asesoría financiera asistida por servicios de RAG (Retrieval-Augmented Generation) y optimización de portafolios.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Tecnologías](#-tecnologías)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Ejecución](#-ejecución)
- [API Endpoints](#-api-endpoints)
- [Documentación](#-documentación)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Desarrollo](#-desarrollo)
- [Deployment](#-deployment)
- [Contribución](#-contribución)

## 🚀 Características

- **Autenticación segura** con tokens PASETO v4
- **Gestión de usuarios** con registro y login
- **Sesiones de asesoría financiera** con historial de chat
- **Integración con servicios RAG** para respuestas inteligentes
- **Optimización de portafolios** mediante servicios externos
- **Envío de emails** para notificaciones de usuario
- **Base de datos PostgreSQL** con migraciones automáticas
- **Contenedorización** con Docker y Docker Compose
- **Documentación automática** con OpenAPI/Swagger

## 🛠 Tecnologías

- **Python 3.12**
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy 2.x** - ORM para Python
- **Alembic** - Migraciones de base de datos
- **PostgreSQL** - Base de datos relacional
- **Pydantic** - Validación de datos y configuración
- **PASETO v4** - Tokens seguros para autenticación
- **Docker & Docker Compose** - Contenedorización

## 📋 Requisitos Previos

### Opción 1: Con Docker (Recomendado)
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Opción 2: Desarrollo Local
- [Python 3.12+](https://www.python.org/downloads/)
- [uv](https://github.com/astral-sh/uv) - Gestor de paquetes rápido para Python
- [PostgreSQL 16+](https://www.postgresql.org/download/)

## ⚙️ Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd maverik_backend
```

### 2. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar el archivo .env con tus configuraciones
# Ver sección de configuración más abajo
```

### 3. Configuración de variables de entorno

Edita el archivo `.env` con los siguientes valores:

```bash
# Base de datos
DB_NAME=maverik
DB_USERNAME=maverik
DB_PASSWORD=tu_password_seguro
DB_HOST=localhost  # usar 'db' para Docker Compose
DB_PORT=5432

# Servicios externos (URLs de tus servicios RAG y optimización)
RAG_SERVICE_URL=http://tu-servicio-rag
PORTFOLIO_OPTIMIZATION_URL=http://tu-servicio-portafolio

# Configuración de email
SMTP_API_URL=tu_smtp_api_url
SMTP_API_KEY=tu_smtp_api_key
MAIL_SENDER_NAME=Maverik App
MAIL_SENDER_ADDRESS=noreply@tudominio.com

# Generar clave secreta:
# python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=tu_clave_secreta_de_64_caracteres
```

## 🚀 Ejecución

### Opción 1: Con Docker Compose (Recomendado)

```bash
# Construir y levantar los servicios
docker compose up --build

# En segundo plano
docker compose up -d --build

# Ejecutar migraciones de base de datos
docker compose exec backend alembic upgrade head
```

La API estará disponible en: http://localhost:8082

### Opción 2: Desarrollo Local

#### Instalar uv (si no lo tienes)

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Configurar el ambiente

```bash
# Instalar Python 3.12
uv python install 3.12

# Crear ambiente virtual
uv venv --python 3.12

# Activar ambiente virtual
# Linux/macOS:
source .venv/bin/activate
# Windows:
.\.venv\Scripts\activate

# Instalar dependencias
uv sync

# Ejecutar migraciones
alembic upgrade head

# Levantar la API
python -m uvicorn maverik_backend.api:app --host 0.0.0.0 --port 8082 --reload
```

## 📚 API Endpoints

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/` | Health check | No |
| POST | `/user/signup` | Registro de usuario | No |
| POST | `/user/login` | Inicio de sesión | No |
| POST | `/copilot/sessions` | Crear sesión de asesoría | Sí |
| POST | `/copilot/sessions/{id}` | Enviar mensaje en sesión | Sí |
| GET | `/copilot/sessions/{id}` | Obtener historial de sesión | Sí |

### Documentación interactiva

Una vez que la aplicación esté ejecutándose, puedes acceder a:

- **Swagger UI**: http://localhost:8082/docs
- **ReDoc**: http://localhost:8082/redoc
- **OpenAPI JSON**: http://localhost:8082/openapi.json

## 📁 Estructura del Proyecto

```
maverik_backend/
├── maverik_backend/           # Código fuente principal
│   ├── api.py                # Definición de endpoints FastAPI
│   ├── settings.py           # Configuración de la aplicación
│   ├── core/                 # Lógica de negocio central
│   │   ├── database.py       # Configuración de base de datos
│   │   ├── models.py         # Modelos SQLAlchemy
│   │   ├── schemas.py        # Esquemas Pydantic
│   │   ├── services.py       # Servicios de negocio
│   │   └── smtp.py           # Servicios de email
│   └── utils/
│       └── auth.py           # Utilidades de autenticación
├── alembic/                  # Migraciones de base de datos
├── deployments/              # Archivos de deployment
├── docs/                     # Documentación del proyecto
├── scripts/                  # Scripts de utilidad
├── docker-compose.yml        # Configuración de Docker Compose
├── pyproject.toml           # Configuración del proyecto Python
└── requirements.txt         # Dependencias (legacy)
```

## 📖 Documentación

Para documentación detallada sobre la arquitectura y funcionamiento del sistema, consulta:

- [**Documentación del Proyecto**](docs/PROYECTO_MAVERIK_BACKEND.md) - Arquitectura completa, flujos de trabajo y consideraciones técnicas

## 🔧 Desarrollo

### Comandos útiles

```bash
# Ejecutar linting
uv run ruff check .

# Formatear código
uv run ruff format .

# Crear nueva migración
alembic revision --autogenerate -m "descripción_del_cambio"

# Ver logs de Docker Compose
docker compose logs -f backend

# Reiniciar servicios
docker compose restart backend
```
## 🚢 Deployment

### Variables de entorno para producción

Asegúrate de configurar estas variables en tu entorno de producción:

```bash
APP_ENV=prod
SECRET_KEY=<clave-secreta-segura-64-chars>
DB_PASSWORD=<password-seguro>
SMTP_API_KEY=<clave-api-real>
RAG_SERVICE_URL=<url-produccion-rag>
```


## 🤝 Contribución

### Preparación para subir a repositorio

Antes de subir el proyecto a un repositorio público:

1. **Verificar .gitignore**: Asegurar que incluya:
   ```
   .env
   .env.local
   .env.prod
   __pycache__/
   .venv/
   *.pyc
   .DS_Store
   ```

2. **Seguridad**:
   - ❌ NO incluir archivos `.env` reales
   - ✅ Solo incluir `.env.example`
   - ✅ Cambiar todas las credenciales por defecto
   - ✅ Usar secrets/variables de entorno en CI/CD

3. **Documentación**:
   - ✅ README actualizado
   - ✅ Documentación en `docs/`
   - ✅ Comentarios en código crítico

### Flujo de desarrollo

1. Fork del repositorio
2. Crear rama para la feature: `git checkout -b feature/nueva-funcionalidad`
3. Hacer commits descriptivos
4. Ejecutar tests y linting
5. Crear Pull Request

### Issues y mejoras prioritarias

Ver [documentación técnica](docs/PROYECTO_MAVERIK_BACKEND.md) para lista de mejoras sugeridas:

- Implementar hashing seguro de contraseñas
- Agregar endpoint `/health`
- Implementar tests automáticos
- Mejorar manejo de errores
- Agregar validaciones de autorización

---

## 📞 Soporte

Para soporte o consultas técnicas, revisar la documentación en `docs/` o crear un issue en el repositorio.

---

⏰ Última actualización: 29 de septiembre de 2025
