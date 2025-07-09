#!/usr/bin/env python3
"""
Complete Offline Hotspot Game - Iran War
Self-contained APK that runs local server on device
Works with mobile hotspot - no external dependencies
"""

import os
import sys
import threading
import time
import socket
import random
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import socketserver

# Embedded game data and logic
IRAN_REGIONS = {
    'tehran': {'name': 'تهران', 'x': 400, 'y': 300, 'population': 15000000, 'type': 'capital'},
    'isfahan': {'name': 'اصفهان', 'x': 380, 'y': 250, 'population': 5000000, 'type': 'cultural'},
    'mashhad': {'name': 'مشهد', 'x': 500, 'y': 320, 'population': 3500000, 'type': 'religious'},
    'shiraz': {'name': 'شیراز', 'x': 380, 'y': 200, 'population': 2000000, 'type': 'cultural'},
    'tabriz': {'name': 'تبریز', 'x': 320, 'y': 380, 'population': 1800000, 'type': 'industrial'},
    'ahvaz': {'name': 'اهواز', 'x': 300, 'y': 220, 'population': 1500000, 'type': 'industrial'},
    'qom': {'name': 'قم', 'x': 390, 'y': 280, 'population': 1200000, 'type': 'religious'},
    'karaj': {'name': 'کرج', 'x': 390, 'y': 310, 'population': 1100000, 'type': 'industrial'},
    'urmia': {'name': 'ارومیه', 'x': 300, 'y': 380, 'population': 900000, 'type': 'cultural'},
    'arak': {'name': 'اراک', 'x': 370, 'y': 270, 'population': 800000, 'type': 'industrial'},
    'yazd': {'name': 'یزد', 'x': 420, 'y': 240, 'population': 700000, 'type': 'cultural'},
    'ardabil': {'name': 'اردبیل', 'x': 340, 'y': 400, 'population': 650000, 'type': 'industrial'},
    'bandar_abbas': {'name': 'بندرعباس', 'x': 420, 'y': 160, 'population': 600000, 'type': 'port'},
    'abadan': {'name': 'آبادان', 'x': 280, 'y': 200, 'population': 400000, 'type': 'port'},
    'kish': {'name': 'کیش', 'x': 430, 'y': 150, 'population': 50000, 'type': 'port'}
}

REGION_NEIGHBORS = {
    'tehran': ['karaj', 'qom', 'arak'],
    'isfahan': ['yazd', 'shiraz', 'arak'],
    'mashhad': ['ardabil'],
    'shiraz': ['isfahan', 'yazd'],
    'tabriz': ['urmia', 'ardabil'],
    'ahvaz': ['abadan'],
    'qom': ['tehran', 'arak'],
    'karaj': ['tehran'],
    'urmia': ['tabriz'],
    'arak': ['tehran', 'qom', 'isfahan'],
    'yazd': ['isfahan', 'shiraz'],
    'ardabil': ['tabriz', 'mashhad'],
    'bandar_abbas': ['kish'],
    'abadan': ['ahvaz'],
    'kish': ['bandar_abbas']
}

# Global game state
games = {}

class GameState:
    def __init__(self, game_id, host_name):
        self.game_id = game_id
        self.players = {}
        self.regions = {}
        self.status = 'waiting'  # waiting, playing, finished
        self.current_turn = 0
        self.turn_order = []
        self.created_time = time.time()
        self.last_activity = time.time()
        
        # Initialize regions
        for region_id, region_data in IRAN_REGIONS.items():
            self.regions[region_id] = {
                **region_data,
                'owner': None,
                'soldiers': 0,
                'buildings': []
            }
        
        # Add host player
        host_id = f'player_{random.randint(1000, 9999)}'
        self.players[host_id] = {
            'id': host_id,
            'name': host_name,
            'color': '#e74c3c',
            'coins': 100,
            'soldiers': 50,
            'regions': [],
            'buildings': {},
            'is_host': True
        }
    
    def add_player(self, player_name):
        if len(self.players) >= 8:
            return None
        
        colors = ['#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#95a5a6']
        player_color = colors[len(self.players) - 1] if len(self.players) <= len(colors) else '#888888'
        
        player_id = f'player_{random.randint(1000, 9999)}'
        self.players[player_id] = {
            'id': player_id,
            'name': player_name,
            'color': player_color,
            'coins': 100,
            'soldiers': 50,
            'regions': [],
            'buildings': {},
            'is_host': False
        }
        
        self.last_activity = time.time()
        return player_id
    
    def start_game(self):
        if len(self.players) < 2:
            return False
        
        self.status = 'playing'
        self.turn_order = list(self.players.keys())
        random.shuffle(self.turn_order)
        
        # Distribute regions
        regions_list = list(self.regions.keys())
        random.shuffle(regions_list)
        
        regions_per_player = len(regions_list) // len(self.players)
        region_index = 0
        
        for player_id in self.turn_order:
            for _ in range(regions_per_player):
                if region_index < len(regions_list):
                    region_id = regions_list[region_index]
                    self.regions[region_id]['owner'] = player_id
                    self.regions[region_id]['soldiers'] = 10
                    self.players[player_id]['regions'].append(region_id)
                    region_index += 1
        
        self.last_activity = time.time()
        return True
    
    def get_current_player(self):
        if not self.turn_order:
            return None
        return self.turn_order[self.current_turn % len(self.turn_order)]
    
    def execute_attack(self, player_id, from_region, to_region, soldiers):
        if self.get_current_player() != player_id:
            return False, "نوبت شما نیست"
        
        if from_region not in self.regions or to_region not in self.regions:
            return False, "منطقه معتبر نیست"
        
        if self.regions[from_region]['owner'] != player_id:
            return False, "این منطقه متعلق به شما نیست"
        
        if self.regions[from_region]['soldiers'] <= soldiers:
            return False, "سربازان کافی ندارید"
        
        # Check if regions are neighbors
        if to_region not in REGION_NEIGHBORS.get(from_region, []):
            return False, "مناطق همسایه نیستند"
        
        # Battle calculation
        attacker_strength = soldiers + random.randint(-2, 3)
        defender_strength = self.regions[to_region]['soldiers'] + random.randint(-1, 4)
        
        # Execute attack
        self.regions[from_region]['soldiers'] -= soldiers
        
        if attacker_strength > defender_strength:
            # Attack successful
            old_owner = self.regions[to_region]['owner']
            if old_owner and old_owner in self.players:
                self.players[old_owner]['regions'].remove(to_region)
            
            self.regions[to_region]['owner'] = player_id
            self.regions[to_region]['soldiers'] = max(1, attacker_strength - defender_strength)
            self.players[player_id]['regions'].append(to_region)
            
            self.next_turn()
            return True, f"حمله موفق! {to_region} تصرف شد"
        else:
            # Attack failed
            remaining = max(1, defender_strength - attacker_strength)
            self.regions[to_region]['soldiers'] = remaining
            
            self.next_turn()
            return False, f"حمله ناموفق! {remaining} سرباز دشمن باقی ماند"
    
    def next_turn(self):
        self.current_turn += 1
        self.last_activity = time.time()
    
    def get_state(self):
        return {
            'game_id': self.game_id,
            'status': self.status,
            'players': self.players,
            'regions': self.regions,
            'current_player': self.get_current_player(),
            'turn_number': self.current_turn + 1
        }

# Embedded HTML template
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>جنگ منطقه‌ای ایران - هات‌اسپات</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Tahoma, Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; min-height: 100vh; padding: 10px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 20px; }
        .header h1 { font-size: 1.8rem; margin-bottom: 10px; }
        .header .flag { font-size: 3rem; margin: 10px 0; }
        .game-section { background: rgba(255,255,255,0.1); padding: 20px; margin: 10px 0; border-radius: 15px; }
        .form-group { margin: 15px 0; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input { width: 100%; padding: 12px; border: none; border-radius: 8px; font-size: 16px; }
        .btn { padding: 12px 24px; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; margin: 5px; }
        .btn-primary { background: #3498db; color: white; }
        .btn-success { background: #2ecc71; color: white; }
        .btn-danger { background: #e74c3c; color: white; }
        .btn-warning { background: #f39c12; color: white; }
        .btn:hover { opacity: 0.9; transform: translateY(-2px); }
        .status-bar { background: rgba(0,0,0,0.3); padding: 15px; border-radius: 10px; margin: 10px 0; }
        .players-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin: 15px 0; }
        .player-card { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; text-align: center; }
        .game-map { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; margin: 20px 0; }
        .region { padding: 15px; border-radius: 10px; text-align: center; cursor: pointer; transition: all 0.3s; }
        .region:hover { transform: scale(1.05); }
        .region.owned { border: 3px solid #fff; }
        .region.selected { box-shadow: 0 0 20px rgba(255,255,0,0.8); }
        .controls { display: flex; flex-wrap: wrap; gap: 10px; margin: 20px 0; }
        .message { padding: 10px; margin: 5px 0; border-radius: 5px; }
        .message.success { background: rgba(46, 204, 113, 0.3); }
        .message.error { background: rgba(231, 76, 60, 0.3); }
        .message.info { background: rgba(52, 152, 219, 0.3); }
        .hidden { display: none; }
        @media (max-width: 768px) {
            .controls { flex-direction: column; }
            .btn { width: 100%; }
            .game-map { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="flag">🏛️</div>
            <h1>جنگ منطقه‌ای ایران</h1>
            <p>بازی آفلاین روی هات‌اسپات</p>
        </div>

        <!-- Main Menu -->
        <div id="menu-screen" class="game-section">
            <h2>منوی اصلی</h2>
            <div class="controls">
                <button class="btn btn-primary" onclick="showCreateGame()">ایجاد بازی جدید</button>
                <button class="btn btn-success" onclick="showJoinGame()">پیوستن به بازی</button>
                <button class="btn btn-warning" onclick="showHelp()">راهنما</button>
            </div>
        </div>

        <!-- Create Game -->
        <div id="create-screen" class="game-section hidden">
            <h2>ایجاد بازی جدید</h2>
            <div class="form-group">
                <label>نام میزبان:</label>
                <input type="text" id="host-name" placeholder="نام خود را وارد کنید">
            </div>
            <div class="controls">
                <button class="btn btn-primary" onclick="createGame()">ایجاد بازی</button>
                <button class="btn" onclick="showMenu()">بازگشت</button>
            </div>
        </div>

        <!-- Join Game -->
        <div id="join-screen" class="game-section hidden">
            <h2>پیوستن به بازی</h2>
            <div class="form-group">
                <label>نام بازیکن:</label>
                <input type="text" id="player-name" placeholder="نام خود را وارد کنید">
            </div>
            <div class="form-group">
                <label>شناسه بازی:</label>
                <input type="text" id="game-id" placeholder="6 رقمی مثل 123456">
            </div>
            <div class="controls">
                <button class="btn btn-success" onclick="joinGame()">پیوستن</button>
                <button class="btn" onclick="showMenu()">بازگشت</button>
            </div>
        </div>

        <!-- Waiting Room -->
        <div id="waiting-screen" class="game-section hidden">
            <h2>اتاق انتظار</h2>
            <div class="status-bar">
                <div>شناسه بازی: <span id="current-game-id">-</span></div>
                <div>تعداد بازیکنان: <span id="player-count">0</span></div>
            </div>
            <div id="players-list" class="players-list"></div>
            <div class="controls">
                <button id="start-btn" class="btn btn-success hidden" onclick="startGame()">شروع بازی</button>
                <button class="btn btn-danger" onclick="leaveGame()">خروج</button>
            </div>
        </div>

        <!-- Game Screen -->
        <div id="game-screen" class="game-section hidden">
            <div class="status-bar">
                <div>نوبت: <span id="current-turn">-</span></div>
                <div>دور: <span id="turn-number">1</span></div>
                <div>آمار شما - سکه: <span id="my-coins">0</span> | سرباز: <span id="my-soldiers">0</span> | مناطق: <span id="my-regions">0</span></div>
            </div>
            
            <div id="game-map" class="game-map"></div>
            
            <div class="controls">
                <button class="btn btn-danger" onclick="showAttackDialog()">حمله</button>
                <button class="btn btn-warning" onclick="endTurn()">پایان نوبت</button>
                <button class="btn" onclick="leaveGame()">خروج از بازی</button>
            </div>
        </div>

        <div id="messages"></div>
    </div>

    <script>
        let gameState = null;
        let myPlayerId = null;
        let selectedRegion = null;
        let pollInterval = null;

        function showMenu() {
            hideAllScreens();
            document.getElementById('menu-screen').classList.remove('hidden');
        }

        function showCreateGame() {
            hideAllScreens();
            document.getElementById('create-screen').classList.remove('hidden');
        }

        function showJoinGame() {
            hideAllScreens();
            document.getElementById('join-screen').classList.remove('hidden');
        }

        function showHelp() {
            alert(`راهنمای بازی:

1. میزبان هات‌اسپات روشن کند
2. بقیه به هات‌اسپات وصل شوند  
3. میزبان بازی ایجاد کند
4. بقیه با Game ID پیوند شوند
5. میزبان بازی را شروع کند
6. به نوبت بازی کنید

هدف: تصرف بیشترین مناطق ایران`);
        }

        function hideAllScreens() {
            document.querySelectorAll('.game-section').forEach(el => el.classList.add('hidden'));
        }

        async function createGame() {
            const name = document.getElementById('host-name').value.trim();
            if (!name) {
                showMessage('نام میزبان را وارد کنید', 'error');
                return;
            }

            try {
                const response = await fetch('/api/create_game', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({player_name: name})
                });
                
                const result = await response.json();
                if (result.success) {
                    myPlayerId = result.player_id;
                    document.getElementById('current-game-id').textContent = result.game_id;
                    showWaitingRoom();
                    startPolling();
                    showMessage(result.message, 'success');
                } else {
                    showMessage(result.message, 'error');
                }
            } catch (error) {
                showMessage('خطا در ایجاد بازی', 'error');
            }
        }

        async function joinGame() {
            const name = document.getElementById('player-name').value.trim();
            const gameId = document.getElementById('game-id').value.trim();
            
            if (!name || !gameId) {
                showMessage('نام و شناسه بازی را وارد کنید', 'error');
                return;
            }

            try {
                const response = await fetch('/api/join_game', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({game_id: gameId, player_name: name})
                });
                
                const result = await response.json();
                if (result.success) {
                    myPlayerId = result.player_id;
                    document.getElementById('current-game-id').textContent = gameId;
                    showWaitingRoom();
                    startPolling();
                    showMessage(result.message, 'success');
                } else {
                    showMessage(result.message, 'error');
                }
            } catch (error) {
                showMessage('خطا در پیوستن به بازی', 'error');
            }
        }

        function showWaitingRoom() {
            hideAllScreens();
            document.getElementById('waiting-screen').classList.remove('hidden');
        }

        function showGameScreen() {
            hideAllScreens();
            document.getElementById('game-screen').classList.remove('hidden');
        }

        function startPolling() {
            if (pollInterval) clearInterval(pollInterval);
            pollInterval = setInterval(updateGameState, 2000);
        }

        async function updateGameState() {
            if (!myPlayerId) return;

            try {
                const gameId = document.getElementById('current-game-id').textContent;
                const response = await fetch('/api/get_game_state', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({game_id: gameId})
                });
                
                const result = await response.json();
                if (result.success) {
                    gameState = result.game_state;
                    updateUI();
                }
            } catch (error) {
                console.error('خطا در بروزرسانی:', error);
            }
        }

        function updateUI() {
            if (!gameState) return;

            if (gameState.status === 'waiting') {
                updateWaitingRoom();
            } else if (gameState.status === 'playing') {
                updateGameScreen();
            }
        }

        function updateWaitingRoom() {
            const playersList = document.getElementById('players-list');
            const playerCount = document.getElementById('player-count');
            const startBtn = document.getElementById('start-btn');
            
            playerCount.textContent = Object.keys(gameState.players).length;
            
            playersList.innerHTML = '';
            Object.values(gameState.players).forEach(player => {
                const div = document.createElement('div');
                div.className = 'player-card';
                div.style.borderLeft = `5px solid ${player.color}`;
                div.innerHTML = `
                    <strong>${player.name}</strong>
                    ${player.is_host ? '<br><small>(میزبان)</small>' : ''}
                `;
                playersList.appendChild(div);
            });

            // Show start button for host
            if (gameState.players[myPlayerId]?.is_host && Object.keys(gameState.players).length >= 2) {
                startBtn.classList.remove('hidden');
            }
        }

        function updateGameScreen() {
            if (document.getElementById('game-screen').classList.contains('hidden')) {
                showGameScreen();
            }

            // Update status
            const currentPlayer = gameState.players[gameState.current_player];
            document.getElementById('current-turn').textContent = currentPlayer ? currentPlayer.name : '-';
            document.getElementById('turn-number').textContent = gameState.turn_number;

            // Update my stats
            const myPlayer = gameState.players[myPlayerId];
            if (myPlayer) {
                document.getElementById('my-coins').textContent = myPlayer.coins;
                document.getElementById('my-soldiers').textContent = myPlayer.soldiers;
                document.getElementById('my-regions').textContent = myPlayer.regions.length;
            }

            // Update map
            updateMap();
        }

        function updateMap() {
            const mapDiv = document.getElementById('game-map');
            mapDiv.innerHTML = '';

            Object.entries(gameState.regions).forEach(([regionId, region]) => {
                const div = document.createElement('div');
                div.className = 'region';
                div.id = `region-${regionId}`;
                
                if (region.owner) {
                    const owner = gameState.players[region.owner];
                    div.style.backgroundColor = owner.color;
                    div.classList.add('owned');
                }
                
                if (selectedRegion === regionId) {
                    div.classList.add('selected');
                }
                
                div.innerHTML = `
                    <strong>${region.name}</strong><br>
                    <small>سرباز: ${region.soldiers}</small>
                `;
                
                div.onclick = () => selectRegion(regionId);
                mapDiv.appendChild(div);
            });
        }

        function selectRegion(regionId) {
            selectedRegion = regionId;
            updateMap();
        }

        async function startGame() {
            try {
                const gameId = document.getElementById('current-game-id').textContent;
                const response = await fetch('/api/start_game', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({game_id: gameId, player_id: myPlayerId})
                });
                
                const result = await response.json();
                if (result.success) {
                    showMessage('بازی شروع شد!', 'success');
                } else {
                    showMessage(result.message, 'error');
                }
            } catch (error) {
                showMessage('خطا در شروع بازی', 'error');
            }
        }

        function showAttackDialog() {
            if (!selectedRegion) {
                showMessage('ابتدا یک منطقه انتخاب کنید', 'error');
                return;
            }

            const soldiers = prompt('تعداد سربازان حمله کننده:');
            if (soldiers && parseInt(soldiers) > 0) {
                const target = prompt('منطقه مقصد:');
                if (target) {
                    executeAttack(selectedRegion, target, parseInt(soldiers));
                }
            }
        }

        async function executeAttack(fromRegion, toRegion, soldiers) {
            try {
                const gameId = document.getElementById('current-game-id').textContent;
                const response = await fetch('/api/attack', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        game_id: gameId,
                        player_id: myPlayerId,
                        from_region: fromRegion,
                        to_region: toRegion,
                        soldiers: soldiers
                    })
                });
                
                const result = await response.json();
                showMessage(result.message, result.success ? 'success' : 'error');
            } catch (error) {
                showMessage('خطا در حمله', 'error');
            }
        }

        function endTurn() {
            showMessage('نوبت شما تمام شد', 'info');
        }

        function leaveGame() {
            if (pollInterval) clearInterval(pollInterval);
            gameState = null;
            myPlayerId = null;
            selectedRegion = null;
            showMenu();
        }

        function showMessage(text, type) {
            const div = document.createElement('div');
            div.className = `message ${type}`;
            div.textContent = text;
            document.getElementById('messages').appendChild(div);
            
            setTimeout(() => div.remove(), 5000);
        }

        // Initialize
        showMenu();
    </script>
</body>
</html>'''

class GameHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
        else:
            self.send_error(404)
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except:
            self.send_error(400)
            return
        
        path = self.path
        response = {'success': False, 'message': 'Unknown endpoint'}
        
        if path == '/api/create_game':
            response = self.handle_create_game(data)
        elif path == '/api/join_game':
            response = self.handle_join_game(data)
        elif path == '/api/start_game':
            response = self.handle_start_game(data)
        elif path == '/api/get_game_state':
            response = self.handle_get_game_state(data)
        elif path == '/api/attack':
            response = self.handle_attack(data)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def handle_create_game(self, data):
        player_name = data.get('player_name', 'میزبان')
        game_id = ''.join(random.choices('0123456789', k=6))
        
        while game_id in games:
            game_id = ''.join(random.choices('0123456789', k=6))
        
        game = GameState(game_id, player_name)
        games[game_id] = game
        
        host_id = list(game.players.keys())[0]
        
        return {
            'success': True,
            'game_id': game_id,
            'player_id': host_id,
            'message': f'بازی با شناسه {game_id} ایجاد شد'
        }
    
    def handle_join_game(self, data):
        game_id = data.get('game_id')
        player_name = data.get('player_name', 'بازیکن')
        
        if game_id not in games:
            return {'success': False, 'message': 'بازی پیدا نشد'}
        
        game = games[game_id]
        if game.status != 'waiting':
            return {'success': False, 'message': 'بازی شروع شده است'}
        
        player_id = game.add_player(player_name)
        if not player_id:
            return {'success': False, 'message': 'بازی پر است'}
        
        return {
            'success': True,
            'player_id': player_id,
            'message': f'{player_name} به بازی پیوست'
        }
    
    def handle_start_game(self, data):
        game_id = data.get('game_id')
        player_id = data.get('player_id')
        
        if game_id not in games:
            return {'success': False, 'message': 'بازی پیدا نشد'}
        
        game = games[game_id]
        if not game.players[player_id]['is_host']:
            return {'success': False, 'message': 'فقط میزبان می‌تواند بازی را شروع کند'}
        
        if game.start_game():
            return {'success': True, 'message': 'بازی شروع شد'}
        else:
            return {'success': False, 'message': 'حداقل 2 بازیکن لازم است'}
    
    def handle_get_game_state(self, data):
        game_id = data.get('game_id')
        
        if game_id not in games:
            return {'success': False, 'message': 'بازی پیدا نشد'}
        
        game = games[game_id]
        return {
            'success': True,
            'game_state': game.get_state()
        }
    
    def handle_attack(self, data):
        game_id = data.get('game_id')
        player_id = data.get('player_id')
        from_region = data.get('from_region')
        to_region = data.get('to_region')
        soldiers = data.get('soldiers', 10)
        
        if game_id not in games:
            return {'success': False, 'message': 'بازی پیدا نشد'}
        
        game = games[game_id]
        success, message = game.execute_attack(player_id, from_region, to_region, soldiers)
        
        return {'success': success, 'message': message}

def get_local_ip():
    """Get device's local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def run_server():
    """Run the game server"""
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, GameHandler)
    
    local_ip = get_local_ip()
    
    print(f"""
    ═══════════════════════════════════════════════════════════
    🏛️           جنگ منطقه‌ای ایران - هات‌اسپات           🏛️  
    ═══════════════════════════════════════════════════════════
    
    ✅ سرور آفلاین آماده است!
    
    📡 آدرس دسترسی:
    ├─ محلی:     http://localhost:8000
    ├─ شبکه:     http://{local_ip}:8000
    └─ هات‌اسپات: http://{local_ip}:8000
    
    📱 دستورات بازی:
    ├─ هات‌اسپات گوشی را روشن کنید
    ├─ دوستان به هات‌اسپات وصل شوند
    ├─ آدرس بالا را در مرورگر باز کنند
    └─ شروع به بازی کنید!
    
    🎯 ویژگی‌ها:
    ├─ بدون نیاز به اینترنت
    ├─ تا 8 بازیکن همزمان
    ├─ نقشه کامل ایران
    └─ رابط کاربری فارسی
    
    ⚠️  برای توقف: Ctrl+C
    ═══════════════════════════════════════════════════════════
    """)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 سرور متوقف شد. خداحافظ!")
        httpd.shutdown()

if __name__ == '__main__':
    run_server()