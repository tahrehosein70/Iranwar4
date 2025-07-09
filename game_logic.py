import random
import math
from typing import Dict, List, Optional, Tuple

class GameLogic:
    def __init__(self):
        self.battle_randomness = 0.3  # 30% randomness in battles
        self.soldier_reduction_rate = 0.1  # 10% reduction every 10 minutes
        self.building_effects = {
            'barracks': {'soldiers_per_turn': 5, 'cost': 200},
            'factory': {'income_multiplier': 1.5, 'cost': 500},
            'bank': {'income_bonus': 50, 'cost': 300}
        }
    
    def calculate_battle_result(self, attacking_soldiers: int, defending_soldiers: int, 
                              attacker_buildings: Dict = None, defender_buildings: Dict = None) -> Tuple[bool, int, int]:
        """
        Calculate battle result between attacking and defending forces
        Returns: (attacker_wins, remaining_attackers, remaining_defenders)
        """
        if attacker_buildings is None:
            attacker_buildings = {}
        if defender_buildings is None:
            defender_buildings = {}
        
        # Base combat values
        attack_power = attacking_soldiers
        defense_power = defending_soldiers
        
        # Apply building bonuses
        barracks_bonus = attacker_buildings.get('barracks', 0) * 0.1
        defense_bonus = defender_buildings.get('barracks', 0) * 0.15
        
        attack_power *= (1 + barracks_bonus)
        defense_power *= (1 + defense_bonus + 0.2)  # Defender advantage
        
        # Add randomness
        attack_power *= (1 + random.uniform(-self.battle_randomness, self.battle_randomness))
        defense_power *= (1 + random.uniform(-self.battle_randomness, self.battle_randomness))
        
        # Calculate casualties
        attacker_casualties = int(defending_soldiers * 0.3 + random.randint(0, defending_soldiers // 4))
        defender_casualties = int(attacking_soldiers * 0.4 + random.randint(0, attacking_soldiers // 3))
        
        # Apply casualties
        remaining_attackers = max(0, attacking_soldiers - attacker_casualties)
        remaining_defenders = max(0, defending_soldiers - defender_casualties)
        
        # Determine winner
        attacker_wins = attack_power > defense_power
        
        if attacker_wins:
            # Attacker wins but loses some soldiers
            remaining_attackers = max(1, remaining_attackers // 2)
            remaining_defenders = 0
        else:
            # Defender wins
            remaining_attackers = 0
            remaining_defenders = max(1, remaining_defenders)
        
        return attacker_wins, remaining_attackers, remaining_defenders
    
    def calculate_income(self, regions: List[Dict], buildings: Dict) -> int:
        """Calculate player's income based on regions and buildings"""
        base_income = len(regions) * 10  # 10 coins per region
        
        # Building bonuses
        factory_bonus = buildings.get('factory', 0) * 25
        bank_bonus = buildings.get('bank', 0) * self.building_effects['bank']['income_bonus']
        
        # Factory multiplier
        factory_multiplier = 1 + (buildings.get('factory', 0) * 0.5)
        
        total_income = (base_income + factory_bonus + bank_bonus) * factory_multiplier
        return int(total_income)
    
    def calculate_soldier_production(self, buildings: Dict) -> int:
        """Calculate soldier production based on barracks"""
        return buildings.get('barracks', 0) * self.building_effects['barracks']['soldiers_per_turn']
    
    def apply_soldier_reduction(self, soldiers: int) -> int:
        """Apply periodic soldier reduction"""
        reduction = max(1, int(soldiers * self.soldier_reduction_rate))
        return max(0, soldiers - reduction)
    
    def get_building_cost(self, building_type: str) -> int:
        """Get cost of building"""
        return self.building_effects.get(building_type, {}).get('cost', 0)
    
    def is_valid_attack_target(self, attacker_regions: List[str], target_region: str, 
                              region_neighbors: Dict) -> bool:
        """Check if target region is valid for attack"""
        # Check if attacker has a neighboring region
        for attacker_region in attacker_regions:
            if target_region in region_neighbors.get(attacker_region, []):
                return True
        return False
    
    def calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate distance between two positions"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def get_victory_condition(self, players: Dict) -> Optional[str]:
        """Check if any player has won the game"""
        active_players = [pid for pid, player in players.items() if player.get('connected', False)]
        
        if len(active_players) <= 1:
            return active_players[0] if active_players else None
        
        # Check if any player controls majority of regions
        total_regions = sum(len(player.get('regions', [])) for player in players.values())
        
        for player_id, player in players.items():
            if player.get('connected', False):
                player_regions = len(player.get('regions', []))
                if player_regions > total_regions * 0.6:  # 60% of regions
                    return player_id
        
        return None
    
    def calculate_region_value(self, region: Dict) -> int:
        """Calculate strategic value of a region"""
        base_value = 10
        
        # Building values
        building_value = sum(region.get('buildings', {}).values()) * 50
        
        # Soldier value
        soldier_value = region.get('soldiers', 0) * 2
        
        return base_value + building_value + soldier_value
    
    def suggest_best_targets(self, attacker_regions: List[str], all_regions: Dict, 
                            region_neighbors: Dict) -> List[str]:
        """Suggest best targets for attack"""
        possible_targets = []
        
        for attacker_region in attacker_regions:
            neighbors = region_neighbors.get(attacker_region, [])
            for neighbor in neighbors:
                if neighbor not in attacker_regions:  # Not owned by attacker
                    possible_targets.append(neighbor)
        
        # Remove duplicates
        possible_targets = list(set(possible_targets))
        
        # Sort by strategic value
        target_values = []
        for target in possible_targets:
            if target in all_regions:
                value = self.calculate_region_value(all_regions[target])
                target_values.append((target, value))
        
        target_values.sort(key=lambda x: x[1], reverse=True)
        return [target for target, _ in target_values[:3]]  # Return top 3 targets
    
    def simulate_battle_outcome(self, attacker_soldiers: int, defender_soldiers: int, 
                               simulations: int = 100) -> Dict:
        """Simulate multiple battles to get probability of success"""
        wins = 0
        total_attacker_losses = 0
        total_defender_losses = 0
        
        for _ in range(simulations):
            attacker_wins, remaining_attackers, remaining_defenders = self.calculate_battle_result(
                attacker_soldiers, defender_soldiers
            )
            
            if attacker_wins:
                wins += 1
            
            total_attacker_losses += (attacker_soldiers - remaining_attackers)
            total_defender_losses += (defender_soldiers - remaining_defenders)
        
        return {
            'win_probability': wins / simulations,
            'avg_attacker_losses': total_attacker_losses / simulations,
            'avg_defender_losses': total_defender_losses / simulations
        }
    
    def get_optimal_soldier_allocation(self, total_soldiers: int, regions: List[Dict], 
                                     threats: Dict) -> Dict:
        """Calculate optimal soldier allocation across regions"""
        if not regions:
            return {}
        
        allocation = {}
        
        # Base allocation
        base_allocation = total_soldiers // len(regions)
        
        for region in regions:
            region_id = region.get('id')
            if region_id:
                threat_level = threats.get(region_id, 0)
                
                # Allocate more soldiers to threatened regions
                if threat_level > 0:
                    allocation[region_id] = base_allocation + (threat_level * 5)
                else:
                    allocation[region_id] = base_allocation
        
        # Normalize allocation to match total soldiers
        total_allocated = sum(allocation.values())
        if total_allocated > 0:
            scaling_factor = total_soldiers / total_allocated
            for region_id in allocation:
                allocation[region_id] = int(allocation[region_id] * scaling_factor)
        
        return allocation
