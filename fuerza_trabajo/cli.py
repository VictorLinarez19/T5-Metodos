"""Interfaz de linea de comandos: une dominio, solucionador y reportes."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional, Sequence

from fuerza_trabajo.dominio.parametros import ParametrosProblema
from fuerza_trabajo.reportes.exportador import ExportadorTexto
from fuerza_trabajo.reportes.formateador import FormateadorReporte
from fuerza_trabajo.solucionador.programacion_dinamica import SolucionadorFuerzaTrabajo

RUTA_SALIDA_POR_DEFECTO = Path("salidas") / "salidas_programa.txt"


def construir_parser() -> argparse.ArgumentParser:
    """Define los argumentos aceptados por el programa."""
    parser = argparse.ArgumentParser(
        prog="fuerza_trabajo",
        description=(
            "Resuelve el modelo de tamano de la fuerza de trabajo por "
            "programacion dinamica y muestra todas las salidas paso por paso."
        ),
    )
    parser.add_argument(
        "--demanda",
        nargs="+",
        type=int,
        metavar="b",
        default=[5, 7, 8, 4, 6],
        help="Trabajadores requeridos por semana (por omision: 5 7 8 4 6).",
    )
    parser.add_argument(
        "--costo-excedente",
        type=float,
        default=300.0,
        metavar="c_e",
        help="Costo por trabajador excedente por semana (por omision: 300).",
    )
    parser.add_argument(
        "--costo-fijo",
        type=float,
        default=400.0,
        metavar="c_f",
        help="Costo fijo por contratar en una semana (por omision: 400).",
    )
    parser.add_argument(
        "--costo-variable",
        type=float,
        default=200.0,
        metavar="c_v",
        help="Costo por cada trabajador contratado (por omision: 200).",
    )
    parser.add_argument(
        "--fuerza-inicial",
        type=int,
        default=0,
        metavar="x_0",
        help="Trabajadores disponibles antes de la semana 1 (por omision: 0).",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=RUTA_SALIDA_POR_DEFECTO,
        metavar="RUTA",
        help=(
            "Archivo .txt donde se guardan las salidas "
            f"(por omision: {RUTA_SALIDA_POR_DEFECTO.as_posix()})."
        ),
    )
    parser.add_argument(
        "--sin-archivo",
        action="store_true",
        help="Solo muestra el reporte en pantalla, sin guardarlo en disco.",
    )
    return parser


def parametros_desde_argumentos(argumentos: argparse.Namespace) -> ParametrosProblema:
    """Traduce los argumentos de la linea de comandos al modelo de dominio."""
    return ParametrosProblema(
        demanda=tuple(argumentos.demanda),
        costo_excedente=argumentos.costo_excedente,
        costo_fijo_contratacion=argumentos.costo_fijo,
        costo_variable_contratacion=argumentos.costo_variable,
        fuerza_inicial=argumentos.fuerza_inicial,
    )


def generar_reporte(parametros: ParametrosProblema) -> str:
    """Resuelve el problema y devuelve el reporte paso a paso."""
    solucion = SolucionadorFuerzaTrabajo(parametros).resolver()
    return FormateadorReporte(solucion).reporte_completo()


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Punto de entrada del programa."""
    argumentos = construir_parser().parse_args(argv)

    try:
        parametros = parametros_desde_argumentos(argumentos)
    except ValueError as error:
        print(f"Error en los datos de entrada: {error}")
        return 2

    reporte = generar_reporte(parametros)
    print(reporte)

    if not argumentos.sin_archivo:
        destino = ExportadorTexto().guardar(reporte, argumentos.salida)
        mensajes: List[str] = [
            f"Salidas guardadas en: {destino.resolve()}",
        ]
        print("\n".join(mensajes))

    return 0
