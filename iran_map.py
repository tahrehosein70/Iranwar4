import random
from typing import Dict, List, Tuple, Set

class IranMap:
    def __init__(self):
        self.regions = self.create_regions()
        self.region_neighbors = self.create_neighbor_map()
    
    def create_regions(self) -> Dict:
        """Create Iran map regions with their properties"""
        regions = {
            "tehran": {
                "name": "تهران",
                "name_en": "Tehran",
                "pos": (500, 300),
                "strategic_value": 10,
                "resource_type": "industrial",
                "population": 100
            },
            "isfahan": {
                "name": "اصفهان",
                "name_en": "Isfahan",
                "pos": (450, 400),
                "strategic_value": 8,
                "resource_type": "cultural",
                "population": 80
            },
            "shiraz": {
                "name": "شیراز",
                "name_en": "Shiraz",
                "pos": (400, 500),
                "strategic_value": 7,
                "resource_type": "cultural",
                "population": 70
            },
            "mashhad": {
                "name": "مشهد",
                "name_en": "Mashhad",
                "pos": (650, 200),
                "strategic_value": 9,
                "resource_type": "religious",
                "population": 90
            },
            "tabriz": {
                "name": "تبریز",
                "name_en": "Tabriz",
                "pos": (350, 150),
                "strategic_value": 8,
                "resource_type": "industrial",
                "population": 85
            },
            "ahvaz": {
                "name": "اهواز",
                "name_en": "Ahvaz",
                "pos": (300, 450),
                "strategic_value": 9,
                "resource_type": "oil",
                "population": 75
            },
            "qazvin": {
                "name": "قزوین",
                "name_en": "Qazvin",
                "pos": (450, 250),
                "strategic_value": 5,
                "resource_type": "agricultural",
                "population": 50
            },
            "semnan": {
                "name": "سمنان",
                "name_en": "Semnan",
                "pos": (550, 250),
                "strategic_value": 4,
                "resource_type": "mining",
                "population": 40
            },
            "qom": {
                "name": "قم",
                "name_en": "Qom",
                "pos": (475, 350),
                "strategic_value": 7,
                "resource_type": "religious",
                "population": 60
            },
            "yazd": {
                "name": "یزد",
                "name_en": "Yazd",
                "pos": (500, 450),
                "strategic_value": 6,
                "resource_type": "desert",
                "population": 55
            },
            "kerman": {
                "name": "کرمان",
                "name_en": "Kerman",
                "pos": (550, 500),
                "strategic_value": 6,
                "resource_type": "mining",
                "population": 65
            },
            "bushehr": {
                "name": "بوشهر",
                "name_en": "Bushehr",
                "pos": (350, 500),
                "strategic_value": 8,
                "resource_type": "port",
                "population": 70
            },
            "zanjan": {
                "name": "زنجان",
                "name_en": "Zanjan",
                "pos": (400, 200),
                "strategic_value": 5,
                "resource_type": "industrial",
                "population": 45
            },
            "ardabil": {
                "name": "اردبیل",
                "name_en": "Ardabil",
                "pos": (350, 100),
                "strategic_value": 4,
                "resource_type": "agricultural",
                "population": 35
            },
            "lorestan": {
                "name": "لرستان",
                "name_en": "Lorestan",
                "pos": (350, 400),
                "strategic_value": 5,
                "resource_type": "mountainous",
                "population": 50
            },
            "chaharmahal": {
                "name": "چهارمحال و بختیاری",
                "name_en": "Chaharmahal",
                "pos": (400, 450),
                "strategic_value": 4,
                "resource_type": "mountainous",
                "population": 40
            },
            "khorasan": {
                "name": "خراسان",
                "name_en": "Khorasan",
                "pos": (700, 250),
                "strategic_value": 6,
                "resource_type": "border",
                "population": 60
            },
            "fars": {
                "name": "فارس",
                "name_en": "Fars",
                "pos": (450, 520),
                "strategic_value": 7,
                "resource_type": "cultural",
                "population": 75
            },
            "khuzestan": {
                "name": "خوزستان",
                "name_en": "Khuzestan",
                "pos": (280, 480),
                "strategic_value": 9,
                "resource_type": "oil",
                "population": 80
            },
            "mazandaran": {
                "name": "مازندران",
                "name_en": "Mazandaran",
                "pos": (500, 180),
                "strategic_value": 6,
                "resource_type": "coastal",
                "population": 65
            },
            "golestan": {
                "name": "گلستان",
                "name_en": "Golestan",
                "pos": (580, 150),
                "strategic_value": 5,
                "resource_type": "agricultural",
                "population": 50
            },
            "hamedan": {
                "name": "همدان",
                "name_en": "Hamedan",
                "pos": (380, 300),
                "strategic_value": 5,
                "resource_type": "historical",
                "population": 55
            },
            "kurdistan": {
                "name": "کردستان",
                "name_en": "Kurdistan",
                "pos": (320, 250),
                "strategic_value": 6,
                "resource_type": "mountainous",
                "population": 60
            },
            "west_azerbaijan": {
                "name": "آذربایجان غربی",
                "name_en": "West Azerbaijan",
                "pos": (300, 150),
                "strategic_value": 7,
                "resource_type": "border",
                "population": 70
            },
            "east_azerbaijan": {
                "name": "آذربایجان شرقی",
                "name_en": "East Azerbaijan",
                "pos": (380, 120),
                "strategic_value": 7,
                "resource_type": "industrial",
                "population": 75
            }
        }
        
        return regions
    
    def create_neighbor_map(self) -> Dict[str, List[str]]:
        """Create adjacency map for regions"""
        neighbors = {
            "tehran": ["qazvin", "semnan", "qom", "mazandaran"],
            "isfahan": ["qom", "yazd", "chaharmahal", "lorestan"],
            "shiraz": ["isfahan", "bushehr", "kerman", "fars"],
            "mashhad": ["semnan", "khorasan", "golestan"],
            "tabriz": ["ardabil", "zanjan", "east_azerbaijan"],
            "ahvaz": ["lorestan", "bushehr", "khuzestan"],
            "qazvin": ["tehran", "zanjan", "hamedan"],
            "semnan": ["tehran", "mashhad", "mazandaran"],
            "qom": ["tehran", "isfahan", "hamedan"],
            "yazd": ["isfahan", "kerman", "fars"],
            "kerman": ["yazd", "shiraz", "fars"],
            "bushehr": ["shiraz", "ahvaz", "khuzestan"],
            "zanjan": ["tabriz", "qazvin", "kurdistan"],
            "ardabil": ["tabriz", "east_azerbaijan"],
            "lorestan": ["ahvaz", "isfahan", "hamedan"],
            "chaharmahal": ["isfahan", "lorestan"],
            "khorasan": ["mashhad", "golestan"],
            "fars": ["shiraz", "yazd", "kerman"],
            "khuzestan": ["ahvaz", "bushehr"],
            "mazandaran": ["tehran", "semnan", "golestan"],
            "golestan": ["mazandaran", "mashhad", "khorasan"],
            "hamedan": ["qazvin", "qom", "lorestan", "kurdistan"],
            "kurdistan": ["zanjan", "hamedan", "west_azerbaijan"],
            "west_azerbaijan": ["kurdistan", "east_azerbaijan"],
            "east_azerbaijan": ["west_azerbaijan", "ardabil", "tabriz"]
        }
        
        return neighbors
    
    def get_regions(self) -> Dict:
        """Get all regions with game properties"""
        game_regions = {}
        
        for region_id, region_data in self.regions.items():
            game_regions[region_id] = {
                "name": region_data["name"],
                "name_en": region_data["name_en"],
                "pos": region_data["pos"],
                "strategic_value": region_data["strategic_value"],
                "resource_type": region_data["resource_type"],
                "population": region_data["population"],
                "neighbors": self.region_neighbors.get(region_id, []),
                "owner": None,
                "soldiers": 0,
                "buildings": {"barracks": 0, "factory": 0, "bank": 0}
            }
        
        return game_regions
    
    def are_neighbors(self, region1: str, region2: str) -> bool:
        """Check if two regions are neighbors"""
        return region2 in self.region_neighbors.get(region1, [])
    
    def get_neighbors(self, region_id: str) -> List[str]:
        """Get all neighbors of a region"""
        return self.region_neighbors.get(region_id, [])
    
    def get_distance(self, region1: str, region2: str) -> float:
        """Calculate distance between two regions"""
        if region1 not in self.regions or region2 not in self.regions:
            return float('inf')
        
        pos1 = self.regions[region1]["pos"]
        pos2 = self.regions[region2]["pos"]
        
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5
    
    def get_shortest_path(self, start: str, end: str) -> List[str]:
        """Find shortest path between two regions using BFS"""
        if start == end:
            return [start]
        
        queue = [(start, [start])]
        visited = {start}
        
        while queue:
            current, path = queue.pop(0)
            
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    new_path = path + [neighbor]
                    
                    if neighbor == end:
                        return new_path
                    
                    queue.append((neighbor, new_path))
                    visited.add(neighbor)
        
        return []  # No path found
    
    def get_regions_by_resource(self, resource_type: str) -> List[str]:
        """Get all regions with specific resource type"""
        return [region_id for region_id, region_data in self.regions.items()
                if region_data["resource_type"] == resource_type]
    
    def get_strategic_regions(self, min_value: int = 7) -> List[str]:
        """Get regions with high strategic value"""
        return [region_id for region_id, region_data in self.regions.items()
                if region_data["strategic_value"] >= min_value]
    
    def get_border_regions(self) -> List[str]:
        """Get regions that are on the border"""
        return self.get_regions_by_resource("border")
    
    def get_coastal_regions(self) -> List[str]:
        """Get coastal regions"""
        return self.get_regions_by_resource("coastal") + self.get_regions_by_resource("port")
    
    def calculate_region_connectivity(self, region_id: str) -> int:
        """Calculate how connected a region is (number of neighbors)"""
        return len(self.get_neighbors(region_id))
    
    def get_central_regions(self) -> List[str]:
        """Get regions with high connectivity (central regions)"""
        connectivity = {}
        for region_id in self.regions:
            connectivity[region_id] = self.calculate_region_connectivity(region_id)
        
        # Get regions with above-average connectivity
        avg_connectivity = sum(connectivity.values()) / len(connectivity)
        return [region_id for region_id, conn in connectivity.items() if conn > avg_connectivity]
    
    def assign_regions_to_players(self, num_players: int) -> Dict[int, List[str]]:
        """Assign regions equally to players"""
        if num_players < 2 or num_players > 8:
            raise ValueError("Number of players must be between 2 and 8")
        
        regions_list = list(self.regions.keys())
        random.shuffle(regions_list)
        
        regions_per_player = len(regions_list) // num_players
        assignments = {}
        
        for player_id in range(num_players):
            start_idx = player_id * regions_per_player
            end_idx = start_idx + regions_per_player
            
            if player_id == num_players - 1:  # Last player gets remaining regions
                assignments[player_id] = regions_list[start_idx:]
            else:
                assignments[player_id] = regions_list[start_idx:end_idx]
        
        return assignments
    
    def get_region_clusters(self, regions: List[str]) -> List[List[str]]:
        """Group regions into connected clusters"""
        if not regions:
            return []
        
        clusters = []
        remaining = set(regions)
        
        while remaining:
            # Start new cluster with any remaining region
            cluster = []
            queue = [remaining.pop()]
            
            while queue:
                current = queue.pop(0)
                cluster.append(current)
                
                # Add connected neighbors to queue
                for neighbor in self.get_neighbors(current):
                    if neighbor in remaining:
                        queue.append(neighbor)
                        remaining.remove(neighbor)
            
            clusters.append(cluster)
        
        return clusters
