# Train Control System

A Python-based implementation demonstrating modern railway control systems including speed regulation, signal monitoring, and safety protocols.

## Mission
Research and implement sample use cases for software controls used in modern train systems, including:
- Automatic Train Protection (ATP)
- Speed enforcement
- Signal aspect monitoring
- Brake curve calculation
- Position tracking

## Features
- Track network modeling
- Train state management
- Speed profile enforcement
- Signal aspect interpretation
- Emergency braking calculation
- Movement authority management

## Installation & Setup

### Prerequisites
- Python 3.8+
- Git

### Quick Start
```bash
# Clone and navigate
cd train-control-system

# Install dependencies
pip install -r requirements.txt

# Run examples
python examples/basic_simulation.py

# Run tests
pytest tests/
```

## Project Structure
```
train-control-system/
├── src/
│   ├── train_control/
│   │   ├── __init__.py
│   │   ├── train.py          # Train state & control
│   │   ├── track.py          # Track network & blocks
│   │   ├── signals.py        # Signal aspect management
│   │   ├── speed_enforcer.py # Speed profile enforcement
│   │   └── safety.py         # Braking calculations
│   └── utils/
│       └── calculations.py   # Physics calculations
├── tests/                    # Unit & integration tests
├── examples/                 # Usage examples
├── docs/                     # Documentation
├── requirements.txt          # Python dependencies
└── TASKS.md                  # Development progress
```

## Architecture
The system is built around these core components:

1. **Track Network** - Represents rail infrastructure with blocks, gradients, and speed limits
2. **Train** - Models train dynamics (position, speed, braking capability)
3. **Signal System** - Manages signal aspects and movement authorities
4. **Speed Enforcer** - Calculates and enforces speed profiles
5. **Safety Monitor** - Emergency braking and collision avoidance

## Current Status
- ✅ Phase 1: Architecture design complete
- 🔄 Phase 2: Core implementation in progress
- ⏳ Phase 3: Testing pending
- ⏳ Phase 4: Documentation & deployment

## License
MIT
