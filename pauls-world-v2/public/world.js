// Paul's World V2 - Canvas Renderer
// Isometric 2D view with 4000 Pauls

const canvas = document.getElementById('worldCanvas');
const ctx = canvas.getContext('2d');

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

// Buildings configuration (isometric positions)
const BUILDING_CONFIG = {
  market: { name: 'Market House', x: 200, y: 150, w: 120, h: 80, color: '#22c55e', emoji: '📈' },
  research: { name: 'Research Lab', x: 500, y: 150, w: 120, h: 80, color: '#3b82f6', emoji: '🔬' },
  social: { name: 'Social Plaza', x: 800, y: 150, w: 140, h: 90, color: '#ec4899', emoji: '💬' },
  cafe: { name: 'The Cafe', x: 200, y: 400, w: 100, h: 70, color: '#eab308', emoji: '☕' },
  dex: { name: 'DEX Terminal', x: 500, y: 400, w: 120, h: 80, color: '#8b5cf6', emoji: '💱' },
  home: { name: 'Paul Estates', x: 800, y: 400, w: 130, h: 85, color: '#6b7280', emoji: '🏠' },
  townhall: { name: 'Town Hall', x: 200, y: 650, w: 130, h: 90, color: '#f59e0b', emoji: '🏛️' },
  arcade: { name: 'Arcade', x: 500, y: 650, w: 140, h: 90, color: '#d946ef', emoji: '🎮' },
  garden: { name: 'Garden', x: 800, y: 650, w: 110, h: 75, color: '#10b981', emoji: '🌱' },
  oracle: { name: 'Oracle Tower', x: 350, y: 275, w: 100, h: 140, color: '#6366f1', emoji: '🔮' },
  power: { name: 'Power Plant', x: 650, y: 275, w: 110, h: 100, color: '#f97316', emoji: '⚡' },
  newsroom: { name: 'Newsroom', x: 350, y: 525, w: 120, h: 80, color: '#06b6d4', emoji: '📰' },
  theater: { name: 'Theater', x: 650, y: 525, w: 110, h: 85, color: '#e11d48', emoji: '🎭' },
  gym: { name: 'Gym', x: 500, y: 800, w: 120, h: 80, color: '#84cc16', emoji: '🏋️' },
  daycare: { name: 'Paul Daycare', x: 950, y: 400, w: 140, h: 90, color: '#f472b6', emoji: '👶' }
};

// Initialize
function init() {
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);
  
  // Center camera
  camera.x = canvas.width / 2 - 500;
  camera.y = canvas.height / 2 - 400;
  
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
}

function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight - 60; // Subtract header
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
      addActivity('🎬 Connected to Paul\'s World');
      break;
      
    case 'worldUpdate':
      worldState = data.data;
      updateUI();
      break;
      
    case 'event':
      handleEvent(data.eventType, data.data);
      break;
      
    case 'paulUpdate':
      // Individual Paul update
      break;
  }
}

function updateConnectionStatus(status) {
  const dot = document.getElementById('connection-dot');
  const text = document.getElementById('connection-text');
  
  dot.className = `status-dot ${status}`;
  text.textContent = status === 'connected' ? 'Live' : status === 'connecting' ? 'Connecting...' : 'Disconnected';
}

function handleEvent(eventType, data) {
  switch (eventType) {
    case 'market_crash':
      addActivity('📉 MARKET CRASH! Pauls panicking...');
      break;
    case 'bull_run':
      addActivity('📈 BULL RUN! Pauls rushing to DEX...');
      break;
  }
}

// Rendering
function render() {
  // Clear canvas
  ctx.fillStyle = '#0a0a0a';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  // Draw grid
  drawGrid();
  
  // Apply camera transform
  ctx.save();
  ctx.translate(-camera.x, -camera.y);
  ctx.scale(camera.zoom, camera.zoom);
  
  // Draw buildings
  drawBuildings();
  
  // Draw Pauls
  drawPauls();
  
  // Draw hovered building highlight
  if (hoveredBuilding) {
    drawBuildingHighlight(hoveredBuilding);
  }
  
  ctx.restore();
  
  // Smooth zoom
  camera.zoom += (camera.targetZoom - camera.zoom) * 0.1;
  
  requestAnimationFrame(render);
}

function drawGrid() {
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
  ctx.lineWidth = 1;
  
  const gridSize = 50 * camera.zoom;
  const offsetX = -camera.x % gridSize;
  const offsetY = -camera.y % gridSize;
  
  for (let x = offsetX; x < canvas.width; x += gridSize) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, canvas.height);
    ctx.stroke();
  }
  
  for (let y = offsetY; y < canvas.height; y += gridSize) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(canvas.width, y);
    ctx.stroke();
  }
}

function drawBuildings() {
  Object.entries(BUILDING_CONFIG).forEach(([id, building]) => {
    const isHovered = hoveredBuilding === id;
    const isActive = worldState.buildings[id]?.active;
    
    // Building shadow
    ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
    ctx.fillRect(building.x + 5, building.y + 5, building.w, building.h);
    
    // Building body
    const gradient = ctx.createLinearGradient(building.x, building.y, building.x, building.y + building.h);
    gradient.addColorStop(0, building.color + '40');
    gradient.addColorStop(1, building.color + '20');
    ctx.fillStyle = gradient;
    ctx.fillRect(building.x, building.y, building.w, building.h);
    
    // Building border
    ctx.strokeStyle = isHovered ? '#fff' : building.color;
    ctx.lineWidth = isHovered ? 3 : 2;
    ctx.strokeRect(building.x, building.y, building.w, building.h);
    
    // Glow effect for active buildings
    if (isActive || isHovered) {
      ctx.shadowColor = building.color;
      ctx.shadowBlur = 20;
      ctx.strokeRect(building.x, building.y, building.w, building.h);
      ctx.shadowBlur = 0;
    }
    
    // Emoji
    ctx.font = '24px Arial';
    ctx.textAlign = 'center';
    ctx.fillStyle = '#fff';
    ctx.fillText(building.emoji, building.x + building.w / 2, building.y + building.h / 2 + 8);
    
    // Label
    ctx.font = '12px Inter, sans-serif';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.fillText(building.name, building.x + building.w / 2, building.y + building.h + 20);
    
    // Paul count
    const paulCount = worldState.pauls?.filter(p => p.building === id).length || 0;
    if (paulCount > 0) {
      ctx.fillStyle = building.color;
      ctx.beginPath();
      ctx.arc(building.x + building.w - 15, building.y + 15, 12, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#000';
      ctx.font = 'bold 10px Inter';
      ctx.fillText(paulCount.toString(), building.x + building.w - 15, building.y + 19);
    }
  });
}

function drawBuildingHighlight(buildingId) {
  const building = BUILDING_CONFIG[buildingId];
  if (!building) return;
  
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
  ctx.lineWidth = 2;
  ctx.setLineDash([5, 5]);
  ctx.strokeRect(building.x - 5, building.y - 5, building.w + 10, building.h + 10);
  ctx.setLineDash([]);
}

function drawPauls() {
  if (!worldState.pauls) return;
  
  // Sort by Y for depth
  const sortedPauls = [...worldState.pauls].sort((a, b) => a.y - b.y);
  
  sortedPauls.forEach(paul => {
    const x = paul.x || 0;
    const y = paul.y || 0;
    const isReal = paul.isReal;
    const isSelected = selectedPaul === paul.id;
    const isHovered = hoveredPaul === paul.id;
    
    // Skip if outside visible area (optimization)
    if (x < camera.x - 100 || x > camera.x + canvas.width + 100 ||
        y < camera.y - 100 || y > camera.y + canvas.height + 100) {
      return;
    }
    
    if (isReal) {
      // Real Paul - full avatar
      const size = isSelected ? 28 : isHovered ? 24 : 20;
      const color = paul.type?.color || '#8b5cf6';
      
      // Shadow
      ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
      ctx.beginPath();
      ctx.ellipse(x + 2, y + size/2 + 2, size/2, size/4, 0, 0, Math.PI * 2);
      ctx.fill();
      
      // Avatar circle
      ctx.fillStyle = color + '30';
      ctx.strokeStyle = isSelected ? '#fff' : color;
      ctx.lineWidth = isSelected ? 3 : 2;
      ctx.beginPath();
      ctx.arc(x, y, size/2, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      
      // Initials
      ctx.fillStyle = '#fff';
      ctx.font = `bold ${size/2}px Inter, sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(paul.initials || 'P', x, y + 1);
      
      // Thought bubble
      if (paul.thought && (isSelected || isHovered)) {
        drawThoughtBubble(x, y - size, paul.thought);
      }
      
      // Selection ring
      if (isSelected) {
        ctx.strokeStyle = '#22d3ee';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(x, y, size/2 + 5, 0, Math.PI * 2);
        ctx.stroke();
      }
    } else {
      // Filler Paul - simple dot
      const color = paul.type?.color || '#6b7280';
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fill();
    }
  });
}

function drawThoughtBubble(x, y, text) {
  const padding = 10;
  ctx.font = '12px Inter, sans-serif';
  const textWidth = ctx.measureText(text).width;
  const width = textWidth + padding * 2;
  const height = 30;
  
  // Bubble
  ctx.fillStyle = 'rgba(0, 0, 0, 0.9)';
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
  ctx.lineWidth = 1;
  
  ctx.beginPath();
  ctx.roundRect(x - width/2, y - height - 10, width, height, 8);
  ctx.fill();
  ctx.stroke();
  
  // Triangle pointer
  ctx.beginPath();
  ctx.moveTo(x - 6, y - 10);
  ctx.lineTo(x, y - 4);
  ctx.lineTo(x + 6, y - 10);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();
  
  // Text
  ctx.fillStyle = '#fff';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, x, y - height/2 - 10);
}

// Mouse/Touch handling
function onMouseDown(e) {
  mouse.isDown = true;
  mouse.lastX = e.clientX;
  mouse.lastY = e.clientY;
  
  // Check for clicks on Pauls or buildings
  const worldX = (e.clientX + camera.x) / camera.zoom;
  const worldY = (e.clientY + camera.y - 60) / camera.zoom;
  
  // Check Pauls first
  let clickedPaul = null;
  if (worldState.pauls) {
    for (const paul of worldState.pauls) {
      if (!paul.isReal) continue;
      const dx = worldX - paul.x;
      const dy = worldY - paul.y;
      if (Math.sqrt(dx * dx + dy * dy) < 15) {
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
      if (worldX >= building.x && worldX <= building.x + building.w &&
          worldY >= building.y && worldY <= building.y + building.h) {
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
        const dx = worldX - paul.x;
        const dy = worldY - paul.y;
        if (Math.sqrt(dx * dx + dy * dy) < 15) {
          hoveredPaul = paul.id;
          canvas.style.cursor = 'pointer';
          break;
        }
      }
    }
    
    // Check buildings
    if (!hoveredPaul) {
      Object.entries(BUILDING_CONFIG).forEach(([id, building]) => {
        if (worldX >= building.x && worldX <= building.x + building.w &&
            worldY >= building.y && worldY <= building.y + building.h) {
          hoveredBuilding = id;
          canvas.style.cursor = 'pointer';
        }
      });
    }
    
    if (!hoveredPaul && !hoveredBuilding) {
      canvas.style.cursor = mouse.isDown ? 'grabbing' : 'grab';
    }
  }
}

function onMouseUp() {
  mouse.isDown = false;
}

function onWheel(e) {
  e.preventDefault();
  const zoomSpeed = 0.1;
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
  
  // Send to server
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'selectPaul', paulId: paul.id }));
  }
}

function selectBuilding(buildingId) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'selectBuilding', buildingId }));
  }
  addActivity(`🏢 Viewing ${BUILDING_CONFIG[buildingId].name}`);
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
  
  document.getElementById('selected-name').textContent = paul.name;
  document.getElementById('selected-role').textContent = paul.profession || 'Trader';
  document.getElementById('selected-avatar').textContent = paul.initials || 'P';
  document.getElementById('selected-avatar').style.borderColor = paul.type?.color || '#8b5cf6';
  document.getElementById('selected-avatar').style.background = (paul.type?.color || '#8b5cf6') + '30';
  
  const building = BUILDING_CONFIG[paul.building];
  document.getElementById('selected-building').textContent = building ? `📍 ${building.name}` : '📍 Wandering';
  document.getElementById('selected-activity').textContent = paul.activity || 'Idle';
  
  if (paul.stats) {
    document.getElementById('selected-roi').textContent = (paul.stats.roi > 0 ? '+' : '') + paul.stats.roi + '%';
    document.getElementById('selected-winrate').textContent = Math.round((paul.stats.wins / paul.stats.trades) * 100) + '%';
    document.getElementById('selected-level').textContent = paul.stats.level;
  }
  
  document.getElementById('selected-thought').textContent = paul.thought ? `"${paul.thought}"` : '...';
}

function updateUI() {
  // Update stats
  document.getElementById('paulCount').textContent = worldState.paulCount || 0;
  
  // Update time
  const hour = worldState.time?.hour?.toString().padStart(2, '0') || '09';
  const minute = worldState.time?.minute?.toString().padStart(2, '0') || '00';
  document.getElementById('gameTime').textContent = `${hour}:${minute}`;
  document.getElementById('gameDay').textContent = worldState.time?.day || 1;
  
  // Update needs bars (using average of real Pauls)
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
  
  // Update selected panel if Paul data changed
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
    'toggle-activity': 'activity-panel'
  };
  
  Object.entries(toggles).forEach(([btnId, panelId]) => {
    const btn = document.getElementById(btnId);
    const panel = document.getElementById(panelId);
    
    btn.addEventListener('click', () => {
      btn.classList.toggle('active');
      panel.classList.toggle('hidden');
    });
  });
}

function addActivity(text) {
  const log = document.getElementById('activity-log');
  const item = document.createElement('div');
  item.className = 'activity-item';
  item.textContent = text;
  log.insertBefore(item, log.firstChild);
  
  // Keep only last 20 items
  while (log.children.length > 20) {
    log.removeChild(log.lastChild);
  }
}

// Control functions
function zoomIn() {
  camera.targetZoom = Math.min(3, camera.targetZoom + 0.3);
}

function zoomOut() {
  camera.targetZoom = Math.max(0.5, camera.targetZoom - 0.3);
}

function resetView() {
  camera.x = canvas.width / 2 - 500;
  camera.y = canvas.height / 2 - 400;
  camera.targetZoom = 1;
}

function triggerEvent(eventType) {
  fetch('/api/events', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type: eventType, data: {} })
  });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);
