"""
Sistema de logging básico y robusto para Maverik Backend.

Versión simplificada que funciona sin dependencias complejas.
Proporciona logging estructurado con rotación automática.
"""

import json
import logging
import logging.handlers
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Formatter que crea logs en formato JSON."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Agregar campos adicionales si existen
        for field in ["request_id", "user_id", "session_id", "duration_ms", 
                     "http_method", "http_status", "endpoint", "external_service"]:
            if hasattr(record, field):
                log_data[field] = getattr(record, field)
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_basic_logging():
    """Configurar logging básico y robusto."""
    
    # Crear directorio de logs
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Limpiar handlers existentes
    logging.root.handlers.clear()
    
    # Configurar nivel
    logging.root.setLevel(logging.INFO)
    
    # Handler para archivo principal
    try:
        main_handler = logging.handlers.RotatingFileHandler(
            logs_dir / "maverik_backend.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        main_handler.setLevel(logging.INFO)
        main_handler.setFormatter(JSONFormatter())
        logging.root.addHandler(main_handler)
    except Exception as e:
        print(f"Error configurando handler principal: {e}")
    
    # Handler para errores
    try:
        error_handler = logging.handlers.RotatingFileHandler(
            logs_dir / "errors.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        logging.root.addHandler(error_handler)
    except Exception as e:
        print(f"Error configurando handler de errores: {e}")
    
    # Handler para consola en desarrollo
    try:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logging.root.addHandler(console_handler)
    except Exception as e:
        print(f"Error configurando handler de consola: {e}")
    
    # Test log
    logging.info("Sistema de logging inicializado correctamente")


def log_request(method: str, endpoint: str, status_code: int, duration_ms: float, **kwargs):
    """Log de request HTTP."""
    logger = logging.getLogger("maverik.requests")
    
    # Crear record con información adicional
    extra = {
        "http_method": method,
        "endpoint": endpoint,
        "http_status": status_code,
        "duration_ms": round(duration_ms, 2),
    }
    extra.update(kwargs)
    
    message = f"{method} {endpoint} -> {status_code} in {duration_ms:.1f}ms"
    
    if status_code >= 400:
        logger.warning(message, extra=extra)
    else:
        logger.info(message, extra=extra)


def log_rag_communication(endpoint: str, duration_ms: float, success: bool, **kwargs):
    """Log de comunicación con RAG."""
    logger = logging.getLogger("maverik.rag")
    
    extra = {
        "external_service": "rag",
        "endpoint": endpoint,
        "response_time_ms": round(duration_ms, 2),
    }
    extra.update(kwargs)
    
    if success:
        message = f"RAG {endpoint} success in {duration_ms:.1f}ms"
        logger.info(message, extra=extra)
    else:
        message = f"RAG {endpoint} failed in {duration_ms:.1f}ms"
        logger.error(message, extra=extra)


def log_business_event(event_type: str, entity_type: str, **kwargs):
    """Log de eventos de negocio."""
    logger = logging.getLogger("maverik.business")
    
    extra = {
        "event_type": event_type,
        "entity_type": entity_type,
    }
    extra.update(kwargs)
    
    message = f"Business event: {event_type} {entity_type}"
    logger.info(message, extra=extra)


def log_auth_event(event_type: str, success: bool, **kwargs):
    """Log de eventos de autenticación."""
    logger = logging.getLogger("maverik.auth")
    
    extra = {
        "event_type": event_type,
    }
    extra.update(kwargs)
    
    if success:
        message = f"Auth success: {event_type}"
        logger.info(message, extra=extra)
    else:
        message = f"Auth failed: {event_type}"
        logger.warning(message, extra=extra)


def log_error(error: Exception, context: str = "", **kwargs):
    """Log de errores."""
    logger = logging.getLogger("maverik.errors")
    
    extra = {
        "error_type": type(error).__name__,
        "context": context,
    }
    extra.update(kwargs)
    
    message = f"Error in {context}: {str(error)}"
    logger.error(message, extra=extra, exc_info=True)


# Inicializar logging al importar
try:
    setup_basic_logging()
except Exception as e:
    print(f"Error inicializando logging: {e}")


# Context manager simple para requests
class RequestLogger:
    def __init__(self, method: str, endpoint: str):
        self.method = method
        self.endpoint = endpoint
        self.start_time = time.time()
        self.request_id = str(uuid.uuid4())[:8]
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        status_code = 500 if exc_type else 200
        
        extra = {"request_id": self.request_id}
        if exc_val:
            extra["error"] = str(exc_val)
        
        log_request(self.method, self.endpoint, status_code, duration_ms, **extra)