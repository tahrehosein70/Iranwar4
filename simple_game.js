class IranWarGame {
    constructor() {
        this.gameState = 'menu';
        this.gameId = null;
        this.playerId = null;
        this.playerName = '';
        this.gameData = {};
        this.selectedRegion = null;
        this.targetRegion = null;
        this.regionElements = {};
        this.pollInterval = null;
        
        this.initializeElements();
        this.setupEventListeners();
        this.showScreen('main-menu');
    }
    
    initializeElements() {
        // Screen elements
        this.screens = {
            'main-menu': document.getElementById('main-menu'),
            'waiting-room': document.getElementById('waiting-room'),
            'game-screen': document.getElementById('game-screen'),
            'game-over': document.getElementById('game-over')
        };
        
        // Main menu elements
        this.playerNameInput = document.getElementById('player-name');
        this.createGameBtn = document.getElementById('create-game-btn');
        this.joinGameBtn = document.getElementById('join-game-btn');
        this.joinGameForm = document.getElementById('join-game-form');
        this.gameIdInput = document.getElementById('game-id');
        this.joinConfirmBtn = document.getElementById('join-confirm-btn');
        
        // Waiting room elements
        this.gameIdDisplay = document.getElementById('game-id-display');
        this.playersUl = document.getElementById('players-ul');
        this.startGameBtn = document.getElementById('start-game-btn');
        this.leaveGameBtn = document.getElementById('leave-game-btn');
        
        // Game screen elements
        this.playerCoins = document.getElementById('player-coins');
        this.playerSoldiers = document.getElementById('player-soldiers');
        this.playerCompanies = document.getElementById('player-companies');
        this.iranMap = document.getElementById('iran-map');
        this.regionDetails = document.getElementById('region-details');
        this.attackPanel = document.getElementById('attack-panel');
        this.buildPanel = document.getElementById('build-panel');
        this.messagesList = document.getElementById('messages-list');
        
        // Action buttons
        this.attackBtn = document.getElementById('attack-btn');
        this.buildBtn = document.getElementById('build-btn');
        this.endTurnBtn = document.getElementById('end-turn-btn');
        this.confirmAttackBtn = document.getElementById('confirm-attack-btn');
        this.attackSoldiersInput = document.getElementById('attack-soldiers');
        
        // Notification
        this.notification = document.getElementById('notification');
        this.notificationText = document.getElementById('notification-text');
        this.notificationClose = document.getElementById('notification-close');
    }
    
    setupEventListeners() {
        // Main menu events
        this.createGameBtn.addEventListener('click', () => this.createGame());
        this.joinGameBtn.addEventListener('click', () => this.toggleJoinForm());
        this.joinConfirmBtn.addEventListener('click', () => this.joinGame());
        
        // Waiting room events
        this.startGameBtn.addEventListener('click', () => this.startGame());
        this.leaveGameBtn.addEventListener('click', () => this.leaveGame());
        
        // Game events
        this.attackBtn.addEventListener('click', () => this.toggleAttackPanel());
        this.buildBtn.addEventListener('click', () => this.toggleBuildPanel());
        this.endTurnBtn.addEventListener('click', () => this.endTurn());
        this.confirmAttackBtn.addEventListener('click', () => this.confirmAttack());
        
        // Build options
        document.querySelectorAll('.build-option').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const buildingType = e.currentTarget.dataset.building;
                this.buildStructure(buildingType);
            });
        });
        
        // Notification close
        this.notificationClose.addEventListener('click', () => this.hideNotification());
        
        // New game button
        document.getElementById('new-game-btn').addEventListener('click', () => {
            this.resetGame();
            this.showScreen('main-menu');
        });
        
        // Enter key handling
        this.playerNameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.createGame();
        });
        
        this.gameIdInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.joinGame();
        });
    }
    
    async apiCall(endpoint, data = {}) {
        try {
            const response = await fetch(`/api/${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            this.showNotification('خطا در ارتباط با سرور', 'error');
            return { success: false, error: 'خطا در ارتباط' };
        }
    }
    
    async createGame() {
        const playerName = this.playerNameInput.value.trim();
        if (!playerName) {
            this.showNotification('نام بازیکن را وارد کنید', 'error');
            return;
        }
        
        this.playerName = playerName;
        const result = await this.apiCall('create_game', { player_name: playerName });
        
        if (result.success) {
            this.gameId = result.game_id;
            this.playerId = result.player_id;
            this.gameData = result.game_state;
            this.gameState = 'waiting';
            this.showScreen('waiting-room');
            this.updateWaitingRoom();
            this.showNotification('بازی با موفقیت ایجاد شد', 'success');
            this.startPolling();
        } else {
            this.showNotification(result.error || 'خطا در ایجاد بازی', 'error');
        }
    }
    
    toggleJoinForm() {
        const isHidden = this.joinGameForm.classList.contains('hidden');
        if (isHidden) {
            this.joinGameForm.classList.remove('hidden');
            this.gameIdInput.focus();
        } else {
            this.joinGameForm.classList.add('hidden');
        }
    }
    
    async joinGame() {
        const playerName = this.playerNameInput.value.trim();
        const gameId = this.gameIdInput.value.trim();
        
        if (!playerName || !gameId) {
            this.showNotification('نام بازیکن و شناسه بازی را وارد کنید', 'error');
            return;
        }
        
        this.playerName = playerName;
        const result = await this.apiCall('join_game', { 
            player_name: playerName, 
            game_id: gameId 
        });
        
        if (result.success) {
            this.gameId = gameId;
            this.playerId = result.player_id;
            this.gameData = result.game_state;
            this.gameState = 'waiting';
            this.showScreen('waiting-room');
            this.updateWaitingRoom();
            this.showNotification('با موفقیت به بازی پیوستید', 'success');
            this.startPolling();
        } else {
            this.showNotification(result.error || 'خطا در پیوستن به بازی', 'error');
        }
    }
    
    async startGame() {
        const result = await this.apiCall('start_game', { 
            game_id: this.gameId,
            player_id: this.playerId
        });
        
        if (result.success) {
            this.gameData = result.game_state;
            this.gameState = 'playing';
            this.showScreen('game-screen');
            this.initializeGameMap();
            this.updateGameInterface();
            this.showNotification('بازی شروع شد!', 'success');
        } else {
            this.showNotification(result.error || 'خطا در شروع بازی', 'error');
        }
    }
    
    leaveGame() {
        this.stopPolling();
        this.resetGame();
        this.showScreen('main-menu');
    }
    
    resetGame() {
        this.gameState = 'menu';
        this.gameId = null;
        this.playerId = null;
        this.playerName = '';
        this.gameData = {};
        this.selectedRegion = null;
        this.targetRegion = null;
        this.regionElements = {};
        
        // Clear inputs
        this.playerNameInput.value = '';
        this.gameIdInput.value = '';
        this.joinGameForm.classList.add('hidden');
        
        // Clear messages
        this.messagesList.innerHTML = '';
        
        this.stopPolling();
    }
    
    startPolling() {
        this.stopPolling();
        this.pollInterval = setInterval(() => {
            this.pollGameState();
        }, 2000); // Poll every 2 seconds
    }
    
    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }
    
    async pollGameState() {
        if (!this.gameId) return;
        
        const result = await this.apiCall('get_game_state', { game_id: this.gameId });
        
        if (result.success) {
            const oldState = this.gameData.game_state;
            this.gameData = result.game_state;
            
            // Check if game state changed
            if (oldState !== this.gameData.game_state) {
                if (this.gameData.game_state === 'playing' && this.gameState === 'waiting') {
                    this.gameState = 'playing';
                    this.showScreen('game-screen');
                    this.initializeGameMap();
                    this.updateGameInterface();
                    this.showNotification('بازی شروع شد!', 'success');
                }
            }
            
            // Update UI based on current screen
            if (this.gameState === 'waiting') {
                this.updateWaitingRoom();
            } else if (this.gameState === 'playing') {
                this.updateGameInterface();
                this.updateMap();
            }
        }
    }
    
    showScreen(screenName) {
        Object.values(this.screens).forEach(screen => {
            screen.classList.remove('active');
        });
        
        if (this.screens[screenName]) {
            this.screens[screenName].classList.add('active');
        }
    }
    
    updateWaitingRoom() {
        // Update game ID display
        this.gameIdDisplay.textContent = `شناسه بازی: ${this.gameId}`;
        
        // Update players list
        this.playersUl.innerHTML = '';
        
        if (this.gameData.players) {
            Object.entries(this.gameData.players).forEach(([playerId, player]) => {
                const li = document.createElement('li');
                li.className = player.connected ? 'player-connected' : 'player-disconnected';
                
                const statusIndicator = document.createElement('span');
                statusIndicator.className = `status-indicator ${player.connected ? 'status-online' : 'status-offline'}`;
                
                const playerInfo = document.createElement('div');
                playerInfo.innerHTML = `
                    <strong>${player.name}</strong>
                    <small>سکه: ${player.coins} | سرباز: ${player.soldiers}</small>
                `;
                
                li.appendChild(statusIndicator);
                li.appendChild(playerInfo);
                this.playersUl.appendChild(li);
            });
        }
        
        // Show start button only for host
        if (this.gameData.host === this.playerId) {
            this.startGameBtn.classList.remove('hidden');
        } else {
            this.startGameBtn.classList.add('hidden');
        }
    }
    
    initializeGameMap() {
        // Clear existing map
        this.iranMap.innerHTML = '';
        this.regionElements = {};
        
        // Create Iran regions
        const regions = this.getIranRegions();
        
        regions.forEach(region => {
            // Create region element
            const regionEl = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            regionEl.setAttribute('cx', region.pos[0]);
            regionEl.setAttribute('cy', region.pos[1]);
            regionEl.setAttribute('r', '25');
            regionEl.setAttribute('fill', '#cccccc');
            regionEl.setAttribute('stroke', '#333333');
            regionEl.setAttribute('stroke-width', '2');
            regionEl.classList.add('region');
            regionEl.dataset.regionId = region.id;
            
            // Add click event
            regionEl.addEventListener('click', () => this.selectRegion(region.id));
            
            this.iranMap.appendChild(regionEl);
            this.regionElements[region.id] = regionEl;
            
            // Add region label
            const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            label.setAttribute('x', region.pos[0]);
            label.setAttribute('y', region.pos[1] - 30);
            label.setAttribute('class', 'region-label');
            label.textContent = region.name;
            this.iranMap.appendChild(label);
            
            // Add soldier count
            const soldierCount = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            soldierCount.setAttribute('x', region.pos[0]);
            soldierCount.setAttribute('y', region.pos[1] + 40);
            soldierCount.setAttribute('class', 'soldier-count');
            soldierCount.textContent = '0';
            this.iranMap.appendChild(soldierCount);
            this.regionElements[region.id + '_soldiers'] = soldierCount;
        });
        
        this.updateMap();
    }
    
    updateMap() {
        if (!this.gameData.regions || !this.gameData.players) return;
        
        Object.entries(this.gameData.regions).forEach(([regionId, regionData]) => {
            const regionEl = this.regionElements[regionId];
            const soldierEl = this.regionElements[regionId + '_soldiers'];
            
            if (regionEl) {
                // Update region color based on owner
                if (regionData.owner && this.gameData.players[regionData.owner]) {
                    const playerColor = this.gameData.players[regionData.owner].color;
                    regionEl.setAttribute('fill', playerColor);
                } else {
                    regionEl.setAttribute('fill', '#cccccc');
                }
                
                // Update selection state
                if (this.selectedRegion === regionId) {
                    regionEl.classList.add('selected');
                } else {
                    regionEl.classList.remove('selected');
                }
                
                if (this.targetRegion === regionId) {
                    regionEl.classList.add('target');
                } else {
                    regionEl.classList.remove('target');
                }
            }
            
            if (soldierEl) {
                soldierEl.textContent = regionData.soldiers || 0;
            }
        });
    }
    
    selectRegion(regionId) {
        if (this.selectedRegion === regionId) {
            // Deselect if clicking the same region
            this.selectedRegion = null;
            this.targetRegion = null;
        } else if (this.selectedRegion === null) {
            // Select first region
            this.selectedRegion = regionId;
            this.targetRegion = null;
        } else {
            // Select target region
            this.targetRegion = regionId;
        }
        
        this.updateMap();
        this.updateRegionDetails();
    }
    
    updateRegionDetails() {
        if (!this.selectedRegion || !this.gameData.regions) {
            this.regionDetails.innerHTML = '<p>منطقه‌ای را انتخاب کنید</p>';
            return;
        }
        
        const region = this.gameData.regions[this.selectedRegion];
        const owner = region.owner ? this.gameData.players[region.owner] : null;
        
        this.regionDetails.innerHTML = `
            <h4>${region.name || this.selectedRegion}</h4>
            <p><strong>مالک:</strong> ${owner ? owner.name : 'بدون مالک'}</p>
            <p><strong>سربازان:</strong> ${region.soldiers}</p>
            <p><strong>ساختمان‌ها:</strong></p>
            <ul>
                <li>پادگان: ${region.buildings.barracks}</li>
                <li>کارخانه: ${region.buildings.factory}</li>
                <li>بانک: ${region.buildings.bank}</li>
            </ul>
        `;
    }
    
    updateGameInterface() {
        if (!this.gameData.players || !this.playerId) return;
        
        const player = this.gameData.players[this.playerId];
        if (player) {
            this.playerCoins.textContent = `سکه: ${player.coins}`;
            this.playerSoldiers.textContent = `سرباز: ${player.soldiers}`;
            this.playerCompanies.textContent = `شرکت: ${player.companies}`;
        }
    }
    
    toggleAttackPanel() {
        const isHidden = this.attackPanel.classList.contains('hidden');
        this.attackPanel.classList.toggle('hidden', !isHidden);
        this.buildPanel.classList.add('hidden');
    }
    
    toggleBuildPanel() {
        const isHidden = this.buildPanel.classList.contains('hidden');
        this.buildPanel.classList.toggle('hidden', !isHidden);
        this.attackPanel.classList.add('hidden');
    }
    
    async confirmAttack() {
        if (!this.selectedRegion || !this.targetRegion) {
            this.showNotification('مبدأ و مقصد حمله را انتخاب کنید', 'error');
            return;
        }
        
        const soldiers = parseInt(this.attackSoldiersInput.value) || 1;
        
        const result = await this.apiCall('attack', {
            game_id: this.gameId,
            player_id: this.playerId,
            from_region: this.selectedRegion,
            to_region: this.targetRegion,
            soldiers: soldiers
        });
        
        this.showNotification(result.message, result.success ? 'success' : 'error');
        this.addMessage(result.message, result.success ? 'success' : 'error');
        
        if (result.success) {
            this.gameData = result.game_state;
            this.updateGameInterface();
            this.updateMap();
            this.selectedRegion = null;
            this.targetRegion = null;
            this.attackPanel.classList.add('hidden');
        }
    }
    
    async buildStructure(buildingType) {
        if (!this.selectedRegion) {
            this.showNotification('منطقه‌ای برای ساخت انتخاب کنید', 'error');
            return;
        }
        
        const result = await this.apiCall('build', {
            game_id: this.gameId,
            player_id: this.playerId,
            region_id: this.selectedRegion,
            structure_type: buildingType
        });
        
        this.showNotification(result.message, result.success ? 'success' : 'error');
        this.addMessage(result.message, result.success ? 'success' : 'error');
        
        if (result.success) {
            this.gameData = result.game_state;
            this.updateGameInterface();
            this.updateRegionDetails();
            this.buildPanel.classList.add('hidden');
        }
    }
    
    endTurn() {
        // Implement turn ending logic
        this.showNotification('نوبت پایان یافت', 'info');
    }
    
    addMessage(message, type = 'info') {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${type}`;
        messageEl.textContent = `${new Date().toLocaleTimeString()}: ${message}`;
        this.messagesList.appendChild(messageEl);
        
        // Scroll to bottom
        this.messagesList.scrollTop = this.messagesList.scrollHeight;
        
        // Keep only last 10 messages
        while (this.messagesList.children.length > 10) {
            this.messagesList.removeChild(this.messagesList.firstChild);
        }
    }
    
    showNotification(message, type = 'info') {
        this.notificationText.textContent = message;
        this.notification.className = `notification ${type}`;
        this.notification.classList.remove('hidden');
        
        // Auto hide after 3 seconds
        setTimeout(() => {
            this.hideNotification();
        }, 3000);
    }
    
    hideNotification() {
        this.notification.classList.add('hidden');
    }
    
    showGameOver(data) {
        // Implement game over screen
        document.getElementById('winner-announcement').textContent = 
            data.winner ? `برنده: ${data.winner}` : 'بازی پایان یافت';
    }
    
    getIranRegions() {
        // Simplified Iran regions for the map
        return [
            { id: 'tehran', name: 'تهران', pos: [400, 200] },
            { id: 'isfahan', name: 'اصفهان', pos: [350, 300] },
            { id: 'shiraz', name: 'شیراز', pos: [300, 400] },
            { id: 'mashhad', name: 'مشهد', pos: [550, 150] },
            { id: 'tabriz', name: 'تبریز', pos: [250, 100] },
            { id: 'ahvaz', name: 'اهواز', pos: [200, 350] },
            { id: 'qazvin', name: 'قزوین', pos: [350, 150] },
            { id: 'semnan', name: 'سمنان', pos: [450, 150] },
            { id: 'qom', name: 'قم', pos: [375, 250] },
            { id: 'yazd', name: 'یزد', pos: [400, 350] },
            { id: 'kerman', name: 'کرمان', pos: [450, 400] },
            { id: 'bushehr', name: 'بوشهر', pos: [250, 400] },
            { id: 'zanjan', name: 'زنجان', pos: [300, 150] },
            { id: 'ardabil', name: 'اردبیل', pos: [250, 50] },
            { id: 'lorestan', name: 'لرستان', pos: [250, 300] },
            { id: 'chaharmahal', name: 'چهارمحال', pos: [300, 350] },
            { id: 'khorasan', name: 'خراسان', pos: [600, 200] },
            { id: 'fars', name: 'فارس', pos: [350, 450] },
            { id: 'khuzestan', name: 'خوزستان', pos: [180, 380] },
            { id: 'mazandaran', name: 'مازندران', pos: [400, 100] },
            { id: 'golestan', name: 'گلستان', pos: [480, 100] },
            { id: 'hamedan', name: 'همدان', pos: [280, 200] },
            { id: 'kurdistan', name: 'کردستان', pos: [220, 200] },
            { id: 'west_azerbaijan', name: 'آذربایجان غربی', pos: [200, 100] },
            { id: 'east_azerbaijan', name: 'آذربایجان شرقی', pos: [280, 80] }
        ];
    }
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new IranWarGame();
});