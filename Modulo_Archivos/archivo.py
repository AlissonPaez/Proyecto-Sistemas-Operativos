# -*- coding: utf-8 -*-
"""
Modulo de Archivos - Clase RecursoArchivo
Representa un archivo del sistema con control de acceso
"""

from collections import deque


class RecursoArchivo:
    """
    Representa un archivo del sistema con control de acceso
    """

    def __init__(self, nombre: str):
        self.nombre = nombre
        self.bloqueado = False
        self.proceso_propietario = None
        self.cola_espera = deque()
        self.veces_usado = 0
        self.conflictos = 0

    def __str__(self) -> str:
        estado = f"P{self.proceso_propietario}" if self.bloqueado else "LIBRE"
        return f"{self.nombre}[{estado}]"

    def __repr__(self) -> str:
        return self.__str__()
