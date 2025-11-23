from typing import Optional
import sys
import os

# Anadir el directorio padre al path para importar modulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Modulo_Procesos.proceso import Proceso
from Modulo_Memoria.memoria import Pagina


class GestorMemoria:
    """
    Memory Management Unit (MMU) - Gestiona la memoria virtual y fisica
    """

    def __init__(self, marcos_totales: int = 6, algoritmo_reemplazo: str = 'FIFO'):
        """
        Inicializa el gestor de memoria
        """
        self.marcos_totales = marcos_totales
        self.marcos = [None] * marcos_totales  # None = marco libre
        self.tabla_paginas = {}  # {id_proceso: [Pagina, Pagina, ...]}
        self.algoritmo_reemplazo = algoritmo_reemplazo.upper()
        self.fallos_pagina = 0
        self.reemplazos = 0
        self.tiempo_actual = 0
        self.siguiente_id_pagina = 0
        self.log_operaciones = []

    def asignar_memoria(self, proceso: Proceso) -> bool:
        """
        Asigna memoria a un proceso (paginacion por demanda)
        """
        if proceso.id in self.tabla_paginas:
            return True  # Ya tiene paginas asignadas

        # Crear paginas para el proceso
        paginas = []
        for i in range(proceso.memoria_requerida):
            pagina = Pagina(self.siguiente_id_pagina, proceso.id)
            self.siguiente_id_pagina += 1
            paginas.append(pagina)

        self.tabla_paginas[proceso.id] = paginas
        proceso.paginas_asignadas = [p.id_pagina for p in paginas]

        # Cargar al menos una pagina inicial
        self.cargar_pagina(paginas[0])

        self.log_operaciones.append(f"T{self.tiempo_actual}: Asignadas {len(paginas)} paginas a P{proceso.id}")

        return True

    def cargar_pagina(self, pagina: Pagina) -> bool:
        """
        Carga una pagina en un marco de memoria fisica
        """
        if pagina.cargada:
            # Actualizar tiempo de acceso (para LRU)
            pagina.ultimo_acceso = self.tiempo_actual
            return True

        # Buscar marco libre
        marco_libre = self.buscar_marco_libre()

        if marco_libre is not None:
            # Hay espacio disponible
            self.marcos[marco_libre] = pagina.id_pagina
            pagina.cargada = True
            pagina.marco_asignado = marco_libre
            pagina.tiempo_carga = self.tiempo_actual
            pagina.ultimo_acceso = self.tiempo_actual
            self.fallos_pagina += 1
            self.log_operaciones.append(f"T{self.tiempo_actual}: Cargada {pagina} en marco {marco_libre}")
            return True
        else:
            # No hay espacio - reemplazar pagina
            return self.reemplazar_pagina(pagina)

    def buscar_marco_libre(self) -> Optional[int]:
        """
        Busca un marco de memoria libre
        """
        for i, marco in enumerate(self.marcos):
            if marco is None:
                return i
        return None

    def reemplazar_pagina(self, nueva_pagina: Pagina) -> bool:
        """
        Reemplaza una pagina segun el algoritmo configurado
        """
        if self.algoritmo_reemplazo == 'FIFO':
            return self._reemplazar_fifo(nueva_pagina)
        elif self.algoritmo_reemplazo == 'LRU':
            return self._reemplazar_lru(nueva_pagina)
        return False

    def _reemplazar_fifo(self, nueva_pagina: Pagina) -> bool:
        """
        Reemplazo FIFO - First In First Out
        """
        # Encontrar la pagina mas antigua
        pagina_victima = None
        tiempo_min = float('inf')
        marco_victima = None

        for marco_idx, pagina_id in enumerate(self.marcos):
            if pagina_id is not None:
                # Buscar esta pagina en todas las tablas
                for paginas in self.tabla_paginas.values():
                    for pagina in paginas:
                        if pagina.id_pagina == pagina_id:
                            if pagina.tiempo_carga < tiempo_min:
                                tiempo_min = pagina.tiempo_carga
                                pagina_victima = pagina
                                marco_victima = marco_idx
                            break

        if pagina_victima:
            # Reemplazar
            self.log_operaciones.append(
                f"T{self.tiempo_actual}: REEMPLAZO FIFO - Sacada {pagina_victima} de marco {marco_victima}"
            )
            pagina_victima.cargada = False
            pagina_victima.marco_asignado = None

            self.marcos[marco_victima] = nueva_pagina.id_pagina
            nueva_pagina.cargada = True
            nueva_pagina.marco_asignado = marco_victima
            nueva_pagina.tiempo_carga = self.tiempo_actual
            nueva_pagina.ultimo_acceso = self.tiempo_actual

            self.fallos_pagina += 1
            self.reemplazos += 1

            self.log_operaciones.append(
                f"T{self.tiempo_actual}: Cargada {nueva_pagina} en marco {marco_victima}"
            )

            return True

        return False

    def _reemplazar_lru(self, nueva_pagina: Pagina) -> bool:
        """
        Reemplazo LRU - Least Recently Used
        """
        # Encontrar la pagina menos recientemente usada
        pagina_victima = None
        tiempo_min = float('inf')
        marco_victima = None

        for marco_idx, pagina_id in enumerate(self.marcos):
            if pagina_id is not None:
                # Buscar esta pagina en todas las tablas
                for paginas in self.tabla_paginas.values():
                    for pagina in paginas:
                        if pagina.id_pagina == pagina_id:
                            if pagina.ultimo_acceso < tiempo_min:
                                tiempo_min = pagina.ultimo_acceso
                                pagina_victima = pagina
                                marco_victima = marco_idx
                            break

        if pagina_victima:
            # Reemplazar
            self.log_operaciones.append(
                f"T{self.tiempo_actual}: REEMPLAZO LRU - Sacada {pagina_victima} de marco {marco_victima}"
            )
            pagina_victima.cargada = False
            pagina_victima.marco_asignado = None

            self.marcos[marco_victima] = nueva_pagina.id_pagina
            nueva_pagina.cargada = True
            nueva_pagina.marco_asignado = marco_victima
            nueva_pagina.tiempo_carga = self.tiempo_actual
            nueva_pagina.ultimo_acceso = self.tiempo_actual

            self.fallos_pagina += 1
            self.reemplazos += 1

            self.log_operaciones.append(
                f"T{self.tiempo_actual}: Cargada {nueva_pagina} en marco {marco_victima}"
            )

            return True

        return False

    def acceder_memoria(self, proceso: Proceso):
        """
        Simula un acceso a memoria por parte de un proceso
        """
        if proceso.id not in self.tabla_paginas:
            return

        # Acceder a una pagina aleatoria del proceso
        paginas = self.tabla_paginas[proceso.id]
        if paginas:
            import random
            pagina = random.choice(paginas)
            if not pagina.cargada:
                self.cargar_pagina(pagina)
            else:
                pagina.ultimo_acceso = self.tiempo_actual

    def liberar_memoria(self, proceso: Proceso):
        """
        Libera la memoria ocupada por un proceso
        """
        if proceso.id not in self.tabla_paginas:
            return

        paginas = self.tabla_paginas[proceso.id]
        for pagina in paginas:
            if pagina.cargada and pagina.marco_asignado is not None:
                self.marcos[pagina.marco_asignado] = None

        del self.tabla_paginas[proceso.id]
        self.log_operaciones.append(f"T{self.tiempo_actual}: Liberada memoria de P{proceso.id}")

    def visualizar_estado(self) -> str:
        """
        Genera una visualizacion del estado actual de la memoria
        """
        resultado = "\nESTADO DE MEMORIA:\n"
        resultado += "+" + "-" * 78 + "+\n"

        marcos_por_linea = 4
        for i in range(0, self.marcos_totales, marcos_por_linea):
            resultado += "| "
            for j in range(i, min(i + marcos_por_linea, self.marcos_totales)):
                if self.marcos[j] is None:
                    resultado += "[LIBRE] "
                else:
                    # Buscar a que proceso pertenece
                    pagina_id = self.marcos[j]
                    proceso_id = None
                    for id_proc, paginas in self.tabla_paginas.items():
                        for pag in paginas:
                            if pag.id_pagina == pagina_id:
                                proceso_id = id_proc
                                break
                    resultado += f"[P{proceso_id}] " if proceso_id is not None else f"[?{pagina_id}] "
            resultado += " " * (75 - len(resultado.split('\n')[-1])) + "|\n"

        resultado += "+" + "-" * 78 + "+\n"
        resultado += f"Fallos de pagina: {self.fallos_pagina} | Reemplazos: {self.reemplazos}\n"

        return resultado

    def hay_marco_libre(self) -> bool:
        """
        Verifica si hay marcos libres
        """
        return None in self.marcos

    def obtener_estadisticas(self) -> dict:
        """
        Obtiene estadisticas de uso de memoria
        """
        marcos_ocupados = sum(1 for m in self.marcos if m is not None)

        return {
            'marcos_totales': self.marcos_totales,
            'marcos_ocupados': marcos_ocupados,
            'marcos_libres': self.marcos_totales - marcos_ocupados,
            'fallos_pagina': self.fallos_pagina,
            'reemplazos': self.reemplazos,
            'algoritmo': self.algoritmo_reemplazo
        }
