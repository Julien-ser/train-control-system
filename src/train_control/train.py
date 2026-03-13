"""Train representation and control."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Train:
    """Represents a train with physical properties and state."""

    id: str
    max_speed: float  # m/s
    acceleration: float  # m/s²
    deceleration: float  # m/s² (service brake)
    emergency_deceleration: float  # m/s² (emergency brake)
    mass: float = 10000.0  # kg (default mass for a typical train)
    length: float = 20.0  # meters

    # Current state
    position: float = 0.0  # meters from network origin
    speed: float = 0.0  # m/s
    current_block_id: Optional[str] = None

    # Control inputs
    commanded_acceleration: float = 0.0
    commanded_brake: float = 0.0  # 0-1 (brake effort fraction)
    emergency_brake: bool = False

    def update(self, dt: float) -> None:
        """
        Update train state using simple physics.

        Args:
            dt: Time step in seconds
        """
        if self.emergency_brake:
            acceleration = -self.emergency_deceleration
        elif self.commanded_brake > 0:
            acceleration = -self.deceleration * self.commanded_brake
        else:
            acceleration = self.commanded_acceleration

        # Limit acceleration to train capabilities
        if acceleration > self.acceleration:
            acceleration = self.acceleration

        # Update speed and position (simple Euler integration)
        self.speed += acceleration * dt
        if self.speed < 0:
            self.speed = 0.0

        if self.speed > self.max_speed:
            self.speed = self.max_speed

        self.position += self.speed * dt

    def apply_emergency_brake(self) -> None:
        """Apply maximum emergency braking."""
        self.emergency_brake = True
        self.commanded_acceleration = 0.0
        self.commanded_brake = 0.0

    def release_emergency_brake(self) -> None:
        """Release emergency brake (requires manual reset in real systems)."""
        self.emergency_brake = False

    def set_throttle(self, throttle: float) -> None:
        """
        Set throttle level (0-1 acceleration fraction).

        Args:
            throttle: Fraction of max acceleration (0.0 to 1.0)
        """
        self.commanded_acceleration = self.acceleration * max(0.0, min(1.0, throttle))
        self.commanded_brake = 0.0

    def set_brake(self, brake: float) -> None:
        """
        Set service brake level.

        Args:
            brake: Fraction of max deceleration (0.0 to 1.0)
        """
        self.commanded_brake = max(0.0, min(1.0, brake))
        self.commanded_acceleration = 0.0
