"""
Módulo para validar habitaciones de dungeon.
Verifica que exista un camino de START a ROOM_EXIT o GOAL.
Autor: CristianIDL
Fecha: Enero 2025
"""

import numpy as np
from collections import deque
from typing import Tuple, List, Set, Optional
from src.config_manager import ConfigManager


class RoomValidator:
    """
    Valida habitaciones de dungeon usando BFS.
    Verifica que haya camino de S a cualquier R (o a G en habitación final).
    """
    
    def __init__(self, config: ConfigManager):
        """
        Inicializa el validador.
        
        Args:
            config: Instancia del ConfigManager
        """
        self.config = config
    
    def is_valid_room(self, room_grid: np.ndarray, verbose: bool = False) -> bool:
        """
        Verifica si la habitación es válida.
        
        Para habitaciones normales: debe existir camino de S a cualquier R
        Para habitación final: debe existir camino de S a G
        
        Args:
            room_grid: Matriz de la habitación
            verbose: Si True, muestra información detallada
            
        Returns:
            True si la habitación es válida
        """
        # Encontrar START
        start_pos = self._find_position(room_grid, 'START')
        
        if start_pos is None:
            if verbose:
                print("✗ No se encontró la posición START")
            return False
        
        # Buscar GOAL (habitación 12)
        goal_pos = self._find_position(room_grid, 'GOAL')
        
        if goal_pos is not None:
            # Es la habitación final, validar camino S→G
            path_exists, path_length = self._bfs_path_exists(room_grid, start_pos, goal_pos)
            
            if verbose:
                if path_exists:
                    print(f"✓ Habitación válida (final) - Camino S→G: {path_length} pasos")
                else:
                    print("✗ Habitación inválida - No hay camino S→G")
            
            return path_exists
        
        # Es una habitación normal, validar camino S→cualquier R
        exit_positions = self._find_all_positions(room_grid, 'ROOM_EXIT')
        
        if not exit_positions:
            if verbose:
                print("✗ No se encontraron salidas (R)")
            return False
        
        # Verificar si existe camino a ALGUNA salida
        for exit_pos in exit_positions:
            path_exists, path_length = self._bfs_path_exists(room_grid, start_pos, exit_pos)
            
            if path_exists:
                if verbose:
                    print(f"✓ Habitación válida - Camino S→R: {path_length} pasos")
                return True
        
        if verbose:
            print("✗ Habitación inválida - No hay camino a ninguna salida")
        
        return False
    
    def _find_position(self, room_grid: np.ndarray, tile_type: str) -> Optional[Tuple[int, int]]:
        """Encuentra la primera posición de un tipo de casilla."""
        char = self.config.get_char(tile_type)
        positions = np.where(room_grid == char)
        
        if len(positions[0]) > 0:
            return (int(positions[0][0]), int(positions[1][0]))
        return None
    
    def _find_all_positions(self, room_grid: np.ndarray, tile_type: str) -> List[Tuple[int, int]]:
        """Encuentra todas las posiciones de un tipo de casilla."""
        char = self.config.get_char(tile_type)
        positions = np.where(room_grid == char)
        
        return [(int(positions[0][i]), int(positions[1][i])) 
                for i in range(len(positions[0]))]
    
    def _bfs_path_exists(self, 
                        room_grid: np.ndarray, 
                        start: Tuple[int, int], 
                        goal: Tuple[int, int]) -> Tuple[bool, int]:
        """
        BFS para verificar si existe camino.
        
        Args:
            room_grid: Matriz de la habitación
            start: Posición inicial
            goal: Posición objetivo
            
        Returns:
            Tupla (existe_camino, longitud_camino)
        """
        # Caracteres transitables (no son paredes)
        wall_char = self.config.get_char('WALL')
        
        queue = deque([(start, 0)])
        visited: Set[Tuple[int, int]] = {start}
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        while queue:
            current_pos, distance = queue.popleft()
            
            if current_pos == goal:
                return True, distance
            
            for dr, dc in directions:
                new_row = current_pos[0] + dr
                new_col = current_pos[1] + dc
                new_pos = (new_row, new_col)
                
                if not (0 <= new_row < room_grid.shape[0] and 
                       0 <= new_col < room_grid.shape[1]):
                    continue
                
                if new_pos in visited:
                    continue
                
                # Puede moverse si NO es pared
                if room_grid[new_pos] != wall_char:
                    visited.add(new_pos)
                    queue.append((new_pos, distance + 1))
        
        return False, -1
    
    def get_shortest_path(self, room_grid: np.ndarray) -> Optional[List[Tuple[int, int]]]:
        """
        Obtiene el camino más corto de S a R o G.
        
        Args:
            room_grid: Matriz de la habitación
            
        Returns:
            Lista de posiciones o None si no existe camino
        """
        start_pos = self._find_position(room_grid, 'START')
        
        if start_pos is None:
            return None
        
        # Verificar si es habitación final (tiene G)
        goal_pos = self._find_position(room_grid, 'GOAL')
        
        if goal_pos is not None:
            return self._bfs_get_path(room_grid, start_pos, goal_pos)
        
        # Es habitación normal, buscar camino a la salida más cercana
        exit_positions = self._find_all_positions(room_grid, 'ROOM_EXIT')
        
        shortest_path = None
        shortest_length = float('inf')
        
        for exit_pos in exit_positions:
            path = self._bfs_get_path(room_grid, start_pos, exit_pos)
            
            if path and len(path) < shortest_length:
                shortest_path = path
                shortest_length = len(path)
        
        return shortest_path
    
    def _bfs_get_path(self, 
                     room_grid: np.ndarray, 
                     start: Tuple[int, int], 
                     goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """BFS que retorna el camino completo."""
        wall_char = self.config.get_char('WALL')
        
        queue = deque([(start, [start])])
        visited: Set[Tuple[int, int]] = {start}
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        while queue:
            current_pos, path = queue.popleft()
            
            if current_pos == goal:
                return path
            
            for dr, dc in directions:
                new_row = current_pos[0] + dr
                new_col = current_pos[1] + dc
                new_pos = (new_row, new_col)
                
                if not (0 <= new_row < room_grid.shape[0] and 
                       0 <= new_col < room_grid.shape[1]):
                    continue
                
                if new_pos in visited:
                    continue
                
                if room_grid[new_pos] != wall_char:
                    visited.add(new_pos)
                    queue.append((new_pos, path + [new_pos]))
        
        return None
    
    def visualize_path(self, room_grid: np.ndarray):
        """Visualiza la habitación con el camino marcado."""
        path = self.get_shortest_path(room_grid)
        
        if path is None:
            print("No existe camino válido para visualizar")
            return
        
        visual_grid = room_grid.copy()
        
        # Caracteres especiales que no deben marcarse
        special_chars = [
            self.config.get_char('START'),
            self.config.get_char('GOAL'),
            self.config.get_char('ROOM_EXIT')
        ]
        
        for pos in path:
            if visual_grid[pos] not in special_chars:
                visual_grid[pos] = '·'
        
        print("\n" + "=" * 40)
        print("  VISUALIZACIÓN DEL CAMINO")
        print("=" * 40)
        
        for row in visual_grid:
            print(''.join(row))
        
        print("=" * 40)
        print(f"Longitud del camino: {len(path)} pasos")
        print("(· = camino óptimo)")
    
    def get_statistics(self, room_grid: np.ndarray) -> dict:
        """Obtiene estadísticas de la habitación."""
        stats = {
            'valid': self.is_valid_room(room_grid),
            'size': room_grid.shape,
            'tiles': {}
        }
        
        # Contar cada tipo de casilla
        for tile_type in ['START', 'GOAL', 'WALL', 'PATH', 'TREASURE', 'PIT', 'ROOM_EXIT']:
            char = self.config.get_char(tile_type)
            count = np.sum(room_grid == char)
            stats['tiles'][tile_type] = int(count)
        
        # Longitud del camino
        if stats['valid']:
            path = self.get_shortest_path(room_grid)
            stats['path_length'] = len(path) if path else 0
        else:
            stats['path_length'] = -1
        
        return stats
    
    def print_statistics(self, room_grid: np.ndarray):
        """Imprime estadísticas de la habitación."""
        stats = self.get_statistics(room_grid)
        
        print("\n" + "=" * 40)
        print("  ESTADÍSTICAS DE LA HABITACIÓN")
        print("=" * 40)
        print(f"Válida:            {'✓ Sí' if stats['valid'] else '✗ No'}")
        print(f"Dimensiones:       {stats['size'][0]}x{stats['size'][1]}")
        print(f"Longitud camino:   {stats['path_length']}")
        print("\nDistribución de casillas:")
        
        for tile_type, count in stats['tiles'].items():
            if count > 0:
                char = self.config.get_char(tile_type)
                print(f"  {tile_type:12} ('{char}'): {count:3}")
        
        print("=" * 40)


# Ejemplo de uso
if __name__ == "__main__":
    from room_generator import RoomGenerator
    
    config = ConfigManager('../config/casillas.txt')
    
    if not config.load_config():
        print("Error al cargar configuración")
        exit(1)
    
    validator = RoomValidator(config)
    
    print("\n--- Generando y validando habitaciones ---\n")
    
    # Probar habitación normal
    print("PRUEBA 1: Habitación normal")
    room = RoomGenerator(config, room_id=5, direccion_salida='DERECHA', 
                        posicion_entrada=8, seed=100)
    room.generate_room(wall_density=0.2, treasure_count=3, pit_count=2)
    room.print_room()
    
    validator.is_valid_room(room.map_grid, verbose=True)
    validator.print_statistics(room.map_grid)
    validator.visualize_path(room.map_grid)
    
    # Probar habitación final
    print("\n\nPRUEBA 2: Habitación final (con G)")
    room12 = RoomGenerator(config, room_id=12, direccion_salida=None, 
                          posicion_entrada=10, seed=200)
    room12.generate_room(wall_density=0.15, treasure_count=4, pit_count=2)
    room12.print_room()
    
    validator.is_valid_room(room12.map_grid, verbose=True)
    validator.print_statistics(room12.map_grid)
    validator.visualize_path(room12.map_grid)