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
├── scripts/                        # Deployment & health check scripts
│   └── healthcheck.py
├── requirements.txt                # Python dependencies
├── setup.py
├── Makefile                        # Deployment shortcuts
├── Dockerfile                      # Container image definition
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
- ✅ Deployment prepared
  - Dockerfile and Makefile created
  - Health check validation script available
- ⏳ Deployment validation pending (run `make docker-build` to build and test)

## Deployment

The Train Control System can be deployed using Docker or directly with Python.

### Docker Deployment (Recommended)

```bash
# Build the Docker image
make docker-build
# or: docker build -t train-control-system:latest .

# Run the basic simulation
make docker-run
# or: docker run --rm train-control-system:latest

# Run tests in Docker
make docker-test
# or: docker run --rm train-control-system:latest pytest tests/ -v

# Get an interactive shell in the container
make docker-shell
# or: docker run -it --rm train-control-system:latest /bin/bash
```

### Local Deployment (without Docker)

```bash
# Install package in development mode
pip install -e .

# Run the basic simulation
python examples/basic_simulation.py

# Run tests
pytest tests/ -v

# Or use Make shortcuts
make run
make test
```

### Make Commands

The project includes a Makefile with convenience commands:

```bash
make help          # Show all available commands
make build         # Install package locally
make run           # Run basic simulation
make test          # Run test suite
make clean         # Clean build artifacts
make docker-build  # Build Docker image
make docker-run    # Run in Docker
make docker-test   # Run tests in Docker
make validate      # Validate deployment readiness
```

### Health Checks

The system includes health check validation:

```bash
# Using Make
make validate

# Using Python directly
python scripts/healthcheck.py
```

The Docker image includes automatic health checks that verify:
- All core modules import correctly
- Test suite passes
- Example files are present

### Production Deployment

For production environments:

1. Build and push to your container registry:
```bash
docker build -t <registry>/train-control-system:latest .
docker push <registry>/train-control-system:latest
```

2. Deploy using your orchestration platform (Kubernetes, Docker Swarm, etc.) with the image.

3. Ensure the container runs with appropriate resource limits and health checks enabled.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing
Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Changelog
See [CHANGELOG.md](CHANGELOG.md) for version history.
