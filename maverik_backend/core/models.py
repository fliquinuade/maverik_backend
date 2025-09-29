import datetime as DT
from datetime import date, datetime

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase): ...


class NivelEducativo(Base):
    __tablename__ = "nivel_educativo"

    id: Mapped[int] = mapped_column(primary_key=True)
    desc: Mapped[str] = mapped_column(String(500))

    usuarios: Mapped[list["Usuario"]] = relationship(
        back_populates="nivel_educativo", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"NivelEducativo(id={self.id!r}, desc={self.desc!r})"


class ConocimientoAltInversion(Base):
    __tablename__ = "conocimiento_alt_inversion"

    id: Mapped[int] = mapped_column(primary_key=True)
    desc: Mapped[str] = mapped_column(String(500))

    usuarios: Mapped[list["Usuario"]] = relationship(
        back_populates="conocimiento_alt_inversion", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"ConocimientoAltInversion(id={self.id!r}, desc={self.desc!r})"


class ExperienciaInvirtiendo(Base):
    __tablename__ = "experiencia_invirtiendo"

    id: Mapped[int] = mapped_column(primary_key=True)
    desc: Mapped[str] = mapped_column(String(500))

    usuarios: Mapped[list["Usuario"]] = relationship(
        back_populates="experiencia_invirtiendo", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"ExperienciaInvirtiendo(id={self.id!r}, desc={self.desc!r})"


class PorcentajeAhorroMensual(Base):
    __tablename__ = "porcentaje_ahorro_mensual"

    id: Mapped[int] = mapped_column(primary_key=True)
    desc: Mapped[str] = mapped_column(String(500))

    usuarios: Mapped[list["Usuario"]] = relationship(
        back_populates="porcentaje_ahorro_mensual", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"PorcentajeAhorroMensual(id={self.id!r}, desc={self.desc!r})"


class PorcentajeAhorroInvertir(Base):
    __tablename__ = "porcentaje_ahorro_invertir"

    id: Mapped[int] = mapped_column(primary_key=True)
    desc: Mapped[str] = mapped_column(String(500))

    usuarios: Mapped[list["Usuario"]] = relationship(
        back_populates="porcentaje_ahorro_invertir", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"PorcentajeAhorroInvertir(id={self.id!r}, desc={self.desc!r})"


class TiempoMantenerInversion(Base):
    __tablename__ = "tiempo_mantener_inversion"

    id: Mapped[int] = mapped_column(primary_key=True)
    desc: Mapped[str] = mapped_column(String(500))

    usuarios: Mapped[list["Usuario"]] = relationship(
        back_populates="tiempo_mantener_inversion", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"TiempoMantenerInversion(id={self.id!r}, desc={self.desc!r})"


class BuscaInvertirEn(Base):
    __tablename__ = "busca_invertir_en"

    id: Mapped[int] = mapped_column(primary_key=True)
    desc: Mapped[str] = mapped_column(String(500))

    usuarios: Mapped[list["Usuario"]] = relationship(
        back_populates="busca_invertir_en", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"BuscaInvertirEn(id={self.id!r}, desc={self.desc!r})"


class ProporcionInversionMantener(Base):
    __tablename__ = "proporcion_inversion_mantener"

    id: Mapped[int] = mapped_column(primary_key=True)
    desc: Mapped[str] = mapped_column(String(500))

    usuarios: Mapped[list["Usuario"]] = relationship(
        back_populates="proporcion_inversion_mantener", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"ProporcionInversionMantener(id={self.id!r}, desc={self.desc!r})"


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(500))
    clave: Mapped[str] = mapped_column(String(500))
    fecha_nacimiento: Mapped[date]
    nivel_educativo_id: Mapped[int] = mapped_column(ForeignKey("nivel_educativo.id"))
    conocimiento_alt_inversion_id: Mapped[int] = mapped_column(ForeignKey("conocimiento_alt_inversion.id"))
    experiencia_invirtiendo_id: Mapped[int] = mapped_column(ForeignKey("experiencia_invirtiendo.id"))
    porcentaje_ahorro_mensual_id: Mapped[int] = mapped_column(ForeignKey("porcentaje_ahorro_mensual.id"))
    porcentaje_ahorro_invertir_id: Mapped[int] = mapped_column(ForeignKey("porcentaje_ahorro_invertir.id"))
    tiempo_mantener_inversion_id: Mapped[int] = mapped_column(ForeignKey("tiempo_mantener_inversion.id"))
    busca_invertir_en_id: Mapped[int] = mapped_column(ForeignKey("busca_invertir_en.id"))
    proporcion_inversion_mantener_id: Mapped[int] = mapped_column(
        ForeignKey("proporcion_inversion_mantener.id")
    )
    fecha_creacion: Mapped[datetime] = mapped_column(default=datetime.now(DT.UTC))
    fecha_actualizacion: Mapped[datetime] = mapped_column(default=datetime.now(DT.UTC))

    nivel_educativo: Mapped["NivelEducativo"] = relationship(back_populates="usuarios")
    conocimiento_alt_inversion: Mapped["ConocimientoAltInversion"] = relationship(back_populates="usuarios")
    experiencia_invirtiendo: Mapped["ExperienciaInvirtiendo"] = relationship(back_populates="usuarios")
    porcentaje_ahorro_mensual: Mapped["PorcentajeAhorroMensual"] = relationship(back_populates="usuarios")
    porcentaje_ahorro_invertir: Mapped["PorcentajeAhorroInvertir"] = relationship(back_populates="usuarios")
    tiempo_mantener_inversion: Mapped["TiempoMantenerInversion"] = relationship(back_populates="usuarios")
    busca_invertir_en: Mapped["BuscaInvertirEn"] = relationship(back_populates="usuarios")
    proporcion_inversion_mantener: Mapped["ProporcionInversionMantener"] = relationship(
        back_populates="usuarios"
    )
    sesiones_asesoria: Mapped[list["SesionAsesoria"]] = relationship(
        back_populates="usuario",
        cascade="all, delete-orphan",
    )

    class Config:
        use_enum_values = True

    def __repr__(self) -> str:
        _repr = "Usuario("
        _repr += f"id={self.id!r}, email={self.email!r}, fecha_nacimiento={self.fecha_nacimiento!r}, "
        _repr += f"nivel_educativo={self.nivel_educativo!r}, "
        _repr += f"conocimiento_alt_inversion={self.conocimiento_alt_inversion!r}, "
        _repr += f"experiencia_invirtiendo={self.experiencia_invirtiendo!r}, "
        _repr += f"porcentaje_ahorro_mensual={self.porcentaje_ahorro_mensual!r}, "
        _repr += f"porcentaje_ahorro_invertir={self.porcentaje_ahorro_invertir!r}, "
        _repr += f"tiempo_mantener_inversion={self.tiempo_mantener_inversion!r}, "
        _repr += f"busca_invertir_en={self.busca_invertir_en!r}, "
        _repr += f"proporcion_inversion_mantener={self.proporcion_inversion_mantener!r}, "
        _repr += f"fecha_creacion={self.fecha_creacion!r}, fecha_actualizacion={self.fecha_actualizacion!r}"
        _repr += ")"
        return _repr


class Objetivo(Base):
    __tablename__ = "objetivo"

    id: Mapped[int] = mapped_column(primary_key=True)
    desc: Mapped[str] = mapped_column(String(500))

    sesiones_asesoria: Mapped[list["SesionAsesoria"]] = relationship(
        back_populates="objetivo",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Objetivo(id={self.id!r}, desc={self.desc!r})"


class ToleranciaAlRiesgo(Base):
    __tablename__ = "tolerancia_al_riesgo"

    id: Mapped[int] = mapped_column(primary_key=True)
    desc: Mapped[str] = mapped_column(String(500))

    sesiones_asesoria: Mapped[list["SesionAsesoria"]] = relationship(
        back_populates="tolerancia_al_riesgo",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"ToleranciaAlRiesgo(id={self.id!r}, desc={self.desc!r})"


class PropositoSesion(Base):
    __tablename__ = "proposito_sesion"

    id: Mapped[int] = mapped_column(primary_key=True)
    desc: Mapped[str] = mapped_column(String(500))

    sesiones_asesoria: Mapped[list["SesionAsesoria"]] = relationship(
        back_populates="proposito_sesion",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"PropositoSesion(id={self.id!r}, desc={self.desc!r})"


class SesionAsesoria(Base):
    __tablename__ = "sesion_asesoria"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    proposito_sesion_id: Mapped[int] = mapped_column(ForeignKey("proposito_sesion.id"))
    objetivo_id: Mapped[int] = mapped_column(ForeignKey("objetivo.id"), nullable=True)
    capital_inicial: Mapped[Numeric] = mapped_column(Numeric(13, 4), nullable=True)
    horizonte_temporal: Mapped[int] = mapped_column(nullable=True)
    tolerancia_al_riesgo_id: Mapped[int] = mapped_column(ForeignKey("tolerancia_al_riesgo.id"), nullable=True)
    fecha_creacion: Mapped[datetime] = mapped_column(default=datetime.now(DT.UTC))

    objetivo: Mapped["Objetivo"] = relationship(back_populates="sesiones_asesoria")
    proposito_sesion: Mapped["PropositoSesion"] = relationship(back_populates="sesiones_asesoria")
    usuario: Mapped["Usuario"] = relationship(back_populates="sesiones_asesoria")
    tolerancia_al_riesgo: Mapped["ToleranciaAlRiesgo"] = relationship(back_populates="sesiones_asesoria")

    class Config:
        use_enum_values = True

    def __repr__(self) -> str:
        _repr = "SesionAsesoria("
        _repr += f"id={self.id!r}, usuario={self.usuario!r}, proposito_sesion={self.proposito_sesion!r}, "
        _repr += f"objetivo={self.objetivo!r}, "
        _repr += f"capital_inicial={self.capital_inicial!r}, "
        _repr += f"horizonte_temporal={self.horizonte_temporal!r}, "
        _repr += f"tolerancia_al_riesgo={self.tolerancia_al_riesgo!r}, "
        _repr += f"fecha_creacion={self.fecha_creacion!r}"
        _repr += ")"
        return _repr


class SesionAsesoriaDetalle(Base):
    __tablename__ = "sesion_asesoria_detalle"

    id: Mapped[int] = mapped_column(primary_key=True)
    sesion_asesoria_id: Mapped[int] = mapped_column(ForeignKey("sesion_asesoria.id"))
    texto_usuario: Mapped[str] = mapped_column(String(2000))
    texto_sistema: Mapped[str] = mapped_column(String(2000))

    def __repr__(self) -> str:
        _repr = "SesionAsesoriaDetalle("
        _repr += f"id={self.id!r}, "
        _repr += f"texto_usuario={self.texto_usuario!r}, "
        _repr += f"texto_sistema={self.texto_sistema!r}"
        _repr += ")"
        return _repr
