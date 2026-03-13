"""Movement Authority management for train control."""

from dataclasses import dataclass
from typing import Optional, Dict, List


@dataclass
class MovementAuthority:
    """Defines the limits within which a train may move."""

    end_position: float  # Maximum position (meters) train can reach
    reason: str = "normal operation"
    issued_at: float = 0.0  # Simulation time when issued

    def is_valid_at(self, position: float) -> bool:
        """Check if given position is within authority."""
        return position <= self.end_position

    def remaining_distance(self, current_position: float) -> float:
        """Return distance remaining before authority expires."""
        return max(0.0, self.end_position - current_position)


class AuthorityManager:
    """Manages movement authorities for trains."""

    def __init__(self, track_network: "TrackNetwork", signals: Dict[str, "Signal"]):
        self.track_network = track_network
        self.signals = signals
        self.current_authority: Optional[MovementAuthority] = None

    def update_authority(
        self, train_position: float, current_time: float
    ) -> MovementAuthority:
        """
        Compute and update movement authority based on current conditions.

        Args:
            train_position: Current train position
            current_time: Current simulation time

        Returns:
            Updated MovementAuthority
        """
        # Find the next signal ahead
        next_signal = self._find_next_signal_ahead(train_position)

        if next_signal:
            # Determine authority end based on signal aspect
            if next_signal.aspect.name in ["RED", "YELLOW"]:
                # Authority ends before the signal
                end_pos = next_signal.location - 10.0  # Stop 10m before signal
                reason = (
                    f"Stop before signal {next_signal.id} ({next_signal.aspect.name})"
                )
            else:
                # GREEN or FLASHING_GREEN: proceed to next signal
                following_signal = self._find_signal_after(next_signal)
                if following_signal:
                    end_pos = following_signal.location - 10.0
                    reason = f"Proceed to signal {following_signal.id}"
                else:
                    # End of network
                    end_pos = self._get_network_end()
                    reason = "End of track"
        else:
            # No signals ahead; use track end
            end_pos = self._get_network_end()
            reason = "End of track"

        self.current_authority = MovementAuthority(
            end_position=end_pos, reason=reason, issued_at=current_time
        )
        return self.current_authority

    def _find_next_signal_ahead(self, position: float) -> Optional["Signal"]:
        """Find the next signal ahead of given position."""
        ahead_signals = [s for s in self.signals.values() if s.location > position]
        if ahead_signals:
            return min(ahead_signals, key=lambda s: s.location)
        return None

    def _find_signal_after(self, signal: "Signal") -> Optional["Signal"]:
        """Find the next signal after the given signal along the track."""
        ahead_signals = [
            s for s in self.signals.values() if s.location > signal.location
        ]
        if ahead_signals:
            return min(ahead_signals, key=lambda s: s.location)
        return None

    def _get_network_end(self) -> float:
        """Get the total length of the track network."""
        total = sum(block.length for block in self.track_network.blocks.values())
        return total
