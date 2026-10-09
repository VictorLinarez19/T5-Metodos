"""Capa de dominio: datos de entrada, costos y entidades del modelo."""

from fuerza_trabajo.dominio.costos import CalculadoraCostos, DesgloseCosto
from fuerza_trabajo.dominio.entidades import (
    Alternativa,
    DecisionOptima,
    EstadoResuelto,
    EtapaResuelta,
    Solucion,
)
from fuerza_trabajo.dominio.parametros import ParametrosProblema

__all__ = [
    "Alternativa",
    "CalculadoraCostos",
    "DecisionOptima",
    "DesgloseCosto",
    "EstadoResuelto",
    "EtapaResuelta",
    "ParametrosProblema",
    "Solucion",
]
