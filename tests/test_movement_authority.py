"""Tests for movement authority system."""

import pytest
import sys

sys.path.insert(0, "src")

from train_control.movement_authority import MovementAuthority, AuthorityManager
from train_control.track import Block, TrackNetwork
from train_control.signals import Signal, SignalAspect, SignalController


class TestMovementAuthority:
    def test_creation(self):
        auth = MovementAuthority(end_position=5000.0, reason="test", issued_at=10.0)
        assert auth.end_position == 5000.0
        assert auth.reason == "test"
        assert auth.issued_at == 10.0

    def test_is_valid_at(self):
        auth = MovementAuthority(end_position=1000.0)
        assert auth.is_valid_at(500.0) == True
        assert auth.is_valid_at(1000.0) == True
        assert auth.is_valid_at(1000.1) == False

    def test_remaining_distance(self):
        auth = MovementAuthority(end_position=1000.0)
        assert auth.remaining_distance(500.0) == pytest.approx(500.0)
        assert auth.remaining_distance(1200.0) == pytest.approx(0.0)  # beyond end


class TestAuthorityManager:
    def setup_method(self):
        # Create simple track with 3 blocks of 1000m each
        self.network = TrackNetwork()
        self.block1 = Block(id="B1", length=1000.0, speed_limit=25.0)
        self.block2 = Block(id="B2", length=1000.0, speed_limit=20.0)
        self.block3 = Block(id="B3", length=1000.0, speed_limit=15.0)
        self.network.add_block(self.block1)
        self.network.add_block(self.block2)
        self.network.add_block(self.block3)

        # Signals at 950m (for B1) and 1950m (for B2)
        self.signal1 = Signal(
            id="SIG1", aspect=SignalAspect.GREEN, location=950.0, linked_block_id="B1"
        )
        self.signal2 = Signal(
            id="SIG2", aspect=SignalAspect.GREEN, location=1950.0, linked_block_id="B2"
        )
        self.signals = {"SIG1": self.signal1, "SIG2": self.signal2}
        self.signal_controller = SignalController(self.signals)

        self.manager = AuthorityManager(self.network, self.signals)

    def test_authority_extends_to_next_signal_when_green(self):
        # Position 0, next signal is SIG1 at 950m (GREEN). Then following signal is SIG2 at 1950m.
        auth = self.manager.update_authority(0.0, 0.0)
        # Should allow to before SIG2 (i.e., 1950 - 10 = 1940)
        assert auth.end_position == pytest.approx(1940.0)
        assert "Proceed to signal SIG2" in auth.reason

    def test_authority_limited_before_red_signal(self):
        # Set SIG1 to RED
        self.signal1.set_aspect(SignalAspect.RED)
        auth = self.manager.update_authority(0.0, 0.0)
        # Authority should end before SIG1: 950 - 10 = 940
        assert auth.end_position == pytest.approx(940.0)
        assert "Stop before signal SIG1" in auth.reason

    def test_authority_limited_before_yellow_signal(self):
        self.signal1.set_aspect(SignalAspect.YELLOW)
        auth = self.manager.update_authority(0.0, 0.0)
        assert auth.end_position == pytest.approx(940.0)
        assert "Stop before signal SIG1" in auth.reason

    def test_no_signal_ahead_uses_network_end(self):
        # Position beyond last signal, e.g., 3000m (past SIG2 at 1950)
        auth = self.manager.update_authority(3000.0, 0.0)
        # Network end = sum lengths = 3000m
        assert auth.end_position == pytest.approx(3000.0)
        assert "End of track" in auth.reason

    def test_authority_updates_over_time(self):
        auth1 = self.manager.update_authority(0.0, 0.0)
        auth2 = self.manager.update_authority(0.0, 10.0)
        assert auth1.issued_at == 0.0
        assert auth2.issued_at == 10.0
        assert self.manager.current_authority == auth2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
