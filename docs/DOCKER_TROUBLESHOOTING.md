# 🐳 Docker Troubleshooting Guide

## Error: ModuleNotFoundError: No module named 'maverik_backend'

### Problema
El contenedor Docker no puede encontrar el módulo `maverik_backend` cuando intenta iniciar la aplicación.

### Solución aplicada
1. **Añadido `PYTHONPATH=/app`** al Dockerfile para que Python pueda encontrar los módulos
2. **Verificado estructura de directorios** correcta
3. **Añadido `.dockerignore`** para optimizar el build

### Verificar la solución

#### Opción 1: Usar script automático
```bash
# Linux/macOS
chmod +x scripts/test_docker.sh
./scripts/test_docker.sh

# Windows
scripts\test_docker.bat
```

#### Opción 2: Pasos manuales

```bash
# 1. Reconstruir contenedores
docker compose down
docker compose up --build -d

# 2. Verificar logs
docker compose logs backend

# 3. Probar endpoints
curl http://localhost:8082/health
curl http://localhost:8082/

# 4. Ejecutar comando dentro del contenedor para debug
docker compose exec backend python -c "import maverik_backend; print('✅ Import successful')"
```

## Otros problemas comunes

### Error de base de datos
```
FATAL: password authentication failed for user "maverik"
```

**Solución:**
1. Verificar archivo `.env` con credenciales correctas
2. Asegurar que `DB_HOST=db` para Docker Compose
3. Reiniciar contenedores: `docker compose down && docker compose up -d`

### Error de puertos
```
Error starting userland proxy: listen tcp4 0.0.0.0:8082: bind: address already in use
```

**Solución:**
1. Verificar qué proceso usa el puerto: `netstat -ano | findstr :8082` (Windows) o `lsof -i :8082` (Linux/macOS)
2. Matar proceso o cambiar puerto en `docker-compose.yml`

### Problemas de permisos en volumes
```
PermissionError: [Errno 13] Permission denied
```

**Solución (Linux/macOS):**
```bash
# Cambiar ownership del directorio
sudo chown -R $USER:$USER .

# O ejecutar Docker con tu usuario
docker compose run --user $(id -u):$(id -g) backend bash
```

### Error de build lento o fallos de cache
**Solución:**
```bash
# Limpiar cache de Docker
docker system prune -a

# Build sin cache
docker compose build --no-cache
```

## Comandos útiles para debug

### Ver logs en tiempo real
```bash
docker compose logs -f backend
```

### Ejecutar shell dentro del contenedor
```bash
docker compose exec backend bash
```

### Verificar variables de entorno
```bash
docker compose exec backend env | grep -i maverik
```

### Verificar estructura de archivos
```bash
docker compose exec backend ls -la /app/
docker compose exec backend ls -la /app/maverik_backend/
```

### Probar importación manual
```bash
docker compose exec backend python -c "
import sys
print('Python path:', sys.path)
import maverik_backend
print('✅ maverik_backend imported successfully')
"
```

## Configuración recomendada para desarrollo

### docker-compose.override.yml
Crear este archivo para configuraciones específicas de desarrollo:

```yaml
services:
  backend:
    volumes:
      - .:/app:cached  # Mejor performance en macOS
    environment:
      - APP_ENV=dev
    command: python -m uvicorn maverik_backend.api:app --host 0.0.0.0 --port 8082 --reload --log-level debug
```

### .env para desarrollo local
```bash
APP_ENV=dev
DB_HOST=db
DB_PORT=5432
DB_NAME=maverik
DB_USERNAME=maverik
DB_PASSWORD=secret
DB_SCHEMA=public

# URLs de servicios (usar mocks para desarrollo)
RAG_SERVICE_URL=http://mock-rag:8080
PORTFOLIO_OPTIMIZATION_URL=http://mock-portfolio:8081
FRONTEND_URL=http://localhost:3000

# SMTP (usar servicio de pruebas)
SMTP_API_URL=https://api.sendgrid.v3/mail/send
SMTP_API_KEY=SG.test-key
MAIL_SENDER_NAME=Maverik Dev
MAIL_SENDER_ADDRESS=dev@maverik.com

# Generar nueva clave para cada entorno
SECRET_KEY=dev_secret_key_change_in_production_64_chars_long_string
```

## Performance y optimización

### Multi-stage build (para producción)
```dockerfile
# Dockerfile.prod
FROM python:3.12-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app
CMD ["python", "-m", "uvicorn", "maverik_backend.api:app", "--host", "0.0.0.0", "--port", "8082"]
```

### Usar .dockerignore optimizado
Ya incluido en el proyecto para reducir el contexto de build.

## Monitoreo en producción

### Health checks
El contenedor incluye health check automático que verifica `/health` cada 30 segundos.

### Logs estructurados
```bash
# Ver logs con timestamps
docker compose logs -f -t backend

# Filtrar logs por nivel
docker compose logs backend | grep "ERROR\|CRITICAL"
```

### Métricas
Considerar agregar Prometheus metrics:
```python
# En api.py
from prometheus_client import Counter, Histogram
REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_LATENCY = Histogram('request_duration_seconds', 'Request latency')
```