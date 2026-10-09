"""Modelo de tamano de la fuerza de trabajo resuelto con Programacion Dinamica.

Paquete organizado en tres capas independientes:

* ``dominio``      -> datos del problema, costos y entidades del modelo.
* ``solucionador`` -> la recursion de programacion dinamica (hacia atras).
* ``reportes``     -> formateo paso a paso y exportacion a archivo de texto.
"""

from fuerza_trabajo.dominio import (
    Alternativa,
    CalculadoraCostos,
    DecisionOptima,
    DesgloseCosto,
    EstadoResuelto,
    EtapaResuelta,
    ParametrosProblema,
    Solucion,
)
from fuerza_trabajo.reportes import ExportadorTexto, FormateadorReporte
from fuerza_trabajo.solucionador import SolucionadorFuerzaTrabajo

__all__ = [
    "Alternativa",
    "CalculadoraCostos",
    "DecisionOptima",
    "DesgloseCosto",
    "EstadoResuelto",
    "EtapaResuelta",
    "ExportadorTexto",
    "FormateadorReporte",
    "ParametrosProblema",
    "Solucion",
    "SolucionadorFuerzaTrabajo",
]

__version__ = "1.0.0"
