"""
Módulo para generar habitaciones individuales de 18x18 para dungeons.
Autor: CristianIDL
Fecha: Enero 2025
"""

import random
import numpy as np
from typing import Tuple, List, Optional
from src.config_manager import ConfigManager


class RoomGenerator:
    """
    Genera habitaciones de 18x18 (16x16 interior + bordes) para dungeons conectados.
    """
    
    def __init__(self, 
                 config: ConfigManager, 
                 room_id: int,
                 direccion_salida: Optional[str] = None,
                 posicion_entrada: Optional[int] = None,
                 seed: Optional[int] = None):
        """
        Inicializa el generador de habitaciones.
        
        Args:
            config: Instancia del ConfigManager
            room_id: ID de la habitación (1-12)
            direccion_salida: 'DERECHA', 'ABAJO', 'IZQUIERDA', 'ARRIBA', None (habitación final)
            posicion_entrada: Posición donde colocar S (1-16), None para habitación inicial
            seed: Semilla para generación pseudoaleatoria
        """
        self.config = config
        self.room_id = room_id
        self.map_size = 18
        self.inner_size = 16
        self.direccion_salida = direccion_salida
        self.posicion_entrada = posicion_entrada
        self.map_grid = None
        
        # Establecer semilla
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            self.seed = seed
        else:
            self.seed = random.randint(0, 999999)
            random.seed(self.seed)
            np.random.seed(self.seed)
    
    def generate_room(self,
                     wall_density: float = 0.2,
                     treasure_count: int = 3,
                     pit_count: int = 3,
                     enemy_count: int = 2) -> np.ndarray:
        """
        Genera una habitación completa.
        
        Args:
            wall_density: Densidad de paredes internas (0.0 a 1.0)
            treasure_count: Número de tesoros
            pit_count: Número de pozos
            enemy_count: Número de enemigos (usa 'E' del treasure/pit si existe)
            
        Returns:
            Matriz numpy con la habitación generada
        """
        # Crear estructura básica
        self._create_base_structure()
        
        # Colocar elementos según tipo de habitación
        reserved_positions = []
        
        # Habitación 1: Solo S aleatorio
        if self.room_id == 1:
            start_pos = self._place_start_random()
            reserved_positions.append(start_pos)
        
        # Habitación 12: S en entrada + G en posición específica
        elif self.room_id == 12:
            start_pos = self._place_start_entrance()
            goal_pos = self._place_goal()
            reserved_positions.extend([start_pos, goal_pos])
        
        # Habitaciones intermedias: S en entrada
        else:
            start_pos = self._place_start_entrance()
            reserved_positions.append(start_pos)
        
        # Colocar salida (R's) si no es la habitación final
        if self.direccion_salida is not None:
            exit_positions = self._place_room_exits()
            reserved_positions.extend(exit_positions)
        
        # Generar elementos aleatorios
        self._place_internal_walls(wall_density, reserved_positions)
        self._place_special_items(treasure_count, pit_count, reserved_positions)
        
        return self.map_grid
    
    def _create_base_structure(self):
        """Crea la estructura base 18x18 con bordes."""
        path_char = self.config.get_char('PATH')
        wall_char = self.config.get_char('WALL')
        
        # Inicializar con caminos
        self.map_grid = np.full((self.map_size, self.map_size), path_char, dtype=str)
        
        # Bordes completos
        self.map_grid[0, :] = wall_char   # Superior
        self.map_grid[17, :] = wall_char  # Inferior
        self.map_grid[:, 0] = wall_char   # Izquierdo
        self.map_grid[:, 17] = wall_char  # Derecho
    
    def _place_start_random(self) -> Tuple[int, int]:
        """Coloca S en posición aleatoria (habitación 1)."""
        start_char = self.config.get_char('START')
        
        # Posición aleatoria en el interior (1-16, 1-16)
        row = random.randint(1, 16)
        col = 0
        start_pos = (row, col)
        
        self.map_grid[start_pos] = start_char
        return start_pos
    
    def _place_start_entrance(self) -> Tuple[int, int]:
        """
        Coloca S en el borde correcto según el tipo de habitación.
        """
        start_char = self.config.get_char('START')

        # Validar posicion_entrada
        if self.posicion_entrada is not None and 1 <= self.posicion_entrada <= 16:
            entrada = self.posicion_entrada
        else:
            entrada = random.randint(1, 16)

        # Habitaciones 05 y 09 → entrada por ARRIBA
        if self.room_id in (5, 9):
            row = 0
            col = entrada

        # Habitaciones 06, 07 y 08 → entrada por DERECHA
        elif self.room_id in (6, 7, 8):
            row = entrada
            col = 17

        # Resto → entrada por IZQUIERDA (comportamiento original)
        else:
            row = entrada
            col = 0

        start_pos = (row, col)
        self.map_grid[start_pos] = start_char
        return start_pos
    
    def _place_goal(self) -> Tuple[int, int]:
        """Coloca G en posición aleatoria (habitación 12)."""
        goal_char = self.config.get_char('GOAL')
        
        # Posición aleatoria evitando bordes
        attempts = 0
        max_attempts = 100
        
        while attempts < max_attempts:
            row = random.randint(2, 15)
            col = 16
            goal_pos = (row, col)
            
            # Verificar que sea un camino libre
            if self.map_grid[goal_pos] == self.config.get_char('PATH'):
                self.map_grid[goal_pos] = goal_char
                return goal_pos
            
            attempts += 1
        
        # Si no encuentra, colocar en posición fija
        goal_pos = (8, 8)
        self.map_grid[goal_pos] = goal_char
        return goal_pos
    
    def _place_room_exits(self) -> List[Tuple[int, int]]:
        """
        Reemplaza una cara completa del borde por ROOM_EXIT.
        """
        exit_char = self.config.get_char('ROOM_EXIT')
        exit_positions = []

        if self.direccion_salida == 'DERECHA':
            col = 17
            for row in range(1, 17):
                self.map_grid[row, col] = exit_char
                exit_positions.append((row, col))

        elif self.direccion_salida == 'IZQUIERDA':
            col = 0
            for row in range(1, 17):
                self.map_grid[row, col] = exit_char
                exit_positions.append((row, col))

        elif self.direccion_salida == 'ABAJO':
            row = 17
            for col in range(1, 17):
                self.map_grid[row, col] = exit_char
                exit_positions.append((row, col))

        elif self.direccion_salida == 'ARRIBA':
            row = 0
            for col in range(1, 17):
                self.map_grid[row, col] = exit_char
                exit_positions.append((row, col))

        return exit_positions

    
    def _place_internal_walls(self, density: float, reserved_positions: List[Tuple[int, int]]):
        """Coloca paredes internas."""
        wall_char = self.config.get_char('WALL')
        
        total_inner_cells = self.inner_size * self.inner_size
        num_walls = int(total_inner_cells * density)
        
        placed_walls = 0
        attempts = 0
        max_attempts = num_walls * 10
        
        while placed_walls < num_walls and attempts < max_attempts:
            row = random.randint(1, 16)
            col = random.randint(1, 16)
            pos = (row, col)
            
            if pos not in reserved_positions:
                if self.map_grid[pos] == self.config.get_char('PATH'):
                    self.map_grid[pos] = wall_char
                    placed_walls += 1
            
            attempts += 1
    
    def _place_special_items(self, treasure_count: int, pit_count: int, 
                            reserved_positions: List[Tuple[int, int]]):
        """Coloca tesoros y pozos."""
        treasure_char = self.config.get_char('TREASURE')
        pit_char = self.config.get_char('PIT')
        path_char = self.config.get_char('PATH')
        
        # Colocar tesoros
        placed_treasures = 0
        attempts = 0
        max_attempts = treasure_count * 20
        
        while placed_treasures < treasure_count and attempts < max_attempts:
            row = random.randint(1, 16)
            col = random.randint(1, 16)
            pos = (row, col)
            
            if pos not in reserved_positions and self.map_grid[pos] == path_char:
                self.map_grid[pos] = treasure_char
                reserved_positions.append(pos)
                placed_treasures += 1
            
            attempts += 1
        
        # Colocar pozos
        placed_pits = 0
        attempts = 0
        
        while placed_pits < pit_count and attempts < max_attempts:
            row = random.randint(1, 16)
            col = random.randint(1, 16)
            pos = (row, col)
            
            if pos not in reserved_positions and self.map_grid[pos] == path_char:
                self.map_grid[pos] = pit_char
                reserved_positions.append(pos)
                placed_pits += 1
            
            attempts += 1
    
    def get_start_position(self) -> Optional[Tuple[int, int]]:
        """Encuentra la posición del START."""
        start_char = self.config.get_char('START')
        positions = np.where(self.map_grid == start_char)
        
        if len(positions[0]) > 0:
            return (int(positions[0][0]), int(positions[1][0]))
        return None
    
    def get_goal_position(self) -> Optional[Tuple[int, int]]:
        """Encuentra la posición del GOAL."""
        goal_char = self.config.get_char('GOAL')
        positions = np.where(self.map_grid == goal_char)
        
        if len(positions[0]) > 0:
            return (int(positions[0][0]), int(positions[1][0]))
        return None
    
    def get_exit_positions(self) -> List[Tuple[int, int]]:
        """Encuentra todas las posiciones de ROOM_EXIT."""
        exit_char = self.config.get_char('ROOM_EXIT')
        positions = np.where(self.map_grid == exit_char)
        
        return [(int(positions[0][i]), int(positions[1][i])) 
                for i in range(len(positions[0]))]
    
    def print_room(self):
        """Imprime la habitación en consola."""
        if self.map_grid is None:
            print("No hay habitación generada aún.")
            return
        
        print("\n" + "=" * 40)
        print(f"  HABITACIÓN {self.room_id} (Semilla: {self.seed})")
        print("=" * 40)
        
        for row in self.map_grid:
            print(''.join(row))
        
        print("=" * 40)
        
        start_pos = self.get_start_position()
        goal_pos = self.get_goal_position()
        exit_count = len(self.get_exit_positions())
        
        print(f"\nInformación:")
        print(f"  Habitación:    {self.room_id}")
        print(f"  Start (S):     {start_pos}")
        if goal_pos:
            print(f"  Goal (G):      {goal_pos}")
        print(f"  Salidas (R):   {exit_count}")
        print(f"  Dirección:     {self.direccion_salida or 'FINAL'}")
        print(f"  Semilla:       {self.seed}")
    
    def save_room(self, filename: str):
        """Guarda la habitación en un archivo."""
        import os
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            for row in self.map_grid:
                f.write(''.join(row) + '\n')
        
        print(f"✓ Habitación {self.room_id} guardada: {filename}")


# Ejemplo de uso
if __name__ == "__main__":
    config = ConfigManager('../config/casillas.txt')
    
    if not config.load_config():
        print("Error al cargar configuración")
        exit(1)
    
    print("\n--- Generando habitaciones de ejemplo ---\n")
    
    # Habitación 1 (inicial)
    print("Generando habitación 1 (inicial)...")
    room1 = RoomGenerator(config, room_id=1, direccion_salida='DERECHA', seed=100)
    room1.generate_room(wall_density=0.15, treasure_count=3, pit_count=2)
    room1.print_room()
    room1.save_room('../maps/rooms/room_01.txt')
    
    # Habitación intermedia
    print("\nGenerando habitación 5 (intermedia)...")
    room5 = RoomGenerator(config, room_id=5, direccion_salida='IZQUIERDA', 
                          posicion_entrada=8, seed=200)
    room5.generate_room(wall_density=0.2, treasure_count=4, pit_count=3)
    room5.print_room()
    room5.save_room('../maps/rooms/room_05.txt')
    
    # Habitación 12 (final)
    print("\nGenerando habitación 12 (final)...")
    room12 = RoomGenerator(config, room_id=12, direccion_salida=None, 
                           posicion_entrada=10, seed=300)
    room12.generate_room(wall_density=0.15, treasure_count=5, pit_count=2)
    room12.print_room()
    room12.save_room('../maps/rooms/room_12.txt')