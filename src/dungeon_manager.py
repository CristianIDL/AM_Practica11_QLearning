"""
Módulo para gestionar la generación completa de dungeons con 12 habitaciones.
Autor: CristianIDL
Fecha: Enero 2025
"""

import random
import os
from typing import Dict, Tuple, Optional, List
from src.config_manager import ConfigManager
from src.room_generator import RoomGenerator


class DungeonManager:
    """
    Gestiona la generación del dungeon completo con 12 habitaciones conectadas.
    
    Layout del dungeon:
    [1,  2,  3,  4]
    [8,  7,  6,  5]
    [9, 10, 11, 12]
    
    Recorrido: 1→2→3→4→5→6→7→8→9→10→11→12
    """
    
    # Layout del dungeon
    DUNGEON_LAYOUT = [
        [1,  2,  3,  4],
        [8,  7,  6,  5],
        [9, 10, 11, 12]
    ]
    
    def __init__(self, config: ConfigManager, dungeon_seed: Optional[int] = None):
        """
        Inicializa el gestor de dungeon.
        
        Args:
            config: Instancia del ConfigManager
            dungeon_seed: Semilla base para el dungeon completo
        """
        self.config = config
        self.rooms: Dict[int, RoomGenerator] = {}
        
        if dungeon_seed is not None:
            self.dungeon_seed = dungeon_seed
        else:
            self.dungeon_seed = random.randint(0, 999999)
    
    def calculate_exit_direction(self, room_id: int) -> Optional[str]:
        """
        Calcula la dirección de salida para una habitación según el recorrido.
        
        Args:
            room_id: ID de la habitación (1-12)
            
        Returns:
            'DERECHA', 'ABAJO', 'IZQUIERDA', 'ARRIBA', o None (habitación final)
        """
        transitions = {
            1: 'DERECHA',      # 1→2
            2: 'DERECHA',      # 2→3
            3: 'DERECHA',      # 3→4
            4: 'ABAJO',        # 4→5
            5: 'IZQUIERDA',    # 5→6
            6: 'IZQUIERDA',    # 6→7
            7: 'IZQUIERDA',    # 7→8
            8: 'ABAJO',        # 8→9
            9: 'DERECHA',      # 9→10
            10: 'DERECHA',     # 10→11
            11: 'DERECHA',     # 11→12
            12: None           # Fin del dungeon
        }
        
        return transitions.get(room_id)
    
    def calculate_entrance_direction(self, room_id: int) -> Optional[str]:
        """
        Calcula la dirección de entrada para una habitación.
        
        Args:
            room_id: ID de la habitación (1-12)
            
        Returns:
            Dirección de donde viene el agente, o None si es la primera habitación
        """
        # Invertir las transiciones para saber de dónde viene
        reverse_transitions = {
            2: 'IZQUIERDA',    # viene de 1 (que sale DERECHA)
            3: 'IZQUIERDA',    # viene de 2
            4: 'IZQUIERDA',    # viene de 3
            5: 'ARRIBA',       # viene de 4 (que sale ABAJO)
            6: 'DERECHA',      # viene de 5 (que sale IZQUIERDA)
            7: 'DERECHA',      # viene de 6
            8: 'DERECHA',      # viene de 7
            9: 'ARRIBA',       # viene de 8 (que sale ABAJO)
            10: 'IZQUIERDA',   # viene de 9 (que sale DERECHA)
            11: 'IZQUIERDA',   # viene de 10
            12: 'IZQUIERDA'    # viene de 11
        }
        
        return reverse_transitions.get(room_id)
    
    def calculate_entrance_position(self, room_id: int) -> Optional[int]:
        """
        Calcula la posición de entrada aleatoria según de dónde viene.
        
        Args:
            room_id: ID de la habitación
            
        Returns:
            Posición en la fila/columna de entrada (1-16), o None para habitación 1
        """
        if room_id == 1:
            return None  # Habitación inicial, S aleatorio
        
        # Generar posición aleatoria en el rango 1-16
        # Usamos la semilla del dungeon + room_id para consistencia
        random.seed(self.dungeon_seed + room_id)
        position = random.randint(1, 16)
        
        return position
    
    def generate_dungeon(self,
                        wall_density: float = 0.2,
                        treasure_count: int = 3,
                        pit_count: int = 3,
                        validate_all: bool = True) -> Dict[int, RoomGenerator]:
        """
        Genera todas las 12 habitaciones del dungeon.
        
        Args:
            wall_density: Densidad de paredes para todas las habitaciones
            treasure_count: Tesoros por habitación
            pit_count: Pozos por habitación
            validate_all: Si True, valida cada habitación generada
            
        Returns:
            Diccionario con las habitaciones generadas {room_id: RoomGenerator}
        """
        print("\n" + "="*60)
        print("  GENERANDO DUNGEON COMPLETO")
        print("="*60)
        print(f"Semilla del dungeon: {self.dungeon_seed}\n")
        
        for room_id in range(1, 13):
            print(f"Generando habitación {room_id}/12...", end=" ")
            
            # Calcular parámetros de la habitación
            exit_direction = self.calculate_exit_direction(room_id)
            entrance_position = self.calculate_entrance_position(room_id)
            
            # Generar semilla específica para esta habitación
            room_seed = self.dungeon_seed + (room_id * 1000)
            
            # Crear generador
            room_gen = RoomGenerator(
                config=self.config,
                room_id=room_id,
                direccion_salida=exit_direction,
                posicion_entrada=entrance_position,
                seed=room_seed
            )
            
            # Generar habitación con validación si se requiere
            max_attempts = 50 if validate_all else 1
            attempts = 0
            
            while attempts < max_attempts:
                room_gen.generate_room(
                    wall_density=wall_density,
                    treasure_count=treasure_count,
                    pit_count=pit_count
                )
                
                # Si no se valida o la habitación es válida, continuar
                if not validate_all or self._validate_room(room_gen):
                    break
                
                # Reintentar con nueva semilla
                room_seed += 1
                room_gen = RoomGenerator(
                    config=self.config,
                    room_id=room_id,
                    direccion_salida=exit_direction,
                    posicion_entrada=entrance_position,
                    seed=room_seed
                )
                attempts += 1
            
            if attempts >= max_attempts:
                print(f"⚠ (no validada después de {max_attempts} intentos)")
            else:
                print(f"✓ (intento {attempts + 1})")
            
            self.rooms[room_id] = room_gen
        
        print("\n" + "="*60)
        print(f"✓ Dungeon completo generado: 12 habitaciones")
        print("="*60)
        
        return self.rooms
    
    def _validate_room(self, room: RoomGenerator) -> bool:
        """
        Valida una habitación (debe haber camino de S a R o G).
        
        Args:
            room: Habitación a validar
            
        Returns:
            True si es válida
        """
        from src.room_validator import RoomValidator
        
        validator = RoomValidator(self.config)
        return validator.is_valid_room(room.map_grid, verbose=False)
    
    def save_all_rooms(self, base_path: str = 'maps/rooms'):
        """
        Guarda todas las habitaciones en archivos individuales.
        
        Args:
            base_path: Directorio base donde guardar las habitaciones
        """
        os.makedirs(base_path, exist_ok=True)
        
        print(f"\nGuardando habitaciones en '{base_path}'...")
        
        for room_id, room in self.rooms.items():
            filename = f"{base_path}/room_{room_id:02d}.txt"
            room.save_room(filename)
        
        print(f"✓ Todas las habitaciones guardadas")
    
    def save_dungeon_metadata(self, filename: str = 'maps/rooms/dungeon_metadata.txt'):
        """
        Guarda información del dungeon completo.
        
        Args:
            filename: Archivo donde guardar los metadatos
        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("  METADATOS DEL DUNGEON\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Semilla del dungeon: {self.dungeon_seed}\n")
            f.write(f"Número de habitaciones: {len(self.rooms)}\n\n")
            
            f.write("Layout del dungeon:\n")
            f.write("  [1,  2,  3,  4]\n")
            f.write("  [8,  7,  6,  5]\n")
            f.write("  [9, 10, 11, 12]\n\n")
            
            f.write("Recorrido: 1→2→3→4→5→6→7→8→9→10→11→12\n\n")
            
            f.write("="*60 + "\n")
            f.write("  INFORMACIÓN DE CADA HABITACIÓN\n")
            f.write("="*60 + "\n\n")
            
            for room_id in range(1, 13):
                if room_id in self.rooms:
                    room = self.rooms[room_id]
                    f.write(f"Habitación {room_id}:\n")
                    f.write(f"  Semilla:       {room.seed}\n")
                    f.write(f"  Dirección:     {room.direccion_salida or 'FINAL'}\n")
                    f.write(f"  Entrada en:    {room.posicion_entrada or 'ALEATORIA'}\n")
                    
                    start_pos = room.get_start_position()
                    f.write(f"  Start (S):     {start_pos}\n")
                    
                    if room_id == 12:
                        goal_pos = room.get_goal_position()
                        f.write(f"  Goal (G):      {goal_pos}\n")
                    else:
                        exit_count = len(room.get_exit_positions())
                        f.write(f"  Salidas (R):   {exit_count}\n")
                    
                    f.write("\n")
        
        print(f"✓ Metadatos guardados: {filename}")
    
    def print_dungeon_summary(self):
        """Imprime un resumen del dungeon generado."""
        print("\n" + "="*60)
        print("  RESUMEN DEL DUNGEON")
        print("="*60)
        
        print(f"\nSemilla: {self.dungeon_seed}")
        print(f"Habitaciones: {len(self.rooms)}/12\n")
        
        print("Recorrido:")
        for room_id in range(1, 13):
            if room_id in self.rooms:
                room = self.rooms[room_id]
                direction = room.direccion_salida or "FIN"
                entrada = room.posicion_entrada or "RANDOM"
                print(f"  Habitación {room_id:2d}: Entrada={entrada:6} → Salida={direction:10}")
        
        print("="*60)
    
    def assemble_full_dungeon(self, output_file: str = 'maps/dungeons/dungeon_full.txt'):
        """
        Ensambla todas las habitaciones en un único archivo TXT gigante.
        
        Args:
            output_file: Archivo de salida
        """
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        print(f"\nEnsamblando dungeon completo...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Escribir encabezado
            f.write("="*90 + "\n")
            f.write("  DUNGEON COMPLETO - 12 HABITACIONES\n")
            f.write(f"  Semilla: {self.dungeon_seed}\n")
            f.write("="*90 + "\n\n")
            
            # Ensamblar por filas del layout
            for row_idx, row in enumerate(self.DUNGEON_LAYOUT):
                f.write(f"--- Fila {row_idx + 1} ---\n\n")
                
                # Para cada habitación en esta fila
                for room_id in row:
                    if room_id in self.rooms:
                        room = self.rooms[room_id]
                        f.write(f"Habitación {room_id}:\n")
                        
                        for map_row in room.map_grid:
                            f.write(''.join(map_row) + "\n")
                        
                        f.write("\n")
                
                f.write("\n")
        
        print(f"✓ Dungeon completo ensamblado: {output_file}")


# Ejemplo de uso
if __name__ == "__main__":
    config = ConfigManager('../config/casillas.txt')
    
    if not config.load_config():
        print("Error al cargar configuración")
        exit(1)
    
    # Crear gestor de dungeon
    dungeon = DungeonManager(config, dungeon_seed=42)
    
    # Generar dungeon completo
    dungeon.generate_dungeon(
        wall_density=0.2,
        treasure_count=3,
        pit_count=3,
        validate_all=True
    )
    
    # Mostrar resumen
    dungeon.print_dungeon_summary()
    
    # Guardar todo
    dungeon.save_all_rooms()
    dungeon.save_dungeon_metadata()
    dungeon.assemble_full_dungeon()
    
    # Mostrar una habitación de ejemplo
    print("\n" + "="*60)
    print("  EJEMPLO: HABITACIÓN 1")
    print("="*60)
    dungeon.rooms[1].print_room()