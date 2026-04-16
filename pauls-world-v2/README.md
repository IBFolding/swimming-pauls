# Paul's World V2 - Advanced Simulation

## Architecture

### Backend (Node.js)
- Express API server
- WebSocket for real-time updates
- SQLite database (local) / PostgreSQL (production)
- Paul AI simulation engine

### Frontend (HTML5 Canvas)
- 2D isometric world view
- Real-time Paul rendering
- Interactive building clicks
- Overlay panels (time, needs, selected Paul)

### Simulation Engine
- 1,000 real Pauls with full AI
- 3,000 visual filler Pauls
- Needs system: Energy, Knowledge, Social, Money
- Activity system: Work, Rest, Socialize, Trade
- Event system: Market crashes, FOMO waves

## File Structure
```
pauls-world-v2/
├── server/
│   ├── index.js              # Main server
│   ├── simulation.js         # Paul AI engine
│   ├── websocket.js          # WebSocket handler
│   └── database.js           # DB connection
├── public/
│   ├── index.html            # Main page
│   ├── world.js              # Canvas renderer
│   ├── pauls.js              # Paul client logic
│   └── styles.css            # Styling
├── package.json
└── README.md
```

## Features
- [x] 1,000 real Pauls with AI
- [x] 3,000 visual filler Pauls
- [x] 14 building locations
- [x] Day/night cycle
- [x] Real-time WebSocket updates
- [x] Interactive overlays
- [x] Paul selection & inspection
- [x] Activity logging

## Local Development
```bash
npm install
npm run dev
```

## Production Deploy
```bash
npm run build
# Deploy to droplet
```
