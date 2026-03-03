"""
Service to load data from JSON files
"""
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from app.core.config import settings


class DataLoaderService:
    """Loads and caches data from scraped JSON files"""
    
    def __init__(self):
        self._jugadores_data: Optional[Dict[str, Any]] = None
        self._tecnicos_data: Optional[Dict[str, Any]] = None
        self._tecnicos_jugadores_data: Optional[Dict[str, Any]] = None
        self._club_posicion_index: Optional[Dict[str, Any]] = None
    
    def load_jugadores(self) -> Dict[str, Any]:
        """Load players data"""
        if self._jugadores_data is None:
            path = Path(settings.JUGADORES_FILE)
            print(f"Loading jugadores from: {path}")
            
            if not path.exists():
                print(f"Warning: Jugadores file not found at {path}")
                return {"jugadores": []}
            
            with open(path, 'r', encoding='utf-8') as f:
                self._jugadores_data = json.load(f)
        
        return self._jugadores_data
    
    def load_tecnicos(self) -> Dict[str, Any]:
        """Load coaches data"""
        if self._tecnicos_data is None:
            path = Path(settings.TECNICOS_FILE)
            print(f"Loading tecnicos from: {path}")
            
            if not path.exists():
                print(f"Warning: Tecnicos file not found at {path}")
                return {"tecnicos": {}}
            
            with open(path, 'r', encoding='utf-8') as f:
                self._tecnicos_data = json.load(f)
        
        return self._tecnicos_data
    
    def load_tecnicos_jugadores(self) -> Dict[str, Any]:
        """Load coaches-players relationship data"""
        if self._tecnicos_jugadores_data is None:
            path = Path(settings.TECNICOS_JUGADORES_FILE)
            print(f"Loading tecnicos_jugadores from: {path}")
            
            if not path.exists():
                print(f"Warning: Tecnicos_jugadores file not found at {path}")
                return {"tecnicos": {}}
            
            with open(path, 'r', encoding='utf-8') as f:
                self._tecnicos_jugadores_data = json.load(f)
        
        return self._tecnicos_jugadores_data
    
    def get_all_jugadores(self) -> List[Dict[str, Any]]:
        """Get all players as list"""
        data = self.load_jugadores()
        return data.get("jugadores", [])
    
    def get_jugadores_con_minimo_partidos(self, min_partidos: int = 10) -> List[Dict[str, Any]]:
        """Get players with minimum number of games"""
        jugadores = self.get_all_jugadores()
        return [j for j in jugadores if j.get("partidos", 0) >= min_partidos]
    
    def get_jugadores_con_clubes_nacionales(self, min_clubes: int = 2) -> List[Dict[str, Any]]:
        """Get players who played in multiple Argentine clubs"""
        jugadores = self.get_all_jugadores()
        result = []
        
        for j in jugadores:
            clubes_arg = [
                c for c in j.get("clubes_historia", [])
                if c.get("pais") == "Argentina"
            ]
            if len(clubes_arg) >= min_clubes:
                result.append(j)
        
        return result
    
    def get_jugadores_con_clubes_internacionales(self, min_clubes: int = 1) -> List[Dict[str, Any]]:
        """Get players who played in international clubs"""
        jugadores = self.get_all_jugadores()
        result = []
        
        for j in jugadores:
            clubes_int = [
                c for c in j.get("clubes_historia", [])
                if c.get("pais") != "Argentina"
            ]
            if len(clubes_int) >= min_clubes:
                result.append(j)
        
        return result
    
    def get_all_tecnicos(self) -> Dict[str, Dict[str, Any]]:
        """Get all coaches"""
        data = self.load_tecnicos()
        return data.get("tecnicos", {})
    
    def get_jugadores_por_tecnico(self, tecnico_nombre: str) -> Optional[Dict[str, Any]]:
        """Get players coached by a specific coach"""
        data = self.load_tecnicos_jugadores()
        tecnicos = data.get("tecnicos", {})
        return tecnicos.get(tecnico_nombre)
    
    def load_club_posicion_index(self) -> Dict[str, Any]:
        """
        Load optimized club-position index for O(1) lookups
        
        Returns:
            Dict[club][position] -> List[player]
        """
        if self._club_posicion_index is None:
            # Try to load index file
            data_dir = Path(settings.JUGADORES_FILE).parent
            index_path = data_dir / 'club_posicion_index.json'
            
            print(f"Loading club_posicion_index from: {index_path}")
            
            if not index_path.exists():
                print(f"Warning: Index file not found at {index_path}")
                print("Run: python3 scraping/scripts/generar_indice_club_posicion.py")
                return {}
            
            with open(index_path, 'r', encoding='utf-8') as f:
                self._club_posicion_index = json.load(f)
        
        return self._club_posicion_index
    
    def get_jugadores_por_club_posicion(
        self, 
        club_nombre: str, 
        posicion: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get players for a specific club and position (O(1) lookup)
        
        Args:
            club_nombre: Club name
            posicion: Optional position filter (e.g., 'DEL', 'MC')
        
        Returns:
            List of players matching criteria
        """
        index = self.load_club_posicion_index()
        
        # Get club data
        club_data = index.get(club_nombre, {})
        
        if not club_data:
            return []
        
        # If no position specified, return all players for the club
        if posicion is None:
            all_players = []
            for pos_players in club_data.values():
                all_players.extend(pos_players)
            return all_players
        
        # Return players for specific position
        return club_data.get(posicion, [])
    
    def reload_all(self):
        """Force reload all data"""
        self._jugadores_data = None
        self._tecnicos_data = None
        self._tecnicos_jugadores_data = None
        self._club_posicion_index = None
        
        self.load_jugadores()
        self.load_tecnicos()
        self.load_tecnicos_jugadores()
        self.load_club_posicion_index()


# Singleton instance
data_loader_service = DataLoaderService()
