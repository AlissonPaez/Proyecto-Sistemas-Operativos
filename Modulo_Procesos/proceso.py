# -*- coding: utf-8 -*-
"""
Modulo de Procesos - Clase Proceso
Representa un proceso en el sistema (Process Control Block)
"""

from typing import List, Optional

class Proceso:
    """
    Process Control Block (PCB) - Representa un proceso en el sistema
    """

    def __init__(self, id: int, prioridad: int, duracion_total: int,
                 tiempo_llegada: int, memoria_requerida: int,
                 archivos_necesarios: List[str]):
        """
        Inicializa un nuevo proceso

        Args:
            id: Identificador unico del proceso
            prioridad: Prioridad (1=alta, 5=baja)
            duracion_total: Tiempo total de ejecucion requerido
            tiempo_llegada: Momento en que llega el proceso
            memoria_requerida: Cantidad de paginas de memoria necesarias
            archivos_necesarios: Lista de archivos que usara el proceso
        """
        self.id = id
        self.estado = 'NUEVO'  # NUEVO, LISTO, EJECUTANDO, BLOQUEADO, TERMINADO
        self.prioridad = prioridad
        self.duracion_total = duracion_total
        self.tiempo_restante = duracion_total
        self.tiempo_llegada = tiempo_llegada
        self.tiempo_inicio = None
        self.tiempo_finalizacion = None
        self.tiempo_espera = 0
        self.tiempo_retorno = 0
        self.memoria_requerida = memoria_requerida
        self.archivos_necesarios = archivos_necesarios.copy()
        self.archivos_usados = []
        self.paginas_asignadas = []
        self.archivo_actual = None
        self.tiempo_io_restante = 0

    def ejecutar(self, quantum: int) -> int:
        """
        Ejecuta el proceso durante un quantum de tiempo

        Args:
            quantum: Tiempo maximo de ejecucion

        Returns:
            Tiempo realmente ejecutado
        """
        tiempo_ejecutado = min(quantum, self.tiempo_restante)
        self.tiempo_restante -= tiempo_ejecutado

        if self.tiempo_restante == 0:
            self.estado = 'TERMINADO'

        return tiempo_ejecutado

    def necesita_io(self) -> bool:
        """
        Determina si el proceso necesita realizar operaciones de I/O

        Returns:
            True si necesita acceder a un archivo
        """
        # Cada 30% del tiempo de ejecucion, necesita I/O
        if self.tiempo_restante > 0 and len(self.archivos_necesarios) > 0:
            progreso = (self.duracion_total - self.tiempo_restante) / self.duracion_total
            if progreso > 0.3 and len(self.archivos_usados) < len(self.archivos_necesarios):
                return True
        return False

    def obtener_archivo_actual(self) -> Optional[str]:
        """
        Obtiene el siguiente archivo que el proceso necesita usar
        """
        if len(self.archivos_usados) < len(self.archivos_necesarios):
            return self.archivos_necesarios[len(self.archivos_usados)]
        return None

    def realizar_io(self):
        """
        Marca que el proceso ha usado su archivo actual
        """
        archivo = self.obtener_archivo_actual()
        if archivo and archivo not in self.archivos_usados:
            self.archivos_usados.append(archivo)

    def __str__(self) -> str:
        return f"P{self.id}[{self.estado[:3]}]"

    def __repr__(self) -> str:
        return self.__str__()
