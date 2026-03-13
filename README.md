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
- Track network modeling (directed graph of blocks)
- Train dynamics simulation (acceleration, braking, Euler integration)
- Signal system with US-style aspects (RED, YELLOW, GREEN, flashing variants)
- Speed enforcement with braking curve calculations
- Safety monitoring (collision avoidance, SPAD prevention)
- Movement authority management
- Physics utilities (braking distance, unit conversions)

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
│   │   ├── train.py                # Train state & control
│   │   ├── track.py                # Track network & blocks
│   │   ├── signals.py              # Signal aspect management
│   │   ├── movement_authority.py   # Movement authority management
│   │   ├── speed_enforcer.py       # Speed profile enforcement
│   │   └── safety.py               # Safety monitoring & braking
│   └── utils/
│       └── calculations.py         # Physics calculations
├── tests/                          # Unit & integration tests
├── examples/                       # Usage examples
├── docs/                           # Documentation
│   ├── architecture.md
│   ├── API_REFERENCE.md
│   └── USER_GUIDE.md
├── logs/                           # Development logs
├── requirements.txt                # Python dependencies
├── setup.py
├── README.md
├── TASKS.md
├── TASKS_original.md
├── LICENSE
├── CONTRIBUTING.md
└── CHANGELOG.md
```

## Architecture
The system is built around these core components:

1. **Track Network** - Represents rail infrastructure with blocks, gradients, and speed limits
2. **Train** - Models train dynamics (position, speed, braking capability)
3. **Signal System** - Manages signal aspects and movement authorities
4. **Speed Enforcer** - Calculates and enforces speed profiles
5. **Safety Monitor** - Emergency braking and collision avoidance
6. **Movement Authority** - Defines permissible travel limits

## Current Status
- ✅ Phase 1: Architecture design complete
- ✅ Phase 2: Core implementation complete
  - Track network modeling
  - Train state management
  - Speed profile enforcement with braking curves
  - Signal aspect interpretation
  - Emergency braking and collision avoidance
  - Movement Authority management
- ✅ Phase 3: Testing complete
  - 54 unit and integration tests passing
  - Full coverage of core components
- ✅ Phase 4: Documentation complete
  - User guide, API reference, architecture docs
  - Contributing guidelines and changelog added
- ⏳ Deployment pending

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing
Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Changelog
See [CHANGELOG.md](CHANGELOG.md) for version history.
