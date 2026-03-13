# Train Control System Architecture

## Overview
This is a simulation of modern train control systems that implement safety-critical software controls found in real-world railway operations.

## Core Components

### 1. Track Network (track.py)
- **Block**: Represents a segment of track with properties:
  - Unique identifier
  - Length
  - Speed limit
  - Gradient (for braking calculations)
  - Occupancy status
- **TrackNetwork**: Collection of blocks forming the complete track layout
  - Block adjacency relationships
  - Route definitions
  - Signal placement

### 2. Train Model (train.py)
- **Train**: Physical train model with:
  - Position (track block + offset)
  - Current speed
  - Acceleration/braking rates
  - Mass (for physics calculations)
  - Braking capability (service/emergency)
- Train movement simulation with simple physics

### 3. Signal System (signals.py)
- **Signal**: Railway signal with aspects:
  - Red/Stop
  - Yellow/Caution
  - Green/Proceed
  - Additional aspects (blinking, etc.)
- **SignalController**:
  - Interlocking logic
  - Aspect setting based on block occupancy
  - Movement authority management

### 4. Speed Enforcement (speed_enforcer.py)
- **SpeedProfile**: Dynamic speed limit based on:
  - Track speed restrictions
  - Signal aspects
  - Braking curves
  - Temporary speed restrictions
- **Enforcer**: Monitors train speed against profile:
  - Warning alerts when approaching limit
  - Automatic braking if limit exceeded
  - Predicts future speed based on braking capability

### 5. Safety Monitor (safety.py)
- **SafetySystem**: Collision avoidance & safety:
  - Braking distance calculation
  - Safe following distance
  - Emergency brake application
  - Overspeed protection
  - Signal passed at danger (SPAD) prevention

### 6. Movement Authority (in progress)
- **Authority**: Permission for train to occupy specific track sections
  - Valid distance/blocks ahead
  - Time-based or distance-based
  - Revocation handling

## Data Flow
1. Track network defines physical constraints
2. Signals provide operational constraints
3. Speed enforcer combines constraints into speed profile
4. Safety monitor ensures train stays within safe limits
5. Train model updates position based on control inputs
6. Loop repeats at configurable intervals (e.g., 100ms)

## Control Algorithms

### Braking Curve Calculation
```
braking_distance = (v^2) / (2 * a)
```
Where:
- v = current speed (m/s)
- a = deceleration (m/s²)

### Safe Following Distance
```
safe_distance = braking_distance_train + safety_margin
```

### Speed Profile Enforcement
- Current speed ≤ Track speed limit
- Current speed ≤ Signal-implied speed (e.g., yellow means prepare to stop)
- Current speed ≤ braking curve to next restrictive signal

## Sample Use Case: Automatic Train Protection (ATP)

Train approaches a yellow signal indicating next block is occupied:
1. Signal aspect = Yellow
2. Speed enforcer calculates braking curve to stop before occupied block
3. Speed profile shows decreasing speed limits ahead
4. Train begins deceleration to meet profile
5. If train fails to decelerate, safety monitor applies emergency brake
6. Train stops safely before occupied block
7. Signal changes to red (stop) while train is stationary

## Technology Choices
- **Language**: Python 3.8+
- **Testing**: pytest
- **No external dependencies** (uses only standard library) - keeps simple and portable
- Can later add: numpy for physics, matplotlib for visualization

## Safety Considerations (Future)
- Formal verification of safety logic
- Redundant systems (2-out-of-3 voting)
- Watchdog timers
- Secure communication protocols