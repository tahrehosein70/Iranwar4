"""
Mobile version of Iran War Game for Android APK creation
Uses Kivy framework for cross-platform mobile development
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scatter import Scatter
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line
from kivy.uix.widget import Widget
import requests
import json
import threading
import time

class IranMapWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.regions = self.get_iran_regions()
        self.selected_region = None
        self.target_region = None
        self.game_data = {}
        self.bind(size=self.update_graphics, pos=self.update_graphics)
    
    def get_iran_regions(self):
        return [
            {'id': 'tehran', 'name': 'تهران', 'pos': (0.5, 0.7)},
            {'id': 'isfahan', 'name': 'اصفهان', 'pos': (0.4, 0.5)},
            {'id': 'shiraz', 'name': 'شیراز', 'pos': (0.3, 0.3)},
            {'id': 'mashhad', 'name': 'مشهد', 'pos': (0.7, 0.8)},
            {'id': 'tabriz', 'name': 'تبریز', 'pos': (0.2, 0.9)},
            {'id': 'ahvaz', 'name': 'اهواز', 'pos': (0.15, 0.4)},
            {'id': 'qazvin', 'name': 'قزوین', 'pos': (0.45, 0.8)},
            {'id': 'semnan', 'name': 'سمنان', 'pos': (0.6, 0.7)},
            {'id': 'qom', 'name': 'قم', 'pos': (0.48, 0.6)},
            {'id': 'yazd', 'name': 'یزد', 'pos': (0.5, 0.4)},
            {'id': 'kerman', 'name': 'کرمان', 'pos': (0.6, 0.3)},
            {'id': 'bushehr', 'name': 'بوشهر', 'pos': (0.25, 0.3)},
            {'id': 'zanjan', 'name': 'زنجان', 'pos': (0.35, 0.8)},
            {'id': 'ardabil', 'name': 'اردبیل', 'pos': (0.25, 0.95)},
            {'id': 'lorestan', 'name': 'لرستان', 'pos': (0.3, 0.5)},
        ]
    
    def update_graphics(self, *args):
        self.canvas.clear()
        with self.canvas:
            for region in self.regions:
                # Calculate position
                x = self.x + region['pos'][0] * self.width
                y = self.y + region['pos'][1] * self.height
                
                # Set color based on owner
                if self.game_data and 'regions' in self.game_data:
                    region_data = self.game_data['regions'].get(region['id'], {})
                    owner = region_data.get('owner')
                    if owner and 'players' in self.game_data:
                        player = self.game_data['players'].get(owner, {})
                        color = player.get('color', '#CCCCCC')
                        # Convert hex to RGB
                        color = color.lstrip('#')
                        r, g, b = tuple(int(color[i:i+2], 16)/255.0 for i in (0, 2, 4))
                        Color(r, g, b, 1)
                    else:
                        Color(0.8, 0.8, 0.8, 1)
                else:
                    Color(0.8, 0.8, 0.8, 1)
                
                # Highlight selected
                if self.selected_region == region['id']:
                    Color(1, 1, 0, 1)  # Yellow
                elif self.target_region == region['id']:
                    Color(0, 1, 1, 1)  # Cyan
                
                # Draw region circle
                d = min(self.width, self.height) * 0.08
                Ellipse(pos=(x - d/2, y - d/2), size=(d, d))
    
    def on_touch_down(self, touch):
        for region in self.regions:
            x = self.x + region['pos'][0] * self.width
            y = self.y + region['pos'][1] * self.height
            d = min(self.width, self.height) * 0.08
            
            if (x - d/2 <= touch.x <= x + d/2 and 
                y - d/2 <= touch.y <= y + d/2):
                self.select_region(region['id'])
                return True
        return super().on_touch_down(touch)
    
    def select_region(self, region_id):
        if self.selected_region == region_id:
            self.selected_region = None
            self.target_region = None
        elif self.selected_region is None:
            self.selected_region = region_id
        else:
            self.target_region = region_id
        self.update_graphics()
    
    def update_game_data(self, game_data):
        self.game_data = game_data
        self.update_graphics()

class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        title = Label(text='جنگ منطقه‌ای ایران', font_size='24sp', size_hint_y=None, height=60)
        layout.add_widget(title)
        
        # Player name input
        self.player_name = TextInput(hint_text='نام بازیکن', multiline=False, size_hint_y=None, height=40)
        layout.add_widget(self.player_name)
        
        # Create game button
        create_btn = Button(text='ساخت بازی جدید', size_hint_y=None, height=50)
        create_btn.bind(on_press=self.create_game)
        layout.add_widget(create_btn)
        
        # Join game input
        self.game_id = TextInput(hint_text='شناسه بازی', multiline=False, size_hint_y=None, height=40)
        layout.add_widget(self.game_id)
        
        # Join game button
        join_btn = Button(text='پیوستن به بازی', size_hint_y=None, height=50)
        join_btn.bind(on_press=self.join_game)
        layout.add_widget(join_btn)
        
        # Status label
        self.status = Label(text='آماده برای بازی', size_hint_y=None, height=40)
        layout.add_widget(self.status)
        
        self.add_widget(layout)
    
    def create_game(self, instance):
        if not self.player_name.text.strip():
            self.show_popup('خطا', 'نام بازیکن را وارد کنید')
            return
        
        app = App.get_running_app()
        app.api_call('create_game', {'player_name': self.player_name.text.strip()}, self.on_game_created)
    
    def join_game(self, instance):
        if not self.player_name.text.strip() or not self.game_id.text.strip():
            self.show_popup('خطا', 'نام بازیکن و شناسه بازی را وارد کنید')
            return
        
        app = App.get_running_app()
        data = {
            'player_name': self.player_name.text.strip(),
            'game_id': self.game_id.text.strip()
        }
        app.api_call('join_game', data, self.on_game_joined)
    
    def on_game_created(self, result):
        if result.get('success'):
            app = App.get_running_app()
            app.game_id = result['game_id']
            app.player_id = result['player_id']
            app.game_data = result['game_state']
            self.manager.current = 'waiting'
        else:
            self.show_popup('خطا', result.get('error', 'خطا در ایجاد بازی'))
    
    def on_game_joined(self, result):
        if result.get('success'):
            app = App.get_running_app()
            app.game_id = self.game_id.text.strip()
            app.player_id = result['player_id']
            app.game_data = result['game_state']
            self.manager.current = 'waiting'
        else:
            self.show_popup('خطا', result.get('error', 'خطا در پیوستن'))
    
    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()

class WaitingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Game ID display
        self.game_id_label = Label(text='', font_size='18sp', size_hint_y=None, height=40)
        layout.add_widget(self.game_id_label)
        
        # Players list
        self.players_label = Label(text='بازیکنان:', size_hint_y=None, height=40)
        layout.add_widget(self.players_label)
        
        self.players_list = Label(text='', halign='center')
        layout.add_widget(self.players_list)
        
        # Start button
        self.start_btn = Button(text='شروع بازی', size_hint_y=None, height=50)
        self.start_btn.bind(on_press=self.start_game)
        layout.add_widget(self.start_btn)
        
        # Back button
        back_btn = Button(text='بازگشت', size_hint_y=None, height=50)
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def on_enter(self):
        app = App.get_running_app()
        self.game_id_label.text = f'شناسه بازی: {app.game_id}'
        self.update_players()
        
        # Start polling for updates
        Clock.schedule_interval(self.poll_game_state, 2)
    
    def on_leave(self):
        Clock.unschedule(self.poll_game_state)
    
    def update_players(self):
        app = App.get_running_app()
        if app.game_data and 'players' in app.game_data:
            players_text = ''
            for player_id, player in app.game_data['players'].items():
                status = '🟢' if player.get('connected') else '🔴'
                players_text += f'{status} {player["name"]}\n'
            self.players_list.text = players_text
            
            # Show start button only for host
            if app.game_data.get('host') == app.player_id:
                self.start_btn.opacity = 1
                self.start_btn.disabled = False
            else:
                self.start_btn.opacity = 0.5
                self.start_btn.disabled = True
    
    def poll_game_state(self, dt):
        app = App.get_running_app()
        app.api_call('get_game_state', {'game_id': app.game_id}, self.on_game_state_updated)
    
    def on_game_state_updated(self, result):
        if result.get('success'):
            app = App.get_running_app()
            old_state = app.game_data.get('game_state')
            app.game_data = result['game_state']
            
            self.update_players()
            
            # Check if game started
            if app.game_data.get('game_state') == 'playing' and old_state != 'playing':
                self.manager.current = 'game'
    
    def start_game(self, instance):
        app = App.get_running_app()
        data = {'game_id': app.game_id, 'player_id': app.player_id}
        app.api_call('start_game', data, self.on_game_started)
    
    def on_game_started(self, result):
        if result.get('success'):
            app = App.get_running_app()
            app.game_data = result['game_state']
            self.manager.current = 'game'
    
    def go_back(self, instance):
        self.manager.current = 'menu'

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical')
        
        # Top info bar
        info_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)
        self.coins_label = Label(text='سکه: 0')
        self.soldiers_label = Label(text='سرباز: 0')
        self.companies_label = Label(text='شرکت: 0')
        info_layout.add_widget(self.coins_label)
        info_layout.add_widget(self.soldiers_label)
        info_layout.add_widget(self.companies_label)
        main_layout.add_widget(info_layout)
        
        # Map area
        self.map_widget = IranMapWidget()
        main_layout.add_widget(self.map_widget)
        
        # Bottom controls
        controls_layout = GridLayout(cols=3, size_hint_y=None, height=60)
        
        attack_btn = Button(text='حمله')
        attack_btn.bind(on_press=self.attack)
        controls_layout.add_widget(attack_btn)
        
        build_btn = Button(text='ساخت')
        build_btn.bind(on_press=self.build)
        controls_layout.add_widget(build_btn)
        
        back_btn = Button(text='خروج')
        back_btn.bind(on_press=self.go_back)
        controls_layout.add_widget(back_btn)
        
        main_layout.add_widget(controls_layout)
        
        self.add_widget(main_layout)
    
    def on_enter(self):
        self.update_interface()
        Clock.schedule_interval(self.poll_game_state, 3)
    
    def on_leave(self):
        Clock.unschedule(self.poll_game_state)
    
    def update_interface(self):
        app = App.get_running_app()
        if app.game_data and 'players' in app.game_data and app.player_id in app.game_data['players']:
            player = app.game_data['players'][app.player_id]
            self.coins_label.text = f'سکه: {player["coins"]}'
            self.soldiers_label.text = f'سرباز: {player["soldiers"]}'
            self.companies_label.text = f'شرکت: {player["companies"]}'
        
        self.map_widget.update_game_data(app.game_data)
    
    def poll_game_state(self, dt):
        app = App.get_running_app()
        app.api_call('get_game_state', {'game_id': app.game_id}, self.on_game_state_updated)
    
    def on_game_state_updated(self, result):
        if result.get('success'):
            app = App.get_running_app()
            app.game_data = result['game_state']
            self.update_interface()
    
    def attack(self, instance):
        if not self.map_widget.selected_region or not self.map_widget.target_region:
            self.show_popup('خطا', 'مبدأ و مقصد حمله را انتخاب کنید')
            return
        
        app = App.get_running_app()
        data = {
            'game_id': app.game_id,
            'player_id': app.player_id,
            'from_region': self.map_widget.selected_region,
            'to_region': self.map_widget.target_region,
            'soldiers': 5
        }
        app.api_call('attack', data, self.on_attack_result)
    
    def on_attack_result(self, result):
        if result.get('success'):
            app = App.get_running_app()
            app.game_data = result['game_state']
            self.update_interface()
            self.map_widget.selected_region = None
            self.map_widget.target_region = None
            self.show_popup('موفق', 'حمله موفق بود!')
        else:
            self.show_popup('ناموفق', result.get('message', 'حمله ناموفق بود'))
    
    def build(self, instance):
        if not self.map_widget.selected_region:
            self.show_popup('خطا', 'منطقه‌ای برای ساخت انتخاب کنید')
            return
        
        app = App.get_running_app()
        data = {
            'game_id': app.game_id,
            'player_id': app.player_id,
            'region_id': self.map_widget.selected_region,
            'structure_type': 'barracks'
        }
        app.api_call('build', data, self.on_build_result)
    
    def on_build_result(self, result):
        if result.get('success'):
            app = App.get_running_app()
            app.game_data = result['game_state']
            self.update_interface()
            self.show_popup('موفق', 'ساخت موفق بود!')
        else:
            self.show_popup('ناموفق', result.get('message', 'ساخت ناموفق بود'))
    
    def go_back(self, instance):
        self.manager.current = 'menu'
    
    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()

class IranWarApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server_url = "http://192.168.1.100:5000"  # Change to your server IP
        self.game_id = None
        self.player_id = None
        self.game_data = {}
    
    def build(self):
        sm = ScreenManager()
        
        sm.add_widget(MainMenuScreen(name='menu'))
        sm.add_widget(WaitingScreen(name='waiting'))
        sm.add_widget(GameScreen(name='game'))
        
        return sm
    
    def api_call(self, endpoint, data, callback):
        def make_request():
            try:
                response = requests.post(f'{self.server_url}/api/{endpoint}', 
                                       json=data, timeout=10)
                result = response.json()
                Clock.schedule_once(lambda dt: callback(result), 0)
            except Exception as e:
                print(f"API call failed: {e}")
                Clock.schedule_once(lambda dt: callback({'success': False, 'error': 'خطا در ارتباط'}), 0)
        
        threading.Thread(target=make_request, daemon=True).start()

if __name__ == '__main__':
    IranWarApp().run()