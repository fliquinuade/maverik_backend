import logging
from datetime import datetime

import requests
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Query, Session

from maverik_backend.core import models, schemas
from maverik_backend.core.models import SesionAsesoria, SesionAsesoriaDetalle, Usuario
from maverik_backend.settings import Settings


def crear_usuario(db: Session, valores: schemas.UsuarioCrear) -> Usuario:
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

    return usuario


def crear_sesion_asesoria(db: Session, valores: schemas.SesionAsesoriaCrear) -> SesionAsesoria:
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

    return sesion_asesoria


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
    Envía un chat al servicio RAG con manejo robusto de errores.
    """
    try:
        sesion_asesoria: SesionAsesoria = cargar_sesion_asesoria(db=db, id=valores.sesion_asesoria_id)
        if not sesion_asesoria:
            logging.error(f"No se encontró la sesión de asesoría con ID: {valores.sesion_asesoria_id}")
            return None
            
        usuario: Usuario = sesion_asesoria.usuario
        if not usuario:
            logging.error(f"No se encontró el usuario para la sesión: {valores.sesion_asesoria_id}")
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

        mensaje_usuario = schemas.RagServiceRequestMessage(
            userProfile=user_profile,
            input=input,
            chatHistory=chat_history,
        )

        # URL del servicio RAG
        rag_url = app_config.rag_service_url + "/api/chat"
        logging.info(f"Enviando input al servicio RAG en {rag_url}: {mensaje_usuario}")
        
        # Realizar petición con timeout y manejo de errores
        try:
            # Usar timeout configurable desde settings
            timeout_seconds = app_config.external_service_timeout
            
            logging.info(f"Enviando petición al RAG con timeout de {timeout_seconds}s...")
            resp = requests.post(
                rag_url, 
                json=mensaje_usuario.dict(), 
                timeout=timeout_seconds,
                headers={"Content-Type": "application/json"}
            )
            logging.info(f"Respuesta del RAG: Status {resp.status_code}")
            
            if resp.status_code == 200:
                try:
                    response_data = resp.json()
                    output = response_data.get("response")
                    
                    if output:
                        logging.info(f"RAG respondió exitosamente. Output length: {len(output)}")
                        return schemas.RagServiceResponseMessage(input=input, output=output)
                    else:
                        logging.error("RAG respondió pero sin campo 'response' en JSON")
                        return None
                        
                except ValueError as e:
                    logging.error(f"Error parseando JSON del RAG: {str(e)}")
                    logging.error(f"Respuesta RAG: {resp.text[:500]}...")
                    return None
            else:
                logging.error(f"RAG respondió con error {resp.status_code}: {resp.text[:500]}...")
                return None
                
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Error de conexión al servicio RAG en {rag_url}: {str(e)}")
            logging.error("Verifica que:")
            logging.error("1. El servicio RAG esté ejecutándose")
            logging.error("2. La URL sea correcta (usar host.docker.internal para Docker)")
            logging.error("3. El puerto esté disponible")
            return None
            
        except requests.exceptions.Timeout as e:
            logging.error(f"Timeout conectando al servicio RAG después de {timeout_seconds}s: {str(e)}")
            logging.error("El servicio RAG está tardando mucho en responder. Considera:")
            logging.error("1. Optimizar el modelo RAG")
            logging.error("2. Usar consultas más simples")
            logging.error("3. Implementar cache de respuestas")
            
            # Retornar respuesta de fallback en lugar de None
            fallback_response = (
                "Disculpa, el servicio de análisis está experimentando demoras. "
                "Mientras tanto, puedo sugerirte que para inversiones básicas consideres: "
                "1) Fondos de inversión diversificados para principiantes, "
                "2) Bonos del gobierno para inversiones conservadoras, "
                "3) Educación financiera continua. "
                "Por favor, intenta tu consulta nuevamente en unos momentos."
            )
            
            logging.info("Devolviendo respuesta de fallback debido a timeout")
            return schemas.RagServiceResponseMessage(input=input, output=fallback_response)
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error en petición al RAG: {str(e)}")
            return None
            
    except Exception as e:
        logging.error(f"Error inesperado en enviar_chat_al_rag: {str(e)}")
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
