# API Reference

## train_control.train

### class Train

Represents a train with physical properties and state.

**Parameters:**
- `id` (str): Unique identifier
- `max_speed` (float): Maximum speed in m/s
- `acceleration` (float): Maximum acceleration in m/s²
- `deceleration` (float): Service braking deceleration in m/s²
- `emergency_deceleration` (float): Emergency braking deceleration in m/s²
- `mass` (float, optional): Train mass in kg. Default: 10000.0
- `length` (float, optional): Train length in meters. Default: 20.0

**Attributes:**
- `position` (float): Current position from network origin in meters
- `speed` (float): Current speed in m/s
- `current_block_id` (str, optional): ID of current track block
- `commanded_acceleration` (float): Current acceleration command
- `commanded_brake` (float): Current brake command (0-1)
- `emergency_brake` (bool): Whether emergency brake is active

**Methods:**

#### `update(dt: float) -> None`

Update train state using simple physics for time step `dt` seconds.

#### `apply_emergency_brake() -> None`

Apply maximum emergency braking. Sets `emergency_brake=True` and clears throttle/brake commands.

#### `release_emergency_brake() -> None`

Release emergency brake. In real systems this typically requires manual reset.

#### `set_throttle(throttle: float) -> None`

Set throttle level (fraction of max acceleration).

- `throttle`: Value between 0.0 and 1.0

#### `set_brake(brake: float) -> None`

Set service brake level (fraction of max deceleration).

- `brake`: Value between 0.0 and 1.0

---

## train_control.track

### class Block

Represents a segment of track (block section).

**Parameters:**
- `id` (str): Unique identifier
- `length` (float): Length in meters
- `speed_limit` (float): Maximum allowed speed in m/s
- `gradient` (float, optional): Gradient as percentage. Default: 0.0
- `occupied` (bool, optional): Whether block is occupied. Default: False
- `signal_id` (str, optional): ID of associated signal. Default: None

**Methods:**

#### `is_safe_for_speed(speed: float, margin: float = 1.0) -> bool`

Check if given speed is safe for this block (allows margin).

- `speed`: Speed to check in m/s
- `margin`: Safety margin in m/s to subtract from limit. Default: 1.0

Returns: `True` if `speed <= (speed_limit - margin)`

### class TrackNetwork

Represents the complete track layout as a directed graph of blocks.

**Attributes:**
- `blocks` (Dict[str, Block]): Dictionary of blocks by ID
- `connections` (Dict[str, List[str]]): Directed adjacency list mapping block ID to list of connected block IDs
- `signals` (Dict[str, Signal]): Dictionary of signals on the network

**Methods:**

#### `add_block(block: Block) -> None`

Add a block to the network.

#### `connect_blocks(from_id: str, to_id: str) -> None`

Create a directed connection from `from_id` to `to_id`.

#### `get_next_blocks(block_id: str) -> List[Block]`

Get all blocks reachable from given block ID.

#### `get_block_by_position(position: float) -> Optional[Block]`

Find the block containing the given distance from network origin. Returns `None` if position is beyond all blocks.

---

## train_control.signals

### class SignalAspect (Enum)

Signal aspects (US-style color signals):
- `RED`: Stop (0 m/s)
- `YELLOW`: Caution, prepare to stop (~30 km/h)
- `GREEN`: Proceed (~108 km/h)
- `FLASHING_YELLOW`: Approach at restricted speed (~54 km/h)
- `FLASHING_GREEN`: Proceed with caution (~90 km/h)

### class Signal

Represents a railway signal.

**Parameters:**
- `id` (str): Unique identifier
- `aspect` (SignalAspect): Current signal aspect
- `location` (float): Distance from network origin in meters
- `linked_block_id` (str): ID of the block this signal protects/governs

**Methods:**

#### `set_aspect(aspect: SignalAspect) -> None`

Change signal aspect.

#### `get_speed_restriction() -> float`

Returns the implied speed restriction in m/s based on current aspect.

### class SignalController

Manages signal aspects based on track occupancy.

**Parameters:**
- `signals` (Dict[str, Signal]): Dictionary of signals to control

**Methods:**

#### `update_signal_aspects(track_network: TrackNetwork) -> None`

Update all signal aspects based on current track occupancy:
- RED if protected block is occupied
- YELLOW if next block after protected block is occupied
- GREEN otherwise

---

## train_control.speed_enforcer

### class SpeedRestriction

A speed limit that applies at a specific location.

**Parameters:**
- `location` (float): Position in meters from origin where restriction applies
- `speed_limit` (float): Maximum allowed speed in m/s
- `reason` (str, optional): Reason for restriction. Default: "track"

**Methods:**

#### `is_active_at(position: float) -> bool`

Check if restriction applies at given position (within 1 meter).

### class SpeedProfile

Combines all speed restrictions affecting a train.

**Attributes:**
- `restrictions` (List[SpeedRestriction]): List of all restrictions

**Methods:**

#### `add_restriction(restriction: SpeedRestriction) -> None`

Add a speed restriction to the profile.

#### `get_max_speed_at(position: float, current_speed: float = 0.0, deceleration: float = 0.6) -> float`

Calculate maximum allowed speed at `position` using braking curves.

- `position`: Current position in meters
- `current_speed`: Current train speed in m/s (for braking curve)
- `deceleration`: Service braking deceleration in m/s²

Returns: Maximum allowed speed in m/s considering all future restrictions. If no restrictions, returns 30.0 m/s (108 km/h).

**Algorithm:**
For each future restriction, calculate:
- Distance to restriction: `d = restriction.location - position`
- Braking speed: `v_brake = sqrt(2 * deceleration * d)`
- Restriction max: `min(restriction.speed_limit, v_brake)`
- Overall max: minimum of all restriction max values

### class SpeedEnforcer

Enforces speed limits and monitors compliance.

**Parameters:**
- `train` (Train): The train being monitored
- `speed_profile` (SpeedProfile): Speed profile to enforce

**Attributes:**
- `warnings` (list): History of warnings
- `violations` (list): History of violations

**Methods:**

#### `check_compliance(position: float, speed: float) -> dict`

Check if `speed` at `position` complies with speed profile.

Returns: Dictionary with keys:
- `compliant` (bool): True if speed is within limits
- `current_speed` (float): Current speed
- `max_allowed` (float): Maximum allowed speed
- `excess` (float): Speed excess (if non-compliant)
- `action` (str): Recommended action:
  - `EMERGENCY_BRAKE` if speed > 110% of limit
  - `SERVICE_BRAKE` if speed exceeds limit
  - `PREPARE_TO_DECELERATE` if within 10% of limit
  - `CONTINUE` if well under limit

---

## train_control.safety

### class SafetyStatus

Status report from safety monitor.

**Attributes:**
- `safe` (bool): True if no immediate danger
- `emergency_brake_required` (bool): True if emergency braking needed
- `reason` (str): Human-readable explanation of why unsafe
- `braking_distance_required` (float): Distance in meters needed to stop from current speed
- `distance_to_obstacle` (float): Distance to nearest obstruction in meters

### class SafetyMonitor

Monitors train safety and applies emergency braking when needed.

**Parameters:**
- `train` (Train): The train being monitored
- `track_network` (TrackNetwork): The track network

**Attributes:**
- `emergency_brake_active` (bool): Whether emergency brake is currently active

**Methods:**

#### `check_safety() -> SafetyStatus`

Perform comprehensive safety check:

1. Verify current speed is safe for current block
2. Check distance to next occupied block vs braking capability

If dangerous condition found:
- Sets `emergency_brake_required=True` in status
- Automatically applies train emergency brake
- Sets `emergency_brake_active=True`

Returns: `SafetyStatus` object with complete status information.

#### `_find_next_occupied_block() -> tuple[Optional[Block], float]`

Find the next occupied block ahead and distance to it.
Returns: (block, distance) or (None, inf) if none found.

#### `_get_braking_distance() -> float`

Calculate braking distance from current speed using: `v² / (2 * emergency_deceleration)`

#### `reset_emergency() -> None`

Reset emergency brake (call after train has stopped).

---

## train_control.movement_authority

### class MovementAuthority

Defines the limits within which a train may move.

**Parameters:**
- `end_position` (float): Maximum position in meters train can reach
- `reason` (str): Reason for this authority limit
- `issued_at` (float): Simulation time when authority was issued

**Methods:**

#### `is_valid_at(position: float) -> bool`

Check if given position is within authority limits.

#### `remaining_distance(current_position: float) -> float`

Return distance remaining before authority expires (0 if already at or past limit).

### class AuthorityManager

Manages movement authorities for trains.

**Parameters:**
- `track_network` (TrackNetwork): The track network
- `signals` (Dict[str, Signal]): Dictionary of signals

**Attributes:**
- `current_authority` (MovementAuthority, optional): Current active authority

**Methods:**

#### `update_authority(train_position: float, current_time: float) -> MovementAuthority`

Compute and update movement authority based on current conditions.

- Finds next signal ahead
- If signal is RED or YELLOW: authority ends 10m before signal
- If signal is GREEN/FLASHING_GREEN: authority extends to next signal
- If no signals: authority extends to network end

Returns: Updated `MovementAuthority` object.

#### `_find_next_signal_ahead(position: float) -> Optional[Signal]`

Find the next signal ahead of given position.

#### `_find_signal_after(signal: Signal) -> Optional[Signal]`

Find the next signal after the given signal along the track.

#### `_get_network_end() -> float`

Get the total length of the track network.

---

## utils.calculations

### Utility Functions

#### `calculate_braking_distance(speed_mps: float, deceleration_mps2: float) -> float`

Calculate braking distance using `v²/(2a)` formula.

Returns: Distance in meters, or `float('inf')` if deceleration ≤ 0.

#### `mph_to_mps(mph: float) -> float`

Convert miles per hour to meters per second.

#### `mps_to_mph(mps: float) -> float`

Convert meters per second to miles per hour.

#### `kmh_to_mps(kmh: float) -> float`

Convert kilometers per hour to meters per second.

#### `mps_to_kmh(mps: float) -> float`

Convert meters per second to kilometers per hour.
