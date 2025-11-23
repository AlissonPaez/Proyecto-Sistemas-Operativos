# -*- coding: utf-8 -*-
"""
Interfaz Grafica (GUI) para el Simulador de Sistema Operativo
Utiliza Tkinter para crear una interfaz profesional y moderna
"""

import random
import time
import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue

# Anadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Modulo_Procesos.proceso import Proceso
from Modulo_Procesos.planificador import Planificador
from Modulo_Memoria.gestorMemoria import GestorMemoria
from Modulo_Archivos.gestorArchivos import GestorArchivos


class SimuladorGUI:
    """
    Interfaz grafica principal del simulador
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Sistema Operativo")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')

        # Variables de control
        self.algoritmo_var = tk.StringVar(value="RR")
        self.quantum_var = tk.IntVar(value=3)
        self.memoria_var = tk.StringVar(value="FIFO")
        self.simulacion_activa = False
        self.cola_mensajes = queue.Queue()

        # Componentes del sistema
        self.planificador = None
        self.gestor_memoria = None
        self.gestor_archivos = None

        # Configurar estilo
        self.configurar_estilos()

        # Crear interfaz
        self.crear_interfaz()

        # Iniciar actualizacion de mensajes
        self.actualizar_mensajes()

    def configurar_estilos(self):
        """Configura los estilos de la interfaz"""
        style = ttk.Style()
        style.theme_use('clam')

        # Colores
        self.color_fondo = '#2c3e50'
        self.color_panel = '#34495e'
        self.color_acento = '#3498db'
        self.color_exito = '#27ae60'
        self.color_error = '#e74c3c'
        self.color_texto = '#ecf0f1'

        # Estilos personalizados
        style.configure('Title.TLabel',
                       background=self.color_fondo,
                       foreground=self.color_texto,
                       font=('Arial', 16, 'bold'))

        style.configure('Panel.TFrame',
                       background=self.color_panel)

        style.configure('Config.TLabelframe',
                       background=self.color_panel,
                       foreground=self.color_texto,
                       borderwidth=2,
                       relief='groove')

        style.configure('Config.TLabelframe.Label',
                       background=self.color_panel,
                       foreground=self.color_texto,
                       font=('Arial', 10, 'bold'))

        style.configure('Custom.TButton',
                       background=self.color_acento,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Arial', 10, 'bold'))

        style.map('Custom.TButton',
                 background=[('active', '#2980b9')])

    def crear_interfaz(self):
        """Crea los elementos de la interfaz"""

        # Titulo principal
        titulo_frame = tk.Frame(self.root, bg=self.color_fondo, height=60)
        titulo_frame.pack(fill='x', padx=10, pady=10)
        titulo_frame.pack_propagate(False)

        titulo = tk.Label(titulo_frame,
                         text="🖥️ SIMULADOR DE SISTEMA OPERATIVO",
                         font=('Arial', 20, 'bold'),
                         bg=self.color_fondo,
                         fg=self.color_texto)
        titulo.pack(expand=True)

        # Frame principal con dos columnas
        main_frame = tk.Frame(self.root, bg=self.color_fondo)
        main_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Columna izquierda (Configuracion y controles)
        left_frame = tk.Frame(main_frame, bg=self.color_fondo, width=350)
        left_frame.pack(side='left', fill='both', padx=(0, 5))
        left_frame.pack_propagate(False)

        self.crear_panel_configuracion(left_frame)
        self.crear_panel_estado(left_frame)

        # Columna derecha (Visualizacion y logs)
        right_frame = tk.Frame(main_frame, bg=self.color_fondo)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))

        self.crear_panel_visualizacion(right_frame)

    def crear_panel_configuracion(self, parent):
        """Crea el panel de configuracion"""
        config_frame = ttk.LabelFrame(parent, text="⚙️ CONFIGURACION",
                                      style='Config.TLabelframe', padding=15)
        config_frame.pack(fill='x', pady=(0, 10))

        # Algoritmo de planificacion
        tk.Label(config_frame, text="Algoritmo de Planificacion:",
                bg=self.color_panel, fg=self.color_texto,
                font=('Arial', 9)).pack(anchor='w', pady=(0, 5))

        algos = [
            ("Round Robin (RR)", "RR"),
            ("Shortest Job First (SJF)", "SJF"),
            ("Por Prioridad", "PRIORIDAD")
        ]

        for texto, valor in algos:
            rb = tk.Radiobutton(config_frame, text=texto, variable=self.algoritmo_var,
                              value=valor, bg=self.color_panel, fg=self.color_texto,
                              selectcolor=self.color_acento, activebackground=self.color_panel,
                              activeforeground=self.color_texto, font=('Arial', 9),
                              command=self.actualizar_quantum_estado)
            rb.pack(anchor='w', padx=20)

        # Quantum (solo para RR)
        tk.Label(config_frame, text="",
                bg=self.color_panel, fg=self.color_texto).pack(pady=5)

        quantum_frame = tk.Frame(config_frame, bg=self.color_panel)
        quantum_frame.pack(fill='x', pady=5)

        self.quantum_label = tk.Label(quantum_frame, text="Quantum:",
                                     bg=self.color_panel, fg=self.color_texto,
                                     font=('Arial', 9))
        self.quantum_label.pack(side='left')

        self.quantum_spinbox = ttk.Spinbox(quantum_frame, from_=1, to=10,
                                          textvariable=self.quantum_var,
                                          width=10, font=('Arial', 9))
        self.quantum_spinbox.pack(side='left', padx=10)

        # Algoritmo de memoria
        tk.Label(config_frame, text="",
                bg=self.color_panel, fg=self.color_texto).pack(pady=5)

        tk.Label(config_frame, text="Algoritmo de Memoria:",
                bg=self.color_panel, fg=self.color_texto,
                font=('Arial', 9)).pack(anchor='w', pady=(0, 5))

        mems = [
            ("FIFO (First In First Out)", "FIFO"),
            ("LRU (Least Recently Used)", "LRU")
        ]

        for texto, valor in mems:
            rb = tk.Radiobutton(config_frame, text=texto, variable=self.memoria_var,
                              value=valor, bg=self.color_panel, fg=self.color_texto,
                              selectcolor=self.color_acento, activebackground=self.color_panel,
                              activeforeground=self.color_texto, font=('Arial', 9))
            rb.pack(anchor='w', padx=20)

        # Botones de control
        tk.Label(config_frame, text="",
                bg=self.color_panel, fg=self.color_texto).pack(pady=10)

        buttons_frame = tk.Frame(config_frame, bg=self.color_panel)
        buttons_frame.pack(fill='x')

        self.btn_iniciar = tk.Button(buttons_frame, text="▶ INICIAR",
                                     command=self.iniciar_simulacion,
                                     bg=self.color_exito, fg='white',
                                     font=('Arial', 10, 'bold'),
                                     relief='flat', padx=20, pady=10,
                                     cursor='hand2')
        self.btn_iniciar.pack(fill='x', pady=5)

        self.btn_detener = tk.Button(buttons_frame, text="⏹ DETENER",
                                     command=self.detener_simulacion,
                                     bg=self.color_error, fg='white',
                                     font=('Arial', 10, 'bold'),
                                     relief='flat', padx=20, pady=10,
                                     cursor='hand2', state='disabled')
        self.btn_detener.pack(fill='x', pady=5)

        self.btn_limpiar = tk.Button(buttons_frame, text="🗑️ LIMPIAR",
                                     command=self.limpiar_pantalla,
                                     bg='#95a5a6', fg='white',
                                     font=('Arial', 10, 'bold'),
                                     relief='flat', padx=20, pady=10,
                                     cursor='hand2')
        self.btn_limpiar.pack(fill='x', pady=5)

        self.actualizar_quantum_estado()

    def crear_panel_estado(self, parent):
        """Crea el panel de estado actual"""
        estado_frame = ttk.LabelFrame(parent, text="📊 ESTADO DEL SISTEMA",
                                     style='Config.TLabelframe', padding=15)
        estado_frame.pack(fill='both', expand=True)

        # Tiempo actual
        self.tiempo_label = tk.Label(estado_frame, text="Tiempo: 0",
                                     bg=self.color_panel, fg=self.color_texto,
                                     font=('Arial', 12, 'bold'))
        self.tiempo_label.pack(pady=10)

        # CPU
        cpu_frame = tk.Frame(estado_frame, bg=self.color_panel)
        cpu_frame.pack(fill='x', pady=5)

        tk.Label(cpu_frame, text="CPU:", bg=self.color_panel,
                fg=self.color_texto, font=('Arial', 10, 'bold')).pack(anchor='w')

        self.cpu_label = tk.Label(cpu_frame, text="IDLE",
                                 bg=self.color_panel, fg='#f39c12',
                                 font=('Arial', 10))
        self.cpu_label.pack(anchor='w', padx=20)

        # Cola de listos
        listos_frame = tk.Frame(estado_frame, bg=self.color_panel)
        listos_frame.pack(fill='x', pady=5)

        tk.Label(listos_frame, text="Cola Listos:", bg=self.color_panel,
                fg=self.color_texto, font=('Arial', 10, 'bold')).pack(anchor='w')

        self.listos_label = tk.Label(listos_frame, text="[]",
                                    bg=self.color_panel, fg=self.color_texto,
                                    font=('Arial', 9), wraplength=280, justify='left')
        self.listos_label.pack(anchor='w', padx=20)

        # Cola de bloqueados
        bloq_frame = tk.Frame(estado_frame, bg=self.color_panel)
        bloq_frame.pack(fill='x', pady=5)

        tk.Label(bloq_frame, text="Cola Bloqueados:", bg=self.color_panel,
                fg=self.color_texto, font=('Arial', 10, 'bold')).pack(anchor='w')

        self.bloqueados_label = tk.Label(bloq_frame, text="[]",
                                        bg=self.color_panel, fg=self.color_texto,
                                        font=('Arial', 9), wraplength=280, justify='left')
        self.bloqueados_label.pack(anchor='w', padx=20)

        # Metricas
        tk.Label(estado_frame, text="", bg=self.color_panel).pack(pady=5)

        metricas_frame = tk.Frame(estado_frame, bg=self.color_panel)
        metricas_frame.pack(fill='x')

        self.metricas_text = tk.Text(metricas_frame, height=8, width=40,
                                    bg='#1c2833', fg=self.color_texto,
                                    font=('Courier', 9), relief='flat',
                                    padx=10, pady=10)
        self.metricas_text.pack(fill='both', expand=True)
        self.metricas_text.insert('1.0', "Esperando inicio de simulacion...")
        self.metricas_text.config(state='disabled')

    def crear_panel_visualizacion(self, parent):
        """Crea el panel de visualizacion principal"""
        # Notebook con pestanas
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True)

        # Pestana de Log
        log_frame = tk.Frame(notebook, bg=self.color_panel)
        notebook.add(log_frame, text="📝 Log de Eventos")

        self.log_text = scrolledtext.ScrolledText(log_frame,
                                                  bg='#1c2833',
                                                  fg='#00ff00',
                                                  font=('Courier', 9),
                                                  relief='flat',
                                                  padx=10, pady=10)
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.agregar_log("Sistema iniciado. Configurar parametros e iniciar simulacion.", "INFO")

        # Pestana de Memoria
        memoria_frame = tk.Frame(notebook, bg=self.color_panel)
        notebook.add(memoria_frame, text="💾 Memoria")

        self.memoria_canvas = tk.Canvas(memoria_frame, bg='#1c2833',
                                       highlightthickness=0)
        self.memoria_canvas.pack(fill='both', expand=True, padx=5, pady=5)

        # Pestana de Archivos
        archivos_frame = tk.Frame(notebook, bg=self.color_panel)
        notebook.add(archivos_frame, text="📁 Archivos")

        self.archivos_text = scrolledtext.ScrolledText(archivos_frame,
                                                       bg='#1c2833',
                                                       fg=self.color_texto,
                                                       font=('Courier', 10),
                                                       relief='flat',
                                                       padx=10, pady=10)
        self.archivos_text.pack(fill='both', expand=True, padx=5, pady=5)

        # Pestana de Gantt
        gantt_frame = tk.Frame(notebook, bg=self.color_panel)
        notebook.add(gantt_frame, text="📊 Diagrama de Gantt")

        self.gantt_text = scrolledtext.ScrolledText(gantt_frame,
                                                    bg='#1c2833',
                                                    fg=self.color_texto,
                                                    font=('Courier', 9),
                                                    relief='flat',
                                                    padx=10, pady=10)
        self.gantt_text.pack(fill='both', expand=True, padx=5, pady=5)

        # Pestana de Metricas Finales
        metricas_frame = tk.Frame(notebook, bg=self.color_panel)
        notebook.add(metricas_frame, text="📈 Metricas Finales")

        self.metricas_finales_text = scrolledtext.ScrolledText(metricas_frame,
                                                              bg='#1c2833',
                                                              fg=self.color_texto,
                                                              font=('Courier', 10),
                                                              relief='flat',
                                                              padx=10, pady=10)
        self.metricas_finales_text.pack(fill='both', expand=True, padx=5, pady=5)

    def actualizar_quantum_estado(self):
        """Actualiza el estado del spinbox de quantum"""
        if self.algoritmo_var.get() == "RR":
            self.quantum_label.config(state='normal')
            self.quantum_spinbox.config(state='normal')
        else:
            self.quantum_label.config(state='disabled')
            self.quantum_spinbox.config(state='disabled')

    def agregar_log(self, mensaje, tipo="INFO"):
        """Agrega un mensaje al log"""
        self.log_text.config(state='normal')

        timestamp = f"[T{getattr(self, 'tiempo_actual', 0):3d}]"

        if tipo == "INFO":
            color_tag = 'info'
            self.log_text.tag_config('info', foreground='#00ff00')
        elif tipo == "SUCCESS":
            color_tag = 'success'
            self.log_text.tag_config('success', foreground='#27ae60')
        elif tipo == "ERROR":
            color_tag = 'error'
            self.log_text.tag_config('error', foreground='#e74c3c')
        elif tipo == "WARNING":
            color_tag = 'warning'
            self.log_text.tag_config('warning', foreground='#f39c12')
        else:
            color_tag = 'default'
            self.log_text.tag_config('default', foreground='#ecf0f1')

        self.log_text.insert('end', f"{timestamp} [{tipo}] {mensaje}\n", color_tag)
        self.log_text.see('end')
        self.log_text.config(state='disabled')

    def actualizar_visualizacion_memoria(self):
        """Actualiza la visualizacion de la memoria"""
        if not self.gestor_memoria:
            return

        self.memoria_canvas.delete('all')
        width = self.memoria_canvas.winfo_width()
        height = self.memoria_canvas.winfo_height()

        if width <= 1:
            width = 800
        if height <= 1:
            height = 600

        # Titulo
        self.memoria_canvas.create_text(width/2, 30,
                                       text=f"MEMORIA RAM - {self.gestor_memoria.algoritmo_reemplazo}",
                                       fill='white', font=('Arial', 12, 'bold'))

        # Dibujar marcos
        marcos_por_fila = 5
        marco_width = (width - 100) / marcos_por_fila
        marco_height = 60
        start_y = 70

        colores_procesos = {
            1: '#3498db',
            2: '#e74c3c',
            3: '#2ecc71',
            4: '#f39c12',
            None: '#34495e'
        }

        for i in range(self.gestor_memoria.marcos_totales):
            fila = i // marcos_por_fila
            col = i % marcos_por_fila

            x = 50 + col * marco_width
            y = start_y + fila * (marco_height + 20)

            pagina_id = self.gestor_memoria.marcos[i]

            # Determinar proceso
            proceso_id = None
            if pagina_id is not None:
                for id_proc, paginas in self.gestor_memoria.tabla_paginas.items():
                    for pag in paginas:
                        if pag.id_pagina == pagina_id:
                            proceso_id = id_proc
                            break

            color = colores_procesos.get(proceso_id, colores_procesos[None])

            # Dibujar marco
            self.memoria_canvas.create_rectangle(x, y, x + marco_width - 10, y + marco_height,
                                                fill=color, outline='white', width=2)

            # Texto
            texto = f"Marco {i}\n"
            if proceso_id is not None:
                texto += f"P{proceso_id}"
            else:
                texto += "LIBRE"

            self.memoria_canvas.create_text(x + marco_width/2 - 5, y + marco_height/2,
                                          text=texto, fill='white',
                                          font=('Arial', 9, 'bold'))

        # Estadisticas
        stats_y = start_y + ((self.gestor_memoria.marcos_totales // marcos_por_fila) + 1) * (marco_height + 20)
        self.memoria_canvas.create_text(width/2, stats_y + 20,
                                       text=f"Fallos de Pagina: {self.gestor_memoria.fallos_pagina} | Reemplazos: {self.gestor_memoria.reemplazos}",
                                       fill='#f39c12', font=('Arial', 11, 'bold'))

    def actualizar_estado_sistema(self):
        """Actualiza el panel de estado del sistema"""
        if not self.planificador:
            return

        # Actualizar tiempo
        self.tiempo_actual = self.planificador.tiempo_actual
        self.tiempo_label.config(text=f"Tiempo: {self.tiempo_actual}")

        # Actualizar CPU
        if self.planificador.proceso_actual:
            self.cpu_label.config(text=str(self.planificador.proceso_actual),
                                fg='#27ae60')
        else:
            self.cpu_label.config(text="IDLE", fg='#f39c12')

        # Actualizar colas
        listos = [str(p) for p in self.planificador.cola_listos]
        self.listos_label.config(text=str(listos) if listos else "[]")

        bloqueados = [str(p) for p in self.planificador.cola_bloqueados]
        self.bloqueados_label.config(text=str(bloqueados) if bloqueados else "[]")

        # Actualizar metricas
        if self.gestor_memoria and self.gestor_archivos:
            stats_mem = self.gestor_memoria.obtener_estadisticas()
            stats_arch = self.gestor_archivos.obtener_estadisticas()

            metricas_texto = f"""
MEMORIA:
  Marcos ocupados: {stats_mem['marcos_ocupados']}/{stats_mem['marcos_totales']}
  Fallos pagina: {stats_mem['fallos_pagina']}
  Reemplazos: {stats_mem['reemplazos']}

ARCHIVOS:
  Bloqueados: {stats_arch['archivos_bloqueados']}/{stats_arch['archivos_totales']}
  Operaciones: {stats_arch['operaciones_exitosas']}
  Conflictos: {stats_arch['conflictos_totales']}
            """

            self.metricas_text.config(state='normal')
            self.metricas_text.delete('1.0', 'end')
            self.metricas_text.insert('1.0', metricas_texto.strip())
            self.metricas_text.config(state='disabled')

    def actualizar_archivos(self):
        """Actualiza la visualizacion de archivos"""
        if not self.gestor_archivos:
            return

        self.archivos_text.config(state='normal')
        self.archivos_text.delete('1.0', 'end')

        texto = self.gestor_archivos.visualizar_estado()
        self.archivos_text.insert('1.0', texto)
        self.archivos_text.config(state='disabled')

    def limpiar_pantalla(self):
        """Limpia todos los paneles de visualizacion"""
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.config(state='disabled')

        self.archivos_text.config(state='normal')
        self.archivos_text.delete('1.0', 'end')
        self.archivos_text.config(state='disabled')

        self.gantt_text.config(state='normal')
        self.gantt_text.delete('1.0', 'end')
        self.gantt_text.config(state='disabled')

        self.metricas_finales_text.config(state='normal')
        self.metricas_finales_text.delete('1.0', 'end')
        self.metricas_finales_text.config(state='disabled')

        self.memoria_canvas.delete('all')

        self.agregar_log("Pantalla limpiada", "INFO")

    def crear_procesos_ejemplo(self, aleatorio: bool = True, seed: int | None = None):
        """
        Crea procesos de ejemplo.
        Si aleatorio==True genera valores aleatorios para duracion/prioridad/llegada.
        Si seed no es None, se fija la semilla para reproducibilidad.
        """
        if seed is not None:
            random.seed(seed)
        else:
            # Semilla variable para que cada corrida sea distinta
            random.seed(time.time_ns() & 0xFFFFFFFF)

        procesos = []
        num_procs = 4

        for i in range(1, num_procs + 1):
            prioridad = random.randint(1, 5)              # 1..5
            duracion_total = random.randint(4, 14)        # duracion entre 4 y 14
            tiempo_llegada = random.randint(0, 6)         # llegada temprana entre 0 y 6
            memoria_requerida = random.randint(1, 4)      # paginas necesarias
            # Elegir archivos aleatorios (pueden repetirse): tomamos de los archivos conocidos del gestor
            archivos_disponibles = ['config.txt', 'data.db', 'log.txt', 'temp.txt']
            archivos_necesarios = random.sample(archivos_disponibles, random.randint(0, 2))

            p = Proceso(i, prioridad, duracion_total, tiempo_llegada, memoria_requerida, archivos_necesarios)
            procesos.append(p)

        return procesos

    def iniciar_simulacion(self):
        """Inicia la simulacion en un thread separado"""
        if self.simulacion_activa:
            return

        self.simulacion_activa = True
        self.btn_iniciar.config(state='disabled')
        self.btn_detener.config(state='normal')

        # Limpiar pantalla
        self.limpiar_pantalla()

        # Crear thread de simulacion
        thread = threading.Thread(target=self.ejecutar_simulacion, daemon=True)
        thread.start()

    def detener_simulacion(self):
        """Detiene la simulacion"""
        self.simulacion_activa = False
        self.btn_iniciar.config(state='normal')
        self.btn_detener.config(state='disabled')
        self.agregar_log("Simulacion detenida por el usuario", "WARNING")

    def ejecutar_simulacion(self):
        """Ejecuta la simulacion (corre en thread separado)"""
        try:
            algoritmo = self.algoritmo_var.get()
            quantum = self.quantum_var.get()
            algoritmo_memoria = self.memoria_var.get()

            self.cola_mensajes.put(('log', f"Iniciando simulacion: {algoritmo} | Quantum: {quantum} | Memoria: {algoritmo_memoria}", "SUCCESS"))

            # Inicializar componentes
            self.planificador = Planificador(algoritmo=algoritmo, quantum=quantum)
            self.gestor_memoria = GestorMemoria(marcos_totales=6, algoritmo_reemplazo=algoritmo_memoria)
            self.gestor_archivos = GestorArchivos(['config.txt', 'data.db', 'log.txt', 'temp.txt'])

            # Crear y agregar procesos
            procesos = self.crear_procesos_ejemplo(aleatorio=True)
            for proceso in procesos:
                self.planificador.agregar_proceso(proceso)
                self.cola_mensajes.put(('log', f"Proceso P{proceso.id} agregado - Duracion: {proceso.duracion_total}", "INFO"))

            # Ciclo de simulacion
            max_ciclos = 100
            ciclo = 0

            while self.planificador.hay_procesos_activos() and ciclo < max_ciclos and self.simulacion_activa:
                ciclo += 1

                # Sincronizar tiempos
                self.gestor_memoria.tiempo_actual = self.planificador.tiempo_actual
                self.gestor_archivos.tiempo_actual = self.planificador.tiempo_actual

                # Verificar llegadas
                self.planificador.verificar_llegadas()

                # Asignar memoria
                for proceso in list(self.planificador.cola_listos):
                    if proceso.id not in self.gestor_memoria.tabla_paginas:
                        self.gestor_memoria.asignar_memoria(proceso)

                # Ejecutar ciclo
                if self.planificador.ejecutar_ciclo():
                    proceso_actual = self.planificador.proceso_actual

                    if proceso_actual:
                        self.gestor_memoria.acceder_memoria(proceso_actual)

                        # I/O
                        if proceso_actual.necesita_io():
                            archivo_necesario = proceso_actual.obtener_archivo_actual()

                            if archivo_necesario:
                                if self.gestor_archivos.solicitar_acceso(proceso_actual, archivo_necesario):
                                    proceso_actual.realizar_io()
                                    self.gestor_archivos.liberar_archivo(archivo_necesario, proceso_actual)
                                    self.cola_mensajes.put(('log', f"P{proceso_actual.id} accedio a {archivo_necesario}", "SUCCESS"))
                                else:
                                    proceso_actual.archivo_actual = archivo_necesario
                                    self.planificador.bloquear_proceso(proceso_actual)
                                    self.cola_mensajes.put(('log', f"P{proceso_actual.id} bloqueado esperando {archivo_necesario}", "WARNING"))

                # Verificar desbloqueos
                self.gestor_archivos.verificar_desbloqueos_pendientes(self.planificador)

                # Actualizar interfaz periodicamente
                if ciclo % 5 == 0:
                    self.cola_mensajes.put(('actualizar', None, None))

                # Pequena pausa para visualizacion
                import time
                time.sleep(0.1)

            # Liberar memoria
            for proceso in self.planificador.procesos_terminados:
                self.gestor_memoria.liberar_memoria(proceso)

            # Mostrar resultados finales
            self.cola_mensajes.put(('finalizar', None, None))

        except Exception as e:
            self.cola_mensajes.put(('log', f"Error en simulacion: {str(e)}", "ERROR"))
        finally:
            self.simulacion_activa = False
            self.cola_mensajes.put(('detener', None, None))

    def mostrar_resultados_finales(self):
        """Muestra los resultados finales de la simulacion"""
        if not self.planificador:
            return

        # Metricas
        metricas = self.planificador.calcular_metricas()
        stats_mem = self.gestor_memoria.obtener_estadisticas()
        stats_arch = self.gestor_archivos.obtener_estadisticas()

        texto_metricas = f"""
╔══════════════════════════════════════════════════════════════╗
║           METRICAS FINALES DE LA SIMULACION                  ║
╚══════════════════════════════════════════════════════════════╝

[PLANIFICACION DE PROCESOS]
  • Procesos completados:      {metricas['procesos_completados']}
  • Tiempo espera promedio:    {metricas.get('tiempo_espera_promedio', 0):.2f} unidades
  • Tiempo retorno promedio:   {metricas.get('tiempo_retorno_promedio', 0):.2f} unidades
  • Cambios de contexto:       {metricas['cambios_contexto']}

[GESTION DE MEMORIA]
  • Algoritmo:                 {stats_mem['algoritmo']}
  • Marcos totales:            {stats_mem['marcos_totales']}
  • Marcos ocupados:           {stats_mem['marcos_ocupados']}
  • Marcos libres:             {stats_mem['marcos_libres']}
  • Fallos de pagina:          {stats_mem['fallos_pagina']}
  • Reemplazos:                {stats_mem['reemplazos']}

[SISTEMA DE ARCHIVOS]
  • Archivos totales:          {stats_arch['archivos_totales']}
  • Archivos bloqueados:       {stats_arch['archivos_bloqueados']}
  • Archivos libres:           {stats_arch['archivos_libres']}
  • Operaciones exitosas:      {stats_arch['operaciones_exitosas']}
  • Conflictos totales:        {stats_arch['conflictos_totales']}
"""

        self.metricas_finales_text.config(state='normal')
        self.metricas_finales_text.delete('1.0', 'end')
        self.metricas_finales_text.insert('1.0', texto_metricas)
        self.metricas_finales_text.config(state='disabled')

        # Diagrama de Gantt
        gantt = self.planificador.generar_diagrama_gantt()
        self.gantt_text.config(state='normal')
        self.gantt_text.delete('1.0', 'end')
        self.gantt_text.insert('1.0', gantt)
        self.gantt_text.config(state='disabled')

        # Log de archivos
        log_archivos = self.gestor_archivos.obtener_log_completo()
        self.agregar_log("Simulacion completada exitosamente", "SUCCESS")

    def actualizar_mensajes(self):
        """Actualiza la interfaz con mensajes de la cola"""
        try:
            while True:
                mensaje = self.cola_mensajes.get_nowait()
                tipo_msg, contenido, extra = mensaje

                if tipo_msg == 'log':
                    self.agregar_log(contenido, extra)
                elif tipo_msg == 'actualizar':
                    self.actualizar_estado_sistema()
                    self.actualizar_visualizacion_memoria()
                    self.actualizar_archivos()
                elif tipo_msg == 'finalizar':
                    self.mostrar_resultados_finales()
                elif tipo_msg == 'detener':
                    self.btn_iniciar.config(state='normal')
                    self.btn_detener.config(state='disabled')
        except queue.Empty:
            pass

        # Programar siguiente actualizacion
        self.root.after(100, self.actualizar_mensajes)


def main():
    """Funcion principal"""
    root = tk.Tk()
    app = SimuladorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
