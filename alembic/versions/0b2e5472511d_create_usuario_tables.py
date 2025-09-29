"""create_usuario_tables

Revision ID: 0b2e5472511d
Revises:
Create Date: 2024-10-03 16:59:43.193954

"""

from collections.abc import Sequence
from typing import Any

import sqlalchemy as sa
from sqlalchemy.sql.schema import Table

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0b2e5472511d"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def create_table(table_name: str, rows: list[dict[str, Any]]) -> Table:
    table = op.create_table(
        table_name,
        sa.Column(
            "id",
            sa.SmallInteger,
            sa.Identity(always=False, start=1, cycle=True),
            primary_key=True,
        ),
        sa.Column("desc", sa.String(length=500), nullable=False),
    )

    op.bulk_insert(table, rows=rows)

    return table


def create_fk(source_table: str, referent_table: str):
    name = "fk_{}_{}".format(source_table, referent_table)
    local_col = "{}_id".format(referent_table)
    op.create_foreign_key(
        constraint_name=name,
        source_table=source_table,
        referent_table=referent_table,
        local_cols=[local_col],
        remote_cols=["id"],
    )


def upgrade() -> None:
    create_table(
        "nivel_educativo",
        [
            {"desc": "Primaria"},
            {"desc": "Secundaria"},
            {"desc": "Superior"},
        ],
    )

    create_table(
        "conocimiento_alt_inversion",
        [
            {"desc": "Nulo"},
            {"desc": "Poco"},
            {"desc": "Minimo"},
            {"desc": "Intermedio"},
            {"desc": "Experto"},
        ],
    )

    create_table(
        "experiencia_invirtiendo",
        [
            {"desc": "Ninguna"},
            {"desc": "Minima"},
            {"desc": "Intermedia"},
            {"desc": "Avanzada"},
            {"desc": "Experto"},
        ],
    )

    create_table(
        "porcentaje_ahorro_mensual",
        [
            {"desc": "Hasta el 10%"},
            {"desc": "Hasta el 25%"},
            {"desc": "Hasta el 50%"},
            {"desc": "Hasta el 75%"},
        ],
    )

    create_table(
        "porcentaje_ahorro_invertir",
        [
            {"desc": "Hasta el 10%"},
            {"desc": "Hasta el 25%"},
            {"desc": "Hasta el 50%"},
            {"desc": "Hasta el 75%"},
        ],
    )

    create_table(
        "tiempo_mantener_inversion",
        [
            {"desc": "Menos de 1 año"},
            {"desc": "Entre 1 y 5 años"},
            {"desc": "Entre 5 y 10 años"},
            {"desc": "Más de 10 años"},
        ],
    )

    create_table(
        "busca_invertir_en",
        [
            {"desc": "Mantener el valor de mis ahorros"},
            {"desc": "Ganarle a la inflación"},
            {"desc": "Obtener rendimientos entre la tasa de inflación y hasta 5% más que la misma"},
            {
                "desc": (
                    "Obtener rendimientos mayores a 5% sobre "
                    "la tasa de inflación, aún si eso implica asumir mayores riesgos"
                )
            },
        ],
    )

    create_table(
        "proporcion_inversion_mantener",
        [
            {"desc": "Me retiro inmediatamente (vendo el total)"},
            {"desc": "Rescato parte de la inversión y el resto lo asigno a productos de menor riesgo"},
            {
                "desc": (
                    "Mi estrategia no varía, ya creo que para obtener rentabilidades superiores, "
                    "existe la posibilidad de que hayan rentabilidades negativas (mantengo el total)"
                )
            },
            {
                "desc": (
                    "Obtener rendimientos mayores a 5% sobre la tasa de inflación, "
                    "aún si eso implica asumir mayores riesgos"
                )
            },
        ],
    )

    op.create_table(
        "usuario",
        sa.Column(
            "id",
            sa.BigInteger,
            sa.Identity(always=False, start=1, cycle=True),
            primary_key=True,
        ),
        sa.Column("email", sa.String(length=500), nullable=False),
        sa.Column("clave", sa.String(length=500), nullable=False),
        sa.Column("fecha_nacimiento", sa.Date, nullable=True),
        sa.Column("nivel_educativo_id", sa.SMALLINT, nullable=True),
        sa.Column("conocimiento_alt_inversion_id", sa.SMALLINT, server_default="1", nullable=False),
        sa.Column("experiencia_invirtiendo_id", sa.SMALLINT, server_default="1", nullable=False),
        sa.Column("porcentaje_ahorro_mensual_id", sa.SMALLINT, server_default="1", nullable=False),
        sa.Column("porcentaje_ahorro_invertir_id", sa.SMALLINT, server_default="1", nullable=False),
        sa.Column("tiempo_mantener_inversion_id", sa.SMALLINT, server_default="1", nullable=False),
        sa.Column("busca_invertir_en_id", sa.SMALLINT, server_default="1", nullable=False),
        sa.Column("proporcion_inversion_mantener_id", sa.SMALLINT, server_default="1", nullable=False),
        sa.Column("fecha_creacion", sa.DateTime, server_default=sa.func.current_timestamp(), nullable=False),
        sa.Column(
            "fecha_actualizacion", sa.DateTime, server_default=sa.func.current_timestamp(), nullable=False
        ),
    )

    create_fk("usuario", "nivel_educativo")
    create_fk("usuario", "conocimiento_alt_inversion")
    create_fk("usuario", "experiencia_invirtiendo")
    create_fk("usuario", "porcentaje_ahorro_mensual")
    create_fk("usuario", "porcentaje_ahorro_invertir")
    create_fk("usuario", "tiempo_mantener_inversion")
    create_fk("usuario", "busca_invertir_en")
    create_fk("usuario", "proporcion_inversion_mantener")

    create_table(
        "tolerancia_al_riesgo",
        [
            {"desc": "baja"},
            {"desc": "media"},
            {"desc": "alta"},
        ],
    )

    create_table(
        "objetivo",
        [
            {"desc": "Comprar una casa o un departamento"},
            {"desc": "Comprar un vehículo"},
            {"desc": "Crear un fondo para estudios universitarios (propios o de un familiar)"},
            {"desc": "Crear un fondo para el retiro jubilatorio"},
            {"desc": "Preservar el valor de los ahorros en el tiempo"},
            {"desc": "Ahorrar para realizar un viaje"},
            {"desc": "Generar un fondo para iniciar un emprendimiento"},
        ],
    )

    create_table(
        "proposito_sesion",
        [
            {"desc": "Fortalecer mis conocimientos financieros"},
            {"desc": "Buscar asistencia para lograr un objetivo personal"},
            {"desc": "Obtener información de los mercados y realizar investigación financiera"},
        ],
    )

    op.create_table(
        "sesion_asesoria",
        sa.Column(
            "id",
            sa.BigInteger,
            sa.Identity(always=False, start=1, cycle=True),
            primary_key=True,
        ),
        sa.Column("proposito_sesion_id", sa.BIGINT, server_default="1"),
        sa.Column("objetivo_id", sa.BIGINT),
        sa.Column("usuario_id", sa.BIGINT, nullable=False),
        sa.Column("capital_inicial", sa.NUMERIC),
        sa.Column("horizonte_temporal", sa.SMALLINT),  # meses
        sa.Column("tolerancia_al_riesgo_id", sa.SMALLINT),
        sa.Column("fecha_creacion", sa.DateTime, server_default=sa.func.current_timestamp(), nullable=False),
    )

    create_fk("sesion_asesoria", "usuario")
    create_fk("sesion_asesoria", "tolerancia_al_riesgo")
    create_fk("sesion_asesoria", "objetivo")
    create_fk("sesion_asesoria", "proposito_sesion")

    op.create_table(
        "sesion_asesoria_detalle",
        sa.Column(
            "id",
            sa.BigInteger,
            sa.Identity(always=False, start=1, cycle=True),
            primary_key=True,
        ),
        sa.Column("sesion_asesoria_id", sa.BIGINT, nullable=False),
        sa.Column("texto_usuario", sa.String(length=8000), nullable=False),
        sa.Column("texto_sistema", sa.String(length=8000), nullable=False),
    )

    create_fk("sesion_asesoria_detalle", "sesion_asesoria")


def downgrade() -> None:
    op.drop_table("sesion_asesoria_detalle")
    op.drop_table("sesion_asesoria")
    op.drop_table("tolerancia_al_riesgo")
    op.drop_table("objetivo")

    op.drop_table("usuario")
    op.drop_table("nivel_educativo")
    op.drop_table("conocimiento_alt_inversion")
    op.drop_table("experiencia_invirtiendo")
    op.drop_table("porcentaje_ahorro_mensual")
    op.drop_table("porcentaje_ahorro_invertir")
    op.drop_table("tiempo_mantener_inversion")
    op.drop_table("busca_invertir_en")
    op.drop_table("proporcion_inversion_mantener")
