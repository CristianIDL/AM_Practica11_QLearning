"""
Generador de Dungeons para Q-Learning
Interfaz principal para generación de habitaciones 18x18

Autor: [Tu nombre]
Fecha: Enero 2025
"""

import os
from src.config_manager import ConfigManager
from src.room_generator import RoomGenerator
from src.dungeon_manager import DungeonManager
from src.room_validator import RoomValidator


def show_menu():
    """Muestra el menú principal."""
    print("\n" + "="*60)
    print("  GENERADOR DE DUNGEONS - Q-LEARNING")
    print("  Habitaciones: 18x18 (16x16 interior)")
    print("="*60)
    print("\n1. Generar habitación individual")
    print("2. Generar dungeon completo (12 habitaciones)")
    print("3. Validar una habitación existente")
    print("4. Ver configuración")
    print("5. Salir")
    print("\n" + "="*60)


def generate_single_room(config: ConfigManager):
    """Genera una habitación individual."""
    print("\n--- GENERACIÓN DE HABITACIÓN INDIVIDUAL ---\n")
    
    try:
        room_id = int(input("ID de habitación (1-12): "))
        
        if not (1 <= room_id <= 12):
            print("✗ ID debe estar entre 1 y 12")
            return
        
        # Configurar según el tipo de habitación
        if room_id == 1:
            print("\nHabitación 1 (inicial): S aleatorio")
            direccion_salida = 'DERECHA'
            posicion_entrada = None
        elif room_id == 12:
            print("\nHabitación 12 (final): Incluye G")
            direccion_salida = None
            entrada_str = input("Posición de entrada (1-16) [8]: ") or "8"
            posicion_entrada = int(entrada_str)
        else:
            print("\nHabitación intermedia")
            direcciones = {'1': 'DERECHA', '2': 'ABAJO', '3': 'IZQUIERDA', '4': 'ARRIBA'}
            print("Dirección de salida:")
            print("  1. DERECHA")
            print("  2. ABAJO")
            print("  3. IZQUIERDA")
            print("  4. ARRIBA")
            dir_choice = input("Seleccione (1-4): ")
            direccion_salida = direcciones.get(dir_choice, 'DERECHA')
            
            entrada_str = input("Posición de entrada (1-16) [8]: ") or "8"
            posicion_entrada = int(entrada_str)
        
        # Parámetros de generación
        seed_input = input("\nSemilla (Enter para aleatorio): ").strip()
        seed = int(seed_input) if seed_input else None
        
        wall_density = float(input("Densidad de paredes (0.0-0.4) [0.2]: ") or "0.2")
        treasure_count = int(input("Número de tesoros [3]: ") or "3")
        pit_count = int(input("Número de pozos [3]: ") or "3")
        
        # Generar habitación
        print("\nGenerando habitación...")
        room = RoomGenerator(
            config=config,
            room_id=room_id,
            direccion_salida=direccion_salida,
            posicion_entrada=posicion_entrada,
            seed=seed
        )
        
        validator = RoomValidator(config)
        max_attempts = 50
        attempts = 0
        
        while attempts < max_attempts:
            room.generate_room(
                wall_density=wall_density,
                treasure_count=treasure_count,
                pit_count=pit_count
            )
            
            if validator.is_valid_room(room.map_grid):
                print(f"✓ Habitación válida generada (intento {attempts + 1})")
                break
            
            attempts += 1
            room = RoomGenerator(
                config=config,
                room_id=room_id,
                direccion_salida=direccion_salida,
                posicion_entrada=posicion_entrada,
                seed=None
            )
        
        if attempts >= max_attempts:
            print("✗ No se pudo generar una habitación válida")
            return
        
        # Mostrar resultado
        room.print_room()
        validator.print_statistics(room.map_grid)
        
        show_path = input("\n¿Mostrar camino óptimo? (s/n): ").lower()
        if show_path == 's':
            validator.visualize_path(room.map_grid)
        
        # Guardar
        save = input("\n¿Guardar habitación? (s/n): ").lower()
        if save == 's':
            filename = f"maps/rooms/room_{room_id:02d}.txt"
            room.save_room(filename)
        
    except ValueError as e:
        print(f"✗ Error en los parámetros: {e}")
    except KeyboardInterrupt:
        print("\n\nOperación cancelada")


def generate_full_dungeon(config: ConfigManager):
    """Genera el dungeon completo de 12 habitaciones."""
    print("\n--- GENERACIÓN DE DUNGEON COMPLETO ---\n")
    
    try:
        seed_input = input("Semilla del dungeon (Enter para aleatorio): ").strip()
        seed = int(seed_input) if seed_input else None
        
        wall_density = float(input("Densidad de paredes (0.0-0.4) [0.2]: ") or "0.2")
        treasure_count = int(input("Tesoros por habitación [3]: ") or "3")
        pit_count = int(input("Pozos por habitación [3]: ") or "3")
        
        validate = input("¿Validar todas las habitaciones? (s/n) [s]: ").lower()
        validate_all = validate != 'n'
        
        # Crear y generar dungeon
        dungeon = DungeonManager(config, dungeon_seed=seed)
        
        dungeon.generate_dungeon(
            wall_density=wall_density,
            treasure_count=treasure_count,
            pit_count=pit_count,
            validate_all=validate_all
        )
        
        # Mostrar resumen
        dungeon.print_dungeon_summary()
        
        # Guardar
        save = input("\n¿Guardar todas las habitaciones? (s/n): ").lower()
        if save == 's':
            dungeon.save_all_rooms()
            dungeon.save_dungeon_metadata()
            
            assemble = input("¿Ensamblar dungeon completo en un archivo? (s/n): ").lower()
            if assemble == 's':
                dungeon.assemble_full_dungeon()
        
        # Mostrar habitación de ejemplo
        show_example = input("\n¿Ver habitación 1 como ejemplo? (s/n): ").lower()
        if show_example == 's':
            dungeon.rooms[1].print_room()
        
    except ValueError as e:
        print(f"✗ Error en los parámetros: {e}")
    except KeyboardInterrupt:
        print("\n\nOperación cancelada")


def validate_existing_room(config: ConfigManager):
    """Valida una habitación existente."""
    print("\n--- VALIDACIÓN DE HABITACIÓN ---\n")
    
    filename = input("Nombre del archivo (en maps/rooms/): ")
    filepath = f"maps/rooms/{filename}"
    
    if not os.path.exists(filepath):
        print(f"✗ No se encontró el archivo: {filepath}")
        return
    
    try:
        # Leer habitación
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.rstrip('\n') for line in f.readlines()]
        
        import numpy as np
        room_grid = np.array([list(line) for line in lines])
        
        # Validar
        validator = RoomValidator(config)
        
        print("\nValidando habitación...\n")
        is_valid = validator.is_valid_room(room_grid, verbose=True)
        
        if is_valid:
            validator.print_statistics(room_grid)
            
            show_path = input("\n¿Mostrar camino óptimo? (s/n): ").lower()
            if show_path == 's':
                validator.visualize_path(room_grid)
    
    except Exception as e:
        print(f"✗ Error al procesar el archivo: {e}")


def show_configuration(config: ConfigManager):
    """Muestra la configuración actual."""
    print("\n--- CONFIGURACIÓN ACTUAL ---\n")
    config._print_mapping()
    print("\nRuta del archivo: " + config.config_path)
    print("\nDimensiones de habitaciones: 18x18 (16x16 interior)")
    print("Layout del dungeon:")
    print("  [1,  2,  3,  4]")
    print("  [8,  7,  6,  5]")
    print("  [9, 10, 11, 12]")
    print("\nRecorrido: 1→2→3→4→5→6→7→8→9→10→11→12")
    input("\nPresione Enter para continuar...")


def main():
    """Función principal del programa."""
    # Inicializar configuración
    config = ConfigManager('config/casillas.txt')
    
    # Crear configuración por defecto si no existe
    if not os.path.exists(config.config_path):
        print("Creando archivo de configuración por defecto...")
        config.create_default_config()
    
    # Cargar configuración
    if not config.load_config():
        print("\n✗ Error al cargar la configuración")
        print("Verifique el archivo config/casillas.txt")
        print("Debe contener 7 líneas (S, G, #, ', T, X, R)")
        return
    
    # Crear directorios necesarios
    os.makedirs('maps/rooms', exist_ok=True)
    os.makedirs('maps/dungeons', exist_ok=True)
    os.makedirs('data/datasets', exist_ok=True)
    
    # Bucle principal
    while True:
        show_menu()
        
        try:
            opcion = input("\nSeleccione una opción: ").strip()
            
            if opcion == '1':
                generate_single_room(config)
            elif opcion == '2':
                generate_full_dungeon(config)
            elif opcion == '3':
                validate_existing_room(config)
            elif opcion == '4':
                show_configuration(config)
            elif opcion == '5':
                print("\n¡Hasta luego!\n")
                break
            else:
                print("\n✗ Opción no válida")
            
            input("\nPresione Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n\n¡Hasta luego!\n")
            break
        except Exception as e:
            print(f"\n✗ Error inesperado: {e}")
            input("\nPresione Enter para continuar...")


if __name__ == "__main__":
    main()