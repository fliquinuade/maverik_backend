import logging
import time
from datetime import datetime

import requests
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Query, Session

from maverik_backend.core import models, schemas
from maverik_backend.core.models import SesionAsesoria, SesionAsesoriaDetalle, Usuario
from maverik_backend.core.simple_logging import (
    log_rag_communication,
    log_business_event,
    log_error
)
from maverik_backend.settings import Settings


def crear_usuario(db: Session, valores: schemas.UsuarioCrear) -> Usuario:
    try:
        # Log inicio de creación
        log_business_event(
            event_type="user_creation_start",
            entity_type="user",
            email=valores.email,
            fecha_nacimiento=str(valores.fecha_nacimiento),
            nivel_educativo_id=valores.nivel_educativo_id
        )
        
        usuario = Usuario(
            email=valores.email,
            clave=valores.clave,
            fecha_nacimiento=valores.fecha_nacimiento,
            nivel_educativo_id=valores.nivel_educativo_id,
            conocimiento_alt_inversion_id=valores.conocimiento_alt_inversion_id,
            experiencia_invirtiendo_id=valores.experiencia_invirtiendo_id,
            porcentaje_ahorro_mensual_id=valores.porcentaje_ahorro_mensual_id,
            porcentaje_ahorro_invertir_id=valores.porcentaje_ahorro_invertir_id,
            tiempo_mantener_inversion_id=valores.tiempo_mantener_inversion_id,
            busca_invertir_en_id=valores.busca_invertir_en_id,
            proporcion_inversion_mantener_id=valores.proporcion_inversion_mantener_id,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

        # Log creación exitosa
        log_business_event(
            event_type="user_creation_success",
            entity_type="user",
            entity_id=usuario.id,
            email=usuario.email,
            user_id=usuario.id
        )

        return usuario
        
    except Exception as e:
        log_error(
            e,
            context="crear_usuario",
            email=valores.email,
            nivel_educativo_id=valores.nivel_educativo_id
        )
        raise


def crear_sesion_asesoria(db: Session, valores: schemas.SesionAsesoriaCrear) -> SesionAsesoria:
    try:
        # Log inicio de creación
        log_business_event(
            event_type="session_creation_start",
            entity_type="session",
            user_id=str(valores.usuario_id),
            proposito_sesion_id=valores.proposito_sesion_id,
            objetivo_id=valores.objetivo_id,
            capital_inicial=float(valores.capital_inicial) if valores.capital_inicial else None,
            horizonte_temporal=valores.horizonte_temporal,
            tolerancia_al_riesgo_id=valores.tolerancia_al_riesgo_id
        )
        
        sesion_asesoria = SesionAsesoria(
            proposito_sesion_id=valores.proposito_sesion_id,
            objetivo_id=valores.objetivo_id,
            usuario_id=valores.usuario_id,
            capital_inicial=valores.capital_inicial,
            horizonte_temporal=valores.horizonte_temporal,
            tolerancia_al_riesgo_id=valores.tolerancia_al_riesgo_id,
        )
        db.add(sesion_asesoria)
        db.commit()
        db.refresh(sesion_asesoria)

        # Log creación exitosa
        log_business_event(
            event_type="session_creation_success",
            entity_type="session",
            entity_id=sesion_asesoria.id,
            user_id=str(valores.usuario_id),
            session_id=sesion_asesoria.id
        )

        return sesion_asesoria
        
    except Exception as e:
        log_error(
            e,
            context="crear_sesion_asesoria",
            user_id=str(valores.usuario_id),
            proposito_sesion_id=valores.proposito_sesion_id,
            objetivo_id=valores.objetivo_id,
            tolerancia_al_riesgo_id=valores.tolerancia_al_riesgo_id
        )
        raise


def crear_sesion_asesoria_detalle(
    db: Session,
    valores: schemas.SesionAsesoriaDetalleCrear,
) -> SesionAsesoriaDetalle:
    detalle = SesionAsesoriaDetalle(
        sesion_asesoria_id=valores.sesion_asesoria_id,
        texto_usuario=valores.texto_usuario,
        texto_sistema=valores.texto_sistema,
    )
    db.add(detalle)
    db.commit()
    db.refresh(detalle)

    return detalle


def verificar_usuario(db: Session, data: schemas.UsuarioLogin) -> Usuario | None:
    query = Query(Usuario).filter(
        Usuario.email == data.email,
        Usuario.clave == data.clave,
    )
    try:
        return query.with_session(db).one()
    except NoResultFound:
        return None


def cargar_sesion_asesoria_detalles(db: Session, sesion_asesoria_id: int) -> list[SesionAsesoriaDetalle]:
    query = (
        Query(SesionAsesoriaDetalle)
        .filter_by(sesion_asesoria_id=sesion_asesoria_id)
        .order_by(SesionAsesoriaDetalle.id.asc())
    )
    try:
        return query.with_session(db).all()
    except NoResultFound:
        return None


def cargar_sesion_asesoria(db: Session, id: int) -> SesionAsesoria:
    """
    Carga una sesión de asesoría con todas sus relaciones necesarias.
    """
    from sqlalchemy.orm import joinedload
    
    query = (
        Query(SesionAsesoria)
        .options(
            joinedload(SesionAsesoria.usuario),
            joinedload(SesionAsesoria.proposito_sesion),
            joinedload(SesionAsesoria.objetivo),
            joinedload(SesionAsesoria.tolerancia_al_riesgo)
        )
        .filter(SesionAsesoria.id == id)
    )
    try:
        return query.with_session(db).one()
    except NoResultFound:
        return None


def obtener_perfil_riesgo(sesion_asesoria: SesionAsesoria) -> str:
    """
    Obtiene el perfil de riesgo de una sesión de asesoría.
    Si no hay tolerancia al riesgo definida, retorna 'moderate' por defecto.
    """
    # Si no hay tolerancia al riesgo definida, usar valor por defecto
    if not sesion_asesoria.tolerancia_al_riesgo:
        return "moderate"
    
    tolerancia_al_riesgo = {
        "baja": "conservative",
        "media": "moderate", 
        "alta": "bold",
    }

    # Obtener la descripción de la tolerancia al riesgo
    desc = sesion_asesoria.tolerancia_al_riesgo.desc
    return tolerancia_al_riesgo.get(desc, "moderate")


def preparar_user_profile(usuario: Usuario) -> str:
    nivel_educativo: models.NivelEducativo = usuario.nivel_educativo
    conocimiento_alt_inversion: models.ConocimientoAltInversion = usuario.conocimiento_alt_inversion
    experiencia_invirtiendo: models.ExperienciaInvirtiendo = usuario.experiencia_invirtiendo
    porcentaje_ahorro_mensual: models.PorcentajeAhorroMensual = usuario.porcentaje_ahorro_mensual
    porcentaje_ahorro_invertir: models.PorcentajeAhorroInvertir = usuario.porcentaje_ahorro_invertir
    tiempo_mantener_inversion: models.TiempoMantenerInversion = usuario.tiempo_mantener_inversion
    busca_invertir_en: models.BuscaInvertirEn = usuario.busca_invertir_en
    proporcion_inversion_mantener: models.ProporcionInversionMantener = usuario.proporcion_inversion_mantener

    username = usuario.email.split("@")[0]

    user_profile = (
        "Hola, mi nombre es {}. "
        "Mi nivel educativo es {}. "
        "Mi experiencia invirtiendo es {}. "
        "Mi conocimiento sobre las distintas alternativas de inversión en el mercado de capitales es {}. "
        "Puedo ahorrar mensualmente {} de mis ingresos. "
        "Estoy dispuesto/a a invertir {} de mis ahorros. "
        "Puedo mantener una inversión por {}. "
        "Cuando realizo inversiones principalmente busco {}. "
        "Si observo una baja importante en el valor de uno de mis activos, {}."
    ).format(
        username,
        nivel_educativo.desc.lower(),
        experiencia_invirtiendo.desc.lower(),
        conocimiento_alt_inversion.desc.lower(),
        porcentaje_ahorro_mensual.desc.lower(),
        porcentaje_ahorro_invertir.desc.lower(),
        tiempo_mantener_inversion.desc.lower(),
        busca_invertir_en.desc.lower(),
        proporcion_inversion_mantener.desc.lower(),
    )

    return user_profile


def preparar_primer_input(sesion: SesionAsesoria) -> str:
    """
    Prepara el primer input para una sesión de asesoría.
    Maneja casos donde algunos campos pueden ser None.
    """
    proposito_sesion: models.PropositoSesion = sesion.proposito_sesion
    objetivo: models.Objetivo = sesion.objetivo
    tolerancia_al_riesgo: models.ToleranciaAlRiesgo = sesion.tolerancia_al_riesgo

    primer_input = "En esta oportunidad, vine a {}.".format(proposito_sesion.desc.lower())
    
    if objetivo:
        tolerancia_desc = "moderada"  # valor por defecto
        if tolerancia_al_riesgo:
            tolerancia_desc = tolerancia_al_riesgo.desc.lower()
            
        primer_input += (
            " Quiero {}. "
            "Dispongo de un capital inicial de {:.2f}. "
            "Me gustaría lograr este objetivo en {} meses. "
            "Mi tolerancia al riesgo para lograr este objetivo es {}."
        ).format(
            objetivo.desc.lower(),
            float(sesion.capital_inicial) if sesion.capital_inicial else 0.0,
            sesion.horizonte_temporal if sesion.horizonte_temporal else 12,
            tolerancia_desc,
        )

    return primer_input


def generar_titulo_chat(sesion: SesionAsesoria) -> str:
    proposito_sesion: models.PropositoSesion = sesion.proposito_sesion
    objetivo: models.Objetivo = sesion.objetivo

    now = datetime.now()
    timestamp = now.strftime("%m/%d/%Y, %H:%M:%S")

    titulo_chat = "({}) ".format(timestamp)
    if sesion.proposito_sesion_id == 2:
        titulo_chat += "{}".format(objetivo.desc)
    else:
        titulo_chat += "{}".format(proposito_sesion.desc)

    return titulo_chat


def enviar_chat_al_rag(
    db: Session,
    valores: schemas.ChatCrear,
    app_config: Settings,
) -> schemas.RagServiceResponseMessage | None:
    """
    Envía un chat al servicio RAG con manejo robusto de errores y logging completo.
    """
    # Información para logging
    session_id = valores.sesion_asesoria_id
    start_time = time.time()
    rag_url = None
    
    try:
        # Log inicio de operación
        log_business_event(
            event_type="rag_communication_start",
            entity_type="session",
            session_id=session_id,
            input_length=len(valores.input) if valores.input else 0
        )
        
        sesion_asesoria: SesionAsesoria = cargar_sesion_asesoria(db=db, id=valores.sesion_asesoria_id)
        if not sesion_asesoria:
            error_msg = f"No se encontró la sesión de asesoría con ID: {valores.sesion_asesoria_id}"
            log_error(
                ValueError(error_msg),
                context="enviar_chat_al_rag - session lookup",
                session_id=session_id
            )
            return None
            
        usuario: Usuario = sesion_asesoria.usuario
        if not usuario:
            error_msg = f"No se encontró el usuario para la sesión: {valores.sesion_asesoria_id}"
            log_error(
                ValueError(error_msg),
                context="enviar_chat_al_rag - user lookup",
                session_id=session_id
            )
            return None

        user_profile = preparar_user_profile(usuario)
        risk_profile = obtener_perfil_riesgo(sesion_asesoria)

        # si el input=None quiere decir que es el primer input
        # entonces se puede generar este input a partir de la informacion ya suministrada
        if valores.input:
            input = valores.input
            detalles: list[SesionAsesoriaDetalle] = cargar_sesion_asesoria_detalles(
                db=db,
                sesion_asesoria_id=valores.sesion_asesoria_id,
            )
            chat_history = [(det.texto_usuario, det.texto_sistema) for det in detalles] if detalles else []
        else:
            input = preparar_primer_input(sesion=sesion_asesoria)
            chat_history = []

        # Preparar mensaje para el RAG
        mensaje_usuario = schemas.RagServiceRequestMessage(
            userProfile=user_profile,
            input=input,
            chatHistory=chat_history,
        )

        # URL del servicio RAG
        rag_url = app_config.rag_service_url + "/api/chat"
        
        # Realizar petición con timeout y manejo de errores
        try:
            # Usar timeout configurable desde settings
            timeout_seconds = app_config.external_service_timeout
            
            logging.info(f"Enviando petición al RAG con timeout de {timeout_seconds}s para sesión {session_id}")
            
            # Medir tiempo exacto de la comunicación con RAG
            rag_start_time = time.time()
            
            resp = requests.post(
                rag_url, 
                json=mensaje_usuario.dict(), 
                timeout=timeout_seconds,
                headers={"Content-Type": "application/json"}
            )
            
            rag_end_time = time.time()
            rag_duration_ms = (rag_end_time - rag_start_time) * 1000
            
            if resp.status_code == 200:
                try:
                    response_data = resp.json()
                    output = response_data.get("response")
                    
                    if output:
                        # Log comunicación exitosa
                        log_rag_communication(
                            endpoint="/api/chat",
                            duration_ms=rag_duration_ms,
                            success=True,
                            session_id=session_id,
                            status_code=resp.status_code,
                            response_length=len(output)
                        )
                        
                        log_business_event(
                            event_type="rag_communication_success",
                            entity_type="session",
                            session_id=session_id,
                            response_length=len(output),
                            duration_ms=rag_duration_ms,
                            chat_history_length=len(chat_history)
                        )
                        
                        return schemas.RagServiceResponseMessage(input=input, output=output)
                    else:
                        error_msg = "RAG respondió pero sin campo 'response' en JSON"
                        log_rag_communication(
                            endpoint="/api/chat",
                            duration_ms=rag_duration_ms,
                            success=False,
                            session_id=session_id,
                            status_code=resp.status_code,
                            error=error_msg
                        )
                        return None
                        
                except ValueError as e:
                    error_msg = f"Error parseando JSON del RAG: {str(e)}"
                    log_rag_communication(
                        endpoint="/api/chat",
                        duration_ms=rag_duration_ms,
                        success=False,
                        session_id=session_id,
                        status_code=resp.status_code,
                        error=error_msg
                    )
                    return None
            else:
                error_msg = f"RAG respondió con error {resp.status_code}"
                log_rag_communication(
                    endpoint="/api/chat",
                    duration_ms=rag_duration_ms,
                    success=False,
                    session_id=session_id,
                    status_code=resp.status_code,
                    error=error_msg
                )
                return None
                
        except requests.exceptions.ConnectionError as e:
            duration_ms = (time.time() - start_time) * 1000
            error_msg = f"Error de conexión al servicio RAG: {str(e)}"
            
            log_rag_communication(
                endpoint="/api/chat",
                duration_ms=duration_ms,
                success=False,
                session_id=session_id,
                error=error_msg
            )
            
            log_error(
                e,
                context="RAG connection error",
                session_id=session_id,
                rag_url=rag_url
            )
            return None
            
        except requests.exceptions.Timeout as e:
            duration_ms = (time.time() - start_time) * 1000
            error_msg = f"Timeout conectando al servicio RAG después de {timeout_seconds}s"
            
            log_rag_communication(
                endpoint="/api/chat",
                duration_ms=duration_ms,
                success=False,
                session_id=session_id,
                error=f"{error_msg}: {str(e)}",
                timeout_seconds=timeout_seconds
            )
            
            # Log sugerencias para optimización
            logging.warning(f"RAG timeout para sesión {session_id} - considerar optimizaciones")
            
            # Retornar respuesta de fallback en lugar de None
            fallback_response = (
                "Disculpa, el servicio de análisis está experimentando demoras. "
                "Mientras tanto, puedo sugerirte que para inversiones básicas consideres: "
                "1) Fondos de inversión diversificados para principiantes, "
                "2) Bonos del gobierno para inversiones conservadoras, "
                "3) Educación financiera continua. "
                "Por favor, intenta tu consulta nuevamente en unos momentos."
            )
            
            log_business_event(
                event_type="rag_fallback_response",
                entity_type="session",
                session_id=session_id,
                reason="timeout",
                timeout_seconds=timeout_seconds,
                fallback_response_length=len(fallback_response)
            )
            
            return schemas.RagServiceResponseMessage(input=input, output=fallback_response)
            
        except requests.exceptions.RequestException as e:
            duration_ms = (time.time() - start_time) * 1000
            error_msg = f"Error en petición al RAG: {str(e)}"
            
            log_rag_communication(
                endpoint="/api/chat",
                duration_ms=duration_ms,
                success=False,
                session_id=session_id,
                error=error_msg
            )
            
            log_error(
                e,
                context="RAG request error",
                session_id=session_id,
                rag_url=rag_url
            )
            return None
            
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        
        log_error(
            e,
            context="enviar_chat_al_rag - unexpected error",
            session_id=session_id,
            rag_url=rag_url,
            duration_ms=duration_ms
        )
        return None


def mantener_servicios_activos(urls: list[str]):
    for url in urls:
        try:
            respuesta = requests.get(url)
            if respuesta.status_code == 200:
                logging.info("Llamada exitosa al servicio {}".format(url))
            else:
                logging.info("Error en la llamada al servicio: Código {}".format(respuesta.status_code))
        except Exception as e:
            print("Ocurrió un error: {}".format(e))
