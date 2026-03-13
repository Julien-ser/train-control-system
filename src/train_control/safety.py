"""Safety monitoring and collision avoidance."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SafetyStatus:
    """Status report from safety monitor."""

    safe: bool
    emergency_brake_required: bool
    reason: str = ""
    braking_distance_required: float = 0.0
    distance_to_obstacle: float = float("inf")


class SafetyMonitor:
    """Monitors train safety and applies emergency braking when needed."""

    def __init__(self, train: "Train", track_network: "TrackNetwork"):
        self.train = train
        self.track_network = track_network
        self.emergency_brake_active = False

    def check_safety(self) -> SafetyStatus:
        """
        Perform safety check.

        Returns:
            SafetyStatus with current safety status
        """
        status = SafetyStatus(safe=True, emergency_brake_required=False)

        # 1. Check if train exceeded safe speed for current block
        current_block = self.track_network.get_block_by_position(self.train.position)
        if current_block:
            if not current_block.is_safe_for_speed(self.train.speed):
                status.emergency_brake_required = True
                status.safe = False
                status.reason = f"Speed {self.train.speed:.1f} m/s exceeds block limit {current_block.speed_limit:.1f} m/s"

        # 2. Check distance to next occupied block (collision avoidance)
        next_occupied_block, distance = self._find_next_occupied_block()
        if next_occupied_block and distance < self._get_braking_distance():
            status.emergency_brake_required = True
            status.safe = False
            status.distance_to_obstacle = distance
            status.reason = f"Obstruction {distance:.1f}m ahead, braking distance {self._get_braking_distance():.1f}m"

        status.braking_distance_required = self._get_braking_distance()

        if status.emergency_brake_required:
            self.train.apply_emergency_brake()
            self.emergency_brake_active = True

        return status

    def _find_next_occupied_block(self) -> tuple[Optional["Block"], float]:
        """Find the next occupied block ahead and distance to it."""
        # Build cumulative start positions for all blocks assuming linear order
        cumulative = 0.0
        start_positions = {}
        for block in self.track_network.blocks.values():
            start_positions[block.id] = cumulative
            cumulative += block.length

        train_pos = self.train.position
        nearest_block = None
        nearest_distance = float("inf")

        # Check all occupied blocks
        for block in self.track_network.blocks.values():
            if not block.occupied:
                continue

            start = start_positions[block.id]
            end = start + block.length

            # Calculate distance from train to this block
            if train_pos < start:
                # Block is ahead
                distance = start - train_pos
            elif start <= train_pos < end:
                # Train is inside this block (collision)
                distance = 0.0
            else:
                # Block is behind
                continue

            if distance < nearest_distance:
                nearest_distance = distance
                nearest_block = block

        return nearest_block, nearest_distance

    def _get_braking_distance(self) -> float:
        """
        Calculate braking distance from current speed.

        Returns:
            Distance in meters needed to stop
        """
        if self.train.speed <= 0:
            return 0.0
        return (self.train.speed**2) / (2 * self.train.emergency_deceleration)

    def reset_emergency(self) -> None:
        """Reset emergency brake (for testing/after stop)."""
        if self.train.speed == 0:
            self.train.release_emergency_brake()
            self.emergency_brake_active = False
