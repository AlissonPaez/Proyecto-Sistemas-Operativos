# -*- coding: utf-8 -*-
"""
Demo automatica del simulador - sin interaccion del usuario
"""

import sys
import os

# Anadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Reemplazar input() para automatizar
def mock_input(prompt=""):
    print(prompt + "[AUTOMATICO]")
    return ""

import builtins
builtins.input = mock_input

from main import ejecutar_simulacion, imprimir_banner, limpiar_pantalla

if __name__ == "__main__":
    limpiar_pantalla()
    imprimir_banner()

    print("\n[MODO DEMO AUTOMATICO - Round Robin con FIFO]\n")

    # Ejecutar simulacion automaticamente
    ejecutar_simulacion(
        algoritmo='RR',
        quantum=3,
        algoritmo_memoria='FIFO',
        mostrar_estados=True
    )
