"""
Punto de entrada principal del generador de laberintos.
"""

import os
from src.config_manager import ConfigManager
from src.prints import crear_headline, clear_screen, show_configuration, show_menu
from src.map_generator import MapGenerator
from src.map_validator import MapValidator

def generate_single_map(config: ConfigManager):
    """Genera un mapa individual con parámetros personalizados."""
    print("\n--- GENERACIÓN DE MAPA INDIVIDUAL ---\n")
    
    try:
        # Solicitar parámetros
        seed_input = input("Semilla (Enter para aleatorio): ").strip()
        seed = int(seed_input) if seed_input else None
        
        wall_density = float(input("Densidad de paredes (0.0 - 0.5) [0.2]: ") or "0.2")
        treasure_count = int(input("Número de tesoros [3]: ") or "3")
        pit_count = int(input("Número de pozos [3]: ") or "3")
        
        # Generar mapa
        generator = MapGenerator(config, seed=seed)
        validator = MapValidator(config)
        
        max_attempts = 100
        attempts = 0
        
        print("\nGenerando mapa válido...")
        
        while attempts < max_attempts:
            map_grid = generator.generate_map(
                wall_density=wall_density,
                treasure_count=treasure_count,
                pit_count=pit_count
            )
            
            if validator.is_valid_map(map_grid):
                print(f"Mapa válido generado (intento {attempts + 1})")
                break
            
            attempts += 1
            generator = MapGenerator(config, seed=None)  # Nueva semilla
        
        if attempts >= max_attempts:
            print("!!! No se pudo generar un mapa válido después de muchos intentos")
            return
        
        # Mostrar mapa
        generator.print_map()
        validator.print_statistics(map_grid)
        
        # Preguntar si desea visualizar el camino
        show_path = input("\n¿Mostrar camino óptimo? (s/n): ").lower()
        if show_path == 's':
            validator.visualize_path(map_grid)
        
        # Preguntar si desea guardar
        save = input("\n¿Guardar mapa? (s/n): ").lower()
        if save == 's':
            filename = input("Nombre del archivo [mapa_custom.txt]: ") or "mapa_custom.txt"
            filepath = f"maps/generated/{filename}"
            generator.save_map(filepath)
        
    except ValueError as e:
        print(f"!!! Error en los parámetros: {e}")
    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario")


def generate_batch_maps(config: ConfigManager):
    """Genera múltiples mapas en lote."""
    print("\n--- GENERACIÓN DE MAPAS EN LOTE ---\n")
    
    try:
        num_maps = int(input("¿Cuántos mapas desea generar?: "))
        wall_density = float(input("Densidad de paredes (0.0 - 0.5) [0.2]: ") or "0.2")
        treasure_count = int(input("Número de tesoros [3]: ") or "3")
        pit_count = int(input("Número de pozos [3]: ") or "3")
        
        validator = MapValidator(config)
        
        print(f"\nGenerando {num_maps} mapas válidos...\n")
        
        successful = 0
        total_attempts = 0
        
        for i in range(num_maps):
            attempts = 0
            max_attempts = 100
            
            while attempts < max_attempts:
                generator = MapGenerator(config, seed=None)
                map_grid = generator.generate_map(
                    wall_density=wall_density,
                    treasure_count=treasure_count,
                    pit_count=pit_count
                )
                
                total_attempts += 1
                
                if validator.is_valid_map(map_grid):
                    filename = f"maps/generated/mapa_{i+1:03d}.txt"
                    generator.save_map(filename)
                    successful += 1
                    print(f"  ✓ Mapa {i+1}/{num_maps} generado (semilla: {generator.seed})")
                    break
                
                attempts += 1
            
            if attempts >= max_attempts:
                print(f"  !!! No se pudo generar el mapa {i+1}")
        
        print(f"\n{'='*50}")
        print(f"Resultados:")
        print(f"  Mapas generados: {successful}/{num_maps}")
        print(f"  Intentos totales: {total_attempts}")
        print(f"  Tasa de éxito: {successful/total_attempts*100:.1f}%")
        print(f"{'='*50}")
        
    except ValueError as e:
        print(f"!!! Error en los parámetros: {e}")
    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario")


def validate_existing_map(config: ConfigManager):
    """Valida un mapa existente."""
    print("\n--- VALIDACIÓN DE MAPA ---\n")
    
    filename = input("Nombre del archivo (en maps/generated/): ")
    filepath = f"maps/generated/{filename}"
    
    if not os.path.exists(filepath):
        print(f"!!! No se encontró el archivo: {filepath}")
        return
    
    try:
        # Leer el mapa
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.rstrip('\n') for line in f.readlines()]
        
        # Convertir a numpy array
        import numpy as np
        map_grid = np.array([list(line) for line in lines])
        
        # Validar
        validator = MapValidator(config)
        
        print("\nValidando mapa...\n")
        is_valid = validator.is_valid_map(map_grid, verbose=True)
        
        if is_valid:
            validator.print_statistics(map_grid)
            
            show_path = input("\n¿Mostrar camino óptimo? (s/n): ").lower()
            if show_path == 's':
                validator.visualize_path(map_grid)
        
    except Exception as e:
        print(f"!!! Error al procesar el archivo: {e}")

def main():
    """Función principal del programa."""

    print(crear_headline("GENERADOR DE LABERINTOS"))

    # Inicializar configuración
    config = ConfigManager('config/casillas.txt')
    
    # Crear configuración por defecto si no existe
    if not os.path.exists(config.config_path):
        print("Creando archivo de configuración por defecto...")
        config.create_default_config()
    
    # Cargar configuración
    if not config.load_config():
        print("\n!!! Error al cargar la configuración")
        print("Verifique el archivo config/casillas.txt")
        return
    
    # Crear directorios necesarios
    os.makedirs('maps/generated', exist_ok=True)
    os.makedirs('data/datasets', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Bucle principal
    while True:
        show_menu()
        
        try:
            opcion = input("\nSeleccione una opción: ").strip()
            
            if opcion == '1':
                generate_single_map(config)
            elif opcion == '2':
                generate_batch_maps(config)
            elif opcion == '3':
                validate_existing_map(config)
            elif opcion == '4':
                show_configuration(config)
            elif opcion == '5':
                print("\n¡Hasta luego!\n")
                break
            else:
                print("\n!!! Opción no válida")
            
            input("\nPresione Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n\n¡Hasta luego!\n")
            break
        except Exception as e:
            print(f"\n!!! Error inesperado: {e}")
            input("\nPresione Enter para continuar...")


if __name__ == "__main__":
    main()