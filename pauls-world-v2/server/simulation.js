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
    
    // Generate reasoning
    const reasonings = [
      `Based on my ${paul.type.specialty} analysis, the chart shows...`,
      `My ${paul.expertise?.[0] || 'technical'} expertise indicates...`,
      `From a ${paul.type.name} perspective, market structure suggests...`,
      `Analyzing ${paul.expertise?.[1] || 'price action'} patterns...`,
      `My ${paul.profession} experience tells me...`,
      `Looking at ${paul.type.specialty} indicators...`,
      `The ${paul.expertise?.[0] || 'market'} data reveals...`,
      `As a ${paul.type.name}, I see ${paul.type.specialty} signals...`
    ];
    
    return {
      answer,
      confidence: Math.round(confidence * 100) / 100,
      reasoning: reasonings[Math.floor(Math.random() * reasonings.length)]
    };
  }
  
  getAnswerTemplates(category, bias) {
    const templates = {
      will: {
        bullish: ['Yes, strong uptrend', 'Highly likely to pump', 'Bullish confirmation', 'Breakout incoming'],
        bearish: ['No, rejection at resistance', 'Likely to dump', 'Bearish divergence', 'Correction coming'],
        neutral: ['Uncertain, wait for confirmation', 'Sideways likely', 'Consolidation phase', 'Need more data'],
        aggressive: ['Absolutely, YOLO', 'All in, send it', 'FOMO is real', 'Parabolic move'],
        diamond_hands: ['Yes, hold long term', 'Accumulate on dips', 'Fundamentals strong', 'Ignore the noise']
      },
      should: {
        bullish: ['Buy the dip', 'Long position recommended', 'Add to position', 'Strong buy signal'],
        bearish: ['Sell now', 'Take profits', 'Short opportunity', 'Reduce exposure'],
        neutral: ['Hold current position', 'Wait for clarity', 'Small position only', 'Hedge your bets'],
        aggressive: ['APE IN', 'Leverage up', 'YOLO trade', 'All or nothing'],
        diamond_hands: ['HODL', 'Never sell', 'Diamond hands only', 'Generational wealth']
      },
      price: {
        bullish: ['Target: +20%', 'New ATH incoming', 'Price discovery mode', 'Moon mission'],
        bearish: ['Support at -15%', 'Expect pullback', 'Lower lows ahead', 'Bear market'],
        neutral: ['Range bound', 'Consolidation', 'Wait for breakout', 'No clear direction'],
        aggressive: ['10x potential', 'Parabolic pump', 'To the moon', 'WAGMI'],
        diamond_hands: ['$100K BTC', 'Long term value', 'Price doesnt matter', 'Stack sats')
      },
      buy: {
        bullish: ['Buy now', 'Perfect entry', 'Accumulate here', 'Strong support'],
        bearish: ['Wait for lower', 'Dont catch knife', 'Better prices coming', 'Patience'],
        neutral: ['Dollar cost average', 'Small position', 'Split orders', 'Limit order'],
        aggressive: ['Market buy', 'All in', 'Send it', 'YOLO'],
        diamond_hands: ['Buy and hold', 'Stack forever', 'Generational buy', 'Never sell')
      },
      sell: {
        bullish: ['Take partial profits', 'Trim position', 'Sell high', 'Secure gains'],
        bearish: ['Sell everything', 'Exit now', 'Cut losses', 'Get out'],
        neutral: ['Sell half', 'Reduce size', 'Take some profit', 'Rebalance'],
        aggressive: ['Dump it all', 'Panic sell', 'Rug pull', 'Exit liquidity'],
        diamond_hands: ['Never sell', 'HODL through dip', 'Diamond hands', 'Buy more instead')
      },
      what: {
        bullish: ['Bullish setup', 'Accumulation zone', 'Institutional buying', 'Whale activity'],
        bearish: ['Distribution phase', 'Smart money selling', 'Liquidity grab', 'Trap setup'],
        neutral: ['Chop zone', 'No mans land', 'Wait and see', 'Sideways action'],
        aggressive: ['Degenerate play', 'Casino mode', 'High risk/high reward', 'Apes together'],
        diamond_hands: ['Quality asset', 'Long term hold', 'Fundamental value', 'Ignore volatility')
      },
      why: {
        bullish: ['Strong fundamentals', 'Institutional adoption', 'Network growth', 'Supply squeeze'],
        bearish: ['Weak volume', 'Bearish structure', 'Macro headwinds', 'Regulation fears'],
        neutral: ['Mixed signals', 'Conflicting data', 'Market indecision', 'Consolidation needed'],
        aggressive: ['Hype cycle', 'Narrative trade', 'Meme momentum', 'FOMO driven'],
        diamond_hands: ['Long term thesis', 'Technology adoption', 'Store of value', 'Scarcity model')
      },
      how: {
        bullish: ['Buy breakout', 'Add on dips', 'Scale in gradually', 'Set stop losses'],
        bearish: ['Short the rally', 'Wait for lower high', 'Reduce size', 'Raise cash'],
        neutral: ['Range trade', 'Wait for direction', 'Small size', 'Tight stops'],
        aggressive: ['Leverage long', 'All in spot', 'Options YOLO', 'Cross margin'],
        diamond_hands: ['DCA weekly', 'Cold storage', 'Forget price', 'Check back in 5 years')
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
