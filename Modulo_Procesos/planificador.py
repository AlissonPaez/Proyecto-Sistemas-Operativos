# -*- coding: utf-8 -*-

from collections import deque
from typing import Optional
import sys
import os

# Anadir el directorio padre al path para importar modulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Modulo_Procesos.proceso import Proceso


class Planificador:

    def __init__(self, algoritmo: str = 'RR', quantum: int = 3, gestor_archivos=None):
        """
        Inicializa el planificador
        """
        self.cola_listos = deque()
        self.cola_bloqueados = deque()
        self.proceso_actual = None
        self.algoritmo = algoritmo.upper()
        self.quantum = quantum
        self.tiempo_actual = 0
        self.procesos_terminados = []
        self.todos_procesos = []
        self.quantum_restante = 0
        self.metricas = {
            'tiempo_espera_total': 0,
            'tiempo_retorno_total': 0,
            'cambios_contexto': 0,
            'procesos_completados': 0
        }
        self.historial_ejecucion = []  # Para diagrama de Gantt
        self.gestor_archivos = gestor_archivos

    def agregar_proceso(self, proceso: Proceso):
        """
        Anade un proceso al planificador
        """
        self.todos_procesos.append(proceso)
        if proceso.tiempo_llegada <= self.tiempo_actual:
            proceso.estado = 'LISTO'
            self.cola_listos.append(proceso)

    def verificar_llegadas(self):
        """
        Verifica si hay procesos nuevos que deben entrar a la cola de listos
        """
        for proceso in self.todos_procesos:
            if proceso.estado == 'NUEVO' and proceso.tiempo_llegada <= self.tiempo_actual:
                proceso.estado = 'LISTO'
                self.cola_listos.append(proceso)

    def seleccionar_siguiente(self) -> Optional[Proceso]:
        """
        Selecciona el siguiente proceso a ejecutar segun el algoritmo activo
        """
        if not self.cola_listos:
            return None

        if self.algoritmo == 'RR':
            return self._round_robin()
        elif self.algoritmo == 'SJF':
            return self._sjf()
        elif self.algoritmo == 'PRIORIDAD':
            return self._prioridad()

        return None

    def _round_robin(self) -> Optional[Proceso]:
        """
        Implementacion de Round Robin
        """
        if self.proceso_actual and self.quantum_restante > 0:
            return self.proceso_actual

        # Cambio de contexto
        if self.proceso_actual:
            if self.proceso_actual.estado == 'EJECUTANDO':
                self.proceso_actual.estado = 'LISTO'
                self.cola_listos.append(self.proceso_actual)
            self.metricas['cambios_contexto'] += 1

        if self.cola_listos:
            proceso = self.cola_listos.popleft()
            proceso.estado = 'EJECUTANDO'
            if proceso.tiempo_inicio is None:
                proceso.tiempo_inicio = self.tiempo_actual
            self.proceso_actual = proceso
            self.quantum_restante = self.quantum
            return proceso

        return None

    def _sjf(self) -> Optional[Proceso]:

        if self.proceso_actual and self.proceso_actual.estado == 'EJECUTANDO':
            return self.proceso_actual

        if not self.cola_listos:
            return None

        lista_procesos = list(self.cola_listos)
        proceso_min = min(lista_procesos, key=lambda p: p.tiempo_restante)

        self.cola_listos.remove(proceso_min)

        if self.proceso_actual != proceso_min:
            if self.proceso_actual:
                self.metricas['cambios_contexto'] += 1
            self.proceso_actual = proceso_min

        proceso_min.estado = 'EJECUTANDO'
        if proceso_min.tiempo_inicio is None:
            proceso_min.tiempo_inicio = self.tiempo_actual

        return proceso_min

    def _prioridad(self) -> Optional[Proceso]:
        if self.proceso_actual and self.proceso_actual.estado == 'EJECUTANDO':
            return self.proceso_actual

        if not self.cola_listos:
            return None

        lista_procesos = list(self.cola_listos)
        proceso_max = min(lista_procesos, key=lambda p: p.prioridad)

        self.cola_listos.remove(proceso_max)

        if self.proceso_actual != proceso_max:
            if self.proceso_actual:
                self.metricas['cambios_contexto'] += 1
            self.proceso_actual = proceso_max

        proceso_max.estado = 'EJECUTANDO'
        if proceso_max.tiempo_inicio is None:
            proceso_max.tiempo_inicio = self.tiempo_actual

        return proceso_max


    def ejecutar_ciclo(self) -> bool:
        """
        Ejecuta un ciclo de reloj del planificador
        """
        self.tiempo_actual += 1

        # Sincronizar tiempo con el gestor de archivos si existe
        if self.gestor_archivos is not None:
            self.gestor_archivos.tiempo_actual = self.tiempo_actual

        self.verificar_llegadas()

        proceso = self.seleccionar_siguiente()

        if proceso:
            # Registrar para diagrama de Gantt
            self.historial_ejecucion.append((self.tiempo_actual, proceso.id))

            # Si el proceso necesita acceder a un archivo, solicitar acceso antes de ejecutar
            archivo_req = getattr(proceso, 'archivo_actual', None)
            if archivo_req:
                if self.gestor_archivos is not None:
                    acceso = self.gestor_archivos.solicitar_acceso(proceso, archivo_req)
                    if not acceso:
                        # pasar a bloqueados; el gestor ya puso el proceso en la cola de espera del archivo
                        self.bloquear_proceso(proceso)
                        # intentar desbloqueos pendientes del gestor (opcional aquí o al final del tick)
                        if self.gestor_archivos is not None:
                            self.gestor_archivos.verificar_desbloqueos_pendientes(self)
                        return True

                    # si obtuvo acceso, limpiar marca y continuar ejecución
                    proceso.archivo_actual = None

            # Ejecutar el proceso
            proceso.ejecutar(1)
            self.quantum_restante -= 1

            # Actualizar tiempos de espera de otros procesos
            for p in self.cola_listos:
                p.tiempo_espera += 1

            # Verificar si el proceso termino
            if proceso.estado == 'TERMINADO':
                # liberar cualquier archivo que pudiera tener
                if self.gestor_archivos is not None and getattr(proceso, 'archivo_actual', None) is None:
                    # si el proceso era propietario de algún archivo, liberarlo
                    # (requiere que el proceso tenga info del archivo actual o list)
                    pass
                proceso.tiempo_finalizacion = self.tiempo_actual
                proceso.tiempo_retorno = proceso.tiempo_finalizacion - proceso.tiempo_llegada
                self.procesos_terminados.append(proceso)
                self.proceso_actual = None
                self.quantum_restante = 0
                self.metricas['procesos_completados'] += 1

                # Después de terminar, intentar desbloquear procesos pendientes
                if self.gestor_archivos is not None:
                    self.gestor_archivos.verificar_desbloqueos_pendientes(self)

                return True

            # Al final del tick, verificar desbloqueos pendientes en el gestor
            if self.gestor_archivos is not None:
                self.gestor_archivos.verificar_desbloqueos_pendientes(self)

            return True

        return False

    def bloquear_proceso(self, proceso: Proceso):
        """
        Bloquea un proceso (por I/O)

        Args:
            proceso: Proceso a bloquear
        """
        proceso.estado = 'BLOQUEADO'
        self.cola_bloqueados.append(proceso)
        if self.proceso_actual == proceso:
            self.proceso_actual = None
            self.quantum_restante = 0

    def desbloquear_proceso(self, proceso: Proceso):
        """
        Desbloquea un proceso y lo pone en cola de listos

        Args:
            proceso: Proceso a desbloquear
        """
        if proceso in self.cola_bloqueados:
            self.cola_bloqueados.remove(proceso)
        proceso.estado = 'LISTO'
        self.cola_listos.append(proceso)

    def hay_procesos_activos(self) -> bool:
        """
        Verifica si aun hay procesos activos en el sistema

        Returns:
            True si hay procesos pendientes
        """
        procesos_activos = len([p for p in self.todos_procesos if p.estado != 'TERMINADO'])
        return procesos_activos > 0

    def calcular_metricas(self) -> dict:
        """:
            Diccionario con metricas calculadas
        """
        if not self.procesos_terminados:
            return self.metricas

        tiempo_espera_promedio = sum(p.tiempo_espera for p in self.procesos_terminados) / len(self.procesos_terminados)
        tiempo_retorno_promedio = sum(p.tiempo_retorno for p in self.procesos_terminados) / len(self.procesos_terminados)

        self.metricas['tiempo_espera_promedio'] = round(tiempo_espera_promedio, 2)
        self.metricas['tiempo_retorno_promedio'] = round(tiempo_retorno_promedio, 2)

        return self.metricas

    def generar_diagrama_gantt(self) -> str:
        """
        Genera un diagrama de Gantt en formato texto
        """
        if not self.historial_ejecucion:
            return "No hay historial de ejecucion"

        gantt = "\n" + "="*80 + "\n"
        gantt += "DIAGRAMA DE GANTT\n"
        gantt += "="*80 + "\n\n"

        # Agrupar ejecuciones consecutivas del mismo proceso
        agrupado = []
        tiempo_inicio = self.historial_ejecucion[0][0]
        proceso_actual = self.historial_ejecucion[0][1]

        for i in range(1, len(self.historial_ejecucion)):
            tiempo, proceso = self.historial_ejecucion[i]
            if proceso != proceso_actual:
                agrupado.append((tiempo_inicio, tiempo - 1, proceso_actual))
                tiempo_inicio = tiempo
                proceso_actual = proceso

        # Anadir el ultimo
        agrupado.append((tiempo_inicio, self.historial_ejecucion[-1][0], proceso_actual))

        # Generar visualizacion
        for inicio, fin, proceso_id in agrupado:
            duracion = fin - inicio + 1
            gantt += f"T{inicio:3d}-{fin:3d} | P{proceso_id} | " + "#" * duracion + "\n"

        gantt += "\n" + "="*80 + "\n"

        return gantt
