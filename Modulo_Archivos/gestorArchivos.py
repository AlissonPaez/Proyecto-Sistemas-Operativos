from typing import Optional
import sys
import os

# Anadir el directorio padre al path para importar modulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Modulo_Procesos.proceso import Proceso
from Modulo_Archivos.archivo import RecursoArchivo


class GestorArchivos:

    def __init__(self, nombres_archivos: list):
        
        self.archivos = {}
        for nombre in nombres_archivos:
            self.archivos[nombre] = RecursoArchivo(nombre)

        self.log_operaciones = []
        self.conflictos_totales = 0
        self.operaciones_exitosas = 0
        self.tiempo_actual = 0

    def solicitar_acceso(self, proceso: Proceso, nombre_archivo: str) -> bool:
    
        if nombre_archivo not in self.archivos:
            self.log_operaciones.append(
                f"T{self.tiempo_actual}: ERROR - P{proceso.id} solicita archivo inexistente: {nombre_archivo}"
            )
            return False

        archivo = self.archivos[nombre_archivo]

        if not archivo.bloqueado:
            # Archivo libre - asignar
            archivo.bloqueado = True
            archivo.proceso_propietario = proceso.id
            archivo.veces_usado += 1
            self.operaciones_exitosas += 1

            self.log_operaciones.append(
                f"T{self.tiempo_actual}: OK - P{proceso.id} obtuvo acceso a {nombre_archivo}"
            )
            return True
        else:
            # Archivo ocupado - anadir a cola de espera
            if proceso.id not in [p.id for p in archivo.cola_espera]:
                archivo.cola_espera.append(proceso)
                archivo.conflictos += 1
                self.conflictos_totales += 1

                self.log_operaciones.append(
                    f"T{self.tiempo_actual}: CONFLICTO - P{proceso.id} espera por {nombre_archivo} (ocupado por P{archivo.proceso_propietario})"
                )
            return False

    def liberar_archivo(self, nombre_archivo: str, proceso: Proceso) -> Optional[Proceso]:
        """
        Libera un archivo y lo asigna al siguiente en cola
        """
        if nombre_archivo not in self.archivos:
            return None

        archivo = self.archivos[nombre_archivo]

        # Verificar que el proceso sea el propietario
        if archivo.proceso_propietario != proceso.id:
            self.log_operaciones.append(
                f"T{self.tiempo_actual}: ERROR - P{proceso.id} intenta liberar {nombre_archivo} sin ser propietario"
            )
            return None

        self.log_operaciones.append(
            f"T{self.tiempo_actual}: P{proceso.id} libero {nombre_archivo}"
        )

        # Liberar el archivo
        archivo.bloqueado = False
        archivo.proceso_propietario = None

        # Asignar al siguiente en cola
        if archivo.cola_espera:
            siguiente_proceso = archivo.cola_espera.popleft()
            archivo.bloqueado = True
            archivo.proceso_propietario = siguiente_proceso.id
            archivo.veces_usado += 1

            self.log_operaciones.append(
                f"T{self.tiempo_actual}: -> {nombre_archivo} asignado a P{siguiente_proceso.id} (de cola de espera)"
            )

            return siguiente_proceso

        return None

    def esta_disponible(self, nombre_archivo: str) -> bool:
        """
        Verifica si un archivo esta disponible
        """
        if nombre_archivo not in self.archivos:
            return False
        return not self.archivos[nombre_archivo].bloqueado

    def obtener_proceso_propietario(self, nombre_archivo: str) -> Optional[int]:
        """
        Obtiene el ID del proceso propietario de un archivo
        """
        if nombre_archivo not in self.archivos:
            return None

        archivo = self.archivos[nombre_archivo]
        return archivo.proceso_propietario if archivo.bloqueado else None

    def registrar_operacion(self, tipo: str, proceso: Proceso, nombre_archivo: str, exito: bool):
        """
        Registra una operacion en el log
        """
        estado = "EXITOSA" if exito else "BLOQUEADA"
        self.log_operaciones.append(
            f"T{self.tiempo_actual}: {tipo} - P{proceso.id} en {nombre_archivo} - {estado}"
        )

    def visualizar_estado(self) -> str:
        """
        Genera una visualizacion del estado de los archivos
        """
        resultado = "\n" + "="*80 + "\n"
        resultado += "ESTADO ACTUAL DE LOS ARCHIVOS\n"
        resultado += "="*80 + "\n\n"

        for nombre, archivo in self.archivos.items():
            resultado += f"[ARCHIVO] {nombre}\n"
            resultado += "-" * 80 + "\n"

            # Estado y propietario
            if archivo.bloqueado:
                resultado += f"  Estado:             BLOQUEADO por Proceso P{archivo.proceso_propietario}\n"
            else:
                resultado += f"  Estado:             LIBRE\n"

            # Procesos en espera
            if archivo.cola_espera:
                procesos_esperando = [f"P{p.id}" for p in archivo.cola_espera]
                resultado += f"  Procesos esperando: {len(archivo.cola_espera)} -> {', '.join(procesos_esperando)}\n"
            else:
                resultado += f"  Procesos esperando: 0\n"

            # Estadísticas del archivo
            resultado += f"  Veces usado:        {archivo.veces_usado}\n"
            resultado += f"  Conflictos:         {archivo.conflictos}\n"
            resultado += "\n"

        # Resumen global
        resultado += "=" * 80 + "\n"
        resultado += "RESUMEN GLOBAL\n"
        resultado += "=" * 80 + "\n"
        resultado += f"  Conflictos totales:       {self.conflictos_totales}\n"
        resultado += f"  Operaciones exitosas:     {self.operaciones_exitosas}\n"

        archivos_bloqueados = sum(1 for a in self.archivos.values() if a.bloqueado)
        procesos_esperando_total = sum(len(a.cola_espera) for a in self.archivos.values())

        resultado += f"  Archivos bloqueados:      {archivos_bloqueados}/{len(self.archivos)}\n"
        resultado += f"  Procesos esperando total: {procesos_esperando_total}\n"
        resultado += "=" * 80 + "\n"

        # Últimas 10 operaciones
        if self.log_operaciones:
            resultado += "\nULTIMAS OPERACIONES:\n"
            resultado += "-" * 80 + "\n"
            ultimas = self.log_operaciones[-10:] if len(self.log_operaciones) > 10 else self.log_operaciones
            for op in ultimas:
                resultado += f"  {op}\n"
            resultado += "-" * 80 + "\n"

        return resultado

    def obtener_estadisticas(self) -> dict:
        """
        Obtiene estadisticas del sistema de archivos
        """
        archivos_bloqueados = sum(1 for a in self.archivos.values() if a.bloqueado)
        procesos_esperando = sum(len(a.cola_espera) for a in self.archivos.values())

        return {
            'archivos_totales': len(self.archivos),
            'archivos_bloqueados': archivos_bloqueados,
            'archivos_libres': len(self.archivos) - archivos_bloqueados,
            'conflictos_totales': self.conflictos_totales,
            'operaciones_exitosas': self.operaciones_exitosas,
            'procesos_esperando': procesos_esperando
        }

    def obtener_log_completo(self) -> str:
        """
        Obtiene el log completo de operaciones
        """
        if not self.log_operaciones:
            return "No hay operaciones registradas"

        resultado = "\n" + "="*80 + "\n"
        resultado += "LOG DE OPERACIONES DE ARCHIVOS\n"
        resultado += "="*80 + "\n\n"

        for operacion in self.log_operaciones:
            resultado += operacion + "\n"

        resultado += "\n" + "="*80 + "\n"

        return resultado

    def verificar_desbloqueos_pendientes(self, planificador) -> list:
        """
        Verifica si hay procesos que pueden ser desbloqueados
        """
        procesos_desbloqueados = []

        for proceso in list(planificador.cola_bloqueados):
            archivo_necesario = proceso.archivo_actual

            if archivo_necesario and archivo_necesario in self.archivos:
                archivo = self.archivos[archivo_necesario]

                # Si el archivo esta libre o el proceso esta en la cola
                if not archivo.bloqueado:
                    if self.solicitar_acceso(proceso, archivo_necesario):
                        proceso.archivo_actual = None
                        planificador.desbloquear_proceso(proceso)
                        procesos_desbloqueados.append(proceso)

        return procesos_desbloqueados
