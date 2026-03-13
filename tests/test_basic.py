"""Initial tests for train control system."""

import pytest
import sys

sys.path.insert(0, "src")

from train_control.train import Train
from train_control.track import Block, TrackNetwork
from utils.calculations import calculate_braking_distance, mph_to_mps


class TestBrakingCalculations:
    """Test physics calculations."""

    def test_braking_distance(self):
        """Test basic braking distance calculation."""
        # v^2/(2*a): 27 m/s (~60 mph) with deceleration 1 m/s^2
        distance = calculate_braking_distance(27.0, 1.0)
        assert distance == pytest.approx(364.5)

    def test_braking_distance_zero_speed(self):
        """Test braking distance at zero speed."""
        distance = calculate_braking_distance(0.0, 1.0)
        assert distance == 0.0

    def test_braking_distance_infinite_on_zero_decel(self):
        """Test braking distance with zero deceleration."""
        distance = calculate_braking_distance(10.0, 0.0)
        assert distance == float("inf")


class TestTrain:
    """Test train model."""

    def test_train_creation(self):
        """Test basic train creation."""
        train = Train(
            id="TRAIN001",
            max_speed=30.0,
            acceleration=0.5,
            deceleration=0.8,
            emergency_deceleration=1.2,
        )
        assert train.id == "TRAIN001"
        assert train.max_speed == 30.0
        assert train.speed == 0.0

    def test_train_acceleration(self):
        """Test train acceleration."""
        train = Train(
            id="TRAIN001",
            max_speed=30.0,
            acceleration=1.0,
            deceleration=0.8,
            emergency_deceleration=1.2,
        )
        train.set_throttle(1.0)
        train.update(dt=1.0)
        assert train.speed == pytest.approx(1.0)

    def test_train_max_speed_limit(self):
        """Test that train cannot exceed max speed."""
        train = Train(
            id="TRAIN001",
            max_speed=20.0,
            acceleration=10.0,
            deceleration=1.0,
            emergency_deceleration=1.2,
        )
        train.set_throttle(1.0)
        for _ in range(10):
            train.update(dt=1.0)
        assert train.speed <= 20.0

    def test_emergency_brake(self):
        """Test emergency brake application."""
        train = Train(
            id="TRAIN001",
            max_speed=30.0,
            acceleration=1.0,
            deceleration=0.8,
            emergency_deceleration=1.2,
        )
        train.speed = 20.0
        train.apply_emergency_brake()
        assert train.emergency_brake == True

        # Should decelerate at emergency rate
        train.update(dt=1.0)
        assert train.speed == pytest.approx(20.0 - 1.2)


class TestTrack:
    """Test track network."""

    def test_block_creation(self):
        """Test block creation."""
        block = Block(
            id="BLOCK1",
            length=1000.0,
            speed_limit=27.0,  # ~60 mph
        )
        assert block.length == 1000.0
        assert block.speed_limit == 27.0
        assert block.occupied == False

    def test_block_speed_check(self):
        """Test block speed safety check."""
        block = Block(id="BLOCK1", length=1000.0, speed_limit=20.0)
        assert block.is_safe_for_speed(19.0) == True
        assert block.is_safe_for_speed(20.0, margin=0.0) == True
        assert block.is_safe_for_speed(21.0) == False

    def test_track_network(self):
        """Test track network creation and connections."""
        network = TrackNetwork()
        block1 = Block(id="A", length=1000.0, speed_limit=25.0)
        block2 = Block(id="B", length=1500.0, speed_limit=20.0)
        network.add_block(block1)
        network.add_block(block2)
        network.connect_blocks("A", "B")

        next_blocks = network.get_next_blocks("A")
        assert len(next_blocks) == 1
        assert next_blocks[0].id == "B"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
