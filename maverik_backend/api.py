import logging
import secrets
from contextlib import asynccontextmanager
from functools import partial
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from sqlalchemy.orm import Session

from maverik_backend.core import schemas, services, smtp
from maverik_backend.core.database import get_sessionmaker
from maverik_backend.settings import Settings, load_config
from maverik_backend.utils import auth

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,%(msecs)d %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)

app_config: Settings = load_config()
send_email = partial(
    smtp.send_email_with_api,
    api_url=app_config.smtp_api_url,
    api_key=app_config.smtp_api_key,
    sender=(
        app_config.mail_sender_name,
        app_config.mail_sender_address,
    ),
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # servicios_urls = [
    #     "https://maverik-backend.onrender.com/",
    # ]
    # mantener_servicios_activos_tarea = repeat_every(
    #     seconds=480,
    #     raise_exceptions=False,
    # )(partial(services.mantener_servicios_activos, servicios_urls))
    # await mantener_servicios_activos_tarea()

    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
handler = Mangum(app)

secret_key = b"k4.local.doPhJGTf4E4lAtRrC8WKUmr18LwF6T_r-kI9D1C_J-k="
# secret_key = auth.create_symmetric_key()


# Dependency
def obtener_db():
    SessionLocal = get_sessionmaker(app_config)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def raiz():
    return {"service": "maverik_backend"}


@app.get("/health")
def health_check():
    """Endpoint de health check para contenedores Docker y load balancers"""
    return {
        "status": "healthy", 
        "service": "maverik_backend",
        "version": "0.1.0"
    }


@app.post("/user/signup", response_model=schemas.Usuario, tags=["user"])
async def crear_usuario(
    data: schemas.UsuarioCrearRequest,
    db: Annotated[Session, Depends(obtener_db)],
):
    logging.info(data)
    clave = secrets.token_urlsafe(20)
    valores = schemas.UsuarioCrear(
        email=data.email,
        clave=clave,
        fecha_nacimiento=data.fecha_nacimiento,
        nivel_educativo_id=data.nivel_educativo_id,
        conocimiento_alt_inversion_id=data.conocimiento_alt_inversion_id,
        experiencia_invirtiendo_id=data.experiencia_invirtiendo_id,
        porcentaje_ahorro_mensual_id=data.porcentaje_ahorro_mensual_id,
        porcentaje_ahorro_invertir_id=data.porcentaje_ahorro_invertir_id,
        tiempo_mantener_inversion_id=data.tiempo_mantener_inversion_id,
        busca_invertir_en_id=data.busca_invertir_en_id,
        proporcion_inversion_mantener_id=data.proporcion_inversion_mantener_id,
    )

    usuario = services.crear_usuario(db=db, valores=valores)

    email_body = (
        "Felicitaciones. Has creado tu cuenta en Maverik Copiloto.<br>"
        "Tus datos para iniciar sesión son:<br/>"
        "Usuario: {username}<br/>"
        "Clave: {password}<br/>"
        "Website: {weburl}"
    ).format(
        username=usuario.email,
        password=usuario.clave,
        weburl=app_config.frontend_url,
    )
    send_email(
        to_email=usuario.email,
        subject="Bienvenido a Maverik",
        body=email_body,
    )
    print("clave={}".format(clave))

    return usuario


@app.post("/user/login", tags=["user"])
async def login_usuario(
    data: schemas.UsuarioLogin,
    db: Annotated[Session, Depends(obtener_db)],
):
    usuario = services.verificar_usuario(db, data)
    if usuario:
        return auth.sign(user=usuario, key=secret_key)
    else:
        return {"error": "wrong credentials"}


@app.post("/copilot/sessions", response_model=schemas.SesionAsesoria, tags=["copilot"])
async def nueva_sesion_asesoria(
    data: schemas.SesionAsesoriaCrearRequest,
    auth_token: Annotated[bytes, Depends(auth.PasetoBearer(key=secret_key))],
    db: Annotated[Session, Depends(obtener_db)],
):
    sesion_asesoria = None
    auth_payload = auth.decode(token=auth_token, key=secret_key)
    if auth_payload:
        usuario_id = auth_payload["user_id"]

        valores = schemas.SesionAsesoriaCrear(
            proposito_sesion_id=data.proposito_sesion_id,
            objetivo_id=data.objetivo_id,
            usuario_id=usuario_id,
            capital_inicial=data.capital_inicial,
            horizonte_temporal=data.horizonte_temporal,
            tolerancia_al_riesgo_id=data.tolerancia_al_riesgo_id,
        )

        new_instance = services.crear_sesion_asesoria(db=db, valores=valores)
        titulo_chat = services.generar_titulo_chat(sesion=new_instance)
        primer_input = services.preparar_primer_input(sesion=new_instance)

        sesion_asesoria = schemas.SesionAsesoria(
            id=new_instance.id,
            usuario_id=new_instance.usuario_id,
            proposito_sesion_id=new_instance.proposito_sesion_id,
            objetivo_id=new_instance.objetivo_id,
            capital_inicial=new_instance.capital_inicial,
            horizonte_temporal=new_instance.horizonte_temporal,
            tolerancia_al_riesgo_id=new_instance.tolerancia_al_riesgo_id,
            fecha_creacion=new_instance.fecha_creacion,
            titulo_chat=titulo_chat,
            primer_input=primer_input,
        )

    return sesion_asesoria


@app.post(
    "/copilot/sessions/{session_id}",
    response_model=schemas.SesionAsesoriaDetalle,
    tags=["copilot"],
)
async def agregar_detalle_asesoria(
    session_id: int,
    data: schemas.SesionAsesoriaDetalleRequest,
    auth_token: Annotated[bytes, Depends(auth.PasetoBearer(key=secret_key))],
    db: Annotated[Session, Depends(obtener_db)],
):
    try:
        # Verificar que la sesión existe antes de procesar
        sesion_existe = services.cargar_sesion_asesoria(db=db, id=session_id)
        if not sesion_existe:
            raise HTTPException(status_code=404, detail="Sesión de asesoría no encontrada")
        
        chat = schemas.ChatCrear(
            sesion_asesoria_id=session_id,
            input=data.input,
        )
        
        rag_response = services.enviar_chat_al_rag(
            db=db,
            valores=chat,
            app_config=app_config,
        )
        logging.info(f"RAG response: {rag_response}")

        sesion_asesoria_detalle = None
        if rag_response:
            valores = schemas.SesionAsesoriaDetalleCrear(
                sesion_asesoria_id=session_id,
                texto_usuario=rag_response.input,
                texto_sistema=rag_response.output,
            )

            new_instance = services.crear_sesion_asesoria_detalle(db=db, valores=valores)
            sesion_asesoria_detalle = schemas.SesionAsesoriaDetalle(
                id=new_instance.id,
                sesion_asesoria_id=new_instance.sesion_asesoria_id,
                input=new_instance.texto_usuario,
                output=new_instance.texto_sistema,
            )
        else:
            # Si el RAG no responde, crear una respuesta de fallback
            logging.warning(f"RAG no respondió para sesión {session_id}, creando respuesta de fallback")
            
            fallback_output = (
                "Disculpa, estoy experimentando algunas dificultades técnicas en este momento. "
                "Por favor, intenta reformular tu pregunta o contacta al soporte técnico si el problema persiste. "
                "Mientras tanto, te recomiendo consultar recursos educativos financieros básicos."
            )
            
            valores = schemas.SesionAsesoriaDetalleCrear(
                sesion_asesoria_id=session_id,
                texto_usuario=data.input,
                texto_sistema=fallback_output,
            )

            new_instance = services.crear_sesion_asesoria_detalle(db=db, valores=valores)
            sesion_asesoria_detalle = schemas.SesionAsesoriaDetalle(
                id=new_instance.id,
                sesion_asesoria_id=new_instance.sesion_asesoria_id,
                input=new_instance.texto_usuario,
                output=new_instance.texto_sistema,
            )

        return sesion_asesoria_detalle
        
    except AttributeError as e:
        logging.error(f"Error de atributo en sesión {session_id}: {str(e)}")
        raise HTTPException(
            status_code=400, 
            detail=f"Datos incompletos en la sesión de asesoría. Por favor, complete todos los campos requeridos."
        )
    except Exception as e:
        logging.error(f"Error inesperado en agregar_detalle_asesoria: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@app.get(
    "/copilot/sessions/{session_id}",
    response_model=list[schemas.SesionAsesoriaDetalle],
    tags=["copilot"],
)
async def ver_sesion_asesoria_detalle(
    session_id: int,
    auth_token: Annotated[bytes, Depends(auth.PasetoBearer(key=secret_key))],
    db: Annotated[Session, Depends(obtener_db)],
):
    detalles = services.cargar_sesion_asesoria_detalles(db=db, sesion_asesoria_id=session_id)
    return [
        schemas.SesionAsesoriaDetalle(
            id=r.id,
            sesion_asesoria_id=r.sesion_asesoria_id,
            input=r.texto_usuario,
            output=r.texto_sistema,
        )
        for r in detalles
    ]


# Endpoint temporal para debugging
@app.get("/copilot/sessions/{session_id}/debug", tags=["debug"])
async def debug_sesion(
    session_id: int,
    auth_token: Annotated[bytes, Depends(auth.PasetoBearer(key=secret_key))],
    db: Annotated[Session, Depends(obtener_db)],
):
    """
    Endpoint temporal para debugging de sesiones.
    Devuelve información detallada sobre una sesión.
    """
    try:
        sesion = services.cargar_sesion_asesoria(db=db, id=session_id)
        if not sesion:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
            
        return {
            "session_id": sesion.id,
            "usuario_id": sesion.usuario_id,
            "proposito_sesion": {
                "id": sesion.proposito_sesion_id,
                "desc": sesion.proposito_sesion.desc if sesion.proposito_sesion else None
            },
            "objetivo": {
                "id": sesion.objetivo_id,
                "desc": sesion.objetivo.desc if sesion.objetivo else None
            },
            "tolerancia_al_riesgo": {
                "id": sesion.tolerancia_al_riesgo_id,
                "desc": sesion.tolerancia_al_riesgo.desc if sesion.tolerancia_al_riesgo else None
            },
            "capital_inicial": float(sesion.capital_inicial) if sesion.capital_inicial else None,
            "horizonte_temporal": sesion.horizonte_temporal,
            "fecha_creacion": sesion.fecha_creacion.isoformat(),
            "usuario": {
                "id": sesion.usuario.id if sesion.usuario else None,
                "email": sesion.usuario.email if sesion.usuario else None
            } if sesion.usuario else None
        }
    except Exception as e:
        logging.error(f"Error en debug_sesion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Endpoint para probar conectividad al servicio RAG
@app.get("/debug/rag-connectivity", tags=["debug"])
async def test_rag_connectivity():
    """
    Endpoint para probar la conectividad al servicio RAG.
    """
    try:
        import requests
        
        rag_url = app_config.rag_service_url
        test_url = f"{rag_url}/api/chat"
        
        # Datos de prueba mínimos
        test_data = {
            "userProfile": "Usuario de prueba",
            "input": "Hola, esto es una prueba de conectividad",
            "chatHistory": []
        }
        
        logging.info(f"Probando conectividad a RAG en: {test_url}")
        
        # Intentar conexión con timeout corto
        response = requests.post(
            test_url,
            json=test_data,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        return {
            "rag_service_url": rag_url,
            "test_url": test_url,
            "status": "success",
            "response_status": response.status_code,
            "response_headers": dict(response.headers),
            "can_connect": True,
            "message": "Conexión exitosa al servicio RAG"
        }
        
    except requests.exceptions.ConnectionError as e:
        return {
            "rag_service_url": app_config.rag_service_url,
            "test_url": f"{app_config.rag_service_url}/api/chat",
            "status": "connection_error",
            "can_connect": False,
            "error": str(e),
            "message": "No se puede conectar al servicio RAG",
            "suggestions": [
                "Verificar que el servicio RAG esté ejecutándose",
                "Para Docker: usar 'host.docker.internal:8000' en lugar de 'localhost:8000'",
                "Verificar que el puerto 8000 esté disponible",
                "Revisar la configuración de RAG_SERVICE_URL en .env"
            ]
        }
    except Exception as e:
        return {
            "rag_service_url": app_config.rag_service_url,
            "status": "error",
            "can_connect": False,
            "error": str(e),
            "message": "Error inesperado al probar conectividad"
        }


# Endpoint para verificar performance del RAG
@app.get("/debug/rag-performance", tags=["debug"])
async def test_rag_performance():
    """
    Endpoint para probar la performance y tiempo de respuesta del servicio RAG.
    """
    try:
        import requests
        import time
        
        rag_url = app_config.rag_service_url
        test_url = f"{rag_url}/api/chat"
        
        # Datos de prueba simples para medir performance
        test_data = {
            "userProfile": "Usuario de prueba de performance",
            "input": "¿Qué es una inversión?",  # Pregunta simple
            "chatHistory": []
        }
        
        logging.info(f"Probando performance del RAG en: {test_url}")
        
        # Medir tiempo de respuesta
        start_time = time.time()
        
        try:
            response = requests.post(
                test_url,
                json=test_data,
                timeout=app_config.external_service_timeout,
                headers={"Content-Type": "application/json"}
            )
            
            end_time = time.time()
            response_time = round(end_time - start_time, 2)
            
            # Analizar performance
            performance_status = "excellent"
            if response_time > 30:
                performance_status = "slow"
            elif response_time > 10:
                performance_status = "moderate"
            elif response_time > 5:
                performance_status = "good"
            
            return {
                "rag_service_url": rag_url,
                "status": "success",
                "response_time_seconds": response_time,
                "performance_status": performance_status,
                "response_status": response.status_code,
                "timeout_configured": app_config.external_service_timeout,
                "recommendations": {
                    "excellent": "Performance óptima",
                    "good": "Performance aceptable",
                    "moderate": "Considera optimizar el modelo RAG",
                    "slow": "Performance muy lenta, revisa la configuración del RAG"
                }.get(performance_status),
                "can_connect": True
            }
            
        except requests.exceptions.Timeout as e:
            end_time = time.time()
            response_time = round(end_time - start_time, 2)
            
            return {
                "rag_service_url": rag_url,
                "status": "timeout",
                "response_time_seconds": response_time,
                "performance_status": "timeout",
                "timeout_configured": app_config.external_service_timeout,
                "can_connect": True,
                "error": f"Timeout después de {app_config.external_service_timeout}s",
                "recommendations": [
                    "Aumentar EXTERNAL_SERVICE_TIMEOUT en .env",
                    "Optimizar el modelo o infraestructura del RAG",
                    "Usar consultas más simples",
                    "Implementar cache de respuestas"
                ]
            }
            
    except Exception as e:
        return {
            "rag_service_url": app_config.rag_service_url,
            "status": "error",
            "error": str(e),
            "message": "Error al probar performance del RAG"
        }


# Para AWS Lambda (usar Mangum adapter)
lambda_handler = Mangum(app)
