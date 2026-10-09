"""Utilidades de formato de texto reutilizadas por el reporte."""

from __future__ import annotations

from typing import List

ANCHO = 88


def dinero(valor: float) -> str:
    """Formatea un monto como moneda sin decimales: 3300 -> '$3,300'."""
    return f"${valor:,.0f}"


def entero(valor: float) -> str:
    """Formatea un numero entero con separador de miles."""
    return f"{valor:,.0f}"


def trabajadores(cantidad: int) -> str:
    """Concuerda el sustantivo en numero: 1 -> '1 trabajador'."""
    return f"{cantidad} trabajador" if cantidad == 1 else f"{cantidad} trabajadores"


def linea(caracter: str = "-", ancho: int = ANCHO) -> str:
    """Devuelve una linea separadora del ancho indicado."""
    return caracter * ancho


def centrar(texto: str, ancho: int = ANCHO) -> str:
    """Centra el texto en el ancho indicado."""
    return texto.center(ancho)


def titulo(texto: str, caracter: str = "=", ancho: int = ANCHO) -> List[str]:
    """Bloque de titulo centrado entre dos lineas separadoras."""
    return [linea(caracter, ancho), centrar(texto.upper(), ancho), linea(caracter, ancho)]


def subtitulo(texto: str, ancho: int = ANCHO) -> List[str]:
    """Bloque de subtitulo alineado a la izquierda y subrayado."""
    return [texto, linea("-", min(ancho, max(len(texto), 3)))]


def sangria(texto: str, nivel: int = 1, paso: int = 2) -> str:
    """Aplica sangria de ``nivel * paso`` espacios a una linea de texto."""
    return f"{' ' * (nivel * paso)}{texto}"
