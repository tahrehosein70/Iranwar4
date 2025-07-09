from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
import json
import threading
import time
import random
from datetime import datetime, timedelta
from game_logic import GameLogic
from iran_map import IranMap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'iran_war_game_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

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
        
        # Simple battle calculation
        attacker_wins = attacking_soldiers > defending_soldiers * 0.8
        
        if attacker_wins:
            # Attacker wins
            remaining_soldiers = max(1, attacking_soldiers - defending_soldiers // 2)
            self.regions[to_region]['owner'] = attacker_id
            self.regions[to_region]['soldiers'] = remaining_soldiers
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
            self.regions[to_region]['soldiers'] -= soldiers // 2
            return False
    
    def build_structure(self, player_id, region_id, structure_type):
        """Build structure in region"""
        if region_id not in self.regions:
            return False
        
        if self.regions[region_id]['owner'] != player_id:
            return False
        
        costs = {'barracks': 200, 'factory': 500, 'bank': 300}
        
        if structure_type not in costs:
            return False
        
        if self.players[player_id]['coins'] < costs[structure_type]:
            return False
        
        self.players[player_id]['coins'] -= costs[structure_type]
        self.regions[region_id]['buildings'][structure_type] += 1
        return True
    
    def reduce_soldiers(self):
        """Reduce soldiers every 10 minutes"""
        now = datetime.now()
        if now - self.last_reduction_time >= timedelta(minutes=10):
            for region_id, region in self.regions.items():
                if region['soldiers'] > 0:
                    reduction = max(1, region['soldiers'] // 10)
                    region['soldiers'] = max(0, region['soldiers'] - reduction)
            
            self.last_reduction_time = now
            return True
        return False
    
    def get_game_state(self):
        """Get current game state"""
        return {
            'game_id': self.game_id,
            'players': self.players,
            'regions': self.regions,
            'game_state': self.game_state,
            'current_turn': self.current_turn,
            'turn_order': self.turn_order
        }

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    emit('connected', {'status': 'success'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    # Handle player disconnection
    for game_id, game in games.items():
        if request.sid in game.players:
            game.players[request.sid]['connected'] = False
            emit('player_disconnected', {'player_id': request.sid}, room=game_id)

@socketio.on('create_game')
def handle_create_game(data):
    player_name = data.get('player_name', 'Player')
    game_id = f"game_{len(games) + 1}_{int(time.time())}"
    
    # Create new game
    game = Game(game_id, request.sid)
    game.add_player(request.sid, player_name)
    games[game_id] = game
    
    # Join room
    join_room(game_id)
    
    emit('game_created', {
        'game_id': game_id,
        'player_id': request.sid,
        'game_state': game.get_game_state()
    })

@socketio.on('join_game')
def handle_join_game(data):
    game_id = data.get('game_id')
    player_name = data.get('player_name', 'Player')
    
    if game_id not in games:
        emit('error', {'message': 'بازی پیدا نشد'})
        return
    
    game = games[game_id]
    
    if not game.add_player(request.sid, player_name):
        emit('error', {'message': 'بازی پر است'})
        return
    
    # Join room
    join_room(game_id)
    
    # Notify all players
    emit('player_joined', {
        'player_id': request.sid,
        'player_name': player_name,
        'game_state': game.get_game_state()
    }, room=game_id)

@socketio.on('start_game')
def handle_start_game(data):
    game_id = data.get('game_id')
    
    if game_id not in games:
        emit('error', {'message': 'بازی پیدا نشد'})
        return
    
    game = games[game_id]
    
    if request.sid != game.host:
        emit('error', {'message': 'فقط میزبان می‌تواند بازی را شروع کند'})
        return
    
    if len(game.players) < game.min_players:
        emit('error', {'message': 'حداقل 2 بازیکن نیاز است'})
        return
    
    game.game_state = "playing"
    game.turn_order = list(game.players.keys())
    random.shuffle(game.turn_order)
    
    emit('game_started', {
        'game_state': game.get_game_state()
    }, room=game_id)

@socketio.on('attack')
def handle_attack(data):
    game_id = data.get('game_id')
    from_region = data.get('from_region')
    to_region = data.get('to_region')
    soldiers = data.get('soldiers', 1)
    
    if game_id not in games:
        emit('error', {'message': 'بازی پیدا نشد'})
        return
    
    game = games[game_id]
    
    if game.game_state != "playing":
        emit('error', {'message': 'بازی شروع نشده است'})
        return
    
    success = game.execute_attack(request.sid, from_region, to_region, soldiers)
    
    if success:
        emit('attack_success', {
            'attacker': request.sid,
            'from_region': from_region,
            'to_region': to_region,
            'soldiers': soldiers,
            'game_state': game.get_game_state()
        }, room=game_id)
    else:
        emit('attack_failed', {
            'message': 'حمله ناموفق بود'
        })

@socketio.on('build')
def handle_build(data):
    game_id = data.get('game_id')
    region_id = data.get('region_id')
    structure_type = data.get('structure_type')
    
    if game_id not in games:
        emit('error', {'message': 'بازی پیدا نشد'})
        return
    
    game = games[game_id]
    
    if game.game_state != "playing":
        emit('error', {'message': 'بازی شروع نشده است'})
        return
    
    success = game.build_structure(request.sid, region_id, structure_type)
    
    if success:
        emit('build_success', {
            'player_id': request.sid,
            'region_id': region_id,
            'structure_type': structure_type,
            'game_state': game.get_game_state()
        }, room=game_id)
    else:
        emit('build_failed', {
            'message': 'ساخت ناموفق بود'
        })

@socketio.on('get_game_state')
def handle_get_game_state(data):
    game_id = data.get('game_id')
    
    if game_id not in games:
        emit('error', {'message': 'بازی پیدا نشد'})
        return
    
    game = games[game_id]
    emit('game_state_update', game.get_game_state())

def soldier_reduction_thread():
    """Background thread to reduce soldiers every 10 minutes"""
    while True:
        time.sleep(60)  # Check every minute
        for game_id, game in games.items():
            if game.game_state == "playing":
                if game.reduce_soldiers():
                    socketio.emit('soldiers_reduced', {
                        'game_state': game.get_game_state()
                    }, room=game_id)

if __name__ == '__main__':
    # Start soldier reduction thread
    reduction_thread = threading.Thread(target=soldier_reduction_thread, daemon=True)
    reduction_thread.start()
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
