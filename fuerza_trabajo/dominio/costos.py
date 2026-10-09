"""Calculo de los costos de una semana del modelo de fuerza de trabajo."""

from __future__ import annotations

from dataclasses import dataclass

from fuerza_trabajo.dominio.parametros import ParametrosProblema


@dataclass(frozen=True)
class DesgloseCosto:
    """Costo de una semana separado en sus componentes.

    Permite mostrar el paso a paso sin recalcular nada en la capa de reportes.
    """

    semana: int
    fuerza_previa: int
    fuerza: int
    demanda: int
    trabajadores_excedentes: int
    trabajadores_contratados: int
    costo_excedente: float
    costo_contratacion_fijo: float
    costo_contratacion_variable: float

    @property
    def hubo_contratacion(self) -> bool:
        """Indica si la semana requirio contratar personal nuevo."""
        return self.trabajadores_contratados > 0

    @property
    def costo_contratacion(self) -> float:
        """Costo total de contratacion (parte fija mas parte variable)."""
        return self.costo_contratacion_fijo + self.costo_contratacion_variable

    @property
    def total(self) -> float:
        """Costo inmediato C_i(x_{i-1}, x_i) de la semana."""
        return self.costo_excedente + self.costo_contratacion


class CalculadoraCostos:
    """Evalua C_i(x_{i-1}, x_i) para el modelo de tamano de fuerza de trabajo.

    C_i(x_{i-1}, x_i) = c_e * (x_i - b_i)
                        + [c_f + c_v * (x_i - x_{i-1})]   si x_i > x_{i-1}
                        + 0                               si x_i <= x_{i-1}
    """

    def __init__(self, parametros: ParametrosProblema) -> None:
        self.parametros = parametros

    # ------------------------------------------------------------------ #
    # Componentes
    # ------------------------------------------------------------------ #
    def trabajadores_excedentes(self, semana: int, fuerza: int) -> int:
        """Trabajadores conservados por encima de la demanda de la semana."""
        demanda = self.parametros.demanda_semana(semana)
        excedente = fuerza - demanda
        if excedente < 0:
            raise ValueError(
                f"La fuerza de trabajo {fuerza} no cubre la demanda {demanda} "
                f"de la semana {semana}."
            )
        return excedente

    def trabajadores_contratados(self, fuerza_previa: int, fuerza: int) -> int:
        """Trabajadores nuevos necesarios para pasar de x_(i-1) a x_i."""
        return max(0, fuerza - fuerza_previa)

    # ------------------------------------------------------------------ #
    # Costo de la semana
    # ------------------------------------------------------------------ #
    def desglose(self, semana: int, fuerza_previa: int, fuerza: int) -> DesgloseCosto:
        """Devuelve el costo de la semana separado en sus componentes."""
        excedentes = self.trabajadores_excedentes(semana, fuerza)
        contratados = self.trabajadores_contratados(fuerza_previa, fuerza)
        hay_contratacion = contratados > 0

        return DesgloseCosto(
            semana=semana,
            fuerza_previa=fuerza_previa,
            fuerza=fuerza,
            demanda=self.parametros.demanda_semana(semana),
            trabajadores_excedentes=excedentes,
            trabajadores_contratados=contratados,
            costo_excedente=self.parametros.costo_excedente * excedentes,
            costo_contratacion_fijo=(
                self.parametros.costo_fijo_contratacion if hay_contratacion else 0.0
            ),
            costo_contratacion_variable=(
                self.parametros.costo_variable_contratacion * contratados
            ),
        )

    def costo(self, semana: int, fuerza_previa: int, fuerza: int) -> float:
        """Costo inmediato de la semana (atajo sobre el desglose)."""
        return self.desglose(semana, fuerza_previa, fuerza).total
