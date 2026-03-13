"""Track network representation for train control system."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Block:
    """Represents a segment of track (block section)."""

    id: str
    length: float  # meters
    speed_limit: float  # m/s
    gradient: float = 0.0  # percent (positive = uphill)
    occupied: bool = False
    signal_id: Optional[str] = None

    def is_safe_for_speed(self, speed: float, margin: float = 1.0) -> bool:
        """Check if given speed is safe for this block."""
        return speed <= (self.speed_limit - margin)


class TrackNetwork:
    """Represents the complete track layout."""

    def __init__(self):
        self.blocks: Dict[str, Block] = {}
        self.connections: Dict[str, List[str]] = {}
        self.signals: Dict[str, "Signal"] = {}

    def add_block(self, block: Block) -> None:
        """Add a block to the network."""
        self.blocks[block.id] = block

    def connect_blocks(self, from_id: str, to_id: str) -> None:
        """Create a directed connection between blocks."""
        if from_id not in self.connections:
            self.connections[from_id] = []
        self.connections[from_id].append(to_id)

    def get_next_blocks(self, block_id: str) -> List[Block]:
        """Get all blocks reachable from given block."""
        return [self.blocks[b] for b in self.connections.get(block_id, [])]

    def get_block_by_position(self, position: float) -> Optional[Block]:
        """Find block containing given distance from origin."""
        cumulative = 0.0
        for block in self.blocks.values():
            if cumulative <= position < cumulative + block.length:
                return block
            cumulative += block.length
        return None
