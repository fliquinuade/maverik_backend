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
    query = Query(SesionAsesoria).filter(SesionAsesoria.id == id)
    try:
        return query.with_session(db).one()
    except NoResultFound:
        return None


def obtener_perfil_riesgo(sesion_asesoria: SesionAsesoria) -> str:
    tolerancia_al_riesgo = {
        "baja": "conservative",
        "media": "moderate",
        "alta": "bold",
    }

    return tolerancia_al_riesgo[sesion_asesoria.tolerancia_al_riesgo.desc]


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
    proposito_sesion: models.PropositoSesion = sesion.proposito_sesion
    objetivo: models.Objetivo = sesion.objetivo
    tolerancia_al_riesgo: models.ToleranciaAlRiesgo = sesion.tolerancia_al_riesgo

    primer_input = "En esta oportunidad, vine a {}.".format(proposito_sesion.desc.lower())
    if objetivo:
        primer_input += (
            " Quiero {}. "
            "Dispongo de un capital inicial de {:.2f}. "
            "Me gustaría lograr este objetivo en {} meses. "
            "Mi tolerancia al riesgo para lograr este objetivo es {}."
        ).format(
            objetivo.desc.lower(),
            float(sesion.capital_inicial),
            sesion.horizonte_temporal,
            tolerancia_al_riesgo.desc.lower(),
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
    sesion_asesoria: SesionAsesoria = cargar_sesion_asesoria(db=db, id=valores.sesion_asesoria_id)
    usuario: Usuario = sesion_asesoria.usuario

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
        chat_history = [(det.texto_usuario, det.texto_sistema) for det in detalles]
    else:
        input = preparar_primer_input(sesion=sesion_asesoria)
        chat_history = []

    mensaje_usuario = schemas.RagServiceRequestMessage(
        userProfile=user_profile,
        input=input,
        chatHistory=chat_history,
    )

    logging.info("enviando input al servicio RAG: %s ...", mensaje_usuario)
    resp = requests.post(app_config.rag_service_url + "/api/chat", json=mensaje_usuario.dict())
    logging.info(resp.status_code)
    output = None
    if resp.status_code == 200:
        output = resp.json()["response"]
        # if output and len(chat_history) == 0:
        #     logging.info("enviando petición al servicio de optimización para obtener un portafolio ...")
        #     url = app_config.portfolio_optimization_url + "/portfolio/generate/{}".format(risk_profile)
        #     os_resp = requests.post(url)
        #     if os_resp.status_code == 200:
        #         portfolio = os_resp.json()
        #         composicion_texto = ", ".join(
        #             [
        #                 "{} ({:.10f}%)".format(asset, portfolio["weights"][index])
        #                 for index, asset in enumerate(portfolio["assets"])
        #             ]
        #         )
        #         portfolio_texto = (
        #             "    Además te traigo una información preliminar que puede ser de tu interés, "
        #             "haciendo uso de un servicio de terceros pude obtener un portafolio "
        #             "con una distribución interesante de acciones "
        #             "para tener en cuenta como una idea de inversión. "
        #             "El portafolio esta compuesto de la siguiente manera: {}"
        #         ).format(composicion_texto)
        #         output += portfolio_texto

    if output:
        return schemas.RagServiceResponseMessage(input=input, output=output)
    else:
        return None

    # return schemas.RagServiceResponseMessage(input=input, output="me parece bien tu objetivo")


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
