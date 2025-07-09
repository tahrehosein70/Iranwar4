class IranWarGame {
    constructor() {
        this.socket = null;
        this.gameState = 'menu';
        this.gameId = null;
        this.playerId = null;
        this.playerName = '';
        this.gameData = {};
        this.selectedRegion = null;
        this.targetRegion = null;
        this.regionElements = {};
        
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
    
    connectToServer() {
        if (this.socket && this.socket.connected) {
            return Promise.resolve();
        }
        
        return new Promise((resolve, reject) => {
            this.socket = io();
            
            this.socket.on('connect', () => {
                console.log('Connected to server');
                this.setupSocketEvents();
                resolve();
            });
            
            this.socket.on('connect_error', (error) => {
                console.error('Connection error:', error);
                this.showNotification('خطا در اتصال به سرور', 'error');
                reject(error);
            });
        });
    }
    
    setupSocketEvents() {
        this.socket.on('game_created', (data) => {
            this.gameId = data.game_id;
            this.playerId = data.player_id;
            this.gameData = data.game_state;
            this.gameState = 'waiting';
            this.showScreen('waiting-room');
            this.updateWaitingRoom();
            this.showNotification('بازی با موفقیت ایجاد شد', 'success');
        });
        
        this.socket.on('player_joined', (data) => {
            this.gameData = data.game_state;
            this.updateWaitingRoom();
            this.showNotification(`${data.player_name} به بازی پیوست`, 'info');
        });
        
        this.socket.on('game_started', (data) => {
            this.gameData = data.game_state;
            this.gameState = 'playing';
            this.showScreen('game-screen');
            this.initializeGameMap();
            this.updateGameInterface();
            this.showNotification('بازی شروع شد!', 'success');
        });
        
        this.socket.on('attack_success', (data) => {
            this.gameData = data.game_state;
            this.updateGameInterface();
            this.updateMap();
            this.showNotification('حمله موفق بود!', 'success');
            this.addMessage('حمله موفق بود!', 'success');
        });
        
        this.socket.on('attack_failed', (data) => {
            this.showNotification('حمله ناموفق بود!', 'error');
            this.addMessage('حمله ناموفق بود!', 'error');
        });
        
        this.socket.on('build_success', (data) => {
            this.gameData = data.game_state;
            this.updateGameInterface();
            this.showNotification('ساخت موفق بود!', 'success');
            this.addMessage('ساخت موفق بود!', 'success');
        });
        
        this.socket.on('build_failed', (data) => {
            this.showNotification('ساخت ناموفق بود!', 'error');
            this.addMessage('ساخت ناموفق بود!', 'error');
        });
        
        this.socket.on('soldiers_reduced', (data) => {
            this.gameData = data.game_state;
            this.updateGameInterface();
            this.updateMap();
            this.showNotification('سربازها کاهش یافتند!', 'warning');
            this.addMessage('سربازها کاهش یافتند!', 'warning');
        });
        
        this.socket.on('game_over', (data) => {
            this.gameState = 'game-over';
            this.showScreen('game-over');
            this.showGameOver(data);
        });
        
        this.socket.on('player_disconnected', (data) => {
            this.showNotification('بازیکنی از بازی خارج شد', 'warning');
            this.addMessage('بازیکنی از بازی خارج شد', 'warning');
        });
        
        this.socket.on('error', (data) => {
            this.showNotification(data.message, 'error');
        });
    }
    
    async createGame() {
        const playerName = this.playerNameInput.value.trim();
        if (!playerName) {
            this.showNotification('نام بازیکن را وارد کنید', 'error');
            return;
        }
        
        this.playerName = playerName;
        
        try {
            await this.connectToServer();
            this.socket.emit('create_game', { player_name: playerName });
        } catch (error) {
            this.showNotification('خطا در اتصال به سرور', 'error');
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
        
        try {
            await this.connectToServer();
            this.socket.emit('join_game', { 
                player_name: playerName, 
                game_id: gameId 
            });
        } catch (error) {
            this.showNotification('خطا در اتصال به سرور', 'error');
        }
    }
    
    startGame() {
        this.socket.emit('start_game', { game_id: this.gameId });
    }
    
    leaveGame() {
        if (this.socket) {
            this.socket.disconnect();
        }
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
        const regionInfo = this.getIranRegions().find(r => r.id === this.selectedRegion);
        
        if (!region || !regionInfo) return;
        
        const owner = region.owner ? this.gameData.players[region.owner] : null;
        
        this.regionDetails.innerHTML = `
            <h4>${regionInfo.name}</h4>
            <p><strong>مالک:</strong> ${owner ? owner.name : 'بدون مالک'}</p>
            <p><strong>سربازها:</strong> ${region.soldiers}</p>
            <p><strong>ساختمان‌ها:</strong></p>
            <ul>
                <li>پادگان: ${region.buildings.barracks}</li>
                <li>کارخانه: ${region.buildings.factory}</li>
                <li>بانک: ${region.buildings.bank}</li>
            </ul>
        `;
    }
    
    updateGameInterface() {
        if (!this.gameData.players || !this.gameData.players[this.playerId]) return;
        
        const player = this.gameData.players[this.playerId];
        
        this.playerCoins.textContent = `سکه: ${player.coins}`;
        this.playerSoldiers.textContent = `سرباز: ${player.soldiers}`;
        this.playerCompanies.textContent = `شرکت: ${player.companies}`;
    }
    
    toggleAttackPanel() {
        const isHidden = this.attackPanel.classList.contains('hidden');
        
        if (isHidden) {
            this.attackPanel.classList.remove('hidden');
            this.buildPanel.classList.add('hidden');
        } else {
            this.attackPanel.classList.add('hidden');
        }
    }
    
    toggleBuildPanel() {
        const isHidden = this.buildPanel.classList.contains('hidden');
        
        if (isHidden) {
            this.buildPanel.classList.remove('hidden');
            this.attackPanel.classList.add('hidden');
        } else {
            this.buildPanel.classList.add('hidden');
        }
    }
    
    confirmAttack() {
        if (!this.selectedRegion || !this.targetRegion) {
            this.showNotification('منطقه مبدا و مقصد را انتخاب کنید', 'error');
            return;
        }
        
        const soldiers = parseInt(this.attackSoldiersInput.value);
        if (soldiers <= 0) {
            this.showNotification('تعداد سربازها باید بیشتر از صفر باشد', 'error');
            return;
        }
        
        this.socket.emit('attack', {
            game_id: this.gameId,
            from_region: this.selectedRegion,
            to_region: this.targetRegion,
            soldiers: soldiers
        });
        
        this.attackPanel.classList.add('hidden');
        this.selectedRegion = null;
        this.targetRegion = null;
        this.updateMap();
    }
    
    buildStructure(buildingType) {
        if (!this.selectedRegion) {
            this.showNotification('منطقه‌ای را انتخاب کنید', 'error');
            return;
        }
        
        this.socket.emit('build', {
            game_id: this.gameId,
            region_id: this.selectedRegion,
            structure_type: buildingType
        });
        
        this.buildPanel.classList.add('hidden');
    }
    
    endTurn() {
        this.socket.emit('end_turn', { game_id: this.gameId });
    }
    
    addMessage(message, type = 'info') {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${type}`;
        messageEl.textContent = `${new Date().toLocaleTimeString()}: ${message}`;
        
        this.messagesList.appendChild(messageEl);
        
        // Keep only last 20 messages
        while (this.messagesList.children.length > 20) {
            this.messagesList.removeChild(this.messagesList.firstChild);
        }
        
        // Scroll to bottom
        this.messagesList.scrollTop = this.messagesList.scrollHeight;
    }
    
    showNotification(message, type = 'info') {
        this.notificationText.textContent = message;
        this.notification.className = `notification ${type}`;
        this.notification.classList.remove('hidden');
        
        // Auto hide after 5 seconds
        setTimeout(() => {
            this.hideNotification();
        }, 5000);
    }
    
    hideNotification() {
        this.notification.classList.add('hidden');
    }
    
    showGameOver(data) {
        const winnerEl = document.getElementById('winner-announcement');
        const statsEl = document.getElementById('final-stats');
        
        if (data.winner) {
            const winner = this.gameData.players[data.winner];
            winnerEl.textContent = `${winner.name} برنده شد!`;
        } else {
            winnerEl.textContent = 'بازی به پایان رسید';
        }
        
        // Show final statistics
        let statsHTML = '<h4>آمار نهایی:</h4>';
        Object.entries(this.gameData.players).forEach(([playerId, player]) => {
            statsHTML += `
                <div class="stat-item">
                    <span>${player.name}</span>
                    <span>مناطق: ${player.regions.length} | سکه: ${player.coins}</span>
                </div>
            `;
        });
        
        statsEl.innerHTML = statsHTML;
    }
    
    getIranRegions() {
        return [
            {id: "tehran", name: "تهران", pos: [500, 300]},
            {id: "isfahan", name: "اصفهان", pos: [450, 400]},
            {id: "shiraz", name: "شیراز", pos: [400, 500]},
            {id: "mashhad", name: "مشهد", pos: [650, 200]},
            {id: "tabriz", name: "تبریز", pos: [350, 150]},
            {id: "ahvaz", name: "اهواز", pos: [300, 450]},
            {id: "qazvin", name: "قزوین", pos: [450, 250]},
            {id: "semnan", name: "سمنان", pos: [550, 250]},
            {id: "qom", name: "قم", pos: [475, 350]},
            {id: "yazd", name: "یزد", pos: [500, 450]},
            {id: "kerman", name: "کرمان", pos: [550, 500]},
            {id: "bushehr", name: "بوشهر", pos: [350, 500]},
            {id: "zanjan", name: "زنجان", pos: [400, 200]},
            {id: "ardabil", name: "اردبیل", pos: [350, 100]},
            {id: "lorestan", name: "لرستان", pos: [350, 400]},
            {id: "chaharmahal", name: "چهارمحال", pos: [400, 450]},
            {id: "khorasan", name: "خراسان", pos: [700, 250]},
            {id: "fars", name: "فارس", pos: [450, 520]},
            {id: "khuzestan", name: "خوزستان", pos: [280, 480]},
            {id: "mazandaran", name: "مازندران", pos: [500, 180]},
            {id: "golestan", name: "گلستان", pos: [580, 150]},
            {id: "hamedan", name: "همدان", pos: [380, 300]},
            {id: "kurdistan", name: "کردستان", pos: [320, 250]},
            {id: "west_azerbaijan", name: "آذربایجان غربی", pos: [300, 150]},
            {id: "east_azerbaijan", name: "آذربایجان شرقی", pos: [380, 120]}
        ];
    }
}

// Initialize game when page loads
document.addEventListener('DOMContentLoaded', () => {
    new IranWarGame();
});
