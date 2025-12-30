''' 
src.prints.py: Módulo para no tener que repetir prints a lo menso
'''

import os
from src.config_manager import ConfigManager

def crear_headline(titulo, caracter="= = ", ancho=10):
    """
    Crea un headline y lo devuelve como string.
    
    Returns:
        String formateado con el headline
    """
    separador = caracter * ancho
    return f"{separador}\n{titulo}\n{separador}"

def clear_screen():
    """Limpia la pantalla de la consola."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_configuration(config: ConfigManager):
    """Muestra la configuración actual."""
    print("\n--- CONFIGURACIÓN ACTUAL ---\n")
    config._print_mapping()
    print("\nRuta del archivo: " + config.config_path)
    input("\nPresione Enter para continuar...")

def show_menu():
    """Muestra el menú principal."""
    print("\n" + "="*50)
    print("  GENERADOR DE LABERINTOS - Q-LEARNING")
    print("="*50)
    print("\n1. Generar un mapa individual")
    print("2. Generar múltiples mapas (lote)")
    print("3. Validar un mapa existente")
    print("4. Configuración")
    print("5. Salir")
    print("\n" + "="*50)