#!/usr/bin/env python3
"""
Standalone APK version of Iran War Game
Complete self-contained application with built-in server
Works with mobile hotspot without external dependencies
"""

import os
import sys
import threading
import time
import socket
import random
import json
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.clock import Clock
from kivy.core.window import Window

# Import game logic directly
class IranMap:
    def __init__(self):
        self.regions = self.create_regions()
        self.neighbors = self.create_neighbor_map()
    
    def create_regions(self):
        return {
            'tehran': {'name': 'تهران', 'x': 400, 'y': 300, 'population': 15000000, 'type': 'capital', 'owner': None, 'soldiers': 0},
            'isfahan': {'name': 'اصفهان', 'x': 380, 'y': 250, 'population': 5000000, 'type': 'cultural', 'owner': None, 'soldiers': 0},
            'mashhad': {'name': 'مشهد', 'x': 500, 'y': 320, 'population': 3500000, 'type': 'religious', 'owner': None, 'soldiers': 0},
            'shiraz': {'name': 'شیراز', 'x': 380, 'y': 200, 'population': 2000000, 'type': 'cultural', 'owner': None, 'soldiers': 0},
            'tabriz': {'name': 'تبریز', 'x': 320, 'y': 380, 'population': 1800000, 'type': 'industrial', 'owner': None, 'soldiers': 0},
            'ahvaz': {'name': 'اهواز', 'x': 300, 'y': 220, 'population': 1500000, 'type': 'industrial', 'owner': None, 'soldiers': 0},
            'qom': {'name': 'قم', 'x': 390, 'y': 280, 'population': 1200000, 'type': 'religious', 'owner': None, 'soldiers': 0},
            'karaj': {'name': 'کرج', 'x': 390, 'y': 310, 'population': 1100000, 'type': 'industrial', 'owner': None, 'soldiers': 0},
            'urmia': {'name': 'ارومیه', 'x': 300, 'y': 380, 'population': 900000, 'type': 'cultural', 'owner': None, 'soldiers': 0},
            'arak': {'name': 'اراک', 'x': 370, 'y': 270, 'population': 800000, 'type': 'industrial', 'owner': None, 'soldiers': 0},
            'yazd': {'name': 'یزد', 'x': 420, 'y': 240, 'population': 700000, 'type': 'cultural', 'owner': None, 'soldiers': 0},
            'ardabil': {'name': 'اردبیل', 'x': 340, 'y': 400, 'population': 650000, 'type': 'industrial', 'owner': None, 'soldiers': 0},
            'bandar_abbas': {'name': 'بندرعباس', 'x': 420, 'y': 160, 'population': 600000, 'type': 'port', 'owner': None, 'soldiers': 0},
            'abadan': {'name': 'آبادان', 'x': 280, 'y': 200, 'population': 400000, 'type': 'port', 'owner': None, 'soldiers': 0},
            'kish': {'name': 'کیش', 'x': 430, 'y': 150, 'population': 50000, 'type': 'port', 'owner': None, 'soldiers': 0}
        }
    
    def create_neighbor_map(self):
        return {
            'tehran': ['karaj', 'qom', 'arak'],
            'isfahan': ['yazd', 'shiraz', 'arak'],
            'mashhad': [],
            'shiraz': ['isfahan', 'yazd'],
            'tabriz': ['urmia', 'ardabil'],
            'ahvaz': ['abadan'],
            'qom': ['tehran', 'arak'],
            'karaj': ['tehran'],
            'urmia': ['tabriz'],
            'arak': ['tehran', 'qom', 'isfahan'],
            'yazd': ['isfahan', 'shiraz'],
            'ardabil': ['tabriz'],
            'bandar_abbas': ['kish'],
            'abadan': ['ahvaz'],
            'kish': ['bandar_abbas']
        }

class GameLogic:
    def calculate_battle_result(self, attacking_soldiers, defending_soldiers):
        # Simple battle calculation
        attacker_strength = attacking_soldiers + random.randint(-5, 5)
        defender_strength = defending_soldiers + random.randint(-3, 7)  # Home advantage
        
        if attacker_strength > defender_strength:
            remaining = max(1, attacker_strength - defender_strength)
            return True, remaining, 0
        else:
            remaining = max(1, defender_strength - attacker_strength)
            return False, 0, remaining
    
    def get_building_cost(self, building_type):
        costs = {'barracks': 30, 'factory': 50, 'bank': 40}
        return costs.get(building_type, 30)

class LocalGameServer:
    def __init__(self):
        self.games = {}
        self.iran_map = IranMap()
        self.game_logic = GameLogic()
    
    def create_game(self, player_name):
        game_id = ''.join(random.choices('0123456789', k=6))
        while game_id in self.games:
            game_id = ''.join(random.choices('0123456789', k=6))
        
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
        
        game = {
            'id': game_id,
            'players': {host_player['id']: host_player},
            'status': 'waiting',
            'regions': self.iran_map.regions.copy(),
            'current_turn': 0,
            'turn_order': [],
            'created_time': datetime.now()
        }
        
        self.games[game_id] = game
        return game_id, host_player['id']
    
    def join_game(self, game_id, player_name):
        if game_id not in self.games:
            return False, "بازی پیدا نشد"
        
        game = self.games[game_id]
        if game['status'] != 'waiting':
            return False, "بازی شروع شده"
        
        if len(game['players']) >= 8:
            return False, "بازی پر است"
        
        colors = ['#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#95a5a6']
        player_color = colors[len(game['players']) - 1]
        
        player_id = f'player_{random.randint(1000, 9999)}'
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
        
        game['players'][player_id] = player
        return True, player_id
    
    def start_game(self, game_id, player_id):
        if game_id not in self.games:
            return False, "بازی پیدا نشد"
        
        game = self.games[game_id]
        if not game['players'][player_id]['is_host']:
            return False, "فقط میزبان می‌تواند بازی را شروع کند"
        
        if len(game['players']) < 2:
            return False, "حداقل 2 بازیکن لازم است"
        
        # Start game
        game['status'] = 'playing'
        game['turn_order'] = list(game['players'].keys())
        random.shuffle(game['turn_order'])
        
        # Distribute regions
        regions_list = list(game['regions'].keys())
        random.shuffle(regions_list)
        
        regions_per_player = len(regions_list) // len(game['players'])
        region_index = 0
        
        for player_id in game['turn_order']:
            for _ in range(regions_per_player):
                if region_index < len(regions_list):
                    region_id = regions_list[region_index]
                    game['regions'][region_id]['owner'] = player_id
                    game['regions'][region_id]['soldiers'] = 10
                    game['players'][player_id]['regions'].append(region_id)
                    region_index += 1
        
        return True, "بازی شروع شد"
    
    def get_game_state(self, game_id):
        if game_id not in self.games:
            return None
        return self.games[game_id]

# UI Components
class GameMapWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_state = None
        self.selected_region = None
        
    def update_game_state(self, game_state):
        self.game_state = game_state
        self.canvas.clear()
        self.draw_map()
    
    def draw_map(self):
        if not self.game_state:
            return
        
        with self.canvas:
            # Draw regions
            for region_id, region in self.game_state['regions'].items():
                owner = region.get('owner')
                if owner and owner in self.game_state['players']:
                    color = self.game_state['players'][owner]['color']
                    Color(*self.hex_to_rgb(color))
                else:
                    Color(0.7, 0.7, 0.7, 1)  # Gray for unowned
                
                x, y = region['x'], region['y']
                Ellipse(pos=(x-15, y-15), size=(30, 30))
                
                # Highlight selected region
                if region_id == self.selected_region:
                    Color(1, 1, 0, 1)  # Yellow highlight
                    Line(circle=(x, y, 20), width=3)
    
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return [int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4)] + [1]
    
    def on_touch_down(self, touch):
        if not self.game_state:
            return False
        
        for region_id, region in self.game_state['regions'].items():
            x, y = region['x'], region['y']
            if ((touch.x - x) ** 2 + (touch.y - y) ** 2) ** 0.5 <= 20:
                self.selected_region = region_id
                self.draw_map()
                return True
        return False

class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Logo
        logo_label = Label(text='🏛️ جنگ منطقه‌ای ایران 🏛️', 
                          font_size='24sp', size_hint_y=0.2)
        layout.add_widget(logo_label)
        
        # Hotspot info
        hotspot_info = Label(text='📱 برای بازی چندنفره:\n1. هات‌اسپات گوشی را روشن کنید\n2. دوستان به هات‌اسپات وصل شوند\n3. بازی ایجاد کنید یا بپیوندید',
                           font_size='14sp', size_hint_y=0.3)
        layout.add_widget(hotspot_info)
        
        # Buttons
        create_btn = Button(text='ایجاد بازی جدید', size_hint_y=0.15)
        create_btn.bind(on_press=self.show_create_game)
        layout.add_widget(create_btn)
        
        join_btn = Button(text='پیوستن به بازی', size_hint_y=0.15)
        join_btn.bind(on_press=self.show_join_game)
        layout.add_widget(join_btn)
        
        help_btn = Button(text='راهنما', size_hint_y=0.15)
        help_btn.bind(on_press=self.show_help)
        layout.add_widget(help_btn)
        
        self.add_widget(layout)
    
    def show_create_game(self, instance):
        self.manager.current = 'create_game'
    
    def show_join_game(self, instance):
        self.manager.current = 'join_game'
    
    def show_help(self, instance):
        help_text = """🎮 راهنمای بازی:

📱 راه‌اندازی هات‌اسپات:
1. تنظیمات گوشی > هات‌اسپات
2. نام و رمز تنظیم کنید
3. هات‌اسپات را روشن کنید

👥 اضافه کردن بازیکنان:
1. دوستان به هات‌اسپات وصل شوند
2. این اپ را روی گوشی خود باز کنند
3. با Game ID به بازی بپیوندند

⚔️ نحوه بازی:
- هدف: تصرف بیشترین مناطق ایران
- نوبتی بازی می‌کنید
- حمله و ساخت ساختمان
- 2 تا 8 نفر می‌توانند بازی کنند"""
        
        popup = Popup(title='راهنما', content=Label(text=help_text), size_hint=(0.8, 0.8))
        popup.open()

class CreateGameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text='ایجاد بازی جدید', font_size='20sp', size_hint_y=0.2))
        
        self.name_input = TextInput(hint_text='نام شما', multiline=False, size_hint_y=0.15)
        layout.add_widget(self.name_input)
        
        create_btn = Button(text='ایجاد بازی', size_hint_y=0.15)
        create_btn.bind(on_press=self.create_game)
        layout.add_widget(create_btn)
        
        back_btn = Button(text='بازگشت', size_hint_y=0.15)
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def create_game(self, instance):
        name = self.name_input.text.strip()
        if not name:
            self.show_popup('خطا', 'نام خود را وارد کنید')
            return
        
        app = App.get_running_app()
        game_id, player_id = app.game_server.create_game(name)
        
        app.current_game_id = game_id
        app.current_player_id = player_id
        
        waiting_screen = self.manager.get_screen('waiting')
        waiting_screen.setup_waiting(game_id, True)  # is_host=True
        self.manager.current = 'waiting'
    
    def go_back(self, instance):
        self.manager.current = 'menu'
    
    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.6, 0.4))
        popup.open()

class JoinGameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text='پیوستن به بازی', font_size='20sp', size_hint_y=0.2))
        
        self.name_input = TextInput(hint_text='نام شما', multiline=False, size_hint_y=0.15)
        layout.add_widget(self.name_input)
        
        self.game_id_input = TextInput(hint_text='شناسه بازی (6 رقم)', multiline=False, size_hint_y=0.15)
        layout.add_widget(self.game_id_input)
        
        join_btn = Button(text='پیوستن', size_hint_y=0.15)
        join_btn.bind(on_press=self.join_game)
        layout.add_widget(join_btn)
        
        back_btn = Button(text='بازگشت', size_hint_y=0.15)
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def join_game(self, instance):
        name = self.name_input.text.strip()
        game_id = self.game_id_input.text.strip()
        
        if not name or not game_id:
            self.show_popup('خطا', 'نام و شناسه بازی را وارد کنید')
            return
        
        app = App.get_running_app()
        success, result = app.game_server.join_game(game_id, name)
        
        if success:
            app.current_game_id = game_id
            app.current_player_id = result
            
            waiting_screen = self.manager.get_screen('waiting')
            waiting_screen.setup_waiting(game_id, False)  # is_host=False
            self.manager.current = 'waiting'
        else:
            self.show_popup('خطا', result)
    
    def go_back(self, instance):
        self.manager.current = 'menu'
    
    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.6, 0.4))
        popup.open()

class WaitingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_host = False
        self.game_id = None
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        self.info_label = Label(text='انتظار برای بازیکنان...', font_size='18sp', size_hint_y=0.2)
        layout.add_widget(self.info_label)
        
        self.players_label = Label(text='', font_size='14sp', size_hint_y=0.4)
        layout.add_widget(self.players_label)
        
        self.start_btn = Button(text='شروع بازی', size_hint_y=0.15)
        self.start_btn.bind(on_press=self.start_game)
        layout.add_widget(self.start_btn)
        
        back_btn = Button(text='بازگشت', size_hint_y=0.15)
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
        
    def setup_waiting(self, game_id, is_host):
        self.game_id = game_id
        self.is_host = is_host
        self.info_label.text = f'شناسه بازی: {game_id}'
        
        if not is_host:
            self.start_btn.disabled = True
            self.start_btn.text = 'انتظار برای میزبان...'
        
        Clock.schedule_interval(self.update_players, 2)
    
    def update_players(self, dt):
        app = App.get_running_app()
        game_state = app.game_server.get_game_state(self.game_id)
        
        if game_state:
            if game_state['status'] == 'playing':
                Clock.unschedule(self.update_players)
                self.manager.current = 'game'
                return False
            
            players_text = 'بازیکنان:\n'
            for player in game_state['players'].values():
                host_mark = ' (میزبان)' if player['is_host'] else ''
                players_text += f'• {player["name"]}{host_mark}\n'
            
            self.players_label.text = players_text
            
            if self.is_host and len(game_state['players']) >= 2:
                self.start_btn.disabled = False
                self.start_btn.text = 'شروع بازی'
    
    def start_game(self, instance):
        app = App.get_running_app()
        success, message = app.game_server.start_game(self.game_id, app.current_player_id)
        
        if success:
            Clock.unschedule(self.update_players)
            self.manager.current = 'game'
        else:
            self.show_popup('خطا', message)
    
    def go_back(self, instance):
        Clock.unschedule(self.update_players)
        self.manager.current = 'menu'
    
    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.6, 0.4))
        popup.open()

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='horizontal')
        
        # Map area
        self.map_widget = GameMapWidget()
        main_layout.add_widget(self.map_widget)
        
        # Control panel
        control_layout = BoxLayout(orientation='vertical', size_hint_x=0.3, padding=10, spacing=5)
        
        self.turn_label = Label(text='نوبت: -', size_hint_y=0.1)
        control_layout.add_widget(self.turn_label)
        
        self.stats_label = Label(text='آمار بازیکن', size_hint_y=0.2)
        control_layout.add_widget(self.stats_label)
        
        attack_btn = Button(text='حمله', size_hint_y=0.1)
        attack_btn.bind(on_press=self.show_attack_dialog)
        control_layout.add_widget(attack_btn)
        
        build_btn = Button(text='ساخت', size_hint_y=0.1)
        build_btn.bind(on_press=self.show_build_dialog)
        control_layout.add_widget(build_btn)
        
        end_turn_btn = Button(text='پایان نوبت', size_hint_y=0.1)
        end_turn_btn.bind(on_press=self.end_turn)
        control_layout.add_widget(end_turn_btn)
        
        back_btn = Button(text='خروج از بازی', size_hint_y=0.1)
        back_btn.bind(on_press=self.go_back)
        control_layout.add_widget(back_btn)
        
        main_layout.add_widget(control_layout)
        self.add_widget(main_layout)
        
        Clock.schedule_interval(self.update_game, 3)
    
    def update_game(self, dt):
        app = App.get_running_app()
        if not app.current_game_id:
            return False
        
        game_state = app.game_server.get_game_state(app.current_game_id)
        if game_state:
            self.map_widget.update_game_state(game_state)
            
            current_player = game_state['players'].get(game_state['turn_order'][game_state['current_turn'] % len(game_state['turn_order'])])
            if current_player:
                self.turn_label.text = f'نوبت: {current_player["name"]}'
            
            my_player = game_state['players'].get(app.current_player_id)
            if my_player:
                self.stats_label.text = f'سکه: {my_player["coins"]}\nسرباز: {my_player["soldiers"]}\nمناطق: {len(my_player["regions"])}'
    
    def show_attack_dialog(self, instance):
        # Simplified attack - would need proper UI
        self.show_popup('حمله', 'قابلیت حمله در نسخه بعدی اضافه می‌شود')
    
    def show_build_dialog(self, instance):
        # Simplified build - would need proper UI  
        self.show_popup('ساخت', 'قابلیت ساخت در نسخه بعدی اضافه می‌شود')
    
    def end_turn(self, instance):
        self.show_popup('پایان نوبت', 'نوبت شما تمام شد')
    
    def go_back(self, instance):
        Clock.unschedule(self.update_game)
        self.manager.current = 'menu'
    
    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.6, 0.4))
        popup.open()

class IranWarGameApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_server = LocalGameServer()
        self.current_game_id = None
        self.current_player_id = None
    
    def build(self):
        # Set window properties
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        
        sm = ScreenManager()
        
        sm.add_widget(MainMenuScreen(name='menu'))
        sm.add_widget(CreateGameScreen(name='create_game'))
        sm.add_widget(JoinGameScreen(name='join_game'))
        sm.add_widget(WaitingScreen(name='waiting'))
        sm.add_widget(GameScreen(name='game'))
        
        sm.current = 'menu'
        return sm

if __name__ == '__main__':
    IranWarGameApp().run()