import logging
import secrets
from contextlib import asynccontextmanager
from functools import partial
from typing import Annotated

from fastapi import Depends, FastAPI
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
    chat = schemas.ChatCrear(
        sesion_asesoria_id=session_id,
        input=data.input,
    )
    rag_response = services.enviar_chat_al_rag(
        db=db,
        valores=chat,
        app_config=app_config,
    )
    logging.info(rag_response)

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

    return sesion_asesoria_detalle


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
