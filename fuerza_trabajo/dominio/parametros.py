"""Parametros de entrada del modelo de tamano de la fuerza de trabajo."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple


@dataclass(frozen=True)
class ParametrosProblema:
    """Datos del problema del contratista.

    Atributos
    ---------
    demanda:
        Trabajadores requeridos (b_i) en cada una de las semanas del horizonte.
    costo_excedente:
        Costo por trabajador excedente conservado una semana en la nomina.
    costo_fijo_contratacion:
        Costo fijo en que se incurre cualquier semana en la que se contrata.
    costo_variable_contratacion:
        Costo por cada trabajador nuevo contratado en la semana.
    fuerza_inicial:
        Tamano de la fuerza de trabajo disponible antes de la semana 1 (x_0).
    """

    demanda: Tuple[int, ...]
    costo_excedente: float = 300.0
    costo_fijo_contratacion: float = 400.0
    costo_variable_contratacion: float = 200.0
    fuerza_inicial: int = 0

    # ------------------------------------------------------------------ #
    # Construccion y validacion
    # ------------------------------------------------------------------ #
    def __post_init__(self) -> None:
        object.__setattr__(self, "demanda", tuple(int(valor) for valor in self.demanda))

        if not self.demanda:
            raise ValueError("La demanda debe tener al menos una semana.")
        if any(valor < 0 for valor in self.demanda):
            raise ValueError("La demanda semanal no puede ser negativa.")
        if self.fuerza_inicial < 0:
            raise ValueError("La fuerza de trabajo inicial no puede ser negativa.")
        for nombre in (
            "costo_excedente",
            "costo_fijo_contratacion",
            "costo_variable_contratacion",
        ):
            if getattr(self, nombre) < 0:
                raise ValueError(f"El parametro '{nombre}' no puede ser negativo.")

    @classmethod
    def problema_del_enunciado(cls) -> "ParametrosProblema":
        """Devuelve la instancia exacta planteada en el enunciado de la tarea."""
        return cls(
            demanda=(5, 7, 8, 4, 6),
            costo_excedente=300.0,
            costo_fijo_contratacion=400.0,
            costo_variable_contratacion=200.0,
            fuerza_inicial=0,
        )

    @classmethod
    def desde_secuencia(cls, demanda: Sequence[int], **kwargs) -> "ParametrosProblema":
        """Crea los parametros a partir de cualquier secuencia de demandas."""
        return cls(demanda=tuple(demanda), **kwargs)

    # ------------------------------------------------------------------ #
    # Consultas del horizonte
    # ------------------------------------------------------------------ #
    @property
    def n_semanas(self) -> int:
        """Cantidad de etapas (semanas) del horizonte de planeacion."""
        return len(self.demanda)

    @property
    def semanas(self) -> Tuple[int, ...]:
        """Semanas numeradas desde 1 hasta ``n_semanas``."""
        return tuple(range(1, self.n_semanas + 1))

    def _validar_semana(self, semana: int) -> None:
        if not 1 <= semana <= self.n_semanas:
            raise ValueError(
                f"Semana {semana} fuera del horizonte 1..{self.n_semanas}."
            )

    def demanda_semana(self, semana: int) -> int:
        """Demanda b_i de la semana indicada (indice base 1)."""
        self._validar_semana(semana)
        return self.demanda[semana - 1]

    # ------------------------------------------------------------------ #
    # Espacio de estados y decisiones
    # ------------------------------------------------------------------ #
    def cota_superior(self, semana: int) -> int:
        """Mayor demanda desde ``semana`` hasta el final del horizonte.

        Nunca conviene conservar mas trabajadores que la demanda maxima que
        resta, porque el excedente solo agrega costo sin evitar contrataciones.
        """
        self._validar_semana(semana)
        return max(self.demanda[semana - 1 :])

    def decisiones(self, semana: int) -> Tuple[int, ...]:
        """Valores factibles de la decision x_i para la semana indicada."""
        self._validar_semana(semana)
        return tuple(range(self.demanda_semana(semana), self.cota_superior(semana) + 1))

    def estados_entrada(self, semana: int) -> Tuple[int, ...]:
        """Estados posibles al entrar a la semana indicada (x_{i-1})."""
        self._validar_semana(semana)
        if semana == 1:
            return (self.fuerza_inicial,)
        return self.decisiones(semana - 1)
