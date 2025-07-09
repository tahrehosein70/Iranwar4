# جنگ منطقه‌ای ایران (Iran Regional War Game)

## Overview

This is a real-time multiplayer strategy game set in Iran, where players compete for territorial control. The game features a web-based interface with Socket.IO for real-time communication, allowing 2-8 players to battle for control of Iranian regions. Players manage resources (coins, soldiers, companies), build structures, and engage in strategic warfare.

## System Architecture

### Client-Server Architecture
- **Frontend**: HTML/CSS/JavaScript with Socket.IO client for real-time communication
- **Backend**: Flask server with Socket.IO for WebSocket connections
- **Game Client**: Python/Pygame desktop client (alternative interface)
- **Game Logic**: Centralized server-side game state management

### Technology Stack
- **Backend**: Python Flask + Flask-SocketIO
- **Frontend**: Vanilla JavaScript + Socket.IO client
- **Desktop Client**: Python Pygame
- **Real-time Communication**: Socket.IO WebSockets
- **Styling**: CSS3 with Persian/RTL support

## Key Components

### 1. Server Architecture (`server.py`)
- **Flask Application**: Serves web interface and handles HTTP requests
- **Socket.IO Server**: Manages real-time game communication
- **Game Manager**: Handles multiple concurrent game sessions
- **Game Class**: Encapsulates individual game state and logic

### 2. Game Logic (`game_logic.py`)
- **Battle System**: Calculates combat outcomes with randomness factors
- **Resource Management**: Handles coins, soldiers, and buildings
- **Turn Management**: Manages player turns and game flow
- **Building Effects**: Implements barracks, factories, and banks

### 3. Map System (`iran_map.py`)
- **Region Definition**: Defines Iranian provinces with strategic values
- **Neighbor Mapping**: Establishes connectivity between regions
- **Resource Types**: Categorizes regions (industrial, cultural, religious)
- **Population Data**: Assigns population values to regions

### 4. Web Client (`static/game.js`)
- **Game State Management**: Handles client-side game state
- **UI Controllers**: Manages screen transitions and user interactions
- **Socket Communication**: Handles real-time server communication
- **Map Rendering**: Displays interactive Iran map

### 5. Desktop Client (`client.py`)
- **Pygame Interface**: Alternative desktop game interface
- **Socket.IO Client**: Connects to the same server as web clients
- **Real-time Rendering**: Handles game visualization and input

## Data Flow

### Game Session Flow
1. **Player Connection**: Players connect via web or desktop client
2. **Game Creation/Joining**: Host creates game, others join with game ID
3. **Game Initialization**: Server assigns regions and initial resources
4. **Turn-Based Gameplay**: Players take turns making moves
5. **Real-time Updates**: All clients receive immediate game state updates
6. **Game Completion**: Server determines winner and ends game

### Communication Protocol
- **Socket.IO Events**: Structured event-based communication
- **JSON Payloads**: All game data transmitted as JSON
- **Room Management**: Players grouped by game sessions
- **State Synchronization**: Server maintains authoritative game state

## External Dependencies

### Python Backend
- **Flask**: Web framework for HTTP server
- **Flask-SocketIO**: WebSocket support for real-time communication
- **Pygame**: Desktop client graphics and input handling

### Frontend
- **Socket.IO Client**: Real-time communication library
- **Vazir Font**: Persian font for UI text rendering

### No Database
- **In-Memory Storage**: All game state stored in server memory
- **Session-Based**: Games exist only during active sessions
- **No Persistence**: Game data is not saved between server restarts

## Deployment Strategy

### Development Setup
- Single server instance with Flask development server
- Static file serving through Flask
- Socket.IO integrated with Flask application
- No external database or cache required

### Production Considerations
- **Scalability**: Current architecture supports single server instance
- **Session Management**: Games stored in memory, limiting concurrent sessions
- **Load Balancing**: Would require session persistence for multiple servers
- **Database Integration**: Could be added for game history and user accounts

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

### July 06, 2025 - Complete Mobile & Offline Implementation

✓ Created complete mobile application using Kivy framework (mobile_app.py)
✓ Added Buildozer configuration for Android APK generation (buildozer.spec)
✓ Implemented Progressive Web App (PWA) features:
  - Service Worker for offline capability (sw.js)
  - Web App Manifest for installable app experience (manifest.json)
  - Mobile-optimized responsive interface
✓ Added comprehensive installation guides:
  - APK building instructions (APK_GUIDE.md)
  - PWA setup documentation (PWA_SETUP.md)
  - Mobile installation guide (MOBILE_INSTALL_GUIDE.md)
✓ Fixed Socket.IO dependency conflicts by creating simplified REST API server
✓ Successfully deployed working multiplayer game server on port 5000

### July 06, 2025 - Offline WiFi/Hotspot Functionality
✓ Created dedicated offline server (offline_simple_server.py) on port 5001
✓ Built offline-specific web interface (templates/offline_index.html)
✓ Implemented local WiFi/Hotspot multiplayer without internet dependency
✓ Added comprehensive offline guide (OFFLINE_WIFI_GUIDE.md) with setup instructions
✓ Created unified game launcher (game_launcher.py) for mode selection
✓ Supports both online (internet) and offline (WiFi-only) gameplay modes

### Architecture Updates
- **Web Client**: Uses REST API polling instead of WebSocket for better mobile compatibility
- **Mobile Client**: Native Kivy application with touch-optimized Iran map interface
- **PWA Support**: Service worker caching and app manifest for mobile installation
- **API Endpoints**: RESTful design for create_game, join_game, attack, build operations
- **Offline Mode**: Dedicated server for WiFi/Hotspot gameplay without internet dependency
- **Game Launcher**: Unified interface for choosing between online and offline modes

### Deployment Status
- Server running successfully on simple_server.py
- Web interface fully functional with Persian UI
- PWA installable on mobile devices via "Add to Home Screen"
- APK build configuration ready for Android deployment

## User Preferences

Preferred communication style: Simple, everyday language in Persian/Farsi.
User requested mobile APK version for WhatsApp sharing and Android installation.

## Changelog

- July 06, 2025: Initial setup and complete mobile implementation