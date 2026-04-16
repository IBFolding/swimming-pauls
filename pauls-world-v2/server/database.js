const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const DB_PATH = path.join(__dirname, 'pauls_world.db');

let db = null;

function initDatabase() {
  return new Promise((resolve, reject) => {
    db = new sqlite3.Database(DB_PATH, (err) => {
      if (err) {
        console.error('Error opening database:', err);
        reject(err);
        return;
      }
      console.log('Connected to SQLite database');
      createTables().then(resolve).catch(reject);
    });
  });
}

function createTables() {
  return new Promise((resolve, reject) => {
    db.serialize(() => {
      // Buildings table
      db.run(`
        CREATE TABLE IF NOT EXISTS buildings (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          type TEXT NOT NULL,
          x REAL NOT NULL,
          y REAL NOT NULL,
          width REAL NOT NULL,
          height REAL NOT NULL,
          capacity INTEGER NOT NULL,
          description TEXT,
          activities TEXT,
          openHour INTEGER DEFAULT 0,
          closeHour INTEGER DEFAULT 24
        )
      `);

      // Pauls table - for the 1000 real Pauls
      db.run(`
        CREATE TABLE IF NOT EXISTS pauls (
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL,
          codename TEXT NOT NULL,
          profession TEXT,
          tradingStyle TEXT,
          riskProfile TEXT,
          specialties TEXT,
          catchphrase TEXT,
          personalityTraits TEXT,
          biases TEXT,
          isReal BOOLEAN DEFAULT 1,
          createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);

      // Paul states - current simulation state
      db.run(`
        CREATE TABLE IF NOT EXISTS paul_states (
          paulId INTEGER PRIMARY KEY,
          x REAL NOT NULL,
          y REAL NOT NULL,
          buildingId TEXT,
          energy INTEGER DEFAULT 50,
          knowledge INTEGER DEFAULT 50,
          social INTEGER DEFAULT 50,
          money INTEGER DEFAULT 50,
          currentActivity TEXT,
          activityStartTime INTEGER,
          lastUpdate INTEGER,
          FOREIGN KEY (paulId) REFERENCES pauls(id)
        )
      `);

      // Activity history
      db.run(`
        CREATE TABLE IF NOT EXISTS activity_history (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          paulId INTEGER NOT NULL,
          activity TEXT NOT NULL,
          buildingId TEXT NOT NULL,
          startTime INTEGER NOT NULL,
          endTime INTEGER,
          energyDelta INTEGER DEFAULT 0,
          knowledgeDelta INTEGER DEFAULT 0,
          socialDelta INTEGER DEFAULT 0,
          moneyDelta INTEGER DEFAULT 0,
          FOREIGN KEY (paulId) REFERENCES pauls(id)
        )
      `);

      // Filler Pauls - 3000 simplified Pauls for visuals
      db.run(`
        CREATE TABLE IF NOT EXISTS filler_pauls (
          id INTEGER PRIMARY KEY,
          x REAL NOT NULL,
          y REAL NOT NULL,
          buildingId TEXT,
          color TEXT,
          size REAL DEFAULT 1,
          lastUpdate INTEGER
        )
      `);

      // Simulation state
      db.run(`
        CREATE TABLE IF NOT EXISTS simulation_state (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        )
      `, (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  });
}

// Building operations
function getBuildings() {
  return new Promise((resolve, reject) => {
    db.all('SELECT * FROM buildings', (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

function initBuildings(buildings) {
  return new Promise((resolve, reject) => {
    const stmt = db.prepare(`
      INSERT OR REPLACE INTO buildings 
      (id, name, type, x, y, width, height, capacity, description, activities, openHour, closeHour)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    
    db.serialize(() => {
      buildings.forEach(b => {
        stmt.run(b.id, b.name, b.type, b.x, b.y, b.width, b.height, 
                 b.capacity, b.description, JSON.stringify(b.activities), 
                 b.openHour || 0, b.closeHour || 24);
      });
      stmt.finalize((err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  });
}

// Paul operations
function savePaul(paul) {
  return new Promise((resolve, reject) => {
    db.run(`
      INSERT OR REPLACE INTO pauls 
      (id, name, codename, profession, tradingStyle, riskProfile, specialties, catchphrase, personalityTraits, biases, isReal)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [paul.id, paul.name, paul.codename, paul.profession, paul.tradingStyle, 
        paul.riskProfile, JSON.stringify(paul.specialties), paul.catchphrase,
        JSON.stringify(paul.personalityTraits), JSON.stringify(paul.biases), 1],
    function(err) {
      if (err) reject(err);
      else resolve(this.lastID);
    });
  });
}

function savePaulsBatch(pauls) {
  return new Promise((resolve, reject) => {
    const stmt = db.prepare(`
      INSERT OR REPLACE INTO pauls 
      (id, name, codename, profession, tradingStyle, riskProfile, specialties, catchphrase, personalityTraits, biases, isReal)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    
    db.serialize(() => {
      pauls.forEach(paul => {
        stmt.run(paul.id, paul.name, paul.codename, paul.profession, paul.tradingStyle, 
                 paul.riskProfile, JSON.stringify(paul.specialties), paul.catchphrase,
                 JSON.stringify(paul.personalityTraits), JSON.stringify(paul.biases), 1);
      });
      stmt.finalize((err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  });
}

function getPauls(limit = 1000, offset = 0) {
  return new Promise((resolve, reject) => {
    db.all('SELECT * FROM pauls WHERE isReal = 1 LIMIT ? OFFSET ?', [limit, offset], (err, rows) => {
      if (err) reject(err);
      else {
        rows.forEach(row => {
          row.specialties = JSON.parse(row.specialties || '[]');
          row.personalityTraits = JSON.parse(row.personalityTraits || '[]');
          row.biases = JSON.parse(row.biases || '{}');
        });
        resolve(rows);
      }
    });
  });
}

function getPaulCount() {
  return new Promise((resolve, reject) => {
    db.get('SELECT COUNT(*) as count FROM pauls WHERE isReal = 1', (err, row) => {
      if (err) reject(err);
      else resolve(row.count);
    });
  });
}

// Paul state operations
function savePaulState(paulId, state) {
  return new Promise((resolve, reject) => {
    db.run(`
      INSERT OR REPLACE INTO paul_states 
      (paulId, x, y, buildingId, energy, knowledge, social, money, currentActivity, activityStartTime, lastUpdate)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [paulId, state.x, state.y, state.buildingId, state.energy, state.knowledge, 
        state.social, state.money, state.currentActivity, state.activityStartTime, Date.now()],
    (err) => {
      if (err) reject(err);
      else resolve();
    });
  });
}

function savePaulStatesBatch(states) {
  return new Promise((resolve, reject) => {
    const stmt = db.prepare(`
      INSERT OR REPLACE INTO paul_states 
      (paulId, x, y, buildingId, energy, knowledge, social, money, currentActivity, activityStartTime, lastUpdate)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    
    db.serialize(() => {
      states.forEach(s => {
        stmt.run(s.paulId, s.x, s.y, s.buildingId, s.energy, s.knowledge, 
                 s.social, s.money, s.currentActivity, s.activityStartTime, Date.now());
      });
      stmt.finalize((err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  });
}

function getPaulStates() {
  return new Promise((resolve, reject) => {
    db.all('SELECT * FROM paul_states', (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

// Activity history
function logActivity(paulId, activity, buildingId, startTime) {
  return new Promise((resolve, reject) => {
    db.run(`
      INSERT INTO activity_history (paulId, activity, buildingId, startTime)
      VALUES (?, ?, ?, ?)
    `, [paulId, activity, buildingId, startTime], function(err) {
      if (err) reject(err);
      else resolve(this.lastID);
    });
  });
}

function endActivity(activityId, endTime, deltas) {
  return new Promise((resolve, reject) => {
    db.run(`
      UPDATE activity_history 
      SET endTime = ?, energyDelta = ?, knowledgeDelta = ?, socialDelta = ?, moneyDelta = ?
      WHERE id = ?
    `, [endTime, deltas.energy, deltas.knowledge, deltas.social, deltas.money, activityId],
    (err) => {
      if (err) reject(err);
      else resolve();
    });
  });
}

// Filler Pauls
function saveFillerPaulsBatch(pauls) {
  return new Promise((resolve, reject) => {
    const stmt = db.prepare(`
      INSERT OR REPLACE INTO filler_pauls (id, x, y, buildingId, color, size, lastUpdate)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `);
    
    db.serialize(() => {
      pauls.forEach(p => {
        stmt.run(p.id, p.x, p.y, p.buildingId, p.color, p.size, Date.now());
      });
      stmt.finalize((err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  });
}

function getFillerPauls() {
  return new Promise((resolve, reject) => {
    db.all('SELECT * FROM filler_pauls', (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

function updateFillerPaulState(id, state) {
  return new Promise((resolve, reject) => {
    db.run(`
      UPDATE filler_pauls SET x = ?, y = ?, buildingId = ?, lastUpdate = ? WHERE id = ?
    `, [state.x, state.y, state.buildingId, Date.now(), id], (err) => {
      if (err) reject(err);
      else resolve();
    });
  });
}

// Simulation state
function setSimulationState(key, value) {
  return new Promise((resolve, reject) => {
    db.run('INSERT OR REPLACE INTO simulation_state (key, value) VALUES (?, ?)', 
           [key, JSON.stringify(value)], (err) => {
      if (err) reject(err);
      else resolve();
    });
  });
}

function getSimulationState(key) {
  return new Promise((resolve, reject) => {
    db.get('SELECT value FROM simulation_state WHERE key = ?', [key], (err, row) => {
      if (err) reject(err);
      else resolve(row ? JSON.parse(row.value) : null);
    });
  });
}

function closeDatabase() {
  return new Promise((resolve, reject) => {
    if (db) {
      db.close((err) => {
        if (err) reject(err);
        else {
          console.log('Database connection closed');
          resolve();
        }
      });
    } else {
      resolve();
    }
  });
}

module.exports = {
  initDatabase,
  closeDatabase,
  getBuildings,
  initBuildings,
  savePaul,
  savePaulsBatch,
  getPauls,
  getPaulCount,
  savePaulState,
  savePaulStatesBatch,
  getPaulStates,
  logActivity,
  endActivity,
  saveFillerPaulsBatch,
  getFillerPauls,
  updateFillerPaulState,
  setSimulationState,
  getSimulationState
};
