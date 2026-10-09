"""Construccion de tablas de texto con ancho de columna automatico."""

from __future__ import annotations

from typing import List, Optional, Sequence

SEPARADOR = " | "


def _anchos(encabezados: Sequence[str], filas: Sequence[Sequence[object]]) -> List[int]:
    """Ancho necesario de cada columna segun su contenido mas largo."""
    anchos = [len(str(encabezado)) for encabezado in encabezados]
    for fila in filas:
        if len(fila) != len(encabezados):
            raise ValueError(
                "Cada fila debe tener la misma cantidad de celdas que encabezados."
            )
        for indice, celda in enumerate(fila):
            anchos[indice] = max(anchos[indice], len(str(celda)))
    return anchos


def _formatear_fila(
    celdas: Sequence[object], anchos: Sequence[int], alineaciones: Sequence[str]
) -> str:
    """Formatea una fila aplicando ancho y alineacion por columna."""
    partes = [
        f"{str(celda):{alineacion}{ancho}}"
        for celda, ancho, alineacion in zip(celdas, anchos, alineaciones)
    ]
    return SEPARADOR.join(partes).rstrip()


def construir_tabla(
    encabezados: Sequence[str],
    filas: Sequence[Sequence[object]],
    alineaciones: Optional[Sequence[str]] = None,
) -> List[str]:
    """Devuelve las lineas de una tabla de texto.

    ``alineaciones`` admite los especificadores de formato de Python
    (``'<'`` izquierda, ``'^'`` centro, ``'>'`` derecha); por omision se
    alinea a la derecha, que es lo adecuado para columnas numericas.
    """
    anchos = _anchos(encabezados, filas)
    if alineaciones is None:
        alineaciones = [">"] * len(encabezados)
    elif len(alineaciones) != len(encabezados):
        raise ValueError("Debe indicarse una alineacion por columna.")

    lineas = [
        _formatear_fila(encabezados, anchos, ["^"] * len(encabezados)),
        "-+-".join("-" * ancho for ancho in anchos),
    ]
    lineas.extend(_formatear_fila(fila, anchos, alineaciones) for fila in filas)
    return lineas
