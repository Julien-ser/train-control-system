# Train Control System - User Guide

## Quick Start

This guide will help you get started with the Train Control System simulation.

### Prerequisites

- Python 3.8 or higher
- pytest (installed via `pip install -r requirements.txt`)

### Running the Basic Simulation

The easiest way to see the system in action is to run the provided simulation:

```bash
python examples/basic_simulation.py
```

This will:
- Create a simple 3-block track network
- Set up signals and speed restrictions
- Run a 60-second simulation
- Show train position, speed, and safety status

### Expected Output

```
============================================================
Train Control System - Basic Simulation
============================================================

[1] Creating track network...
  Created 3 blocks

[2] Creating signals...
...

[5] Starting simulation (60 seconds...
------------------------------------------------------------
Time   Pos(m)    Speed(m/s)  Signal   Safety
------------------------------------------------------------
0      0.0       0.00        GREEN    OK
5      37.2      1.86        GREEN    OK
...
!!! EMERGENCY BRAKE APPLIED at t=45s, position=2341.5m
    Reason: Speed 12.3 m/s exceeds block limit 10.0 m/s
```

## Core Concepts

### Track Blocks

A **Block** is a segment of track with defined properties:

```python
from train_control.track import Block, TrackNetwork

# Create blocks
block1 = Block(
    id="BLOCK_1",
    length=1000.0,      # meters
    speed_limit=25.0,   # m/s (~90 km/h)
    gradient=0.0        # percent (0 = flat)
)

# Build network
network = TrackNetwork()
network.add_block(block1)
network.connect_blocks("BLOCK_1", "BLOCK_2")
```

### Trains

The **Train** class models a physical train:

```python
from train_control.train import Train

train = Train(
    id="TRAIN001",
    max_speed=30.0,           # m/s
    acceleration=0.8,         # m/s²
    deceleration=0.6,         # m/s² (service brake)
    emergency_deceleration=1.0 # m/s² (emergency brake)
)
```

Control the train with:

```python
train.set_throttle(0.5)   # 50% acceleration
train.set_brake(0.3)      # 30% braking
train.update(dt=1.0)      # Advance simulation by 1 second
```

### Signals

Signals provide operational instructions:

```python
from train_control.signals import Signal, SignalAspect, SignalController

# Create a signal
signal = Signal(
    id="SIG1",
    aspect=SignalAspect.GREEN,
    location=950.0,          # meters from origin
    linked_block_id="BLOCK_1"
)

# Signal aspects and their speed restrictions:
# RED        -> 0.0 m/s (stop)
# YELLOW     -> 8.0 m/s (~30 km/h, prepare to stop)
# GREEN      -> 30.0 m/s (~108 km/h, proceed)
# FLASHING_YELLOW -> 15.0 m/s
# FLASHING_GREEN  -> 25.0 m/s

# Controller automatically updates aspects based on occupancy
controller = SignalController(network.signals)
controller.update_signal_aspects(network)
```

### Speed Enforcement

The speed enforcement system combines all speed restrictions:

```python
from train_control.speed_enforcer import SpeedProfile, SpeedEnforcer, SpeedRestriction

# Create speed profile
profile = SpeedProfile()

# Add static speed restrictions
profile.add_restriction(SpeedRestriction(
    location=2000.0,      # position where restriction applies
    speed_limit=20.0,     # m/s
    reason="track"        # reason for restriction
))

# Create enforcer
enforcer = SpeedEnforcer(train, profile)

# Check compliance
compliance = enforcer.check_compliance(
    position=train.position,
    speed=train.speed
)

# Returns:
# {
#     "compliant": True/False,
#     "current_speed": 25.0,
#     "max_allowed": 22.5,
#     "excess": 2.5,  # if non-compliant
#     "action": "PREPARE_TO_DECELERATE|SERVICE_BRAKE|EMERGENCY_BRAKE|CONTINUE"
# }
```

The speed profile automatically calculates braking curves, ensuring the train can stop before any future restriction.

### Safety Monitoring

The safety system checks for dangerous conditions:

```python
from train_control.safety import SafetyMonitor

safety = SafetyMonitor(train, network)
status = safety.check_safety()

# Returns SafetyStatus:
# - safe: True if no immediate danger
# - emergency_brake_required: True if emergency braking needed
# - reason: Human-readable explanation
# - braking_distance_required: meters needed to stop
# - distance_to_obstacle: meters to nearest obstruction
```

The safety monitor automatically applies emergency brakes when dangerous conditions are detected.

### Movement Authority

Movement authority defines how far a train may travel:

```python
from train_control.movement_authority import AuthorityManager

authority_mgr = AuthorityManager(network, network.signals)
authority = authority_mgr.update_authority(
    train_position=train.position,
    current_time=simulation_time
)

# Returns MovementAuthority:
# - end_position: maximum allowed position
# - reason: why this limit exists
# - remaining_distance(): distance remaining
```

## Building a Complete Simulation

Here's the typical structure:

```python
# 1. Setup
network = TrackNetwork()
# ... add blocks and connections
signals = {...}
signal_controller = SignalController(signals)

train = Train(...)
speed_profile = SpeedProfile()
# ... add speed restrictions
enforcer = SpeedEnforcer(train, speed_profile)
safety = SafetyMonitor(train, network)
authority_mgr = AuthorityManager(network, signals)

# 2. Simulation loop
time = 0.0
dt = 1.0  # seconds

while time < 60.0:
    # Update signals based on track occupancy
    signal_controller.update_signal_aspects(network)

    # Check speed compliance
    compliance = enforcer.check_compliance(train.position, train.speed)

    # Apply control logic based on compliance and signals
    current_block = network.get_block_by_position(train.position)
    if current_block:
        for signal in signals.values():
            if signal.linked_block_id == current_block.id:
                if signal.aspect.name in ["RED", "YELLOW"]:
                    train.set_brake(0.5)
                elif train.speed < compliance["max_allowed"] - 1.0:
                    train.set_throttle(0.3)
                else:
                    train.set_throttle(0.0)
                break

    # Check safety (automatically applies emergency brake if needed)
    safety.check_safety()

    # Update train physics
    train.update(dt)
    time += dt
```

## Advanced Features

### Custom Braking Curves

The speed profile uses the formula:

```
braking_speed = sqrt(2 * deceleration * distance_to_restriction)
```

You can customize the deceleration value used:

```python
max_speed = speed_profile.get_max_speed_at(
    position=1000.0,
    current_speed=25.0,
    deceleration=0.6  # custom service brake rate
)
```

### Gradient Effects

Blocks can have gradients (positive = uphill, negative = downhill):

```python
block = Block(
    id="HILL_1",
    length=500.0,
    speed_limit=20.0,
    gradient=2.5  # 2.5% uphill
)
```

The current model doesn't adjust speed for gradients, but you could extend the `Train.update()` method to include gravitational acceleration effects.

### Emergency Brake Release

In real systems, emergency brakes require manual reset:

```python
# Emergency brake was applied automatically
if train.emergency_brake and train.speed == 0.0:
    train.release_emergency_brake()  # Manual reset required
    safety.reset_emergency()
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_speed_enforcer.py

# Run specific test
pytest tests/test_speed_enforcer.py::TestSpeedProfile::test_braking_curve
```

## FAQ

### Q: Why is the train not stopping at red signals?
A: The simulation requires explicit control logic to respond to signals. Check your control loop is decoding signal aspects and applying brakes appropriately.

### Q: How accurate is the physics simulation?
A: The model uses simple Euler integration with constant acceleration. For more accuracy, you could integrate with smaller time steps or use RK4 integration.

### Q: Can I model multiple trains?
A: Yes! Create multiple Train objects and add them to the same TrackNetwork. Update each train in the simulation loop and mark blocks as occupied when trains enter them.

### Q: How do I add more signal aspects?
A: Extend the `SignalAspect` enum in `signals.py` and update the `get_speed_restriction()` method accordingly.

### Q: What's the difference between service brake and emergency brake?
A: Service brake is normal deceleration (deceleration parameter). Emergency brake uses emergency_deceleration which is typically higher (faster stopping). Emergency brake also triggers safety interlocks that may require manual reset.

## Troubleshooting

### Tests failing
- Ensure you're using Python 3.8+
- Install dependencies: `pip install -r requirements.txt`
- Run from project root directory

### Simulation crashes
- Check that all train positions are within track network bounds
- Verify block IDs in connections exist
- Ensure signal linked_block_id references valid blocks

### No output from simulation
- The simulation prints status every 5 seconds by default
- Check that train is moving (initial position may be 0 with no throttle)

## Next Steps

1. **Explore the example**: Read `examples/basic_simulation.py` to see a complete implementation
2. **Review architecture**: See `docs/architecture.md` for system design
3. **Read API reference**: Check docstrings in source files for detailed method signatures
4. **Extend functionality**: Add features like passenger management, fuel consumption, or advanced signaling
5. **Visualize**: Add plotting with matplotlib to show train trajectories

## Contributing

When extending the system:
- Follow existing code style (PEP 8, type hints where used)
- Write tests for new functionality
- Update documentation for any API changes
- Keep safety-critical logic simple and verifiable
