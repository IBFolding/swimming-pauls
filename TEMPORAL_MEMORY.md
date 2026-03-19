# Temporal Memory System for Swimming Pauls

## Overview

The Temporal Memory system allows Pauls to have **dynamic beliefs that evolve over simulation time**. Instead of static knowledge, Pauls now have beliefs with confidence levels that decay or reinforce based on new evidence.

## Key Features

### 1. Belief Formation & Storage
- Beliefs have **confidence levels** (0.0 to 1.0)
- Beliefs track **evidence history** and revision logs
- Beliefs have **status**: ACTIVE, REINFORCED, CHALLENGED, DECAYING, ABANDONED, REVISED

### 2. Evidence-Based Updates
- **Supporting evidence** increases confidence
- **Contradicting evidence** decreases confidence
- Evidence has **reliability scores** (sources weighted by trustworthiness)
- Strong contradictions can **abandon beliefs entirely**

### 3. Time-Based Decay
- Beliefs **decay over time** if not reinforced
- Configurable decay rate (default: 5% per day)
- Decay only starts after 24 hours of inactivity
- Decayed beliefs below threshold are automatically abandoned

### 4. Temporal Context in Predictions
- Predictions include **belief evolution narrative**
- Format: *"3 days ago I thought X (50% confidence), now I think Y (75% confidence)"*
- Shows belief shift direction and magnitude
- Tracks time span between belief updates

### 5. Social Influence
- Pauls can **influence each other's beliefs**
- Similar beliefs are reinforced
- Different beliefs are challenged
- Influence strength based on relationship (trust + respect)

## Files Created

### Core Module
- **`temporal_memory.py`** - Main temporal memory system
  - `TemporalMemory` - Individual Paul's belief store
  - `TemporalMemoryManager` - Coordinates all Pauls' memories
  - `Belief` - Belief data structure with temporal tracking
  - `TemporalContext` - Context for predictions with history
  - Helper functions for reasoning and simulation

### Integration
- **`temporal_integration.py`** - Integration with PaulWorld
  - `TemporalPaulState` - Wraps PaulState with temporal memory
  - `TemporalPaulWorld` - Enhanced PaulWorld with belief evolution
  - Factory functions for creating temporal worlds

### Testing & Demo
- **`test_temporal_memory.py`** - Comprehensive test suite (34 tests)
- **`temporal_demo.py`** - Interactive demonstration script

## Usage Examples

### Basic Belief Management
```python
from swimming_pauls import TemporalMemory

# Create temporal memory for a Paul
memory = TemporalMemory(paul_name="TraderPaul", db_path=None)

# Form a belief
memory.form_belief(
    topic="BTC",
    proposition="Bitcoin is bullish",
    initial_confidence=0.6
)

# Add supporting evidence
memory.add_evidence(
    topic="BTC",
    content="ETF approvals announced",
    impact=0.8,
    reliability=0.9
)

# Check updated belief
belief = memory.get_belief("BTC")
print(f"Confidence: {belief.confidence:.0%}")  # Increased!
```

### Temporal Context in Predictions
```python
# Get temporal context for a prediction
context = memory.get_temporal_context("BTC")

# Format as natural language
reasoning = context.format_temporal_reasoning()
# Output: "3 days ago I thought Bitcoin was neutral (confidence: 50%). 
#          Now I'm more convinced: Bitcoin is bullish (confidence: 75%)."
```

### Social Influence
```python
from swimming_pauls import TemporalMemoryManager

manager = TemporalMemoryManager()

# Paul1 influences Paul2
manager.spread_influence(
    source_paul="VisionaryPaul",
    target_paul="SkepticPaul",
    topic="BTC",
    influence_strength=0.5
)
```

### Integration with PaulWorld
```python
from swimming_pauls import create_temporal_world

# Create world with temporal memory
temporal_world = create_temporal_world()

# Run simulation (beliefs evolve automatically)
await temporal_world.run_simulation()

# Ask with temporal context
result = await temporal_world.ask_pauls("What about Bitcoin?")
# Responses include "3 days ago I thought..." style reasoning
```

## Belief Status Lifecycle

```
FORMED → ACTIVE → REINFORCED (with evidence)
  ↓
CHALLENGED (with contradicting evidence)
  ↓
DECAYING (over time without updates)
  ↓
ABANDONED (confidence below threshold)
  ↓
REVISED (new belief supersedes old)
```

## Configuration

```python
TemporalMemory(
    paul_name="PaulName",
    decay_rate=0.05,          # 5% per day decay
    reinforcement_rate=0.15,   # 15% confidence boost per evidence
    db_path="data/temporal.db" # Optional persistence
)
```

## Running Tests

```bash
cd swimming_pauls
python3 -m pytest test_temporal_memory.py -v
```

## Running Demo

```bash
cd swimming_pauls
python3 temporal_demo.py
```

## Database Schema

The system uses SQLite for persistence:

- `temporal_beliefs` - Stores belief states with history
- `temporal_evidence` - Tracks all evidence events
- `temporal_memory_config` - Per-Paul configuration

## Integration Points

The temporal memory system integrates with:

1. **PaulWorld** - Beliefs form from knowledge, update during simulation ticks
2. **PaulState** - Memories processed into beliefs and evidence
3. **Social Dynamics** - Relationships affect belief influence strength
4. **Predictions** - Temporal context added to prediction reasoning

## Benefits

- **Realistic belief dynamics** - Beliefs aren't static facts
- **Explainable predictions** - Pauls explain *why* they changed their minds
- **Emergent behavior** - Belief cascades and consensus formation
- **Persistent learning** - Pauls remember and evolve over time
- **Testable** - 34 comprehensive unit tests
