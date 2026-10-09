"""Entidades que describen el desarrollo y el resultado de la recursion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from fuerza_trabajo.dominio.costos import DesgloseCosto
from fuerza_trabajo.dominio.parametros import ParametrosProblema


@dataclass(frozen=True)
class Alternativa:
    """Una decision x_i evaluada desde un estado x_(i-1) de la etapa i."""

    semana: int
    fuerza_previa: int
    fuerza: int
    desglose: DesgloseCosto
    costo_futuro: float

    @property
    def costo_inmediato(self) -> float:
        """Costo de la semana actual C_i(x_(i-1), x_i)."""
        return self.desglose.total

    @property
    def costo_total(self) -> float:
        """Valor C_i(x_(i-1), x_i) + f_(i+1)(x_i) evaluado en la recursion."""
        return self.costo_inmediato + self.costo_futuro


@dataclass(frozen=True)
class EstadoResuelto:
    """Resultado de optimizar un estado x_(i-1) dentro de una etapa."""

    semana: int
    fuerza_previa: int
    alternativas: Tuple[Alternativa, ...]

    def __post_init__(self) -> None:
        if not self.alternativas:
            raise ValueError(
                f"El estado x={self.fuerza_previa} de la semana {self.semana} "
                "no tiene alternativas factibles."
            )

    @property
    def mejor_alternativa(self) -> Alternativa:
        """Alternativa de costo minimo; ante empate, la de menor x_i."""
        return min(self.alternativas, key=lambda alt: (alt.costo_total, alt.fuerza))

    @property
    def valor_optimo(self) -> float:
        """Valor f_i(x_(i-1)) de la funcion optima para este estado."""
        return self.mejor_alternativa.costo_total

    @property
    def decision_optima(self) -> int:
        """Decision x_i* asociada a f_i(x_(i-1))."""
        return self.mejor_alternativa.fuerza

    @property
    def decisiones_evaluadas(self) -> Tuple[int, ...]:
        """Valores de x_i considerados en este estado."""
        return tuple(alt.fuerza for alt in self.alternativas)

    def alternativa(self, fuerza: int) -> Alternativa:
        """Recupera la alternativa evaluada para una decision x_i concreta."""
        for alternativa in self.alternativas:
            if alternativa.fuerza == fuerza:
                return alternativa
        raise KeyError(
            f"La decision x={fuerza} no fue evaluada en la semana {self.semana}."
        )


@dataclass(frozen=True)
class EtapaResuelta:
    """Etapa i (semana i) con todos sus estados ya optimizados."""

    semana: int
    demanda: int
    decisiones: Tuple[int, ...]
    estados: Tuple[EstadoResuelto, ...]

    @property
    def estados_entrada(self) -> Tuple[int, ...]:
        """Estados x_(i-1) tabulados en la etapa."""
        return tuple(estado.fuerza_previa for estado in self.estados)

    def estado(self, fuerza_previa: int) -> EstadoResuelto:
        """Recupera el estado tabulado para un x_(i-1) dado."""
        for estado in self.estados:
            if estado.fuerza_previa == fuerza_previa:
                return estado
        raise KeyError(
            f"El estado x={fuerza_previa} no fue tabulado en la semana {self.semana}."
        )


@dataclass(frozen=True)
class DecisionOptima:
    """Decision de una semana dentro de la politica optima recuperada."""

    semana: int
    demanda: int
    fuerza_previa: int
    fuerza: int
    desglose: DesgloseCosto
    costo_acumulado: float

    @property
    def costo_semana(self) -> float:
        """Costo de la semana en la politica optima."""
        return self.desglose.total


@dataclass(frozen=True)
class Solucion:
    """Solucion completa: tablas de cada etapa y politica optima recuperada."""

    parametros: ParametrosProblema
    etapas: Tuple[EtapaResuelta, ...]
    decisiones: Tuple[DecisionOptima, ...]

    @property
    def plan(self) -> Tuple[int, ...]:
        """Tamano optimo de la fuerza de trabajo para cada semana."""
        return tuple(decision.fuerza for decision in self.decisiones)

    @property
    def costo_total(self) -> float:
        """Costo minimo total del horizonte."""
        return sum(decision.costo_semana for decision in self.decisiones)

    @property
    def costo_total_excedente(self) -> float:
        """Parte del costo optimo atribuible a mano de obra excedente."""
        return sum(d.desglose.costo_excedente for d in self.decisiones)

    @property
    def costo_total_contratacion(self) -> float:
        """Parte del costo optimo atribuible a contrataciones."""
        return sum(d.desglose.costo_contratacion for d in self.decisiones)

    def etapa(self, semana: int) -> EtapaResuelta:
        """Recupera la etapa correspondiente a una semana."""
        for etapa in self.etapas:
            if etapa.semana == semana:
                return etapa
        raise KeyError(f"No existe la etapa de la semana {semana}.")
