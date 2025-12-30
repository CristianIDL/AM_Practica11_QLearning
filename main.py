"""
Punto de entrada principal del generador de laberintos.
"""

from src.config_manager import ConfigManager
from src.prints import crear_headline


def main():
    print(crear_headline("GENERADOR DE LABERINTOS"))
    
    # Creamos una instancia de la clase de la configuración
    config = ConfigManager('config/casillas.txt')
    
    # Cargar configuración
    if not config.load_config():
        print("\n¿Quieres crear una configuración por defecto? (s/n): ", end="")
        respuesta = input().lower()
        if respuesta == 's':
            config.create_default_config()
            config.load_config()
        else:
            print("Saliendo del programa...")
            return
    
    print("\nSistema inicializado correctamente :D")

if __name__ == "__main__":
    main()