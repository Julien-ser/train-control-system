"""Speed profile enforcement and monitoring."""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SpeedRestriction:
    """A speed limit that applies at a specific location."""

    location: float  # meters from origin
    speed_limit: float  # m/s
    reason: str = "track"

    def is_active_at(self, position: float) -> bool:
        """Check if restriction applies at given position."""
        return abs(position - self.location) < 1.0  # Within 1 meter


class SpeedProfile:
    """Combines all speed restrictions affecting a train."""

    def __init__(self):
        self.restrictions: List[SpeedRestriction] = []

    def add_restriction(self, restriction: SpeedRestriction) -> None:
        """Add a speed restriction to the profile."""
        self.restrictions.append(restriction)

    def get_max_speed_at(self, position: float, current_speed: float = 0.0) -> float:
        """
        Calculate maximum allowed speed at given position.

        Args:
            position: Current position (meters)
            current_speed: Current train speed for braking curve calc

        Returns:
            Maximum allowed speed in m/s
        """
        max_speed = float("inf")

        for restriction in self.restrictions:
            if restriction.location >= position:
                # Future restriction: calculate braking curve
                distance = restriction.location - position
                # Simple: assume instant deceleration at max decel
                # TODO: Add proper braking curve calculation
                max_speed = min(max_speed, restriction.speed_limit)
            else:
                # Past restriction (shouldn't happen if ordered correctly)
                pass

        return max_speed if max_speed != float("inf") else 60.0  # Default 135 km/h


class SpeedEnforcer:
    """Enforces speed limits and monitors compliance."""

    def __init__(self, train: "Train", speed_profile: SpeedProfile):
        self.train = train
        self.speed_profile = speed_profile
        self.warnings = []
        self.violations = []

    def check_compliance(self, position: float, speed: float) -> dict:
        """
        Check if train is complying with speed profile.

        Returns:
            Dict with compliance status and recommended action
        """
        max_allowed = self.speed_profile.get_max_speed_at(position, speed)

        if speed > max_allowed:
            return {
                "compliant": False,
                "current_speed": speed,
                "max_allowed": max_allowed,
                "excess": speed - max_allowed,
                "action": "EMERGENCY_BRAKE"
                if speed > max_allowed * 1.1
                else "SERVICE_BRAKE",
            }
        elif speed > max_allowed * 0.9:  # Within 10% of limit
            return {
                "compliant": True,
                "current_speed": speed,
                "max_allowed": max_allowed,
                "warning": "Approaching speed limit",
                "action": "PREPARE_TO_DECELERATE",
            }
        else:
            return {
                "compliant": True,
                "current_speed": speed,
                "max_allowed": max_allowed,
                "action": "CONTINUE",
            }
