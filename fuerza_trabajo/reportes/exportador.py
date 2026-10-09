"""Exportacion del reporte a un archivo de texto."""

from __future__ import annotations

from pathlib import Path


class ExportadorTexto:
    """Guarda el reporte en un archivo .txt codificado en UTF-8."""

    def __init__(self, codificacion: str = "utf-8") -> None:
        self.codificacion = codificacion

    def guardar(self, contenido: str, ruta: Path | str) -> Path:
        """Escribe ``contenido`` en ``ruta`` creando la carpeta si no existe."""
        destino = Path(ruta)
        if destino.parent and not destino.parent.exists():
            destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(contenido, encoding=self.codificacion)
        return destino
