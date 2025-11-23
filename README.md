# Simulador de Sistema Operativo

Proyecto final de Sistemas Operativos que implementa un simulador completo con tres módulos principales:

1. **Módulo de Procesos**: Planificación de procesos con múltiples algoritmos
2. **Módulo de Memoria**: Gestión de memoria con paginación por demanda
3. **Módulo de Archivos**: Control de concurrencia y bloqueo de recursos

## 🎨 Dos Interfaces Disponibles

Este simulador ofrece **dos formas de interactuar**:

### 🖥️ Interfaz de Terminal (CLI)
- Interfaz de línea de comandos con colores
- Ideal para servidores o entornos sin GUI
- Ligera y rápida

### 🎨 Interfaz Gráfica (GUI - Tkinter)
- Interfaz gráfica moderna y profesional
- Visualización en tiempo real
- Múltiples pestañas con información
- **¡RECOMENDADA para presentaciones y aprendizaje!**

## Estructura del Proyecto

```
proyectoFinal/
│
├── Modulo_Procesos/
│   ├── __init__.py
│   └── proceso.py          # Clases Proceso y Planificador
│
├── Modulo_Memoria/
│   ├── __init__.py
│   └── gestorMemoria.py    # Clases Pagina y GestorMemoria
│
├── Modulo_Archivos/
│   ├── __init__.py
│   └── gestorArchivos.py   # Clases RecursoArchivo y GestorArchivos
│
├── main.py                 # Interfaz de terminal (CLI)
├── gui.py                  # Interfaz gráfica (GUI) - Tkinter
├── demo.py                 # Demo automática
├── README.md
├── README_GUI.md           # Documentación de la GUI
├── GUIA_USO.md            # Guía de uso detallada
├── INICIAR_GUI.bat        # Launcher Windows
└── INICIAR_GUI.sh         # Launcher Linux/Mac
```

## Características Implementadas

### Módulo de Procesos

- **Process Control Block (PCB)**: Cada proceso contiene toda la información necesaria
- **Algoritmos de Planificación**:
  - Round Robin (RR)
  - Shortest Job First (SJF)
  - Por Prioridad
- **Estados del proceso**: NUEVO, LISTO, EJECUTANDO, BLOQUEADO, TERMINADO
- **Métricas**: Tiempo de espera, tiempo de retorno, cambios de contexto
- **Diagrama de Gantt**: Visualización gráfica de la ejecución

### Módulo de Memoria

- **Paginación por demanda**: Las páginas se cargan solo cuando se necesitan
- **Algoritmos de reemplazo de páginas**:
  - FIFO (First In First Out)
  - LRU (Least Recently Used)
- **Tabla de páginas**: Por cada proceso
- **Fallos de página**: Contador de page faults
- **Visualización**: Estado actual de los marcos de memoria

### Módulo de Archivos

- **Control de concurrencia**: Implementación de Mutex
- **Bloqueo de recursos**: Solo un proceso puede acceder a un archivo a la vez
- **Cola de espera**: Para procesos que esperan acceso a archivos
- **Registro de conflictos**: Estadísticas de contención de recursos
- **Log de operaciones**: Registro detallado de todas las operaciones de I/O

## Cómo Ejecutar

### Requisitos

- Python 3.7 o superior
- Tkinter (incluido con Python, para GUI)

### 🎨 Interfaz Gráfica (Recomendado)

**Windows:**
```bash
python gui.py
```
O doble clic en `INICIAR_GUI.bat`

**Linux/Mac:**
```bash
python3 gui.py
```

### 🖥️ Interfaz de Terminal

```bash
python main.py
```

### 🎬 Modo Demo (Terminal)

```bash
python demo.py
```

## Configuración

Puedes modificar los parámetros de la simulación en el archivo `main.py`:

```python
ejecutar_simulacion(
    algoritmo='RR',          # Opciones: 'RR', 'SJF', 'PRIORIDAD'
    quantum=3,               # Solo aplica para Round Robin
    algoritmo_memoria='FIFO' # Opciones: 'FIFO', 'LRU'
)
```

### Crear Procesos Personalizados

Modifica la función `crear_procesos_ejemplo()` en `main.py`:

```python
Proceso(
    id=1,                              # ID único del proceso
    prioridad=2,                       # 1=alta, 5=baja
    duracion_total=10,                 # Tiempo total de ejecución
    tiempo_llegada=0,                  # Momento de llegada al sistema
    memoria_requerida=3,               # Número de páginas de memoria
    archivos_necesarios=['config.txt'] # Archivos que usará el proceso
)
```

## Salida del Simulador

El simulador muestra:

1. **Estado periódico** (cada 10 ciclos):
   - Proceso actual en ejecución
   - Cola de procesos listos
   - Cola de procesos bloqueados
   - Estado de la memoria (marcos ocupados/libres)
   - Estado de los archivos (bloqueados/libres)

2. **Métricas finales**:
   - Planificación: procesos completados, tiempos promedio, cambios de contexto
   - Memoria: fallos de página, reemplazos, marcos utilizados
   - Archivos: operaciones exitosas, conflictos, procesos en espera

3. **Diagrama de Gantt**: Visualización temporal de la ejecución de procesos

4. **Log de operaciones**: Registro detallado de todas las operaciones de I/O

## Conceptos de Sistemas Operativos Implementados

- **Multiprogramación**: Varios procesos en memoria simultáneamente
- **Cambio de contexto**: Alternancia entre procesos
- **Planificación de CPU**: Algoritmos RR, SJF y por prioridad
- **Gestión de memoria virtual**: Paginación por demanda
- **Reemplazo de páginas**: FIFO y LRU
- **Sincronización**: Mutex para control de acceso a archivos
- **Bloqueo de procesos**: Por operaciones de I/O
- **Interbloqueo (prevención)**: Mediante liberación ordenada de recursos

## Ejemplo de Salida

```
METRICAS DE PLANIFICACION:
  - Procesos completados: 4
  - Tiempo de espera promedio: 15.5 unidades
  - Tiempo de retorno promedio: 23.75 unidades
  - Cambios de contexto: 12

METRICAS DE MEMORIA:
  - Algoritmo: FIFO
  - Marcos totales: 10
  - Fallos de pagina: 15
  - Reemplazos: 5

METRICAS DE ARCHIVOS:
  - Archivos totales: 4
  - Operaciones exitosas: 8
  - Conflictos totales: 2
```

## Autor

Proyecto de Sistemas Operativos

## Licencia

Este proyecto es de uso académico.
