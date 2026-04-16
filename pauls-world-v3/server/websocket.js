const WebSocket = require('ws');

class WebSocketManager {
  constructor(server) {
    this.wss = new WebSocket.Server({ server });
    this.clients = new Set();
    this.setupHandlers();
  }

  setupHandlers() {
    this.wss.on('connection', (ws) => {
      console.log('New WebSocket client connected');
      this.clients.add(ws);

      // Send initial world state
      ws.send(JSON.stringify({
        type: 'connected',
        message: 'Welcome to Paul\'s World'
      }));

      ws.on('message', (data) => {
        try {
          const message = JSON.parse(data);
          this.handleMessage(ws, message);
        } catch (err) {
          console.error('Invalid WebSocket message:', err);
        }
      });

      ws.on('close', () => {
        console.log('WebSocket client disconnected');
        this.clients.delete(ws);
      });

      ws.on('error', (err) => {
        console.error('WebSocket error:', err);
        this.clients.delete(ws);
      });
    });
  }

  handleMessage(ws, message) {
    switch (message.type) {
      case 'ping':
        ws.send(JSON.stringify({ type: 'pong' }));
        break;
      case 'selectPaul':
        // Client selected a Paul to inspect
        ws.selectedPaulId = message.paulId;
        break;
      case 'selectBuilding':
        // Client selected a building
        ws.selectedBuildingId = message.buildingId;
        break;
      default:
        console.log('Unknown message type:', message.type);
    }
  }

  // Broadcast world state to all clients
  broadcastWorldState(worldState) {
    const message = JSON.stringify({
      type: 'worldUpdate',
      timestamp: Date.now(),
      data: worldState
    });

    this.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    });
  }

  // Broadcast specific event
  broadcastEvent(eventType, data) {
    const message = JSON.stringify({
      type: 'event',
      eventType,
      timestamp: Date.now(),
      data
    });

    this.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    });
  }

  // Send specific Paul update to interested clients
  broadcastPaulUpdate(paul) {
    const message = JSON.stringify({
      type: 'paulUpdate',
      paul
    });

    this.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        // Send to everyone or just those who selected this Paul
        if (!client.selectedPaulId || client.selectedPaulId === paul.id) {
          client.send(message);
        }
      }
    });
  }

  getClientCount() {
    return this.clients.size;
  }
}

module.exports = WebSocketManager;
