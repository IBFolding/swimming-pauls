// Paul's World V3 - 8-Bit Pixel Art Renderer
// SimCity-style retro aesthetic

const canvas = document.getElementById('worldCanvas');
const ctx = canvas.getContext('2d');

// Disable anti-aliasing for pixel art look
ctx.imageSmoothingEnabled = false;

// World state
let worldState = {
  pauls: [],
  buildings: {},
  time: { hour: 9, minute: 0, day: 1 }
};

let selectedPaul = null;
let hoveredPaul = null;
let hoveredBuilding = null;

// Camera
let camera = {
  x: 0,
  y: 0,
  zoom: 1,
  targetZoom: 1
};

// Mouse tracking
let mouse = { x: 0, y: 0, isDown: false, lastX: 0, lastY: 0 };

// WebSocket
let ws = null;
let reconnectAttempts = 0;
const MAX_RECONNECT = 5;

// Active side panel
let activeSidePanel = 'diary';
let currentPlatform = 'twitter';
let socialDays = 1;

// Diary filters
let diaryTimeRange = 7;
let diaryTypes = ['activity', 'thought', 'prediction', 'trade', 'dream', 'interaction'];

// Create Paul form state
let selectedColor = '#8b5cf6';
let selectedBias = 'neutral';

// 8-bit color palette
const PALETTE = {
  grass: '#2d4a3e',
  grassDark: '#1e3328',
  water: '#1e3a5f',
  road: '#3d3d3d',
  roadLine: '#f0f0f0',
  building: {
    market: '#22c55e',
    research: '#3b82f6',
    social: '#ec4899',
    cafe: '#eab308',
    dex: '#8b5cf6',
    home: '#6b7280',
    townhall: '#f59e0b',
    arcade: '#d946ef',
    garden: '#10b981',
    oracle: '#6366f1',
    power: '#f97316',
    newsroom: '#06b6d4',
    theater: '#e11d48',
    gym: '#84cc16',
    daycare: '#f472b6'
  }
};

// 8-bit Paul sprites (8x8 pixels represented as arrays)
const PAUL_SPRITES = {
  standing: [
    [0,1,1,1,1,1,1,0],
    [0,1,1,1,1,1,1,0],
    [0,0,1,1,1,1,0,0],
    [0,1,1,1,1,1,1,0],
    [1,1,0,1,1,0,1,1],
    [1,0,0,1,1,0,0,1],
    [1,0,0,0,0,0,0,1],
    [0,1,0,0,0,0,1,0]
  ],
  walking1: [
    [0,1,1,1,1,1,1,0],
    [0,1,1,1,1,1,1,0],
    [0,0,1,1,1,1,0,0],
    [0,1,1,1,1,1,1,0],
    [1,1,0,1,1,0,1,1],
    [1,0,0,1,1,0,0,0],
    [1,0,0,0,0,0,1,0],
    [0,1,0,0,0,1,0,0]
  ],
  walking2: [
    [0,1,1,1,1,1,1,0],
    [0,1,1,1,1,1,1,0],
    [0,0,1,1,1,1,0,0],
    [0,1,1,1,1,1,1,0],
    [1,1,0,1,1,0,1,1],
    [0,0,0,1,1,0,0,1],
    [0,1,0,0,0,0,0,1],
    [0,0,1,0,0,0,1,0]
  ]
};

// Building configurations (grid-based positions for 8-bit look)
const BUILDING_CONFIG = {
  market: { name: 'MARKET', x: 5, y: 3, w: 4, h: 3, color: PALETTE.building.market, emoji: '📈' },
  research: { name: 'LAB', x: 12, y: 3, w: 4, h: 3, color: PALETTE.building.research, emoji: '🔬' },
  social: { name: 'PLAZA', x: 19, y: 3, w: 4, h: 3, color: PALETTE.building.social, emoji: '💬' },
  cafe: { name: 'CAFE', x: 5, y: 8, w: 3, h: 2, color: PALETTE.building.cafe, emoji: '☕' },
  dex: { name: 'DEX', x: 12, y: 8, w: 4, h: 3, color: PALETTE.building.dex, emoji: '💱' },
  home: { name: 'HOMES', x: 19, y: 8, w: 4, h: 3, color: PALETTE.building.home, emoji: '🏠' },
  townhall: { name: 'HALL', x: 5, y: 13, w: 4, h: 3, color: PALETTE.building.townhall, emoji: '🏛️' },
  arcade: { name: 'ARCADE', x: 12, y: 13, w: 4, h: 3, color: PALETTE.building.arcade, emoji: '🎮' },
  garden: { name: 'GARDEN', x: 19, y: 13, w: 3, h: 2, color: PALETTE.building.garden, emoji: '🌱' },
  oracle: { name: 'ORACLE', x: 9, y: 5, w: 3, h: 4, color: PALETTE.building.oracle, emoji: '🔮' },
  power: { name: 'POWER', x: 16, y: 5, w: 3, h: 3, color: PALETTE.building.power, emoji: '⚡' },
  newsroom: { name: 'NEWS', x: 9, y: 10, w: 4, h: 3, color: PALETTE.building.newsroom, emoji: '📰' },
  theater: { name: 'THEATER', x: 16, y: 10, w: 3, h: 3, color: PALETTE.building.theater, emoji: '🎭' },
  gym: { name: 'GYM', x: 12, y: 16, w: 4, h: 3, color: PALETTE.building.gym, emoji: '🏋️' },
  daycare: { name: 'DAYCARE', x: 23, y: 8, w: 4, h: 3, color: PALETTE.building.daycare, emoji: '👶' }
};

// Grid settings
const TILE_SIZE = 32; // Size of each grid tile in pixels
const GRID_WIDTH = 32;
const GRID_HEIGHT = 24;

// Initialize
function init() {
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);
  
  // Center camera on world center
  const worldCenterX = (GRID_WIDTH * TILE_SIZE) / 2;
  const worldCenterY = (GRID_HEIGHT * TILE_SIZE) / 2;
  camera.x = worldCenterX - canvas.width / 2;
  camera.y = worldCenterY - canvas.height / 2;
  
  // Mouse events
  canvas.addEventListener('mousedown', onMouseDown);
  canvas.addEventListener('mousemove', onMouseMove);
  canvas.addEventListener('mouseup', onMouseUp);
  canvas.addEventListener('wheel', onWheel);
  
  // Touch events for mobile
  canvas.addEventListener('touchstart', onTouchStart, { passive: false });
  canvas.addEventListener('touchmove', onTouchMove, { passive: false });
  canvas.addEventListener('touchend', onTouchEnd);
  
  // Start render loop
  requestAnimationFrame(render);
  
  // Connect WebSocket
  connectWebSocket();
  
  // Setup toggle buttons
  setupToggles();
  
  // Setup Create Paul form
  setupCreateForm();
  
  // Setup Social platforms
  setupSocialPlatforms();
  
  // Generate initial diary entries
  generateDiaryEntries();
  
  // Generate initial social posts
  generateSocialPosts();
  
  // Start animation loop for Pauls
  setInterval(animatePauls, 200);
}

let paulAnimationFrame = 0;

function animatePauls() {
  paulAnimationFrame = (paulAnimationFrame + 1) % 2;
}

function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight - 50; // Subtract header
}

// WebSocket
function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}`;
  
  ws = new WebSocket(wsUrl);
  
  ws.onopen = () => {
    console.log('WebSocket connected');
    updateConnectionStatus('connected');
    reconnectAttempts = 0;
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleWebSocketMessage(data);
  };
  
  ws.onclose = () => {
    console.log('WebSocket disconnected');
    updateConnectionStatus('disconnected');
    attemptReconnect();
  };
  
  ws.onerror = (err) => {
    console.error('WebSocket error:', err);
    updateConnectionStatus('disconnected');
  };
}

function attemptReconnect() {
  if (reconnectAttempts < MAX_RECONNECT) {
    reconnectAttempts++;
    updateConnectionStatus('connecting');
    setTimeout(connectWebSocket, 2000 * reconnectAttempts);
  }
}

function handleWebSocketMessage(data) {
  switch (data.type) {
    case 'connected':
      addActivity('🎬 CONNECTED TO PAUL\'S WORLD');
      break;
      
    case 'worldUpdate':
      worldState = data.data;
      updateUI();
      break;
      
    case 'event':
      handleEvent(data.eventType, data.data);
      break;
  }
}

function updateConnectionStatus(status) {
  const dot = document.getElementById('connection-dot');
  const text = document.getElementById('connection-text');
  
  dot.className = `status-dot ${status}`;
  text.textContent = status === 'connected' ? 'ONLINE' : status === 'connecting' ? 'CONNECTING...' : 'OFFLINE';
}

function handleEvent(eventType, data) {
  switch (eventType) {
    case 'market_crash':
      addActivity('📉 MARKET CRASH! PAULS PANICKING...');
      addDiaryEntry('trade', 'MARKET CRASH DETECTED! PAULS RUSHING TO SAFETY.', 'SYSTEM');
      break;
    case 'bull_run':
      addActivity('📈 BULL RUN! PAULS TO DEX...');
      addDiaryEntry('trade', 'BULL RUN IN PROGRESS! PAULS CELEBRATING.', 'SYSTEM');
      break;
    case 'news_break':
      addActivity('📰 BREAKING NEWS! PAULS TO NEWSROOM...');
      addDiaryEntry('activity', 'BREAKING NEWS! PAULS GATHERING INFO.', 'SYSTEM');
      break;
    case 'whale_alert':
      addActivity('🐋 WHALE ALERT! PAULS WATCHING...');
      addDiaryEntry('prediction', 'WHALE MOVEMENT! PAULS ANALYZING IMPACT.', 'SYSTEM');
      break;
  }
}

// 8-bit Pixel Art Rendering
function render() {
  // Clear canvas with grass color
  ctx.fillStyle = PALETTE.grass;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  // Apply camera transform
  ctx.save();
  ctx.translate(-camera.x, -camera.y);
  ctx.scale(camera.zoom, camera.zoom);
  
  // Draw grid (roads/paths)
  drawGrid();
  
  // Draw buildings
  drawBuildings();
  
  // Draw Pauls
  drawPauls();
  
  // Draw hover highlight
  if (hoveredBuilding) {
    drawBuildingHighlight(hoveredBuilding);
  }
  
  ctx.restore();
  
  // Smooth zoom
  camera.zoom += (camera.targetZoom - camera.zoom) * 0.1;
  
  requestAnimationFrame(render);
}

function drawGrid() {
  // Draw roads between buildings
  ctx.fillStyle = PALETTE.road;
  
  // Horizontal roads
  for (let y = 0; y < GRID_HEIGHT; y += 5) {
    ctx.fillRect(0, y * TILE_SIZE, GRID_WIDTH * TILE_SIZE, TILE_SIZE);
  }
  
  // Vertical roads
  for (let x = 0; x < GRID_WIDTH; x += 5) {
    ctx.fillRect(x * TILE_SIZE, 0, TILE_SIZE, GRID_HEIGHT * TILE_SIZE);
  }
  
  // Draw road lines (dashed)
  ctx.fillStyle = PALETTE.roadLine;
  for (let x = 0; x < GRID_WIDTH; x += 5) {
    for (let y = 2; y < GRID_HEIGHT; y += 2) {
      ctx.fillRect(x * TILE_SIZE + TILE_SIZE/2 - 2, y * TILE_SIZE + TILE_SIZE/2 - 1, 4, 2);
    }
  }
  
  // Draw grass details (random pixels)
  ctx.fillStyle = PALETTE.grassDark;
  for (let x = 0; x < GRID_WIDTH; x++) {
    for (let y = 0; y < GRID_HEIGHT; y++) {
      if (Math.random() < 0.05) {
        ctx.fillRect(x * TILE_SIZE + 8, y * TILE_SIZE + 8, 4, 4);
      }
    }
  }
}

function drawBuildings() {
  Object.entries(BUILDING_CONFIG).forEach(([id, building]) => {
    const isHovered = hoveredBuilding === id;
    const pixelX = building.x * TILE_SIZE;
    const pixelY = building.y * TILE_SIZE;
    const pixelW = building.w * TILE_SIZE;
    const pixelH = building.h * TILE_SIZE;
    
    // Building shadow (offset)
    ctx.fillStyle = 'rgba(0,0,0,0.3)';
    ctx.fillRect(pixelX + 4, pixelY + 4, pixelW, pixelH);
    
    // Building body (pixelated block)
    ctx.fillStyle = building.color;
    ctx.fillRect(pixelX, pixelY, pixelW, pixelH);
    
    // Building highlight (top-left)
    ctx.fillStyle = 'rgba(255,255,255,0.3)';
    ctx.fillRect(pixelX, pixelY, pixelW, 4);
    ctx.fillRect(pixelX, pixelY, 4, pixelH);
    
    // Building shadow (bottom-right)
    ctx.fillStyle = 'rgba(0,0,0,0.2)';
    ctx.fillRect(pixelX, pixelY + pixelH - 4, pixelW, 4);
    ctx.fillRect(pixelX + pixelW - 4, pixelY, 4, pixelH);
    
    // Border
    ctx.strokeStyle = isHovered ? '#fff' : 'rgba(0,0,0,0.3)';
    ctx.lineWidth = isHovered ? 4 : 2;
    ctx.strokeRect(pixelX, pixelY, pixelW, pixelH);
    
    // Building details (windows/door)
    ctx.fillStyle = 'rgba(255,255,255,0.4)';
    // Windows
    for (let wx = 1; wx < building.w - 1; wx += 2) {
      for (let wy = 1; wy < building.h - 1; wy++) {
        ctx.fillRect(pixelX + wx * TILE_SIZE + 4, pixelY + wy * TILE_SIZE + 4, TILE_SIZE - 8, TILE_SIZE - 8);
      }
    }
    
    // Door
    ctx.fillStyle = 'rgba(0,0,0,0.4)';
    ctx.fillRect(pixelX + pixelW/2 - TILE_SIZE/2, pixelY + pixelH - TILE_SIZE, TILE_SIZE, TILE_SIZE);
    
    // Label (8-bit text)
    ctx.fillStyle = '#fff';
    ctx.font = '8px "Press Start 2P"';
    ctx.textAlign = 'center';
    ctx.fillText(building.name, pixelX + pixelW/2, pixelY - 8);
    
    // Paul count badge
    const paulCount = worldState.pauls?.filter(p => p.building === id).length || 0;
    if (paulCount > 0) {
      ctx.fillStyle = '#e94560';
      ctx.fillRect(pixelX + pixelW - 20, pixelY - 10, 20, 14);
      ctx.fillStyle = '#fff';
      ctx.font = '8px "Press Start 2P"';
      ctx.fillText(paulCount.toString(), pixelX + pixelW - 10, pixelY);
    }
  });
}

function drawBuildingHighlight(buildingId) {
  const building = BUILDING_CONFIG[buildingId];
  if (!building) return;
  
  const pixelX = building.x * TILE_SIZE;
  const pixelY = building.y * TILE_SIZE;
  const pixelW = building.w * TILE_SIZE;
  const pixelH = building.h * TILE_SIZE;
  
  // Pulsing highlight effect
  const pulse = Math.sin(Date.now() / 200) * 0.3 + 0.7;
  ctx.strokeStyle = `rgba(233, 69, 96, ${pulse})`;
  ctx.lineWidth = 4;
  ctx.setLineDash([8, 4]);
  ctx.strokeRect(pixelX - 4, pixelY - 4, pixelW + 8, pixelH + 8);
  ctx.setLineDash([]);
}

function drawPauls() {
  if (!worldState.pauls) return;
  
  // Sort by Y for depth
  const sortedPauls = [...worldState.pauls].sort((a, b) => a.y - b.y);
  
  sortedPauls.forEach(paul => {
    // Convert grid position to pixel position
    const pixelX = Math.floor(paul.x / TILE_SIZE) * TILE_SIZE;
    const pixelY = Math.floor(paul.y / TILE_SIZE) * TILE_SIZE;
    
    const isReal = paul.isReal;
    const isSelected = selectedPaul === paul.id;
    const isHovered = hoveredPaul === paul.id;
    
    // Skip if outside visible area
    if (pixelX < camera.x - 100 || pixelX > camera.x + canvas.width + 100 ||
        pixelY < camera.y - 100 || pixelY > camera.y + canvas.height + 100) {
      return;
    }
    
    if (isReal) {
      // Draw 8-bit Paul sprite
      const sprite = paulAnimationFrame === 0 ? PAUL_SPRITES.standing : 
                    (Math.floor(Date.now() / 500) % 2 === 0 ? PAUL_SPRITES.walking1 : PAUL_SPRITES.walking2);
      
      const color = paul.type?.color || '#8b5cf6';
      const scale = isSelected ? 2 : (isHovered ? 1.5 : 1);
      const size = 8 * scale;
      
      // Draw sprite pixels
      for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
          if (sprite[row][col] === 1) {
            ctx.fillStyle = color;
            ctx.fillRect(
              pixelX + col * size/8 + (TILE_SIZE - size)/2,
              pixelY + row * size/8 + (TILE_SIZE - size)/2,
              size/8 + 1,
              size/8 + 1
            );
          }
        }
      }
      
      // Draw initials above Paul
      if (isSelected || isHovered) {
        ctx.fillStyle = '#fff';
        ctx.font = '8px "Press Start 2P"';
        ctx.textAlign = 'center';
        ctx.fillText(
          paul.initials || 'P',
          pixelX + TILE_SIZE/2,
          pixelY - 4
        );
      }
      
      // Selection ring
      if (isSelected) {
        ctx.strokeStyle = '#0f0';
        ctx.lineWidth = 2;
        ctx.strokeRect(pixelX + 2, pixelY + 2, TILE_SIZE - 4, TILE_SIZE - 4);
      }
    } else {
      // Visual Paul - simple pixel dot
      const color = paul.type?.color || '#6b7280';
      ctx.fillStyle = color;
      ctx.fillRect(pixelX + TILE_SIZE/2 - 2, pixelY + TILE_SIZE/2 - 2, 4, 4);
    }
  });
}

// Mouse/Touch handling
function onMouseDown(e) {
  mouse.isDown = true;
  mouse.lastX = e.clientX;
  mouse.lastY = e.clientY;
  
  // Convert screen to world coordinates
  const worldX = (e.clientX + camera.x) / camera.zoom;
  const worldY = (e.clientY + camera.y - 50) / camera.zoom;
  
  // Check for clicks on Pauls
  let clickedPaul = null;
  if (worldState.pauls) {
    for (const paul of worldState.pauls) {
      if (!paul.isReal) continue;
      const pixelX = Math.floor(paul.x / TILE_SIZE) * TILE_SIZE;
      const pixelY = Math.floor(paul.y / TILE_SIZE) * TILE_SIZE;
      if (worldX >= pixelX && worldX <= pixelX + TILE_SIZE &&
          worldY >= pixelY && worldY <= pixelY + TILE_SIZE) {
        clickedPaul = paul;
        break;
      }
    }
  }
  
  if (clickedPaul) {
    selectPaul(clickedPaul);
  } else {
    // Check buildings
    let clickedBuilding = null;
    Object.entries(BUILDING_CONFIG).forEach(([id, building]) => {
      const pixelX = building.x * TILE_SIZE;
      const pixelY = building.y * TILE_SIZE;
      const pixelW = building.w * TILE_SIZE;
      const pixelH = building.h * TILE_SIZE;
      
      if (worldX >= pixelX && worldX <= pixelX + pixelW &&
          worldY >= pixelY && worldY <= pixelY + pixelH) {
        clickedBuilding = id;
      }
    });
    
    if (clickedBuilding) {
      selectBuilding(clickedBuilding);
    } else {
      selectedPaul = null;
      updateSelectedPanel();
    }
  }
}

function onMouseMove(e) {
  const rect = canvas.getBoundingClientRect();
  mouse.x = e.clientX - rect.left;
  mouse.y = e.clientY - rect.top;
  
  const worldX = (mouse.x + camera.x) / camera.zoom;
  const worldY = (mouse.y + camera.y) / camera.zoom;
  
  if (mouse.isDown) {
    // Pan
    camera.x -= (e.clientX - mouse.lastX);
    camera.y -= (e.clientY - mouse.lastY);
    mouse.lastX = e.clientX;
    mouse.lastY = e.clientY;
  } else {
    // Hover detection
    hoveredPaul = null;
    hoveredBuilding = null;
    
    // Check Pauls
    if (worldState.pauls) {
      for (const paul of worldState.pauls) {
        if (!paul.isReal) continue;
        const pixelX = Math.floor(paul.x / TILE_SIZE) * TILE_SIZE;
        const pixelY = Math.floor(paul.y / TILE_SIZE) * TILE_SIZE;
        if (worldX >= pixelX && worldX <= pixelX + TILE_SIZE &&
            worldY >= pixelY && worldY <= pixelY + TILE_SIZE) {
          hoveredPaul = paul.id;
          canvas.style.cursor = 'pointer';
          break;
        }
      }
    }
    
    // Check buildings
    if (!hoveredPaul) {
      Object.entries(BUILDING_CONFIG).forEach(([id, building]) => {
        const pixelX = building.x * TILE_SIZE;
        const pixelY = building.y * TILE_SIZE;
        const pixelW = building.w * TILE_SIZE;
        const pixelH = building.h * TILE_SIZE;
        
        if (worldX >= pixelX && worldX <= pixelX + pixelW &&
            worldY >= pixelY && worldY <= pixelY + pixelH) {
          hoveredBuilding = id;
          canvas.style.cursor = 'pointer';
        }
      });
    }
    
    if (!hoveredPaul && !hoveredBuilding) {
      canvas.style.cursor = mouse.isDown ? 'grabbing' : 'crosshair';
    }
  }
}

function onMouseUp() {
  mouse.isDown = false;
}

function onWheel(e) {
  e.preventDefault();
  const zoomSpeed = 0.2;
  const newZoom = camera.targetZoom + (e.deltaY > 0 ? -zoomSpeed : zoomSpeed);
  camera.targetZoom = Math.max(0.5, Math.min(3, newZoom));
}

// Touch events
function onTouchStart(e) {
  e.preventDefault();
  if (e.touches.length === 1) {
    mouse.isDown = true;
    mouse.lastX = e.touches[0].clientX;
    mouse.lastY = e.touches[0].clientY;
  }
}

function onTouchMove(e) {
  e.preventDefault();
  if (e.touches.length === 1 && mouse.isDown) {
    camera.x -= (e.touches[0].clientX - mouse.lastX);
    camera.y -= (e.touches[0].clientY - mouse.lastY);
    mouse.lastX = e.touches[0].clientX;
    mouse.lastY = e.touches[0].clientY;
  }
}

function onTouchEnd() {
  mouse.isDown = false;
}

// UI Functions
function selectPaul(paul) {
  selectedPaul = paul.id;
  updateSelectedPanel(paul);
  
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'selectPaul', paulId: paul.id }));
  }
}

function selectBuilding(buildingId) {
  const building = BUILDING_CONFIG[buildingId];
  const paulsInside = worldState.pauls?.filter(p => p.building === buildingId) || [];
  const realPaulsInside = paulsInside.filter(p => p.isReal);
  
  showBuildingPopup(building, paulsInside.length, realPaulsInside);
  
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'selectBuilding', buildingId }));
  }
  addActivity(`🏢 VIEWING ${building.name} (${paulsInside.length} PAULS INSIDE)`);
}

function showBuildingPopup(building, totalCount, realPauls) {
  const existing = document.getElementById('building-popup');
  if (existing) existing.remove();
  
  const popup = document.createElement('div');
  popup.id = 'building-popup';
  popup.className = 'overlay-panel';
  popup.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 320px;
    max-height: 400px;
    background: #16213e;
    border: 4px solid ${building.color};
    padding: 16px;
    z-index: 2000;
    overflow-y: auto;
    font-family: 'Press Start 2P', cursive;
  `;
  
  const realCount = realPauls.length;
  const fillerCount = totalCount - realCount;
  
  let paulsList = '';
  if (realPauls.length > 0) {
    paulsList = realPauls.slice(0, 8).map(p => `
      <div style="display: flex; align-items: center; gap: 8px; padding: 8px; background: #0f3460; border: 2px solid #533483; margin-bottom: 8px; font-size: 8px;">
        <div style="width: 24px; height: 24px; background: ${p.type?.color || '#8b5cf6'}; display: flex; align-items: center; justify-content: center; font-size: 10px;">${p.initials || 'P'}</div>
        <div style="flex: 1;">
          <div style="color: #e94560;">${p.name}</div>
          <div style="color: #888; font-size: 6px; margin-top: 4px;">${p.type?.name || 'TRADER'} • ${p.activity || 'IDLE'}</div>
        </div>
        <div style="color: ${p.stats?.roi > 0 ? '#0f0' : '#f00'}; font-size: 8px;">${p.stats?.roi > 0 ? '+' : ''}${p.stats?.roi || 0}%</div>
      </div>
    `).join('');
    
    if (realPauls.length > 8) {
      paulsList += `<div style="text-align: center; color: #888; font-size: 8px; padding: 8px;">+ ${realPauls.length - 8} MORE...</div>`;
    }
  } else {
    paulsList = '<div style="text-align: center; color: #888; padding: 20px; font-size: 8px;">NO PAULS INSIDE</div>';
  }
  
  popup.innerHTML = `
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; border-bottom: 2px solid ${building.color}; padding-bottom: 12px;">
      <div style="font-size: 12px; color: ${building.color};">${building.emoji} ${building.name}</div>
      <button onclick="document.getElementById('building-popup').remove()" style="background: #e94560; border: 2px solid #fff; color: #fff; font-family: 'Press Start 2P', cursive; font-size: 10px; cursor: pointer; padding: 4px 8px;">X</button>
    </div>
    <div style="font-size: 8px; color: #888; margin-bottom: 16px;">
      ${totalCount} PAULS INSIDE (${realCount} REAL, ${fillerCount} VISUAL)
    </div>
    <div style="font-size: 8px; color: #e94560; margin-bottom: 12px;">PAULS INSIDE:</div>
    ${paulsList}
  `;
  
  document.body.appendChild(popup);
}

function updateSelectedPanel(paul) {
  const panel = document.getElementById('selected-panel');
  
  if (!paul) {
    panel.classList.add('hidden');
    document.getElementById('toggle-selected').classList.remove('active');
    return;
  }
  
  panel.classList.remove('hidden');
  document.getElementById('toggle-selected').classList.add('active');
  
  document.getElementById('selected-name').textContent = paul.name.toUpperCase();
  document.getElementById('selected-role').textContent = (paul.profession || 'TRADER').toUpperCase();
  document.getElementById('selected-avatar').textContent = paul.initials || 'P';
  document.getElementById('selected-avatar').style.background = paul.type?.color || '#8b5cf6';
  
  const building = BUILDING_CONFIG[paul.building];
  document.getElementById('selected-building').textContent = building ? `📍 ${building.name}` : '📍 WANDERING';
  document.getElementById('selected-activity').textContent = (paul.activity || 'IDLE').toUpperCase();
  
  if (paul.stats) {
    document.getElementById('selected-roi').textContent = (paul.stats.roi > 0 ? '+' : '') + paul.stats.roi + '%';
    document.getElementById('selected-winrate').textContent = Math.round((paul.stats.wins / paul.stats.trades) * 100) + '%';
    document.getElementById('selected-level').textContent = paul.stats.level;
  }
  
  document.getElementById('selected-thought').textContent = paul.thought ? `"${paul.thought.toUpperCase()}"` : '...';
}

function updateUI() {
  document.getElementById('paulCount').textContent = worldState.paulCount || 0;
  
  const hour = Math.floor(worldState.time?.hour || 9);
  const minute = Math.floor(worldState.time?.minute || 0);
  document.getElementById('gameTime').textContent = `${hour.toString().padStart(2,'0')}:${minute.toString().padStart(2,'0')}`;
  document.getElementById('gameDay').textContent = worldState.time?.day || 1;
  
  // Weather
  const weatherTypes = [
    { icon: '☀️', text: 'SUNNY' },
    { icon: '⛅', text: 'CLOUDY' },
    { icon: '🌧️', text: 'RAINY' },
    { icon: '⛈️', text: 'STORMY' },
    { icon: '🌨️', text: 'SNOWY' }
  ];
  const weather = weatherTypes[(worldState.time?.day || 1) % weatherTypes.length];
  document.getElementById('weather-icon').textContent = weather.icon;
  document.getElementById('weather-text').textContent = weather.text;
  
  // Needs bars
  if (worldState.pauls) {
    const realPauls = worldState.pauls.filter(p => p.isReal);
    if (realPauls.length > 0) {
      const avgEnergy = realPauls.reduce((sum, p) => sum + (p.needs?.energy || 0), 0) / realPauls.length;
      const avgKnowledge = realPauls.reduce((sum, p) => sum + (p.needs?.knowledge || 0), 0) / realPauls.length;
      const avgSocial = realPauls.reduce((sum, p) => sum + (p.needs?.social || 0), 0) / realPauls.length;
      const avgMoney = realPauls.reduce((sum, p) => sum + (p.needs?.money || 0), 0) / realPauls.length;
      
      document.getElementById('avgEnergy').textContent = Math.round(avgEnergy) + '%';
      document.getElementById('energyBar').style.width = avgEnergy + '%';
      
      document.getElementById('avgKnowledge').textContent = Math.round(avgKnowledge) + '%';
      document.getElementById('knowledgeBar').style.width = avgKnowledge + '%';
      
      document.getElementById('avgSocial').textContent = Math.round(avgSocial) + '%';
      document.getElementById('socialBar').style.width = avgSocial + '%';
      
      document.getElementById('avgMoney').textContent = Math.round(avgMoney) + '%';
      document.getElementById('moneyBar').style.width = avgMoney + '%';
    }
  }
  
  if (selectedPaul) {
    const paul = worldState.pauls?.find(p => p.id === selectedPaul);
    if (paul) {
      updateSelectedPanel(paul);
    }
  }
}

function setupToggles() {
  const toggles = {
    'toggle-time': 'time-panel',
    'toggle-needs': 'needs-panel',
    'toggle-selected': 'selected-panel',
    'toggle-activity': 'activity-panel',
    'toggle-chat': 'chat-panel'
  };
  
  Object.entries(toggles).forEach(([btnId, panelId]) => {
    const btn = document.getElementById(btnId);
    const panel = document.getElementById(panelId);
    if (!btn || !panel) return;
    
    btn.addEventListener('click', () => {
      btn.classList.toggle('active');
      panel.classList.toggle('hidden');
    });
  });
  
  const sideToggles = {
    'toggle-diary': 'diary-panel',
    'toggle-social': 'social-panel',
    'toggle-create': 'create-panel'
  };
  
  Object.entries(sideToggles).forEach(([btnId, panelId]) => {
    const btn = document.getElementById(btnId);
    const panel = document.getElementById(panelId);
    if (!btn || !panel) return;
    
    btn.addEventListener('click', () => {
      if (activeSidePanel === btnId.replace('toggle-', '')) {
        panel.classList.add('hidden');
        btn.classList.remove('active');
        activeSidePanel = null;
        return;
      }
      
      Object.values(sideToggles).forEach(pid => {
        const p = document.getElementById(pid);
        if (p) p.classList.add('hidden');
      });
      
      Object.keys(sideToggles).forEach(bid => {
        const b = document.getElementById(bid);
        if (b) b.classList.remove('active');
      });
      
      panel.classList.remove('hidden');
      btn.classList.add('active');
      activeSidePanel = btnId.replace('toggle-', '');
    });
  });
  
  setupChat();
}

// Diary Filter Functions
function filterDiary() {
  const timeFilter = document.getElementById('diary-time-filter');
  if (timeFilter) {
    diaryTimeRange = parseInt(timeFilter.value) || 7;
  }
  generateDiaryEntries();
}

function toggleDiaryType(type) {
  const btn = document.querySelector(`.filter-chip[data-type="${type}"]`);
  if (!btn) return;
  
  if (diaryTypes.includes(type)) {
    diaryTypes = diaryTypes.filter(t => t !== type);
    btn.classList.remove('active');
    btn.style.opacity = '0.5';
  } else {
    diaryTypes.push(type);
    btn.classList.add('active');
    btn.style.opacity = '1';
  }
  
  generateDiaryEntries();
}

// Social Days Function
function setSocialDays(days) {
  socialDays = days;
  
  document.querySelectorAll('.days-btn').forEach(btn => {
    const btnDays = parseInt(btn.dataset.days);
    if (btnDays === days) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
  
  generateSocialPosts();
}

// Create Paul Form
function setupCreateForm() {
  updateCreatePreview();
}

function selectColor(color) {
  selectedColor = color;
  document.querySelectorAll('.color-option').forEach(o => {
    o.classList.toggle('selected', o.dataset.color === color);
  });
  updateCreatePreview();
}

function selectBias(bias) {
  selectedBias = bias;
  document.querySelectorAll('.bias-btn').forEach(b => {
    b.classList.toggle('selected', b.dataset.bias === bias);
  });
  updateCreatePreview();
}

function updateCreatePreview() {
  const name = document.getElementById('new-paul-name')?.value || 'PAUL NAME';
  const initials = document.getElementById('new-paul-initials')?.value || 'PA';
  const specialty = document.getElementById('new-paul-specialty')?.value || 'SELECT SPECIALTY';
  
  const previewAvatar = document.getElementById('preview-avatar');
  const previewName = document.getElementById('preview-name');
  const previewDetails = document.getElementById('preview-details');
  
  if (previewAvatar) {
    previewAvatar.textContent = initials.toUpperCase();
    previewAvatar.style.background = selectedColor;
  }
  if (previewName) previewName.textContent = name.toUpperCase();
  if (previewDetails) previewDetails.textContent = `${specialty.toUpperCase()} • ${selectedBias.toUpperCase()}`;
}

function createNewPaul() {
  const name = document.getElementById('new-paul-name')?.value?.trim();
  const initials = document.getElementById('new-paul-initials')?.value?.trim()?.toUpperCase();
  const specialty = document.getElementById('new-paul-specialty')?.value;
  
  if (!name || !initials || !specialty) {
    addChatMessage('system', 'PLEASE FILL IN ALL REQUIRED FIELDS!');
    return;
  }
  
  if (userCredits < 2) {
    addChatMessage('system', 'NOT ENOUGH CREDITS! NEED 2 💎');
    return;
  }
  
  userCredits -= 2;
  localStorage.setItem('paulWorldCredits', userCredits);
  updateCredits();
  
  document.getElementById('new-paul-name').value = '';
  document.getElementById('new-paul-initials').value = '';
  document.getElementById('new-paul-specialty').value = '';
  document.getElementById('new-paul-quirk').value = '';
  updateCreatePreview();
  
  addChatMessage('system', `🍼 CREATED ${name.toUpperCase()}! WELCOME!`);
  addActivity(`✨ NEW PAUL: ${name.toUpperCase()}`);
  addDiaryEntry('activity', `${name.toUpperCase()} HAS JOINED!`, name.toUpperCase());
}

// Social Platform Setup
function setupSocialPlatforms() {
  const platformBtns = document.querySelectorAll('.platform-btn');
  platformBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      platformBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentPlatform = btn.dataset.platform;
      generateSocialPosts();
    });
  });
}

// Generate Diary Entries
function generateDiaryEntries() {
  const entries = [];
  
  entries.push({ type: 'activity', text: 'THE WORLD AWAKENS. 1000 PAULS BEGIN THEIR TRADING JOURNEY.', paul: 'WORLD', time: 'DAY 1, 09:00', day: 1 });
  
  const entryCount = diaryTimeRange === 1 ? 5 : diaryTimeRange === 7 ? 15 : diaryTimeRange === 30 ? 30 : 50;
  
  const entryTypes = ['activity', 'thought', 'prediction', 'trade', 'dream', 'interaction'];
  const pauls = ['VISIONARY PAUL', 'DEGEN PAUL', 'SKEPTIC PAUL', 'WHALE PAUL', 'QUANT PAUL', 'CONTRARIAN PAUL', 'MOONSHOT PAUL'];
  
  for (let i = 0; i < entryCount; i++) {
    const type = entryTypes[Math.floor(Math.random() * entryTypes.length)];
    const paul = pauls[Math.floor(Math.random() * pauls.length)];
    const day = Math.floor(Math.random() * diaryTimeRange) + 1;
    const hour = Math.floor(Math.random() * 24);
    const minute = Math.floor(Math.random() * 60);
    
    let text = '';
    switch (type) {
      case 'activity': text = 'ANALYZING MARKET TRENDS'; break;
      case 'thought': text = 'THE MARKET FEELS DIFFERENT TODAY...'; break;
      case 'prediction': text = 'BTC WILL MOVE SOON'; break;
      case 'trade': text = 'CLOSED POSITION FOR +12%'; break;
      case 'dream': text = 'DREAMT OF GREEN CANDLES'; break;
      case 'interaction': text = 'HAD A GREAT DISCUSSION WITH WHALE PAUL'; break;
    }
    
    entries.push({ type, text, paul, time: `DAY ${day}, ${hour.toString().padStart(2,'0')}:${minute.toString().padStart(2,'0')}`, day });
  }
  
  entries.sort((a, b) => b.day - a.day);
  
  const filteredEntries = entries.filter(e => diaryTypes.includes(e.type));
  
  const container = document.getElementById('diary-entries');
  if (!container) return;
  
  container.innerHTML = filteredEntries.map(entry => `
    <div class="diary-entry ${entry.type}">
      <div class="diary-time">${entry.time}</div>
      <div class="diary-text">${entry.text}</div>
      <div class="diary-paul">— ${entry.paul}</div>
    </div>
  `).join('');
}

function addDiaryEntry(type, text, paul) {
  const container = document.getElementById('diary-entries');
  if (!container) return;
  
  const entry = document.createElement('div');
  entry.className = `diary-entry ${type}`;
  entry.innerHTML = `
    <div class="diary-time">JUST NOW</div>
    <div class="diary-text">${text}</div>
    <div class="diary-paul">— ${paul}</div>
  `;
  container.insertBefore(entry, container.firstChild);
  
  while (container.children.length > 20) {
    container.removeChild(container.lastChild);
  }
}

// Generate Social Posts
function generateSocialPosts() {
  const postCount = socialDays === 1 ? 5 : socialDays === 7 ? 12 : 20;
  const posts = [];
  
  const pauls = [
    { name: 'VISIONARY PAUL', initials: 'VP', color: '#8b5cf6' },
    { name: 'DEGEN PAUL', initials: 'DP', color: '#ec4899' },
    { name: 'SKEPTIC PAUL', initials: 'SP', color: '#6b7280' },
    { name: 'WHALE PAUL', initials: 'WP', color: '#f59e0b' },
    { name: 'QUANT PAUL', initials: 'QP', color: '#10b981' },
    { name: 'CONTRARIAN PAUL', initials: 'CP', color: '#e11d48' },
    { name: 'MOONSHOT PAUL', initials: 'MP', color: '#3b82f6' },
    { name: 'VALUE PAUL', initials: 'VaP', color: '#06b6d4' }
  ];
  
  const texts = [
    'FEELING BULLISH TODAY! THE CHARTS LOOK PRIMED FOR A BREAKOUT. 📈',
    'JUST APED INTO A NEW MEME COIN. EITHER RETIRING TOMORROW OR EATING RAMEN. 🎰',
    'EVERYONE IS TOO EUPHORIC RIGHT NOW. BE CAREFUL OUT THERE. 🤨',
    'ACCUMULATING QUIETLY. PATIENCE PAYS. 🐋',
    'MY MODELS SHOW 73% PROBABILITY OF UPWARD MOVEMENT. 🧮',
    'MARKETS ARE IRRATIONAL LONGER THAN YOU CAN STAY SOLVENT. 📉',
    'THE TREND IS YOUR FRIEND UNTIL IT ENDS. WATCHING CLOSELY. 👀',
    'BOUGHT THE DIP. NOW WE WAIT. 💎',
    'TAKING PROFITS HERE. BETTER SAFE THAN SORRY. 💰',
    'THIS CONSOLIDATION IS SETTING UP SOMETHING BIG. 🔮'
  ];
  
  for (let i = 0; i < postCount; i++) {
    const paul = pauls[Math.floor(Math.random() * pauls.length)];
    const text = texts[Math.floor(Math.random() * texts.length)];
    const likes = Math.floor(Math.random() * 100) + 1;
    const replies = Math.floor(Math.random() * 20);
    const shares = Math.floor(Math.random() * 15);
    const viral = likes > 50;
    
    let time;
    if (socialDays === 1) {
      time = `${Math.floor(Math.random() * 24)}H AGO`;
    } else if (socialDays === 7) {
      time = `${Math.floor(Math.random() * 7) + 1}D AGO`;
    } else {
      time = `${Math.floor(Math.random() * 30) + 1}D AGO`;
    }
    
    posts.push({ ...paul, text, likes, replies, shares, viral, time });
  }
  
  const container = document.getElementById('social-feed');
  if (!container) return;
  
  container.innerHTML = posts.map(post => `
    <div class="social-post">
      <div class="post-header">
        <span class="post-avatar" style="background: ${post.color};">${post.initials}</span>
        <span class="post-name">${post.name}</span>
        ${post.viral ? '<span class="viral-badge">🔥 VIRAL</span>' : ''}
        <span class="post-time">${post.time}</span>
      </div>
      <div class="post-text">${post.text}</div>
      <div class="post-actions">
        <button>❤️ ${post.likes}</button>
        <button>💬 ${post.replies}</button>
        <button>🔄 ${post.shares}</button>
      </div>
    </div>
  `).join('');
}

// Chat system
let userCredits = 100;

function setupChat() {
  const input = document.getElementById('chat-input');
  const sendBtn = document.getElementById('chat-send');
  
  if (!input || !sendBtn) return;
  
  const savedCredits = localStorage.getItem('paulWorldCredits');
  if (savedCredits) {
    userCredits = parseInt(savedCredits);
    updateCredits();
  }
  
  function sendMessage() {
    const question = input.value.trim();
    if (!question) return;
    if (userCredits < 1) {
      addChatMessage('system', 'NOT ENOUGH CREDITS!');
      return;
    }
    
    userCredits--;
    localStorage.setItem('paulWorldCredits', userCredits);
    updateCredits();
    
    addChatMessage('user', question);
    input.value = '';
    
    sendBtn.disabled = true;
    sendBtn.textContent = 'ASKING...';
    
    fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, numPauls: 50 })
    })
    .then(res => res.json())
    .then(data => {
      displayPaulResponse(data);
      sendBtn.disabled = false;
      sendBtn.textContent = 'ASK (1💎)';
    })
    .catch(err => {
      addChatMessage('system', 'ERROR ASKING PAULS. TRY AGAIN!');
      sendBtn.disabled = false;
      sendBtn.textContent = 'ASK (1💎)';
    });
  }
  
  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
  });
}

function updateCredits() {
  const creditsEl = document.getElementById('chat-credits');
  if (creditsEl) creditsEl.textContent = userCredits;
}

function addChatMessage(type, content) {
  const messages = document.getElementById('chat-messages');
  if (!messages) return;
  
  const msg = document.createElement('div');
  msg.className = `chat-message ${type}`;
  msg.innerHTML = `<strong>${type === 'user' ? 'YOU' : 'SYSTEM'}:</strong> ${content}`;
  
  messages.appendChild(msg);
  messages.scrollTop = messages.scrollHeight;
}

function displayPaulResponse(data) {
  const messages = document.getElementById('chat-messages');
  if (!messages) return;
  
  const consensusMsg = document.createElement('div');
  consensusMsg.className = 'chat-message consensus';
  consensusMsg.innerHTML = `
    <strong>📊 CONSENSUS (${data.consensus.agreement}% AGREEMENT)</strong><br>
    ${data.consensus.majority.toUpperCase()}<br>
    <span style="color: #888;">CONFIDENCE: ${Math.round(data.consensus.confidence * 100)}%</span>
  `;
  
  messages.appendChild(consensusMsg);
  messages.scrollTop = messages.scrollHeight;
}

function addActivity(text) {
  const log = document.getElementById('activity-log');
  if (!log) return;
  
  const item = document.createElement('div');
  item.className = 'activity-item';
  item.textContent = text;
  log.insertBefore(item, log.firstChild);
  
  while (log.children.length > 20) {
    log.removeChild(log.lastChild);
  }
}

// Controls
function zoomIn() {
  camera.targetZoom = Math.min(3, camera.targetZoom + 0.3);
}

function zoomOut() {
  camera.targetZoom = Math.max(0.5, camera.targetZoom - 0.3);
}

function resetView() {
  const worldCenterX = (GRID_WIDTH * TILE_SIZE) / 2;
  const worldCenterY = (GRID_HEIGHT * TILE_SIZE) / 2;
  camera.x = worldCenterX - canvas.width / 2;
  camera.y = worldCenterY - canvas.height / 2;
  camera.targetZoom = 1;
}

// Initialize
document.addEventListener('DOMContentLoaded', init);
