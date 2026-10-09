"""Solucionador del modelo de tamano de la fuerza de trabajo.

Se usa programacion dinamica con recursion hacia atras:

    Etapa  i  : semana i (i = 1, 2, ..., n)
    Estado x_(i-1) : tamano de la fuerza de trabajo de la semana anterior
    Decision x_i   : tamano de la fuerza de trabajo de la semana i, con
                     x_i >= b_i

    f_n(x_(n-1)) = min { C_n(x_(n-1), x_n) }
    f_i(x_(i-1)) = min { C_i(x_(i-1), x_i) + f_(i+1)(x_i) }
"""

from __future__ import annotations

from typing import Dict, List, Optional

from fuerza_trabajo.dominio.costos import CalculadoraCostos
from fuerza_trabajo.dominio.entidades import (
    Alternativa,
    DecisionOptima,
    EstadoResuelto,
    EtapaResuelta,
    Solucion,
)
from fuerza_trabajo.dominio.parametros import ParametrosProblema


class SolucionadorFuerzaTrabajo:
    """Resuelve el modelo y conserva las tablas intermedias de cada etapa."""

    def __init__(
        self,
        parametros: ParametrosProblema,
        calculadora: Optional[CalculadoraCostos] = None,
    ) -> None:
        self.parametros = parametros
        self.calculadora = calculadora or CalculadoraCostos(parametros)

    # ------------------------------------------------------------------ #
    # API publica
    # ------------------------------------------------------------------ #
    def resolver(self) -> Solucion:
        """Ejecuta la recursion y recupera la politica optima."""
        etapas = self._resolver_etapas()
        decisiones = self._recuperar_politica(etapas)
        return Solucion(
            parametros=self.parametros,
            etapas=tuple(etapas),
            decisiones=tuple(decisiones),
        )

    # ------------------------------------------------------------------ #
    # Paso 1: recursion hacia atras (de la ultima semana a la primera)
    # ------------------------------------------------------------------ #
    def _resolver_etapas(self) -> List[EtapaResuelta]:
        """Tabula f_i(x_(i-1)) para todas las etapas, desde la ultima."""
        etapas: List[EtapaResuelta] = []
        # f_(i+1)(x_i): costo optimo de las etapas posteriores. Para la ultima
        # etapa no hay futuro, por lo que el costo es cero.
        costos_futuros: Dict[int, float] = {}

        for semana in reversed(self.parametros.semanas):
            etapa = self._resolver_etapa(semana, costos_futuros)
            etapas.append(etapa)
            costos_futuros = {
                estado.fuerza_previa: estado.valor_optimo for estado in etapa.estados
            }

        etapas.reverse()
        return etapas

    def _resolver_etapa(
        self, semana: int, costos_futuros: Dict[int, float]
    ) -> EtapaResuelta:
        """Optimiza todos los estados de entrada de una etapa."""
        decisiones = self.parametros.decisiones(semana)
        estados = tuple(
            self._resolver_estado(semana, fuerza_previa, decisiones, costos_futuros)
            for fuerza_previa in self.parametros.estados_entrada(semana)
        )
        return EtapaResuelta(
            semana=semana,
            demanda=self.parametros.demanda_semana(semana),
            decisiones=decisiones,
            estados=estados,
        )

    def _resolver_estado(
        self,
        semana: int,
        fuerza_previa: int,
        decisiones,
        costos_futuros: Dict[int, float],
    ) -> EstadoResuelto:
        """Evalua todas las decisiones factibles desde un estado de entrada."""
        alternativas = tuple(
            Alternativa(
                semana=semana,
                fuerza_previa=fuerza_previa,
                fuerza=fuerza,
                desglose=self.calculadora.desglose(semana, fuerza_previa, fuerza),
                costo_futuro=costos_futuros.get(fuerza, 0.0),
            )
            for fuerza in decisiones
        )
        return EstadoResuelto(
            semana=semana,
            fuerza_previa=fuerza_previa,
            alternativas=alternativas,
        )

    # ------------------------------------------------------------------ #
    # Paso 2: recuperacion de la politica optima (hacia adelante)
    # ------------------------------------------------------------------ #
    def _recuperar_politica(self, etapas: List[EtapaResuelta]) -> List[DecisionOptima]:
        """Recorre las etapas hacia adelante siguiendo las decisiones x_i*."""
        decisiones: List[DecisionOptima] = []
        fuerza_previa = self.parametros.fuerza_inicial
        acumulado = 0.0

        for etapa in etapas:
            mejor = etapa.estado(fuerza_previa).mejor_alternativa
            acumulado += mejor.costo_inmediato
            decisiones.append(
                DecisionOptima(
                    semana=etapa.semana,
                    demanda=etapa.demanda,
                    fuerza_previa=fuerza_previa,
                    fuerza=mejor.fuerza,
                    desglose=mejor.desglose,
                    costo_acumulado=acumulado,
                )
            )
            fuerza_previa = mejor.fuerza

        return decisiones
