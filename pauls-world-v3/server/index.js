const express = require('express');
const cors = require('cors');
const path = require('path');
const http = require('http');

const { initDatabase } = require('./database');
const { Simulation } = require('./simulation');
const WebSocketManager = require('./websocket');

const app = express();
const server = http.createServer(app);
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));

// Initialize simulation
const simulation = new Simulation();

// Initialize WebSocket
const wsManager = new WebSocketManager(server);

// API Routes

// Get world state
app.get('/api/world', (req, res) => {
  res.json(simulation.getWorldState());
});

// Get all buildings
app.get('/api/buildings', (req, res) => {
  const { BUILDINGS } = require('./simulation');
  res.json(BUILDINGS);
});

// Get Pauls in a specific building
app.get('/api/buildings/:id/pauls', (req, res) => {
  const pauls = simulation.getPaulsInBuilding(req.params.id);
  res.json(pauls.map(p => p.toJSON()));
});

// Get specific Paul
app.get('/api/pauls/:id', (req, res) => {
  const paul = simulation.getPaulById(parseInt(req.params.id));
  if (paul) {
    res.json(paul.toJSON());
  } else {
    res.status(404).json({ error: 'Paul not found' });
  }
});

// Get top Pauls by ROI
app.get('/api/leaderboard', (req, res) => {
  const topPauls = simulation.realPauls
    .sort((a, b) => parseFloat(b.stats.roi) - parseFloat(a.stats.roi))
    .slice(0, 50)
    .map(p => p.toJSON());
  res.json(topPauls);
});

// Get world stats
app.get('/api/stats', (req, res) => {
  const stats = {
    totalPauls: simulation.pauls.length,
    realPauls: simulation.realPauls.length,
    fillerPauls: simulation.fillerPauls.length,
    avgEnergy: simulation.realPauls.reduce((sum, p) => sum + p.needs.energy, 0) / simulation.realPauls.length,
    avgKnowledge: simulation.realPauls.reduce((sum, p) => sum + p.needs.knowledge, 0) / simulation.realPauls.length,
    avgSocial: simulation.realPauls.reduce((sum, p) => sum + p.needs.social, 0) / simulation.realPauls.length,
    avgMoney: simulation.realPauls.reduce((sum, p) => sum + p.needs.money, 0) / simulation.realPauls.length,
    gameTime: simulation.gameTime,
    connectedClients: wsManager.getClientCount()
  };
  res.json(stats);
});

// Trigger world event (admin endpoint)
app.post('/api/events', (req, res) => {
  const { type, data } = req.body;
  simulation.triggerEvent(type, data);
  wsManager.broadcastEvent(type, data);
  res.json({ success: true, message: `Event ${type} triggered` });
});

// Ask a question to the Pauls
app.post('/api/ask', (req, res) => {
  const { question, numPauls = 100 } = req.body;
  
  if (!question) {
    return res.status(400).json({ error: 'Question required' });
  }
  
  const result = simulation.askQuestion(question, numPauls);
  
  // Broadcast to all clients that a question was asked
  wsManager.broadcastEvent('question_asked', {
    question,
    consensus: result.consensus.majority,
    responses: result.totalResponses
  });
  
  res.json(result);
});

// Get recent predictions/history
app.get('/api/predictions', (req, res) => {
  // Return recent question history from simulation
  res.json({
    recent: simulation.predictionHistory || [],
    totalQuestions: simulation.totalQuestionsAsked || 0
  });
});

// Main page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/index.html'));
});

// Start server
async function start() {
  try {
    // Initialize database
    await initDatabase();
    console.log('Database initialized');
    
    // Start simulation
    simulation.start();
    console.log('Simulation started');
    
    // Broadcast world state every 100ms (10 times per second)
    setInterval(() => {
      const worldState = simulation.getWorldState();
      wsManager.broadcastWorldState(worldState);
    }, 100);
    
    server.listen(PORT, () => {
      console.log(`Paul's World V2 server running on port ${PORT}`);
      console.log(`WebSocket server ready for connections`);
      console.log(`Simulating ${simulation.pauls.length} Pauls (${simulation.realPauls.length} real, ${simulation.fillerPauls.length} filler)`);
    });
  } catch (err) {
    console.error('Failed to start server:', err);
    process.exit(1);
  }
}

start();
