"""Tests for signal system."""

import pytest
import sys

sys.path.insert(0, "src")

from train_control.signals import Signal, SignalAspect, SignalController
from train_control.track import Block, TrackNetwork


class TestSignal:
    def test_creation(self):
        signal = Signal(
            id="SIG1",
            aspect=SignalAspect.GREEN,
            location=1000.0,
            linked_block_id="BLOCK1",
        )
        assert signal.id == "SIG1"
        assert signal.aspect == SignalAspect.GREEN
        assert signal.location == 1000.0
        assert signal.linked_block_id == "BLOCK1"

    def test_set_aspect(self):
        signal = Signal(
            id="SIG1", aspect=SignalAspect.RED, location=0.0, linked_block_id="B1"
        )
        signal.set_aspect(SignalAspect.GREEN)
        assert signal.aspect == SignalAspect.GREEN

    def test_speed_restriction_by_aspect(self):
        assert (
            Signal(
                id="S", aspect=SignalAspect.RED, location=0, linked_block_id="B"
            ).get_speed_restriction()
            == 0.0
        )
        assert Signal(
            id="S", aspect=SignalAspect.YELLOW, location=0, linked_block_id="B"
        ).get_speed_restriction() == pytest.approx(8.0)
        assert Signal(
            id="S", aspect=SignalAspect.GREEN, location=0, linked_block_id="B"
        ).get_speed_restriction() == pytest.approx(30.0)
        assert Signal(
            id="S", aspect=SignalAspect.FLASHING_YELLOW, location=0, linked_block_id="B"
        ).get_speed_restriction() == pytest.approx(15.0)
        assert Signal(
            id="S", aspect=SignalAspect.FLASHING_GREEN, location=0, linked_block_id="B"
        ).get_speed_restriction() == pytest.approx(25.0)


class TestSignalController:
    def test_signal_red_when_protected_block_occupied(self):
        network = TrackNetwork()
        block = Block(id="B1", length=1000.0, speed_limit=20.0, occupied=True)
        network.add_block(block)
        signal = Signal(
            id="SIG1", aspect=SignalAspect.GREEN, location=900.0, linked_block_id="B1"
        )
        controller = SignalController({"SIG1": signal})

        controller.update_signal_aspects(network)
        assert signal.aspect == SignalAspect.RED

    def test_signal_green_when_block_clear_and_next_clear(self):
        network = TrackNetwork()
        block1 = Block(id="B1", length=1000.0, speed_limit=20.0, occupied=False)
        block2 = Block(id="B2", length=1000.0, speed_limit=20.0, occupied=False)
        network.add_block(block1)
        network.add_block(block2)
        network.connect_blocks("B1", "B2")
        signal = Signal(
            id="SIG1", aspect=SignalAspect.RED, location=900.0, linked_block_id="B1"
        )
        network.signals["SIG1"] = signal
        controller = SignalController(network.signals)

        controller.update_signal_aspects(network)
        assert signal.aspect == SignalAspect.GREEN

    def test_signal_yellow_when_next_block_occupied(self):
        network = TrackNetwork()
        block1 = Block(id="B1", length=1000.0, speed_limit=20.0, occupied=False)
        block2 = Block(
            id="B2", length=1000.0, speed_limit=20.0, occupied=True
        )  # occupied
        network.add_block(block1)
        network.add_block(block2)
        network.connect_blocks("B1", "B2")
        signal = Signal(
            id="SIG1", aspect=SignalAspect.RED, location=900.0, linked_block_id="B1"
        )
        network.signals["SIG1"] = signal
        controller = SignalController(network.signals)

        controller.update_signal_aspects(network)
        assert signal.aspect == SignalAspect.YELLOW


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
