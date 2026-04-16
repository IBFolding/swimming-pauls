// Paul AI Simulation Engine
// Handles 1000 real Pauls + 3000 visual fillers

const PAUL_TYPES = [
  { name: 'Visionary', emoji: '🎯', color: '#8b5cf6', bias: 'bullish' },
  { name: 'Trader', emoji: '📊', color: '#3b82f6', bias: 'neutral' },
  { name: 'Quant', emoji: '🧮', color: '#10b981', bias: 'neutral' },
  { name: 'Whale', emoji: '🐋', color: '#f59e0b', bias: 'bullish' },
  { name: 'Degen', emoji: '🎰', color: '#ec4899', bias: 'high_risk' },
  { name: 'Skeptic', emoji: '🤨', color: '#6b7280', bias: 'bearish' },
  { name: 'Professor', emoji: '🎓', color: '#ef4444', bias: 'research' },
  { name: 'Contrarian', emoji: '↔️', color: '#f97316', bias: 'contrarian' }
];

const PROFESSIONS = [
  'Day Trader', 'Swing Trader', 'Quant Analyst', 'Researcher', 'Portfolio Manager',
  'Risk Analyst', 'Crypto Specialist', 'Meme Coin Expert', 'DeFi Researcher',
  'NFT Flipper', 'Options Trader', 'Macro Analyst', 'Technical Analyst',
  'Fundamental Analyst', 'Sentiment Analyst'
];

const BUILDINGS = {
  market: { name: 'Market House', x: 100, y: 100, capacity: 300, activities: ['trading', 'analyzing'], color: '#22c55e' },
  research: { name: 'Research Lab', x: 400, y: 100, capacity: 250, activities: ['studying', 'researching'], color: '#3b82f6' },
  social: { name: 'Social Plaza', x: 700, y: 100, capacity: 400, activities: ['chatting', 'networking'], color: '#ec4899' },
  cafe: { name: 'The Cafe', x: 100, y: 350, capacity: 200, activities: ['relaxing', 'discussing'], color: '#eab308' },
  dex: { name: 'DEX Terminal', x: 400, y: 350, capacity: 200, activities: ['trading', 'swapping'], color: '#8b5cf6' },
  home: { name: 'Paul Estates', x: 700, y: 350, capacity: 150, activities: ['sleeping', 'resting'], color: '#6b7280' },
  townhall: { name: 'Town Hall', x: 100, y: 600, capacity: 250, activities: ['governing', 'voting'], color: '#f59e0b' },
  arcade: { name: 'Arcade', x: 400, y: 600, capacity: 350, activities: ['gaming', 'competing'], color: '#d946ef' },
  garden: { name: 'Garden', x: 700, y: 600, capacity: 150, activities: ['training', 'meditating'], color: '#10b981' },
  oracle: { name: 'Oracle Tower', x: 250, y: 225, capacity: 200, activities: ['predicting', 'forecasting'], color: '#6366f1' },
  power: { name: 'Power Plant', x: 550, y: 225, capacity: 150, activities: ['computing', 'processing'], color: '#f97316' },
  newsroom: { name: 'Newsroom', x: 250, y: 475, capacity: 250, activities: ['reporting', 'aggregating'], color: '#06b6d4' },
  theater: { name: 'Theater', x: 550, y: 475, capacity: 120, activities: ['presenting', 'watching'], color: '#e11d48' },
  gym: { name: 'Gym', x: 400, y: 725, capacity: 200, activities: ['training', 'improving'], color: '#84cc16' },
  daycare: { name: 'Paul Daycare', x: 950, y: 400, capacity: 100, activities: ['breeding', 'nurturing'], color: '#f472b6' }
};

class Paul {
  constructor(id, isReal = true) {
    this.id = id;
    this.isReal = isReal;
    this.type = PAUL_TYPES[Math.floor(Math.random() * PAUL_TYPES.length)];
    
    if (isReal) {
      this.name = this.generateName();
      this.profession = PROFESSIONS[Math.floor(Math.random() * PROFESSIONS.length)];
      this.initials = this.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
    } else {
      this.name = `Paul #${id}`;
      this.initials = 'P' + (id % 10);
    }
    
    // Position
    this.x = Math.random() * 800;
    this.y = Math.random() * 800;
    this.targetX = this.x;
    this.targetY = this.y;
    this.speed = 0.5 + Math.random() * 1.5;
    
    // State
    this.currentBuilding = null;
    this.activity = 'idle';
    this.thought = '';
    
    // Needs (0-100)
    this.needs = {
      energy: 50 + Math.random() * 50,
      knowledge: 30 + Math.random() * 70,
      social: 30 + Math.random() * 70,
      money: 20 + Math.random() * 80
    };
    
    // Stats
    this.stats = {
      trades: Math.floor(Math.random() * 100),
      wins: Math.floor(Math.random() * 60),
      roi: (Math.random() * 200 - 50).toFixed(1),
      level: Math.floor(Math.random() * 20) + 1
    };
    
    // Breeding system
    this.canBreed = isReal && Math.random() > 0.3; // 70% of real Pauls can breed
    this.children = [];
    this.parents = [];
    this.breedCooldown = 0;
    this.lookingForMate = false;
    
    // Timers
    this.lastDecision = 0;
    this.decisionInterval = 3000 + Math.random() * 5000;
    this.thoughtTimer = 0;
  }
  
  generateName() {
    const firstNames = ['Visionary', 'Trader', 'Quant', 'Whale', 'Degen', 'Skeptic', 'Professor', 'Contrarian', 'Analyst', 'Strategist'];
    const lastNames = ['Paul', 'Alpha', 'Sigma', 'Chad', 'Doomer', 'Bloomer', 'Bear', 'Bull', 'Ape', 'Diamond'];
    return `${firstNames[Math.floor(Math.random() * firstNames.length)]} ${lastNames[Math.floor(Math.random() * lastNames.length)]}`;
  }
  
  update(deltaTime, gameTime) {
    // Decay needs
    this.needs.energy -= 0.01;
    this.needs.knowledge -= 0.005;
    this.needs.social -= 0.008;
    this.needs.money -= 0.002;
    
    // Clamp needs
    Object.keys(this.needs).forEach(key => {
      this.needs[key] = Math.max(0, Math.min(100, this.needs[key]));
    });
    
    // Make decisions
    this.lastDecision += deltaTime;
    if (this.lastDecision > this.decisionInterval) {
      this.makeDecision(gameTime);
      this.lastDecision = 0;
    }
    
    // Move towards target
    const dx = this.targetX - this.x;
    const dy = this.targetY - this.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    if (distance > 5) {
      this.x += (dx / distance) * this.speed;
      this.y += (dy / distance) * this.speed;
    } else {
      this.activity = this.currentBuilding ? 
        BUILDINGS[this.currentBuilding].activities[Math.floor(Math.random() * BUILDINGS[this.currentBuilding].activities.length)] :
        'idle';
    }
    
    // Generate thoughts
    this.thoughtTimer += deltaTime;
    if (this.thoughtTimer > 10000 && this.isReal) {
      this.generateThought();
      this.thoughtTimer = 0;
    }
  }
  
  makeDecision(gameTime) {
    const hour = gameTime.hour;
    
    // Sleep at night
    if (hour >= 22 || hour < 6) {
      if (this.needs.energy < 80) {
        this.moveTo('home');
        return;
      }
    }
    
    // Find need with lowest value
    const lowestNeed = Object.entries(this.needs).sort((a, b) => a[1] - b[1])[0];
    
    switch (lowestNeed[0]) {
      case 'energy':
        this.moveTo('home');
        break;
      case 'knowledge':
        this.moveTo(Math.random() > 0.5 ? 'research' : 'oracle');
        break;
      case 'social':
        this.moveTo(Math.random() > 0.5 ? 'social' : 'cafe');
        break;
      case 'money':
        this.moveTo(Math.random() > 0.5 ? 'market' : 'dex');
        break;
    }
  }
  
  moveTo(buildingId) {
    const building = BUILDINGS[buildingId];
    if (!building) return;
    
    this.currentBuilding = buildingId;
    this.targetX = building.x + (Math.random() - 0.5) * building.capacity * 0.5;
    this.targetY = building.y + (Math.random() - 0.5) * building.capacity * 0.5;
  }
  
  generateThought() {
    const thoughts = [
      'BTC looking bullish...',
      'Need to research this token',
      'Market feels overheated',
      'Time to take profits',
      'Should I ape into this?',
      'Waiting for the dip',
      'Diamond hands only',
      'Paper hands everywhere',
      'The trend is your friend',
      'Buy the rumor, sell the news'
    ];
    this.thought = thoughts[Math.floor(Math.random() * thoughts.length)];
  }
  
  toJSON() {
    return {
      id: this.id,
      isReal: this.isReal,
      name: this.name,
      initials: this.initials,
      type: this.type,
      x: Math.round(this.x * 10) / 10,
      y: Math.round(this.y * 10) / 10,
      building: this.currentBuilding,
      activity: this.activity,
      thought: this.thought,
      needs: this.needs,
      stats: this.isReal ? this.stats : undefined
    };
  }
}

class Simulation {
  constructor() {
    this.pauls = [];
    this.realPauls = [];
    this.fillerPauls = [];
    this.gameTime = { hour: 9, minute: 0, day: 1 };
    this.lastUpdate = Date.now();
    this.tickRate = 100; // 10 updates per second
    this.isRunning = false;
    
    this.initPauls();
  }
  
  initPauls() {
    // Create 1000 real Pauls
    for (let i = 0; i < 1000; i++) {
      const paul = new Paul(i, true);
      this.realPauls.push(paul);
      this.pauls.push(paul);
    }
    
    // Create 3000 filler Pauls
    for (let i = 1000; i < 4000; i++) {
      const paul = new Paul(i, false);
      paul.type = PAUL_TYPES[Math.floor(Math.random() * PAUL_TYPES.length)];
      this.fillerPauls.push(paul);
      this.pauls.push(paul);
    }
    
    console.log(`Created ${this.realPauls.length} real Pauls and ${this.fillerPauls.length} filler Pauls`);
  }
  
  start() {
    this.isRunning = true;
    this.tick();
  }
  
  stop() {
    this.isRunning = false;
  }
  
  tick() {
    if (!this.isRunning) return;
    
    const now = Date.now();
    const deltaTime = now - this.lastUpdate;
    this.lastUpdate = now;
    
    // Update game time (10x faster than real)
    this.gameTime.minute += deltaTime / 100;
    if (this.gameTime.minute >= 60) {
      this.gameTime.minute = 0;
      this.gameTime.hour++;
      if (this.gameTime.hour >= 24) {
        this.gameTime.hour = 0;
        this.gameTime.day++;
      }
    }
    
    // Update all Pauls
    // Only update real Pauls every tick, fillers every 5th tick
    this.realPauls.forEach(paul => {
      paul.update(deltaTime, this.gameTime);
      // Handle breeding for eligible Pauls at daycare
      if (paul.canBreed && paul.currentBuilding === 'daycare') {
        this.handleBreeding(paul, deltaTime);
      }
    });
    
    if (Math.floor(now / 100) % 5 === 0) {
      this.fillerPauls.forEach(paul => paul.update(deltaTime, this.gameTime));
    }
    
    setTimeout(() => this.tick(), this.tickRate);
  }
  
  handleBreeding(paul, deltaTime) {
    // Decrease cooldown
    if (paul.breedCooldown > 0) {
      paul.breedCooldown -= deltaTime;
      return;
    }
    
    if (!paul.lookingForMate) {
      // 10% chance per tick to start looking
      if (Math.random() < 0.1) {
        paul.lookingForMate = true;
        paul.thought = "Looking for a trading partner... 💕";
      }
      return;
    }
    
    // Find potential mate at daycare
    const potentialMates = this.realPauls.filter(p => 
      p.id !== paul.id && 
      p.currentBuilding === 'daycare' && 
      p.canBreed && 
      p.breedCooldown <= 0 &&
      p.lookingForMate
    );
    
    if (potentialMates.length > 0) {
      const mate = potentialMates[Math.floor(Math.random() * potentialMates.length)];
      this.breedPauls(paul, mate);
    }
  }
  
  breedPauls(parent1, parent2) {
    // Create child with combined traits
    const childId = this.pauls.length;
    const child = new Paul(childId, true);
    
    // Inherit traits
    child.parents = [parent1.id, parent2.id];
    parent1.children.push(childId);
    parent2.children.push(childId);
    
    // Type inheritance (50/50 or mutation)
    if (Math.random() < 0.1) {
      child.type = PAUL_TYPES[Math.floor(Math.random() * PAUL_TYPES.length)];
    } else {
      child.type = Math.random() < 0.5 ? parent1.type : parent2.type;
    }
    
    // Stats inheritance
    const avgRoi = (parseFloat(parent1.stats.roi) + parseFloat(parent2.stats.roi)) / 2;
    child.stats.roi = (avgRoi + (Math.random() * 20 - 10)).toFixed(1);
    child.stats.level = 1;
    
    // Name combining parents
    const p1First = parent1.name.split(' ')[0];
    const p2Last = parent2.name.split(' ').pop();
    child.name = `${p1First} Jr ${p2Last}`;
    child.initials = child.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
    
    // Happy baby!
    child.needs.social = 100;
    child.needs.energy = 80;
    child.thought = "Born to trade! 🍼";
    child.activity = 'being born';
    
    // Add to simulation
    this.realPauls.push(child);
    this.pauls.push(child);
    
    // Parent cooldown (2 game hours)
    parent1.breedCooldown = 720000; // 2 game hours in ms
    parent2.breedCooldown = 720000;
    parent1.lookingForMate = false;
    parent2.lookingForMate = false;
    parent1.thought = "Just had a baby Paul! 🎉";
    parent2.thought = "Our child will be a great trader! 📈";
    parent1.activity = 'celebrating';
    parent2.activity = 'celebrating';
    
    console.log(`🍼 NEW PAUL BORN: ${child.name} (${child.type.name}) - Parents: ${parent1.name} & ${parent2.name}`);
  }
  
  getWorldState() {
    return {
      time: this.gameTime,
      paulCount: this.pauls.length,
      realPaulCount: this.realPauls.length,
      buildings: BUILDINGS,
      // Only send visible Pauls (optimization)
      pauls: this.pauls.map(p => p.toJSON())
    };
  }
  
  getPaulById(id) {
    return this.pauls.find(p => p.id === id);
  }
  
  getPaulsInBuilding(buildingId) {
    return this.pauls.filter(p => p.currentBuilding === buildingId);
  }
  
  triggerEvent(eventType, data) {
    // Handle world events
    switch (eventType) {
      case 'market_crash':
        // All Pauls rush to market or home
        this.pauls.forEach(paul => {
          if (paul.type.bias === 'bearish') {
            paul.moveTo('market');
          } else {
            paul.moveTo('home');
          }
        });
        break;
      case 'bull_run':
        // Everyone to DEX
        this.pauls.forEach(paul => paul.moveTo('dex'));
        break;
    }
  }
}

module.exports = { Simulation, Paul, BUILDINGS };
