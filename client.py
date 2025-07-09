import pygame
import socketio
import json
import sys
import threading
import time
from typing import Dict, List, Optional

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

class GameClient:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("جنگ منطقه‌ای ایران")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.game_state = "menu"  # menu, waiting, playing
        self.game_id = None
        self.player_id = None
        self.player_name = ""
        self.game_data = {}
        self.selected_region = None
        self.target_region = None
        self.server_ip = "localhost"
        self.server_port = 5000
        
        # Socket.IO client
        self.sio = socketio.Client()
        self.setup_socket_events()
        
        # UI elements
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.input_text = ""
        self.input_active = False
        self.input_rect = pygame.Rect(400, 300, 200, 32)
        self.messages = []
        
        # Iran map regions (simplified representation)
        self.regions = self.create_iran_regions()
        
    def create_iran_regions(self):
        """Create simplified Iran map regions"""
        regions = {}
        
        # Define regions with approximate positions and neighbors
        region_data = [
            {"id": "tehran", "name": "تهران", "pos": (500, 300), "neighbors": ["qazvin", "semnan", "qom"]},
            {"id": "isfahan", "name": "اصفهان", "pos": (450, 400), "neighbors": ["qom", "yazd", "chaharmahal"]},
            {"id": "shiraz", "name": "شیراز", "pos": (400, 500), "neighbors": ["isfahan", "bushehr", "kerman"]},
            {"id": "mashhad", "name": "مشهد", "pos": (650, 200), "neighbors": ["semnan", "khorasan"]},
            {"id": "tabriz", "name": "تبریز", "pos": (350, 150), "neighbors": ["ardabil", "zanjan"]},
            {"id": "ahvaz", "name": "اهواز", "pos": (300, 450), "neighbors": ["lorestan", "bushehr"]},
            {"id": "qazvin", "name": "قزوین", "pos": (450, 250), "neighbors": ["tehran", "zanjan"]},
            {"id": "semnan", "name": "سمنان", "pos": (550, 250), "neighbors": ["tehran", "mashhad"]},
            {"id": "qom", "name": "قم", "pos": (475, 350), "neighbors": ["tehran", "isfahan"]},
            {"id": "yazd", "name": "یزد", "pos": (500, 450), "neighbors": ["isfahan", "kerman"]},
            {"id": "kerman", "name": "کرمان", "pos": (550, 500), "neighbors": ["yazd", "shiraz"]},
            {"id": "bushehr", "name": "بوشهر", "pos": (350, 500), "neighbors": ["shiraz", "ahvaz"]},
            {"id": "zanjan", "name": "زنجان", "pos": (400, 200), "neighbors": ["tabriz", "qazvin"]},
            {"id": "ardabil", "name": "اردبیل", "pos": (350, 100), "neighbors": ["tabriz"]},
            {"id": "lorestan", "name": "لرستان", "pos": (350, 400), "neighbors": ["ahvaz"]},
            {"id": "chaharmahal", "name": "چهارمحال", "pos": (400, 450), "neighbors": ["isfahan"]},
            {"id": "khorasan", "name": "خراسان", "pos": (700, 250), "neighbors": ["mashhad"]},
        ]
        
        for region in region_data:
            regions[region["id"]] = {
                "name": region["name"],
                "pos": region["pos"],
                "neighbors": region["neighbors"],
                "owner": None,
                "soldiers": 0,
                "buildings": {"barracks": 0, "factory": 0, "bank": 0},
                "rect": pygame.Rect(region["pos"][0] - 30, region["pos"][1] - 20, 60, 40)
            }
        
        return regions
    
    def setup_socket_events(self):
        """Setup Socket.IO event handlers"""
        @self.sio.event
        def connect():
            print("Connected to server")
            self.add_message("متصل به سرور شد")
        
        @self.sio.event
        def disconnect():
            print("Disconnected from server")
            self.add_message("اتصال قطع شد")
        
        @self.sio.event
        def game_created(data):
            self.game_id = data['game_id']
            self.player_id = data['player_id']
            self.game_data = data['game_state']
            self.game_state = "waiting"
            self.add_message(f"بازی {self.game_id} ایجاد شد")
        
        @self.sio.event
        def player_joined(data):
            self.game_data = data['game_state']
            self.add_message(f"{data['player_name']} به بازی پیوست")
        
        @self.sio.event
        def game_started(data):
            self.game_data = data['game_state']
            self.game_state = "playing"
            self.add_message("بازی شروع شد!")
        
        @self.sio.event
        def attack_success(data):
            self.game_data = data['game_state']
            self.add_message("حمله موفق بود!")
        
        @self.sio.event
        def attack_failed(data):
            self.add_message("حمله ناموفق بود!")
        
        @self.sio.event
        def build_success(data):
            self.game_data = data['game_state']
            self.add_message("ساخت موفق بود!")
        
        @self.sio.event
        def build_failed(data):
            self.add_message("ساخت ناموفق بود!")
        
        @self.sio.event
        def error(data):
            self.add_message(f"خطا: {data['message']}")
        
        @self.sio.event
        def game_state_update(data):
            self.game_data = data
        
        @self.sio.event
        def soldiers_reduced(data):
            self.game_data = data['game_state']
            self.add_message("سربازها کاهش یافتند!")
    
    def add_message(self, message):
        """Add message to message list"""
        self.messages.append(message)
        if len(self.messages) > 10:
            self.messages.pop(0)
    
    def connect_to_server(self):
        """Connect to game server"""
        try:
            self.sio.connect(f'http://{self.server_ip}:{self.server_port}')
            return True
        except Exception as e:
            self.add_message(f"خطا در اتصال: {str(e)}")
            return False
    
    def draw_menu(self):
        """Draw main menu"""
        self.screen.fill(WHITE)
        
        # Title
        title = self.font.render("جنگ منطقه‌ای ایران", True, BLACK)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Player name input
        name_label = self.small_font.render("نام بازیکن:", True, BLACK)
        self.screen.blit(name_label, (300, 270))
        
        # Input box
        color = BLUE if self.input_active else BLACK
        pygame.draw.rect(self.screen, color, self.input_rect, 2)
        
        # Input text
        input_surface = self.small_font.render(self.input_text, True, BLACK)
        self.screen.blit(input_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
        
        # Buttons
        create_button = pygame.Rect(300, 400, 150, 50)
        join_button = pygame.Rect(500, 400, 150, 50)
        
        pygame.draw.rect(self.screen, LIGHT_GRAY, create_button)
        pygame.draw.rect(self.screen, LIGHT_GRAY, join_button)
        pygame.draw.rect(self.screen, BLACK, create_button, 2)
        pygame.draw.rect(self.screen, BLACK, join_button, 2)
        
        create_text = self.small_font.render("ساخت بازی", True, BLACK)
        join_text = self.small_font.render("پیوستن", True, BLACK)
        
        create_rect = create_text.get_rect(center=create_button.center)
        join_rect = join_text.get_rect(center=join_button.center)
        
        self.screen.blit(create_text, create_rect)
        self.screen.blit(join_text, join_rect)
        
        # Messages
        y_offset = 500
        for message in self.messages[-5:]:
            msg_surface = self.small_font.render(message, True, BLACK)
            self.screen.blit(msg_surface, (50, y_offset))
            y_offset += 25
        
        return create_button, join_button
    
    def draw_waiting_room(self):
        """Draw waiting room"""
        self.screen.fill(WHITE)
        
        # Title
        title = self.font.render(f"انتظار برای بازی {self.game_id}", True, BLACK)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Players list
        if self.game_data and 'players' in self.game_data:
            y_offset = 200
            for player_id, player_data in self.game_data['players'].items():
                player_text = f"{player_data['name']} - سکه: {player_data['coins']} - سرباز: {player_data['soldiers']}"
                color = GREEN if player_data['connected'] else RED
                text_surface = self.small_font.render(player_text, True, color)
                self.screen.blit(text_surface, (50, y_offset))
                y_offset += 30
        
        # Start button (only for host)
        start_button = None
        if self.game_data and self.player_id == self.game_data.get('host'):
            start_button = pygame.Rect(450, 400, 150, 50)
            pygame.draw.rect(self.screen, GREEN, start_button)
            pygame.draw.rect(self.screen, BLACK, start_button, 2)
            
            start_text = self.small_font.render("شروع بازی", True, BLACK)
            start_rect = start_text.get_rect(center=start_button.center)
            self.screen.blit(start_text, start_rect)
        
        # Messages
        y_offset = 500
        for message in self.messages[-5:]:
            msg_surface = self.small_font.render(message, True, BLACK)
            self.screen.blit(msg_surface, (50, y_offset))
            y_offset += 25
        
        return start_button
    
    def draw_game(self):
        """Draw game interface"""
        self.screen.fill(WHITE)
        
        # Draw regions
        for region_id, region in self.regions.items():
            # Get region data from server
            server_region = None
            if self.game_data and 'regions' in self.game_data:
                server_region = self.game_data['regions'].get(region_id)
            
            # Determine color
            color = GRAY
            if server_region and server_region['owner']:
                player_color = self.game_data['players'][server_region['owner']]['color']
                color = tuple(int(player_color[i:i+2], 16) for i in (1, 3, 5))
            
            # Draw region
            pygame.draw.ellipse(self.screen, color, region['rect'])
            pygame.draw.ellipse(self.screen, BLACK, region['rect'], 2)
            
            # Highlight selected region
            if self.selected_region == region_id:
                pygame.draw.ellipse(self.screen, YELLOW, region['rect'], 4)
            
            # Draw region name
            name_surface = self.small_font.render(region['name'], True, BLACK)
            name_rect = name_surface.get_rect(center=region['rect'].center)
            self.screen.blit(name_surface, name_rect)
            
            # Draw soldier count
            if server_region:
                soldiers_text = str(server_region['soldiers'])
                soldiers_surface = self.small_font.render(soldiers_text, True, BLACK)
                soldiers_rect = soldiers_surface.get_rect(center=(region['rect'].centerx, region['rect'].bottom + 15))
                self.screen.blit(soldiers_surface, soldiers_rect)
        
        # Draw player info
        if self.game_data and 'players' in self.game_data and self.player_id in self.game_data['players']:
            player = self.game_data['players'][self.player_id]
            info_text = f"سکه: {player['coins']} | سرباز: {player['soldiers']} | شرکت: {player['companies']}"
            info_surface = self.small_font.render(info_text, True, BLACK)
            self.screen.blit(info_surface, (10, 10))
        
        # Draw action buttons
        attack_button = pygame.Rect(50, 650, 100, 40)
        build_button = pygame.Rect(160, 650, 100, 40)
        
        pygame.draw.rect(self.screen, RED, attack_button)
        pygame.draw.rect(self.screen, BLUE, build_button)
        pygame.draw.rect(self.screen, BLACK, attack_button, 2)
        pygame.draw.rect(self.screen, BLACK, build_button, 2)
        
        attack_text = self.small_font.render("حمله", True, WHITE)
        build_text = self.small_font.render("ساخت", True, WHITE)
        
        attack_rect = attack_text.get_rect(center=attack_button.center)
        build_rect = build_text.get_rect(center=build_button.center)
        
        self.screen.blit(attack_text, attack_rect)
        self.screen.blit(build_text, build_rect)
        
        # Messages
        y_offset = 50
        for message in self.messages[-3:]:
            msg_surface = self.small_font.render(message, True, BLACK)
            self.screen.blit(msg_surface, (700, y_offset))
            y_offset += 25
        
        return attack_button, build_button
    
    def handle_menu_click(self, pos, create_button, join_button):
        """Handle menu clicks"""
        if create_button.collidepoint(pos):
            if self.input_text.strip():
                self.player_name = self.input_text.strip()
                if self.connect_to_server():
                    self.sio.emit('create_game', {'player_name': self.player_name})
        
        elif join_button.collidepoint(pos):
            if self.input_text.strip():
                parts = self.input_text.strip().split()
                if len(parts) >= 2:
                    self.player_name = parts[0]
                    game_id = parts[1]
                    if self.connect_to_server():
                        self.sio.emit('join_game', {'game_id': game_id, 'player_name': self.player_name})
        
        elif self.input_rect.collidepoint(pos):
            self.input_active = True
        else:
            self.input_active = False
    
    def handle_waiting_click(self, pos, start_button):
        """Handle waiting room clicks"""
        if start_button and start_button.collidepoint(pos):
            self.sio.emit('start_game', {'game_id': self.game_id})
    
    def handle_game_click(self, pos, attack_button, build_button):
        """Handle game clicks"""
        if attack_button.collidepoint(pos):
            if self.selected_region and self.target_region:
                self.sio.emit('attack', {
                    'game_id': self.game_id,
                    'from_region': self.selected_region,
                    'to_region': self.target_region,
                    'soldiers': 5
                })
                self.selected_region = None
                self.target_region = None
        
        elif build_button.collidepoint(pos):
            if self.selected_region:
                self.sio.emit('build', {
                    'game_id': self.game_id,
                    'region_id': self.selected_region,
                    'structure_type': 'barracks'
                })
        
        else:
            # Check region clicks
            for region_id, region in self.regions.items():
                if region['rect'].collidepoint(pos):
                    if self.selected_region is None:
                        self.selected_region = region_id
                    elif self.selected_region == region_id:
                        self.selected_region = None
                        self.target_region = None
                    else:
                        self.target_region = region_id
                    break
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_state == "menu":
                        create_button, join_button = self.draw_menu()
                        self.handle_menu_click(event.pos, create_button, join_button)
                    
                    elif self.game_state == "waiting":
                        start_button = self.draw_waiting_room()
                        self.handle_waiting_click(event.pos, start_button)
                    
                    elif self.game_state == "playing":
                        attack_button, build_button = self.draw_game()
                        self.handle_game_click(event.pos, attack_button, build_button)
                
                elif event.type == pygame.KEYDOWN:
                    if self.input_active:
                        if event.key == pygame.K_RETURN:
                            self.input_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        else:
                            self.input_text += event.unicode
            
            # Draw based on game state
            if self.game_state == "menu":
                self.draw_menu()
            elif self.game_state == "waiting":
                self.draw_waiting_room()
            elif self.game_state == "playing":
                self.draw_game()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        # Cleanup
        if self.sio.connected:
            self.sio.disconnect()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    client = GameClient()
    client.run()
