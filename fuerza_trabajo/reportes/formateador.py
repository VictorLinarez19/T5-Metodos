"""Armado del reporte paso a paso de la solucion."""

from __future__ import annotations

from typing import List

from fuerza_trabajo.dominio.costos import DesgloseCosto
from fuerza_trabajo.dominio.entidades import (
    Alternativa,
    EstadoResuelto,
    EtapaResuelta,
    Solucion,
)
from fuerza_trabajo.reportes.formatos import (
    centrar,
    dinero,
    linea,
    sangria,
    subtitulo,
    titulo,
    trabajadores,
)
from fuerza_trabajo.reportes.tablas import construir_tabla


class FormateadorReporte:
    """Convierte una :class:`Solucion` en el reporte de texto completo."""

    def __init__(self, solucion: Solucion) -> None:
        self.solucion = solucion
        self.parametros = solucion.parametros

    # ------------------------------------------------------------------ #
    # Reporte completo
    # ------------------------------------------------------------------ #
    def reporte_completo(self) -> str:
        """Devuelve todo el reporte como una sola cadena de texto."""
        lineas: List[str] = []
        for bloque in (
            self.encabezado(),
            self.datos_problema(),
            self.formulacion(),
            self.espacio_estados(),
            self.etapas(),
            self.politica_optima(),
            self.resumen(),
        ):
            lineas.extend(bloque)
            lineas.append("")
        return "\n".join(lineas).rstrip() + "\n"

    # ------------------------------------------------------------------ #
    # Secciones
    # ------------------------------------------------------------------ #
    def encabezado(self) -> List[str]:
        """Portada del reporte."""
        return [
            linea("="),
            centrar("UNIVERSIDAD JOSE ANTONIO PAEZ"),
            centrar("FACULTAD DE INGENIERIA"),
            centrar("ESCUELA DE INGENIERIA EN COMPUTACION"),
            "",
            centrar("MODELO DE TAMANO DE LA FUERZA DE TRABAJO"),
            centrar("Solucion por Programacion Dinamica (recursion hacia atras)"),
            linea("="),
        ]

    def datos_problema(self) -> List[str]:
        """Enunciado y datos de entrada del problema."""
        lineas = titulo("1. datos del problema")
        lineas.append("")
        lineas.append(
            "Un contratista estima el tamano de la fuerza de trabajo necesaria durante"
        )
        lineas.append(
            f"las siguientes {self.parametros.n_semanas} semanas. Conservar mano de obra"
            " excedente cuesta"
        )
        lineas.append(
            f"{dinero(self.parametros.costo_excedente)} por trabajador por semana, y"
            " contratar en cualquier semana"
        )
        lineas.append(
            f"incurre en un costo fijo de"
            f" {dinero(self.parametros.costo_fijo_contratacion)} mas"
            f" {dinero(self.parametros.costo_variable_contratacion)} por trabajador."
        )
        lineas.append("")

        lineas.extend(subtitulo("Demanda de trabajadores por semana (b_i)"))
        lineas.extend(
            construir_tabla(
                ["Semana i", *[str(semana) for semana in self.parametros.semanas]],
                [
                    [
                        "Demanda b_i",
                        *[
                            str(self.parametros.demanda_semana(semana))
                            for semana in self.parametros.semanas
                        ],
                    ]
                ],
                alineaciones=["<", *[">"] * self.parametros.n_semanas],
            )
        )
        lineas.append("")

        lineas.extend(subtitulo("Parametros de costo"))
        lineas.extend(
            construir_tabla(
                ["Parametro", "Simbolo", "Valor"],
                [
                    [
                        "Costo por trabajador excedente por semana",
                        "c_e",
                        dinero(self.parametros.costo_excedente),
                    ],
                    [
                        "Costo fijo por contratar en una semana",
                        "c_f",
                        dinero(self.parametros.costo_fijo_contratacion),
                    ],
                    [
                        "Costo variable por trabajador contratado",
                        "c_v",
                        dinero(self.parametros.costo_variable_contratacion),
                    ],
                    [
                        "Fuerza de trabajo inicial",
                        "x_0",
                        f"{self.parametros.fuerza_inicial} trabajadores",
                    ],
                ],
                alineaciones=["<", "^", ">"],
            )
        )
        return lineas

    def formulacion(self) -> List[str]:
        """Definicion de etapas, estados, decisiones y ecuacion recursiva."""
        n = self.parametros.n_semanas
        lineas = titulo("2. formulacion del modelo de programacion dinamica")
        lineas.extend(
            [
                "",
                "Etapa   i        : la semana i, con i = 1, 2, ..., " f"{n}.",
                "Estado  x_(i-1)  : trabajadores disponibles al terminar la semana"
                " anterior.",
                "Decision x_i     : trabajadores que se conservan en la semana i,"
                " con x_i >= b_i.",
                "",
                "Costo inmediato de la semana i:",
                "",
                sangria("C_i(x_(i-1), x_i) = c_e * (x_i - b_i) + H(x_(i-1), x_i)", 2),
                "",
                sangria("donde  H(x_(i-1), x_i) = c_f + c_v * (x_i - x_(i-1))"
                        "   si x_i >  x_(i-1)", 2),
                sangria("       H(x_(i-1), x_i) = 0"
                        "                            si x_i <= x_(i-1)", 2),
                "",
                "Ecuacion recursiva (hacia atras):",
                "",
                sangria(f"f_{n}(x_{n - 1}) = min  C_{n}(x_{n - 1}, x_{n})", 2),
                sangria(f"           x_{n} >= b_{n}", 2),
                "",
                sangria("f_i(x_(i-1)) = min  [ C_i(x_(i-1), x_i)"
                        " + f_(i+1)(x_i) ]", 2),
                sangria("              x_i >= b_i", 2),
                "",
                "Cota superior del estado: nunca conviene conservar mas trabajadores"
                " que la",
                "demanda maxima que resta, es decir x_i <= max(b_i, ..., b_n).",
            ]
        )
        return lineas

    def espacio_estados(self) -> List[str]:
        """Tabla con los estados y decisiones factibles de cada etapa."""
        lineas = titulo("3. espacio de estados y decisiones")
        lineas.append("")
        filas = []
        for semana in self.parametros.semanas:
            filas.append(
                [
                    str(semana),
                    str(self.parametros.demanda_semana(semana)),
                    self._conjunto(self.parametros.estados_entrada(semana)),
                    self._conjunto(self.parametros.decisiones(semana)),
                ]
            )
        lineas.extend(
            construir_tabla(
                ["Etapa i", "b_i", "Estados x_(i-1)", "Decisiones x_i"],
                filas,
                alineaciones=["^", "^", "<", "<"],
            )
        )
        return lineas

    def etapas(self) -> List[str]:
        """Desarrollo paso a paso de todas las etapas, en orden de resolucion."""
        lineas = titulo("4. desarrollo de la recursion (de la ultima semana a la primera)")
        for etapa in reversed(self.solucion.etapas):
            lineas.append("")
            lineas.extend(self.etapa(etapa))
        return lineas

    def etapa(self, etapa: EtapaResuelta) -> List[str]:
        """Desarrollo detallado de una etapa: cada estado y cada alternativa."""
        es_ultima = etapa.semana == self.parametros.n_semanas
        lineas = [
            linea("-"),
            f"ETAPA {etapa.semana}  (semana {etapa.semana})   demanda"
            f" b_{etapa.semana} = {etapa.demanda}",
            linea("-"),
            f"Decisiones factibles x_{etapa.semana}:"
            f" {self._conjunto(etapa.decisiones)}",
            f"Estados de entrada x_{etapa.semana - 1}:"
            f" {self._conjunto(etapa.estados_entrada)}",
        ]
        if es_ultima:
            lineas.append(
                f"Ultima etapa: no hay costo futuro, por lo que"
                f" f_{etapa.semana + 1}(x_{etapa.semana}) = $0."
            )
        lineas.append("")
        lineas.append("Evaluacion de cada combinacion estado-decision:")

        for estado in etapa.estados:
            lineas.append("")
            lineas.extend(self.estado(estado))

        lineas.append("")
        lineas.extend(subtitulo(f"Tabla resumen de la etapa {etapa.semana}"))
        lineas.extend(self.tabla_etapa(etapa))
        return lineas

    def estado(self, estado: EstadoResuelto) -> List[str]:
        """Paso a paso de un estado: formulas de cada alternativa y el minimo."""
        semana = estado.semana
        lineas = [
            sangria(
                f"Estado x_{semana - 1} = {estado.fuerza_previa}"
                f"  (se entra a la semana {semana} con {estado.fuerza_previa}"
                " trabajadores)",
                1,
            )
        ]

        for alternativa in estado.alternativas:
            lineas.extend(self.alternativa(alternativa))

        lineas.append(
            sangria(
                f"=> f_{semana}({estado.fuerza_previa}) ="
                f" {dinero(estado.valor_optimo)}"
                f"   con  x_{semana}* = {estado.decision_optima}"
                f"   (minimo entre"
                f" {', '.join(dinero(a.costo_total) for a in estado.alternativas)})",
                2,
            )
        )
        return lineas

    def alternativa(self, alternativa: Alternativa) -> List[str]:
        """Formulas desarrolladas de una alternativa (una decision x_i)."""
        semana = alternativa.semana
        desglose = alternativa.desglose
        etiqueta_costo = (
            f"C_{semana}({alternativa.fuerza_previa}, {alternativa.fuerza})"
        )

        if semana < self.parametros.n_semanas:
            cierre = sangria(
                f"total = {etiqueta_costo} + f_{semana + 1}({alternativa.fuerza}) ="
                f" {dinero(desglose.total)} +"
                f" {dinero(alternativa.costo_futuro)} ="
                f" {dinero(alternativa.costo_total)}",
                4,
            )
        else:
            cierre = sangria(
                f"total = {etiqueta_costo} = {dinero(alternativa.costo_total)}"
                f"   (ultima etapa: sin costo futuro)",
                4,
            )

        return [
            sangria(f"x_{semana} = {alternativa.fuerza}:", 2),
            sangria(f"contratacion: {self._formula_contratacion(desglose)}", 4),
            sangria(f"excedente   : {self._formula_excedente(desglose)}", 4),
            sangria(
                f"{etiqueta_costo} ="
                f" {dinero(desglose.costo_excedente)} +"
                f" {dinero(desglose.costo_contratacion)} ="
                f" {dinero(desglose.total)}",
                4,
            ),
            cierre,
        ]

    def tabla_etapa(self, etapa: EtapaResuelta) -> List[str]:
        """Tabla clasica de la etapa: C_i + f_(i+1) para cada estado y decision."""
        semana = etapa.semana
        encabezados = [f"x_{semana - 1}"]
        encabezados += [
            f"x_{semana} = {decision}" for decision in etapa.decisiones
        ]
        encabezados += [f"f_{semana}(x_{semana - 1})", f"x_{semana}*"]

        filas = []
        for estado in etapa.estados:
            fila: List[object] = [str(estado.fuerza_previa)]
            for decision in etapa.decisiones:
                alternativa = estado.alternativa(decision)
                marca = "*" if decision == estado.decision_optima else " "
                fila.append(f"{dinero(alternativa.costo_total)}{marca}")
            fila.append(dinero(estado.valor_optimo))
            fila.append(str(estado.decision_optima))
            filas.append(fila)

        lineas = construir_tabla(
            encabezados,
            filas,
            alineaciones=["^", *[">"] * len(etapa.decisiones), ">", "^"],
        )
        lineas.append("(*) decision optima de cada estado")
        return lineas

    def politica_optima(self) -> List[str]:
        """Recuperacion hacia adelante de la politica optima."""
        lineas = titulo("5. recuperacion de la politica optima (hacia adelante)")
        lineas.append("")
        lineas.append(
            f"Se parte de x_0 = {self.parametros.fuerza_inicial} y en cada etapa se"
            " toma la decision x_i*"
        )
        lineas.append("que el paso anterior tabulo para el estado alcanzado:")
        lineas.append("")

        for decision in self.solucion.decisiones:
            lineas.append(
                sangria(
                    f"Semana {decision.semana}: estado"
                    f" x_{decision.semana - 1} = {decision.fuerza_previa}"
                    f"  ->  x_{decision.semana}* = {decision.fuerza}"
                    f"   (costo de la semana {dinero(decision.costo_semana)},"
                    f" acumulado {dinero(decision.costo_acumulado)})",
                    1,
                )
            )

        lineas.append("")
        lineas.extend(subtitulo("Plan optimo de contratacion"))
        filas = []
        for decision in self.solucion.decisiones:
            desglose = decision.desglose
            filas.append(
                [
                    str(decision.semana),
                    str(decision.demanda),
                    str(decision.fuerza),
                    str(desglose.trabajadores_contratados),
                    str(desglose.trabajadores_excedentes),
                    dinero(desglose.costo_contratacion),
                    dinero(desglose.costo_excedente),
                    dinero(decision.costo_semana),
                    dinero(decision.costo_acumulado),
                ]
            )
        lineas.extend(
            construir_tabla(
                [
                    "Semana",
                    "b_i",
                    "x_i*",
                    "Contrata",
                    "Exced.",
                    "C. contrat.",
                    "C. exced.",
                    "C. semana",
                    "Acumulado",
                ],
                filas,
                alineaciones=["^", "^", "^", "^", "^", ">", ">", ">", ">"],
            )
        )
        return lineas

    def resumen(self) -> List[str]:
        """Resumen final, verificacion del costo y conclusion."""
        solucion = self.solucion
        plan = ", ".join(str(valor) for valor in solucion.plan)
        detalle = " + ".join(
            dinero(decision.costo_semana) for decision in solucion.decisiones
        )
        if len(solucion.decisiones) == 1:
            detalle = ""
        lineas = titulo("6. solucion optima")
        lineas.extend(
            [
                "",
                f"Tamano optimo de la fuerza de trabajo: ({plan})",
                "",
                sangria(
                    "Costo total = "
                    + (f"{detalle} = " if detalle else "")
                    + dinero(solucion.costo_total),
                    1,
                ),
                "",
            ]
        )
        lineas.extend(
            construir_tabla(
                ["Concepto", "Monto"],
                [
                    ["Costo por mano de obra excedente", dinero(solucion.costo_total_excedente)],
                    ["Costo por contrataciones", dinero(solucion.costo_total_contratacion)],
                    ["COSTO TOTAL MINIMO", dinero(solucion.costo_total)],
                ],
                alineaciones=["<", ">"],
            )
        )
        lineas.append("")
        semanas_contrata = [
            decision.semana
            for decision in solucion.decisiones
            if decision.desglose.hubo_contratacion
        ]
        lineas.append(
            "Se contrata personal en las semanas: "
            + (", ".join(str(s) for s in semanas_contrata) if semanas_contrata else "ninguna")
            + "."
        )
        lineas.append(
            "En las demas semanas el excedente se conserva o la plantilla se reduce"
        )
        lineas.append("sin incurrir en costo de contratacion.")
        lineas.append(linea("="))
        return lineas

    # ------------------------------------------------------------------ #
    # Auxiliares
    # ------------------------------------------------------------------ #
    @staticmethod
    def _conjunto(valores) -> str:
        """Representa una coleccion de enteros como conjunto: '{5, 6, 7}'."""
        return "{" + ", ".join(str(valor) for valor in valores) + "}"

    def _formula_contratacion(self, desglose: DesgloseCosto) -> str:
        """Formula desarrollada del costo de contratacion de una semana."""
        if not desglose.hubo_contratacion:
            return (
                f"x_{desglose.semana} = {desglose.fuerza} <="
                f" x_{desglose.semana - 1} = {desglose.fuerza_previa}, no se contrata"
                " -> $0"
            )
        return (
            f"{trabajadores(desglose.trabajadores_contratados)}"
            f" ({desglose.fuerza} - {desglose.fuerza_previa});"
            f" {dinero(self.parametros.costo_fijo_contratacion)} +"
            f" {dinero(self.parametros.costo_variable_contratacion)} *"
            f" {desglose.trabajadores_contratados} ="
            f" {dinero(desglose.costo_contratacion)}"
        )

    def _formula_excedente(self, desglose: DesgloseCosto) -> str:
        """Formula desarrollada del costo de mano de obra excedente."""
        return (
            f"{trabajadores(desglose.trabajadores_excedentes)}"
            f" ({desglose.fuerza} - {desglose.demanda});"
            f" {dinero(self.parametros.costo_excedente)} *"
            f" {desglose.trabajadores_excedentes} ="
            f" {dinero(desglose.costo_excedente)}"
        )
