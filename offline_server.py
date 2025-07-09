#!/usr/bin/env python3
"""
Offline WiFi/Hotspot Server for Iran War Game
Server runs on local WiFi network without internet connection
"""

from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
import threading
import time
import json
import socket
import random
from datetime import datetime
from iran_map import IranMap
from game_logic import GameLogic

app = Flask(__name__)
app.config['SECRET_KEY'] = 'iran_war_offline_2025'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global game state
games = {}
game_logic = GameLogic()
iran_map = IranMap()

class OfflineGame:
    def __init__(self, game_id, host_player):
        self.game_id = game_id
        self.host_player = host_player
        self.players = {host_player['id']: host_player}
        self.status = 'waiting'  # waiting, playing, finished
        self.regions = {}
        self.current_turn = 0
        self.turn_order = []
        self.created_time = datetime.now()
        self.last_activity = datetime.now()
        self.initialize_regions()
        
    def initialize_regions(self):
        """Initialize Iran map regions for offline play"""
        self.regions = iran_map.get_regions()
        
    def add_player(self, player_id, player_name):
        if len(self.players) >= 8:
            return False
            
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', 
                 '#9b59b6', '#1abc9c', '#e67e22', '#95a5a6']
        player_color = colors[len(self.players)]
        
        player = {
            'id': player_id,
            'name': player_name,
            'color': player_color,
            'coins': 100,
            'soldiers': 50,
            'regions': [],
            'buildings': {},
            'is_host': False
        }
        
        self.players[player_id] = player
        self.last_activity = datetime.now()
        return True
        
    def start_game(self):
        if len(self.players) < 2:
            return False
            
        self.status = 'playing'
        self.turn_order = list(self.players.keys())
        random.shuffle(self.turn_order)
        
        # توزیع مناطق بین بازیکنان
        regions_list = list(self.regions.keys())
        random.shuffle(regions_list)
        
        regions_per_player = len(regions_list) // len(self.players)
        remaining_regions = len(regions_list) % len(self.players)
        
        region_index = 0
        for i, player_id in enumerate(self.turn_order):
            player_regions = regions_per_player
            if i < remaining_regions:
                player_regions += 1
                
            for j in range(player_regions):
                if region_index < len(regions_list):
                    region_id = regions_list[region_index]
                    self.regions[region_id]['owner'] = player_id
                    self.regions[region_id]['soldiers'] = 10
                    self.players[player_id]['regions'].append(region_id)
                    region_index += 1
        
        self.last_activity = datetime.now()
        return True
        
    def get_current_player(self):
        if not self.turn_order:
            return None
        return self.turn_order[self.current_turn % len(self.turn_order)]
        
    def next_turn(self):
        self.current_turn += 1
        self.last_activity = datetime.now()
        
    def get_game_state(self):
        return {
            'game_id': self.game_id,
            'status': self.status,
            'players': self.players,
            'regions': self.regions,
            'current_player': self.get_current_player(),
            'turn_number': self.current_turn + 1,
            'created_time': self.created_time.isoformat(),
            'last_activity': self.last_activity.isoformat()
        }

def get_local_ip():
    """Get local IP address for WiFi network"""
    try:
        # اتصال به Google DNS برای پیدا کردن IP محلی
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

@app.route('/')
def index():
    return render_template('offline_index.html')

@app.route('/api/server_info')
def server_info():
    """اطلاعات سرور برای نمایش در کلاینت"""
    return jsonify({
        'server_ip': get_local_ip(),
        'server_port': 5000,
        'status': 'online',
        'mode': 'offline',
        'total_games': len(games),
        'active_players': sum(len(game.players) for game in games.values())
    })

@app.route('/api/create_game', methods=['POST'])
def create_game():
    data = request.get_json()
    player_name = data.get('player_name', 'میزبان')
    
    # تولید Game ID منحصر به فرد
    game_id = ''.join(random.choices('0123456789', k=6))
    while game_id in games:
        game_id = ''.join(random.choices('0123456789', k=6))
    
    # ایجاد بازیکن میزبان
    host_player = {
        'id': f'player_{random.randint(1000, 9999)}',
        'name': player_name,
        'color': '#e74c3c',
        'coins': 100,
        'soldiers': 50,
        'regions': [],
        'buildings': {},
        'is_host': True
    }
    
    # ایجاد بازی جدید
    game = OfflineGame(game_id, host_player)
    games[game_id] = game
    
    return jsonify({
        'success': True,
        'game_id': game_id,
        'player_id': host_player['id'],
        'server_ip': get_local_ip(),
        'message': f'بازی با شناسه {game_id} ایجاد شد'
    })

@app.route('/api/join_game', methods=['POST'])
def join_game():
    data = request.get_json()
    game_id = data.get('game_id')
    player_name = data.get('player_name', 'بازیکن')
    
    if game_id not in games:
        return jsonify({
            'success': False,
            'message': 'بازی پیدا نشد'
        })
    
    game = games[game_id]
    
    if game.status != 'waiting':
        return jsonify({
            'success': False,
            'message': 'بازی قبلاً شروع شده است'
        })
    
    player_id = f'player_{random.randint(1000, 9999)}'
    success = game.add_player(player_id, player_name)
    
    if not success:
        return jsonify({
            'success': False,
            'message': 'بازی پر است (حداکثر 8 نفر)'
        })
    
    # اطلاع‌رسانی به سایر بازیکنان
    socketio.emit('player_joined', {
        'player_name': player_name,
        'total_players': len(game.players)
    })
    
    return jsonify({
        'success': True,
        'player_id': player_id,
        'game_id': game_id,
        'message': f'{player_name} به بازی پیوست'
    })

@app.route('/api/start_game', methods=['POST'])
def start_game():
    data = request.get_json()
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    
    if game_id not in games:
        return jsonify({
            'success': False,
            'message': 'بازی پیدا نشد'
        })
    
    game = games[game_id]
    
    # تنها میزبان می‌تواند بازی را شروع کند
    if not game.players[player_id]['is_host']:
        return jsonify({
            'success': False,
            'message': 'فقط میزبان می‌تواند بازی را شروع کند'
        })
    
    success = game.start_game()
    
    if not success:
        return jsonify({
            'success': False,
            'message': 'حداقل 2 بازیکن لازم است'
        })
    
    # اطلاع‌رسانی شروع بازی
    socketio.emit('game_started', {
        'message': 'بازی شروع شد!',
        'current_player': game.get_current_player()
    })
    
    return jsonify({
        'success': True,
        'message': 'بازی شروع شد'
    })

@app.route('/api/get_game_state', methods=['POST'])
def get_game_state():
    data = request.get_json()
    game_id = data.get('game_id')
    
    if game_id not in games:
        return jsonify({
            'success': False,
            'message': 'بازی پیدا نشد'
        })
    
    game = games[game_id]
    return jsonify({
        'success': True,
        'game_state': game.get_game_state()
    })

@app.route('/api/attack', methods=['POST'])
def attack():
    data = request.get_json()
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    from_region = data.get('from_region')
    to_region = data.get('to_region')
    soldiers = data.get('soldiers', 10)
    
    if game_id not in games:
        return jsonify({
            'success': False,
            'message': 'بازی پیدا نشد'
        })
    
    game = games[game_id]
    
    # بررسی نوبت بازیکن
    if game.get_current_player() != player_id:
        return jsonify({
            'success': False,
            'message': 'نوبت شما نیست'
        })
    
    # اجرای حمله
    if from_region not in game.regions or to_region not in game.regions:
        return jsonify({
            'success': False,
            'message': 'منطقه معتبر نیست'
        })
    
    # بررسی مالکیت منطقه مهاجم
    if game.regions[from_region]['owner'] != player_id:
        return jsonify({
            'success': False,
            'message': 'این منطقه متعلق به شما نیست'
        })
    
    # بررسی تعداد سربازان
    if game.regions[from_region]['soldiers'] <= soldiers:
        return jsonify({
            'success': False,
            'message': 'تعداد سربازان کافی نیست'
        })
    
    # محاسبه نتیجه نبرد
    attacker_soldiers = soldiers
    defender_soldiers = game.regions[to_region]['soldiers']
    
    success, remaining_attackers, remaining_defenders = game_logic.calculate_battle_result(
        attacker_soldiers, defender_soldiers
    )
    
    # اعمال نتیجه
    game.regions[from_region]['soldiers'] -= soldiers
    
    if success:
        # حمله موفق
        old_owner = game.regions[to_region]['owner']
        if old_owner and old_owner in game.players:
            game.players[old_owner]['regions'].remove(to_region)
        
        game.regions[to_region]['owner'] = player_id
        game.regions[to_region]['soldiers'] = remaining_attackers
        game.players[player_id]['regions'].append(to_region)
        
        result_message = f'حمله موفق! {to_region} تصرف شد'
    else:
        # حمله ناموفق
        game.regions[to_region]['soldiers'] = remaining_defenders
        result_message = f'حمله ناموفق! {remaining_defenders} سرباز دشمن باقی ماند'
    
    # اطلاع‌رسانی به تمام بازیکنان
    socketio.emit('attack_result', {
        'success': success,
        'from_region': from_region,
        'to_region': to_region,
        'attacker': game.players[player_id]['name'],
        'message': result_message
    })
    
    return jsonify({
        'success': True,
        'attack_successful': success,
        'message': result_message
    })

# تنظیمات Socket.IO
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_game_room')
def handle_join_room(data):
    game_id = data.get('game_id')
    if game_id in games:
        join_room(game_id)
        emit('joined_room', {'game_id': game_id})

def cleanup_old_games():
    """پاکسازی بازی‌های قدیمی"""
    while True:
        time.sleep(300)  # هر 5 دقیقه چک کن
        current_time = datetime.now()
        to_remove = []
        
        for game_id, game in games.items():
            # بازی‌های بیش از 2 ساعت بی‌استفاده را پاک کن
            if (current_time - game.last_activity).seconds > 7200:
                to_remove.append(game_id)
        
        for game_id in to_remove:
            del games[game_id]
            print(f'Removed old game: {game_id}')

if __name__ == '__main__':
    # شروع thread پاکسازی
    cleanup_thread = threading.Thread(target=cleanup_old_games, daemon=True)
    cleanup_thread.start()
    
    # نمایش اطلاعات شبکه
    local_ip = get_local_ip()
    print(f"""
    ====================================
    🎮 سرور آفلاین جنگ منطقه‌ای ایران
    ====================================
    
    📡 آدرس سرور: {local_ip}:5000
    🔗 لینک کامل: http://{local_ip}:5000
    
    📱 برای اتصال از گوشی:
    1. به همان WiFi وصل شوید
    2. آدرس بالا را در مرورگر باز کنید
    3. بازی کنید!
    
    📋 دستورات:
    - Ctrl+C برای توقف سرور
    - کلیدهای بازی در صفحه وب
    ====================================
    """)
    
    # اجرای سرور
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=True, log_output=True)