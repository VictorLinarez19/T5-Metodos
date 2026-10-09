"""Programa principal.

Modelo de tamano de la fuerza de trabajo resuelto con Programacion Dinamica.

Uso:
    python main.py
    python main.py --demanda 5 7 8 4 6 --salida salidas/salidas_programa.txt
    python main.py --sin-archivo
"""

from fuerza_trabajo.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
