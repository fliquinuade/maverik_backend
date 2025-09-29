from datetime import date, datetime

from pydantic import BaseModel, EmailStr


class UsuarioCrear(BaseModel):
    email: EmailStr
    clave: str
    fecha_nacimiento: date
    nivel_educativo_id: int
    conocimiento_alt_inversion_id: int
    experiencia_invirtiendo_id: int
    porcentaje_ahorro_mensual_id: int
    porcentaje_ahorro_invertir_id: int
    tiempo_mantener_inversion_id: int
    busca_invertir_en_id: int
    proporcion_inversion_mantener_id: int


class UsuarioActualizar(BaseModel):
    fecha_actualizacion: datetime


class Usuario(BaseModel):
    id: int
    email: EmailStr
    fecha_nacimiento: date
    nivel_educativo_id: int
    conocimiento_alt_inversion_id: int
    experiencia_invirtiendo_id: int
    porcentaje_ahorro_mensual_id: int
    porcentaje_ahorro_invertir_id: int
    tiempo_mantener_inversion_id: int
    busca_invertir_en_id: int
    proporcion_inversion_mantener_id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True


class UsuarioLogin(BaseModel):
    email: EmailStr
    clave: str


class SesionAsesoriaCrear(BaseModel):
    usuario_id: int
    proposito_sesion_id: int
    objetivo_id: int | None
    capital_inicial: float | None
    horizonte_temporal: int | None
    tolerancia_al_riesgo_id: int | None


class SesionAsesoria(BaseModel):
    id: int
    usuario_id: int
    proposito_sesion_id: int
    objetivo_id: int | None
    capital_inicial: float | None
    horizonte_temporal: int | None
    tolerancia_al_riesgo_id: int | None
    fecha_creacion: datetime
    titulo_chat: str | None
    primer_input: str | None

    class Config:
        from_attributes = True


class SesionAsesoriaDetalleCrear(BaseModel):
    sesion_asesoria_id: int
    texto_usuario: str
    texto_sistema: str


class SesionAsesoriaDetalle(BaseModel):
    id: int
    sesion_asesoria_id: int
    input: str
    output: str


class SesionAsesoriaConDetalles(BaseModel):
    id: int
    detalles: list[SesionAsesoriaDetalle]


class ChatCrear(BaseModel):
    sesion_asesoria_id: int
    input: str | None


class UsuarioCrearRequest(BaseModel):
    email: str
    fecha_nacimiento: date | None
    nivel_educativo_id: int
    conocimiento_alt_inversion_id: int
    experiencia_invirtiendo_id: int
    porcentaje_ahorro_mensual_id: int
    porcentaje_ahorro_invertir_id: int
    tiempo_mantener_inversion_id: int
    busca_invertir_en_id: int
    proporcion_inversion_mantener_id: int


class SesionAsesoriaCrearRequest(BaseModel):
    proposito_sesion_id: int
    objetivo_id: int | None
    capital_inicial: float | None
    horizonte_temporal: int | None
    tolerancia_al_riesgo_id: int | None


class SesionAsesoriaDetalleRequest(BaseModel):
    input: str | None


class ChatCrearRequest(BaseModel):
    sesion_asesoria_id: int
    texto_usuario: str
    texto_sistema: str


class RagServiceRequestMessage(BaseModel):
    userProfile: str
    chatHistory: list[tuple[str, str]] = []
    input: str


class RagServiceResponseMessage(BaseModel):
    input: str
    output: str
