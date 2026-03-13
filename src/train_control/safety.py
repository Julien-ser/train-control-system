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
        # Simple implementation: scan forward from current position
        cumulative_distance = 0.0
        current_pos = self.train.position

        # Start from current block
        block = self.track_network.get_block_by_position(current_pos)
        if not block:
            return None, float("inf")

        # Check blocks in order until we find occupied or reach end
        checked_blocks = set()
        blocks_to_check = [block.id]

        while blocks_to_check:
            block_id = blocks_to_check.pop(0)
            if block_id in checked_blocks:
                continue
            checked_blocks.add(block_id)

            current_block = self.track_network.blocks.get(block_id)
            if not current_block:
                continue

            if current_block.id != block.id and current_block.occupied:
                # Found occupied block, calculate distance
                distance = (
                    current_block.id
                )  # simplified - would need proper calculation
                # For now, return a simple estimate
                return current_block, 100.0  # placeholder

            # Add connected blocks
            for next_id in self.track_network.connections.get(block_id, []):
                if next_id not in checked_blocks:
                    blocks_to_check.append(next_id)

        return None, float("inf")

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
