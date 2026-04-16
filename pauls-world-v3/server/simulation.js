// Paul AI Simulation Engine
// Multi-agent prediction engine for ANY question

const PAUL_TYPES = [
  { name: 'Visionary', emoji: '🎯', color: '#8b5cf6', specialty: 'trends', bias: 'bullish' },
  { name: 'DayTrader', emoji: '📈', color: '#22c55e', specialty: 'intraday', bias: 'aggressive' },
  { name: 'SwingTrader', emoji: '📊', color: '#3b82f6', specialty: 'swings', bias: 'neutral' },
  { name: 'Quant', emoji: '🧮', color: '#10b981', specialty: 'algorithms', bias: 'systematic' },
  { name: 'Whale', emoji: '🐋', color: '#f59e0b', specialty: 'institutional', bias: 'smart_money' },
  { name: 'Degen', emoji: '🎰', color: '#ec4899', specialty: 'memes', bias: 'yolo' },
  { name: 'Skeptic', emoji: '🤨', color: '#6b7280', specialty: 'risk', bias: 'bearish' },
  { name: 'Value', emoji: '💎', color: '#06b6d4', specialty: 'fundamentals', bias: 'diamond_hands' },
  { name: 'Momentum', emoji: '🚀', color: '#f97316', specialty: 'breakouts', bias: 'fomo' },
  { name: 'Contrarian', emoji: '↔️', color: '#e11d48', specialty: 'reversals', bias: 'against_crowd' }
];

const TRADING_EXPERTISE = [
  'Crypto', 'Stocks', 'Forex', 'Options', 'Futures', 'DeFi', 'NFTs', 'MemeCoins',
  'Technical Analysis', 'Fundamental Analysis', 'Sentiment Analysis', 'On-Chain Analysis',
  'Macro Economics', 'Market Microstructure', 'Risk Management', 'Portfolio Theory',
  'Arbitrage', 'Market Making', 'High Frequency', 'Algorithmic Trading'
];

const PROFESSIONS = [
  'Day Trader', 'Swing Trader', 'Quant Analyst', 'Researcher', 'Portfolio Manager',
  'Risk Analyst', 'Crypto Specialist', 'Meme Coin Expert', 'DeFi Researcher',
  'NFT Flipper', 'Options Trader', 'Macro Analyst', 'Technical Analyst',
  'Fundamental Analyst', 'Sentiment Analyst'
];

const QUESTION_CATEGORIES = {
  will: { building: 'oracle', activity: 'predicting', confidence: 0.7 },
  should: { building: 'townhall', activity: 'debating', confidence: 0.6 },
  what: { building: 'research', activity: 'analyzing', confidence: 0.8 },
  why: { building: 'philosophy', activity: 'reasoning', confidence: 0.5 },
  how: { building: 'power', activity: 'problem-solving', confidence: 0.75 },
  when: { building: 'oracle', activity: 'forecasting', confidence: 0.65 },
  who: { building: 'detective', activity: 'investigating', confidence: 0.8 },
  which: { building: 'research', activity: 'comparing', confidence: 0.7 },
  price: { building: 'market', activity: 'charting', confidence: 0.85 },
  buy: { building: 'dex', activity: 'executing', confidence: 0.9 },
  sell: { building: 'dex', activity: 'exiting', confidence: 0.9 }
};

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
    
    // Expertise - 2-3 trading domains this Paul specializes in
    this.expertise = [];
    if (isReal) {
      const numExpertise = 2 + Math.floor(Math.random() * 2);
      const shuffled = [...TRADING_EXPERTISE].sort(() => 0.5 - Math.random());
      this.expertise = shuffled.slice(0, numExpertise);
    }
    
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
    // Create 1000 real Pauls (all active, no fillers)
    for (let i = 0; i < 1000; i++) {
      const paul = new Paul(i, true);
      this.realPauls.push(paul);
      this.pauls.push(paul);
    }
    
    console.log(`Created ${this.realPauls.length} Pauls (all real, active)`);
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
    
    // Update game time (5x slower than before - was /100, now /500)
    this.gameTime.minute += deltaTime / 500;
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
  
  // Ask the Pauls a question - any question!
  askQuestion(question, numPauls = 100) {
    // Parse question type
    const questionLower = question.toLowerCase();
    let category = 'what';
    
    for (const [type, config] of Object.entries(QUESTION_CATEGORIES)) {
      if (questionLower.startsWith(type)) {
        category = type;
        break;
      }
    }
    
    // Select relevant Pauls based on question keywords
    const keywords = this.extractKeywords(question);
    const relevantPauls = this.selectRelevantPauls(keywords, numPauls);
    
    // Gather predictions from each Paul
    const predictions = relevantPauls.map(paul => {
      const prediction = this.generatePrediction(paul, question, category);
      return {
        paulId: paul.id,
        paulName: paul.name,
        paulType: paul.type.name,
        prediction: prediction.answer,
        confidence: prediction.confidence,
        reasoning: prediction.reasoning,
        bias: paul.type.bias,
        specialty: paul.type.specialty
      };
    });
    
    // Calculate consensus
    const consensus = this.calculateConsensus(predictions);
    
    return {
      question,
      category,
      totalResponses: predictions.length,
      consensus,
      predictions: predictions.sort((a, b) => b.confidence - a.confidence),
      timestamp: new Date().toISOString()
    };
  }
  
  extractKeywords(question) {
    // Simple keyword extraction
    const stopWords = ['the', 'a', 'an', 'is', 'are', 'will', 'should', 'what', 'why', 'how', 'when', 'who', 'which'];
    return question.toLowerCase()
      .replace(/[^\w\s]/g, '')
      .split(' ')
      .filter(word => !stopWords.includes(word) && word.length > 2);
  }
  
  selectRelevantPauls(keywords, numPauls) {
    // Score each Paul based on keyword relevance
    const scoredPauls = this.realPauls.map(paul => {
      let score = 0;
      
      // Check if Paul's expertise matches keywords
      keywords.forEach(keyword => {
        if (paul.expertise?.some(e => e.toLowerCase().includes(keyword))) score += 3;
        if (paul.profession?.toLowerCase().includes(keyword)) score += 2;
        if (paul.type.specialty.includes(keyword)) score += 2;
      });
      
      // Random factor for diversity
      score += Math.random() * 2;
      
      return { paul, score };
    });
    
    // Sort by score and take top numPauls
    return scoredPauls
      .sort((a, b) => b.score - a.score)
      .slice(0, numPauls)
      .map(s => s.paul);
  }
  
  generatePrediction(paul, question, category) {
    const config = QUESTION_CATEGORIES[category] || QUESTION_CATEGORIES.what;
    
    // Base confidence on Paul's type and random factor
    let confidence = config.confidence + (Math.random() * 0.3 - 0.15);
    confidence = Math.max(0.1, Math.min(0.99, confidence));
    
    // Generate answer based on Paul's bias and specialty
    const answers = this.getAnswerTemplates(category, paul.type.bias);
    const answer = answers[Math.floor(Math.random() * answers.length)];
    
    // Generate reasoning - natural and varied
    const reasonings = [
      `From my perspective as a ${paul.type.name}, I think...`,
      `Based on what I've observed in ${paul.expertise?.[0] || 'the markets'}...`,
      `My experience tells me...`,
      `Looking at this as a ${paul.profession}...`,
      `The way I see it...`,
      `In my opinion...`,
      `Drawing from my background...`,
      `My analysis suggests...`,
      `I've been watching this closely and...`,
      `From where I stand...`
    ];
    
    return {
      answer,
      confidence: Math.round(confidence * 100) / 100,
      reasoning: reasonings[Math.floor(Math.random() * reasonings.length)]
    };
  }
  
  getAnswerTemplates(category, bias) {
    // Natural, varied responses - not always trader-speak
    const templates = {
      will: {
        bullish: ['I believe so', 'Looks promising', 'Trending positive', 'Signs point to yes'],
        bearish: ['Doubtful', 'Not looking good', 'I\'d be cautious', 'Signs say no'],
        neutral: ['Maybe', 'Could go either way', 'Unclear right now', 'Need more info'],
        aggressive: ['Absolutely', 'All in', '100% yes', 'No doubt'],
        diamond_hands: ['In the long run, yes', 'Patience will pay off', 'Hold strong', 'Time is on your side']
      },
      should: {
        bullish: ['Go for it', 'Seems like a good move', 'I\'d support that', 'Wise choice'],
        bearish: ['Probably not', 'I\'d reconsider', 'Risk seems high', 'Better to wait'],
        neutral: ['Up to you', 'Consider the trade-offs', 'Depends on your goals', 'Either way works'],
        aggressive: ['Do it now', 'Strike while hot', 'Seize the moment', 'Fortune favors bold'],
        diamond_hands: ['Stick to your plan', 'Trust your research', 'Conviction matters', 'Stay the course']
      },
      price: {
        bullish: ['Higher', 'Upward trend', 'Growth expected', 'Positive momentum'],
        bearish: ['Lower', 'Downward pressure', 'Expect decline', 'Negative trend'],
        neutral: ['Sideways', 'Range bound', 'Stable', 'No major change'],
        aggressive: ['To the moon', 'Parabolic', 'Explosive growth', 'Breakout imminent'],
        diamond_hands: ['Value will show', 'Price is noise', 'Focus on fundamentals', 'Long term appreciation']
      },
      buy: {
        bullish: ['Good entry', 'Solid opportunity', 'Worth considering', 'Attractive price'],
        bearish: ['Wait', 'Better entry coming', 'Not convinced', 'Hold off'],
        neutral: ['Dollar cost average', 'Small position', 'Split your order', 'Be patient'],
        aggressive: ['All in', 'Max leverage', 'YOLO', 'Send it'],
        diamond_hands: ['Accumulate', 'Stack regularly', 'Buy and hold', 'Think long term']
      },
      sell: {
        bullish: ['Take some profit', 'Trim position', 'Secure gains', 'Partial exit'],
        bearish: ['Exit now', 'Cut losses', 'Get out', 'Protect capital'],
        neutral: ['Sell half', 'Reduce size', 'Take profit', 'Rebalance'],
        aggressive: ['Dump it', 'Panic sell', 'Exit everything', 'Run for hills'],
        diamond_hands: ['Never sell', 'HODL', 'Diamond hands', 'Buy the dip instead']
      },
      what: {
        bullish: ['Opportunity', 'Growth potential', 'Positive development', 'Good news'],
        bearish: ['Risk', 'Challenge ahead', 'Warning sign', 'Concern'],
        neutral: ['Mixed signals', 'Unclear', 'Wait and see', 'More data needed'],
        aggressive: ['Game changer', 'Revolutionary', 'Once in lifetime', 'Unprecedented'],
        diamond_hands: ['Fundamental shift', 'Paradigm change', 'Long term value', 'Quality asset']
      },
      why: {
        bullish: ['Strong fundamentals', 'Growing adoption', 'Market demand', 'Innovation'],
        bearish: ['Weak sentiment', 'Macro factors', 'Technical breakdown', 'Uncertainty'],
        neutral: ['Complex factors', 'Multiple variables', 'Conflicting data', 'Early to tell'],
        aggressive: ['Hype cycle', 'Narrative driven', 'Speculation', 'FOMO'],
        diamond_hands: ['Technology maturing', 'Real world use', 'Network effects', 'Scarcity']
      },
      how: {
        bullish: ['Gradually build', 'Add on strength', 'Scale in', 'Compound gains'],
        bearish: ['Reduce exposure', 'Hedge position', 'Raise cash', 'Stay defensive'],
        neutral: ['Balanced approach', 'Diversify', 'Steady allocation', 'Consistent strategy'],
        aggressive: ['Full deployment', 'Leverage up', 'Concentrated bet', 'High conviction'],
        diamond_hands: ['Consistent buying', 'Ignore volatility', 'Focus on thesis', 'Time in market']
      }
    };
    
    return templates[category]?.[bias] || templates.what.neutral;
  }
  
  calculateConsensus(predictions) {
    // Group by answer similarity
    const groups = {};
    predictions.forEach(p => {
      const key = p.prediction.toLowerCase().replace(/[^\w]/g, '');
      if (!groups[key]) groups[key] = [];
      groups[key].push(p);
    });
    
    // Find majority
    let majority = { answer: 'No consensus', count: 0, confidence: 0 };
    Object.entries(groups).forEach(([key, group]) => {
      if (group.length > majority.count) {
        majority = {
          answer: group[0].prediction,
          count: group.length,
          confidence: group.reduce((sum, p) => sum + p.confidence, 0) / group.length
        };
      }
    });
    
    // Calculate overall sentiment
    const avgConfidence = predictions.reduce((sum, p) => sum + p.confidence, 0) / predictions.length;
    const bullishCount = predictions.filter(p => p.bias === 'optimistic' || p.bias === 'bullish').length;
    const bearishCount = predictions.filter(p => p.bias === 'pessimistic' || p.bias === 'bearish').length;
    
    let sentiment = 'neutral';
    if (bullishCount > bearishCount * 1.5) sentiment = 'optimistic';
    else if (bearishCount > bullishCount * 1.5) sentiment = 'pessimistic';
    else if (bullishCount > bearishCount) sentiment = 'slightly optimistic';
    else if (bearishCount > bullishCount) sentiment = 'slightly pessimistic';
    
    return {
      majority: majority.answer,
      agreement: Math.round((majority.count / predictions.length) * 100),
      confidence: Math.round(avgConfidence * 100) / 100,
      sentiment,
      distribution: {
        optimistic: bullishCount,
        pessimistic: bearishCount,
        neutral: predictions.length - bullishCount - bearishCount
      }
    };
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
