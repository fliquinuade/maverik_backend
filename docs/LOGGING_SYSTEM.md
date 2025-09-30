# 📋 Sistema de Logging Profesional - Maverik Backend

## 🎯 Descripción General

Sistema de logging simplificado  que proporciona trazabilidad completa de todas las operaciones del backend, incluyendo:

- **Requests HTTP**: Logging directo en endpoints importantes
- **Comunicación con RAG**: Logging detallado de intercambios con el servicio RAG
- **Eventos de negocio**: Registro de operaciones importantes (creación de usuarios, autenticación, etc.)
- **Errores y excepciones**: Captura estructurada de todos los errores con contexto
- **Performance**: Métricas de tiempo de respuesta y rendimiento

**Enfoque simplificado**: En lugar de middleware automático, usa logging directo en endpoints para mayor control y menor overhead.

## 📁 Estructura de Archivos

```
logs/
├── maverik_backend.log    # Log principal (todos los eventos)
├── errors.log             # Solo errores críticos  
└── .gitkeep              # Mantener directorio en git

maverik_backend/core/
└── simple_logging.py      # Sistema de logging simplificado y eficiente

scripts/
└── analyze_logs.py        # Herramienta de análisis de logs

docs/
├── LOGGING_SYSTEM.md      # Documentación técnica (este archivo)
└── RESUMEN_SISTEMA_LOGGING.md  # Resumen ejecutivo
```

## 🔧 Configuración

### Configuración Simplificada

El sistema se inicializa automáticamente al importar `simple_logging.py`:

**Características principales**:
- Formato JSON estructurado para facilidad de análisis
- Logs en archivos con rotación automática
- Nivel INFO por defecto
- Sistema robusto sin dependencias complejas

### Rotación de Archivos

```python
# Configuración automática de rotación
- Archivo principal: 10MB máximo, 5 backups
- Archivo de errores: 5MB máximo, 3 backups  
- Encoding UTF-8 para caracteres especiales
- Formato JSON para fácil parsing
```

## 📊 Tipos de Logs

### 1. **Request Logging** (`maverik.requests`)

Logging directo en endpoints importantes:

```json
{
  "timestamp": "2025-09-30T14:50:53.124893Z",
  "level": "INFO",
  "logger": "maverik.requests", 
  "message": "GET /debug/rag-connectivity -> 200 in 10017.3ms",
  "module": "simple_logging",
  "function": "log_request",
  "line": 117,
  "duration_ms": 10017.27,
  "http_method": "GET",
  "http_status": 200,
  "endpoint": "/debug/rag-connectivity"
}
```

### 2. **RAG Communication** (`maverik.rag`)

Comunicación detallada con el servicio RAG:

```json
{
  "timestamp": "2025-09-30T14:50:53.122842Z",
  "level": "ERROR",
  "logger": "maverik.rag",
  "message": "RAG /api/chat failed in 10015.1ms",
  "module": "simple_logging",
  "function": "log_rag_communication", 
  "line": 136,
  "endpoint": "/api/chat",
  "external_service": "rag",
  "response_time_ms": 10015.1,
  "error_type": "ReadTimeout",
  "test_mode": true
}
```

### 3. **Business Events** (`maverik.business`)

Eventos importantes de negocio:

```json
{
  "timestamp": "2025-09-30T10:30:43.000Z",
  "level": "INFO",
  "logger": "maverik.business",
  "message": "Business event: user_registration_success user",
  "module": "simple_logging",
  "function": "log_business_event",
  "event_type": "user_registration_success",
  "entity_type": "user",
  "entity_id": 123,
  "user_email": "user@example.com"
}
```

### 4. **Authentication** (`maverik.auth`)

Eventos de autenticación y autorización:

```json
{
  "timestamp": "2025-09-30T10:30:42.000Z",
  "level": "INFO",
  "logger": "maverik.auth",
  "message": "Auth success: login_success for user@example.com",
  "module": "simple_logging",
  "function": "log_auth_event",
  "event_type": "login_success",
  "user_email": "user@example.com",
  "user_id": 123
}
```

### 5. **Error Logging** (`maverik.errors`)

Errores estructurados con contexto completo:

```json
{
  "timestamp": "2025-09-30T14:43:27.567378Z",
  "level": "ERROR",
  "logger": "maverik.errors",
  "message": "Error in log_request() missing parameter: Error en health check",
  "module": "simple_logging",
  "function": "log_error",
  "line": 181,
  "error_type": "TypeError",
  "context": "health_check_endpoint"
}
```

## 🛠 Uso del Sistema

### Importación y Uso Básico

```python
from maverik_backend.core.simple_logging import (
    log_request,
    log_rag_communication,
    log_business_event,
    log_auth_event,
    log_error
)

# Logging de peticiones HTTP (en endpoints)
log_request(
    method="POST",
    endpoint="/user/signup", 
    status_code=201,
    duration_ms=245.3,
    user_email="user@example.com"
)

# Logging de comunicación RAG
log_rag_communication(
    endpoint="/api/chat",
    duration_ms=1500.2,
    success=True,
    session_id=123,
    user_id=456
)

# Logging de eventos de negocio  
log_business_event(
    event_type="user_registration",
    entity_type="user",
    entity_id=123,
    user_email="user@example.com"
)

# Logging de autenticación
log_auth_event(
    event_type="login_success",
    user_id=123,
    user_email="user@example.com"
)

# Logging de errores
log_error(
    message="Database connection failed",
    error_details=str(exception),
    context="user_registration"
)
```

### Ejemplo de Implementación en Endpoint

```python
@app.post("/user/signup")
async def crear_usuario(data: schemas.UsuarioCrearRequest):
    import time
    start_time = time.time()
    
    try:
        # Lógica de creación de usuario
        usuario = create_user(data)
        
        # Log de evento de negocio
        log_business_event(
            event_type="user_registration_success",
            entity_type="user", 
            entity_id=usuario.id,
            user_email=data.email
        )
        
        # Log de autenticación
        log_auth_event(
            event_type="signup_success",
            user_id=usuario.id,
            user_email=data.email
        )
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Log de petición HTTP
        log_request(
            method="POST",
            endpoint="/user/signup",
            status_code=201,
            duration_ms=duration_ms,
            user_email=data.email
        )
        
        return usuario
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        
        # Log de error
        log_error(
            message=f"Error en registro de usuario: {str(e)}",
            error_details=str(e),
            context="user_registration",
            user_email=data.email
        )
        
        # Log de petición con error
        log_request(
            method="POST", 
            endpoint="/user/signup",
            status_code=500,
            duration_ms=duration_ms,
            error=True
        )
        
        raise
```

## 📈 Análisis de Logs

### Herramienta de Análisis

```bash
# Análisis de performance de endpoints
python scripts/analyze_logs.py --report performance

# Performance del RAG
python scripts/analyze_logs.py --report rag-performance

# Análisis de errores de las últimas 24 horas
python scripts/analyze_logs.py --report errors --last-hours 24

# Eventos de negocio
python scripts/analyze_logs.py --report business
```

### Comandos Útiles de Terminal

```bash
# Ver logs en tiempo real
tail -f logs/maverik_backend.log

# Filtrar solo errores
grep '"level":"ERROR"' logs/maverik_backend.log

# Buscar logs de un usuario específico
grep '"user_id":"123"' logs/maverik_backend.log

# Buscar problemas de RAG
grep '"external_service":"rag"' logs/maverik_backend.log

# Contar errores por tipo
grep '"level":"ERROR"' logs/maverik_backend.log | grep -o '"error_type":"[^"]*"' | sort | uniq -c

# Ver performance de endpoints
grep '"logger":"maverik.requests"' logs/maverik_backend.log | grep -o '"duration_ms":[0-9.]*'
```

## 🐳 Docker Integration

### Configuración en Docker Compose

Los logs se persisten usando volúmenes:

```yaml
backend:
  volumes:
    - ./logs:/app/logs  # Persistir logs fuera del contenedor
```

### Comandos Docker

```bash
# Ver logs del contenedor
docker compose logs backend

# Ver logs de archivos persistentes
docker compose exec backend tail -f logs/maverik_backend.log

# Copiar logs desde contenedor
docker cp maverik_backend-backend-1:/app/logs ./logs-backup
```

## 🔍 Monitoreo y Alertas

### Métricas Clave

1. **Tasa de errores**: `< 1%` en producción
2. **Tiempo de respuesta promedio**: `< 500ms` para endpoints críticos
3. **Tasa de éxito RAG**: `> 95%`
4. **Timeouts RAG**: `< 5%` de las comunicaciones

### Alertas Automáticas (Futuro)

```python
# Implementación futura de alertas
# - Email cuando tasa de error > 5%
# - Slack cuando RAG tiene > 10 timeouts/hora
# - Dashboard para métricas en tiempo real
```

## 🚀 Performance

### Optimizaciones Implementadas

1. **Logging directo**: Sin overhead de middleware automático
2. **Rotación automática**: Evita archivos gigantes (10MB/5MB limits)
3. **Formato JSON eficiente**: Parsing rápido y estructurado
4. **Sin dependencias complejas**: Solo librerías estándar de Python
5. **Llamadas selectivas**: Solo en endpoints importantes

### Impacto en Performance

- **Overhead**: < 0.5ms por llamada de logging
- **Memoria**: < 5MB adicionales  
- **Disk I/O**: Buffering automático del sistema de logging
- **CPU**: Formateo JSON optimizado
- **Control total**: Logging solo donde es necesario

## 🆘 Troubleshooting

### Problema: Logs no aparecen

```bash
# Verificar permisos del directorio logs/
ls -la logs/

# Verificar que simple_logging se inicializa correctamente
python -c "from maverik_backend.core.simple_logging import setup_basic_logging; setup_basic_logging()"

# Verificar contenido de logs
cat logs/maverik_backend.log | tail -10
```

### Problema: Archivos de log muy grandes

```bash
# Verificar tamaño actual
ls -lh logs/

# Los logs rotan automáticamente:
# - maverik_backend.log: 10MB máx
# - errors.log: 5MB máx

# Ver archivos rotados
ls -la logs/maverik_backend.log.*
```

### Problema: Performance degradada

```bash
# El sistema simple_logging es muy eficiente
# Si hay problemas, verificar:

# 1. Que no se esté loggeando en exceso
grep -c "GET /health" logs/maverik_backend.log

# 2. Verificar rotación automática está funcionando
python -c "
import logging.handlers
import os
print(f'Tamaño actual: {os.path.getsize(\"logs/maverik_backend.log\")} bytes')
"
```
