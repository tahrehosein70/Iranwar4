from flask import Flask, render_template, request, jsonify
import json
import threading
import time
import random
from datetime import datetime, timedelta
from game_logic import GameLogic
from iran_map import IranMap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'iran_war_game_secret'

# Global game state
games = {}
game_logic = GameLogic()
iran_map = IranMap()

class Game:
    def __init__(self, game_id, host_player):
        self.game_id = game_id
        self.players = {}
        self.regions = {}
        self.game_state = "waiting"  # waiting, playing, finished
        self.host = host_player
        self.max_players = 8
        self.min_players = 2
        self.last_reduction_time = datetime.now()
        self.turn_order = []
        self.current_turn = 0
        self.initialize_regions()
    
    def initialize_regions(self):
        """Initialize Iran map regions"""
        self.regions = iran_map.get_regions()
        for region_id, region in self.regions.items():
            region['owner'] = None
            region['soldiers'] = 0
            region['buildings'] = {'barracks': 0, 'factory': 0, 'bank': 0}
    
    def add_player(self, player_id, player_name):
        if len(self.players) >= self.max_players:
            return False
        
        self.players[player_id] = {
            'name': player_name,
            'coins': 1000,
            'soldiers': 100,
            'companies': 1,
            'color': self.get_player_color(len(self.players)),
            'regions': [],
            'connected': True
        }
        
        # Assign regions to player
        self.assign_regions_to_player(player_id)
        return True
    
    def get_player_color(self, player_index):
        colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#FFA500', '#800080']
        return colors[player_index % len(colors)]
    
    def assign_regions_to_player(self, player_id):
        """Assign regions equally to players"""
        total_regions = len(self.regions)
        player_count = len(self.players)
        regions_per_player = total_regions // player_count
        
        # Get unassigned regions
        unassigned_regions = [rid for rid, region in self.regions.items() if region['owner'] is None]
        
        # Assign regions to this player
        player_regions = random.sample(unassigned_regions, min(regions_per_player, len(unassigned_regions)))
        
        for region_id in player_regions:
            self.regions[region_id]['owner'] = player_id
            self.regions[region_id]['soldiers'] = 10
            self.players[player_id]['regions'].append(region_id)
    
    def can_attack(self, attacker_id, from_region, to_region):
        """Check if attack is valid"""
        if from_region not in self.regions or to_region not in self.regions:
            return False
        
        if self.regions[from_region]['owner'] != attacker_id:
            return False
        
        if self.regions[to_region]['owner'] == attacker_id:
            return False
        
        # Check if regions are neighbors
        return iran_map.are_neighbors(from_region, to_region)
    
    def execute_attack(self, attacker_id, from_region, to_region, soldiers):
        """Execute attack between regions"""
        if not self.can_attack(attacker_id, from_region, to_region):
            return False
        
        if self.regions[from_region]['soldiers'] <= soldiers:
            return False
        
        # Calculate battle result
        attacking_soldiers = soldiers
        defending_soldiers = self.regions[to_region]['soldiers']
        
        # Use game logic for battle calculation
        attacker_wins, remaining_attackers, remaining_defenders = game_logic.calculate_battle_result(
            attacking_soldiers, defending_soldiers
        )
        
        if attacker_wins:
            # Attacker wins
            self.regions[to_region]['owner'] = attacker_id
            self.regions[to_region]['soldiers'] = remaining_attackers
            self.regions[from_region]['soldiers'] -= soldiers
            
            # Update player regions
            old_owner = None
            for pid, player in self.players.items():
                if to_region in player['regions']:
                    old_owner = pid
                    player['regions'].remove(to_region)
                    break
            
            self.players[attacker_id]['regions'].append(to_region)
            return True
        else:
            # Defender wins
            self.regions[from_region]['soldiers'] -= soldiers
            self.regions[to_region]['soldiers'] = remaining_defenders
            return False
    
    def build_structure(self, player_id, region_id, structure_type):
        """Build structure in region"""
        if region_id not in self.regions:
            return False
        
        if self.regions[region_id]['owner'] != player_id:
            return False
        
        cost = game_logic.get_building_cost(structure_type)
        
        if self.players[player_id]['coins'] < cost:
            return False
        
        self.players[player_id]['coins'] -= cost
        self.regions[region_id]['buildings'][structure_type] += 1
        return True
    
    def get_game_state(self):
        """Get current game state"""
        return {
            'game_id': self.game_id,
            'players': self.players,
            'regions': self.regions,
            'game_state': self.game_state,
            'current_turn': self.current_turn,
            'turn_order': self.turn_order,
            'host': self.host
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/create_game', methods=['POST'])
def create_game():
    data = request.json
    player_name = data.get('player_name', 'Player')
    player_id = f"player_{int(time.time() * 1000)}"
    game_id = f"game_{len(games) + 1}_{int(time.time())}"
    
    # Create new game
    game = Game(game_id, player_id)
    game.add_player(player_id, player_name)
    games[game_id] = game
    
    return jsonify({
        'success': True,
        'game_id': game_id,
        'player_id': player_id,
        'game_state': game.get_game_state()
    })

@app.route('/api/join_game', methods=['POST'])
def join_game():
    data = request.json
    game_id = data.get('game_id')
    player_name = data.get('player_name', 'Player')
    player_id = f"player_{int(time.time() * 1000)}"
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'بازی پیدا نشد'})
    
    game = games[game_id]
    
    if not game.add_player(player_id, player_name):
        return jsonify({'success': False, 'error': 'بازی پر است'})
    
    return jsonify({
        'success': True,
        'player_id': player_id,
        'game_state': game.get_game_state()
    })

@app.route('/api/start_game', methods=['POST'])
def start_game():
    data = request.json
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'بازی پیدا نشد'})
    
    game = games[game_id]
    
    if player_id != game.host:
        return jsonify({'success': False, 'error': 'فقط میزبان می‌تواند بازی را شروع کند'})
    
    if len(game.players) < game.min_players:
        return jsonify({'success': False, 'error': 'حداقل 2 بازیکن نیاز است'})
    
    game.game_state = "playing"
    game.turn_order = list(game.players.keys())
    random.shuffle(game.turn_order)
    
    return jsonify({
        'success': True,
        'game_state': game.get_game_state()
    })

@app.route('/api/attack', methods=['POST'])
def attack():
    data = request.json
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    from_region = data.get('from_region')
    to_region = data.get('to_region')
    soldiers = data.get('soldiers', 1)
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'بازی پیدا نشد'})
    
    game = games[game_id]
    
    if game.game_state != "playing":
        return jsonify({'success': False, 'error': 'بازی شروع نشده است'})
    
    success = game.execute_attack(player_id, from_region, to_region, soldiers)
    
    return jsonify({
        'success': success,
        'game_state': game.get_game_state(),
        'message': 'حمله موفق بود!' if success else 'حمله ناموفق بود!'
    })

@app.route('/api/build', methods=['POST'])
def build():
    data = request.json
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    region_id = data.get('region_id')
    structure_type = data.get('structure_type')
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'بازی پیدا نشد'})
    
    game = games[game_id]
    
    if game.game_state != "playing":
        return jsonify({'success': False, 'error': 'بازی شروع نشده است'})
    
    success = game.build_structure(player_id, region_id, structure_type)
    
    return jsonify({
        'success': success,
        'game_state': game.get_game_state(),
        'message': 'ساخت موفق بود!' if success else 'ساخت ناموفق بود!'
    })

@app.route('/api/get_game_state', methods=['POST'])
def get_game_state():
    data = request.json
    game_id = data.get('game_id')
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'بازی پیدا نشد'})
    
    game = games[game_id]
    return jsonify({
        'success': True,
        'game_state': game.get_game_state()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)