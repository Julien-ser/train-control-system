"""Signal aspect and control system."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict


class SignalAspect(Enum):
    """Signal aspects (US-style color signals)."""

    RED = auto()  # Stop
    YELLOW = auto()  # Caution, prepare to stop
    GREEN = auto()  # Proceed
    FLASHING_YELLOW = auto()  # Approach at restricted speed
    FLASHING_GREEN = auto()  # Proceed with caution


@dataclass
class Signal:
    """Railway signal."""

    id: str
    aspect: SignalAspect
    location: float  # distance from network origin (meters)
    linked_block_id: str  # block this signal protects/governs

    def set_aspect(self, aspect: SignalAspect) -> None:
        """Change signal aspect."""
        self.aspect = aspect

    def get_speed_restriction(self) -> float:
        """
        Get implied speed restriction based on aspect.

        Returns:
            Maximum allowed speed in m/s (0 for stop)
        """
        restrictions = {
            SignalAspect.RED: 0.0,
            SignalAspect.YELLOW: 8.0,  # ~18 mph - prepare to stop
            SignalAspect.GREEN: 30.0,  # ~67 mph - proceed
            SignalAspect.FLASHING_YELLOW: 15.0,  # ~34 mph
            SignalAspect.FLASHING_GREEN: 25.0,  # ~56 mph
        }
        return restrictions.get(self.aspect, 0.0)


class SignalController:
    """Manages signal aspects based on track occupancy."""

    def __init__(self, signals: Dict[str, Signal]):
        self.signals = signals

    def update_signal_aspects(self, track_network: "TrackNetwork") -> None:
        """
        Update all signal aspects based on current track occupancy.

        Simple logic:
        - Signal is RED if its protected block is occupied
        - Signal is GREEN if block is clear
        - Signal is YELLOW if next block after protected block is occupied
        """
        for signal in self.signals.values():
            block = track_network.blocks.get(signal.linked_block_id)
            if not block:
                continue

            if block.occupied:
                signal.set_aspect(SignalAspect.RED)
            else:
                # Check next block for occupancy
                next_blocks = track_network.get_next_blocks(signal.linked_block_id)
                if next_blocks and next_blocks[0].occupied:
                    signal.set_aspect(SignalAspect.YELLOW)
                else:
                    signal.set_aspect(SignalAspect.GREEN)
