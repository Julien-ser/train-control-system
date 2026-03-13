"""Tests for safety monitoring system."""

import pytest
import sys

sys.path.insert(0, "src")

from train_control.safety import SafetyMonitor, SafetyStatus
from train_control.train import Train
from train_control.track import Block, TrackNetwork


class TestSafetyStatus:
    def test_creation(self):
        status = SafetyStatus(safe=True, emergency_brake_required=False)
        assert status.safe == True
        assert status.emergency_brake_required == False

    def test_unsafe_status(self):
        status = SafetyStatus(
            safe=False,
            emergency_brake_required=True,
            reason="Overspeed",
            braking_distance_required=100.0,
            distance_to_obstacle=50.0,
        )
        assert status.safe == False
        assert status.emergency_brake_required == True
        assert status.reason == "Overspeed"
        assert status.braking_distance_required == 100.0
        assert status.distance_to_obstacle == 50.0


class TestSafetyMonitor:
    def setup_method(self):
        # Create a simple track: 3 blocks, each 1000m
        self.network = TrackNetwork()
        self.block1 = Block(id="B1", length=1000.0, speed_limit=20.0)
        self.block2 = Block(id="B2", length=1000.0, speed_limit=20.0)
        self.block3 = Block(id="B3", length=1000.0, speed_limit=20.0)
        self.network.add_block(self.block1)
        self.network.add_block(self.block2)
        self.network.add_block(self.block3)
        self.network.connect_blocks("B1", "B2")
        self.network.connect_blocks("B2", "B3")

        self.train = Train(
            id="TRAIN001",
            max_speed=30.0,
            acceleration=1.0,
            deceleration=0.6,
            emergency_deceleration=1.2,
        )
        self.monitor = SafetyMonitor(self.train, self.network)

    def test_safe_when_speed_within_block_limit(self):
        self.train.position = 500.0  # in block1
        self.train.speed = 15.0  # below block1 limit 20
        status = self.monitor.check_safety()
        assert status.safe == True
        assert not status.emergency_brake_required

    def test_emergency_brake_when_speed_exceeds_block_limit(self):
        self.train.position = 500.0  # in block1, limit 20
        self.train.speed = 25.0  # exceeds limit
        status = self.monitor.check_safety()
        assert status.safe == False
        assert status.emergency_brake_required == True
        assert "exceeds block limit" in status.reason
        assert self.train.emergency_brake == True

    def test_emergency_brake_when_obstruction_ahead_within_braking_distance(self):
        # Use speed safely within block limit to isolate obstruction test
        self.train.position = 500.0  # block1
        self.train.speed = 10.0  # well below block1 limit 20
        # Mark block2 as occupied (obstruction ahead)
        self.block2.occupied = True
        # Braking distance from 10 m/s with emergency decel 1.2: d = 100/2.4 = 41.67 m
        # Distance from train at 500 to block2 start: 1000 - 500 = 500 m, > 41.67, so safe
        status = self.monitor.check_safety()
        assert status.safe == True  # obstruction far enough

        # Move train closer: position 950m (near end of block1)
        self.train.position = 950.0
        self.train.speed = 10.0
        # Distance to block2 start = 50m, braking distance 41.67m -> 50 > 41.67 still >? Actually 50 > 41.67 so safe? To be unsafe, need distance < braking_distance. Let's move to 990m: distance = 10m.
        self.train.position = 990.0
        status = self.monitor.check_safety()
        # 10m < 41.67m, so unsafe
        assert status.safe == False
        assert status.emergency_brake_required == True
        assert "Obstruction" in status.reason

    def test_find_next_occupied_block_calculates_distance(self):
        self.block2.occupied = True
        self.block3.occupied = False
        self.train.position = 0.0  # start of block1
        block, distance = self.monitor._find_next_occupied_block()
        # block2 starts at 1000m (since block1 is 1000m)
        assert block == self.block2
        assert distance == pytest.approx(1000.0)

        # Train at 500m, distance to block2 start = 500m
        self.train.position = 500.0
        block, distance = self.monitor._find_next_occupied_block()
        assert distance == pytest.approx(500.0)

        # Train at 1200m (in block2), block2 occupied -> distance 0 (inside occupied block)
        self.train.position = 1200.0
        block, distance = self.monitor._find_next_occupied_block()
        assert distance == 0.0

    def test_braking_distance_calculation(self):
        self.train.speed = 20.0
        bd = self.monitor._get_braking_distance()
        expected = (20.0**2) / (2 * self.train.emergency_deceleration)
        assert bd == pytest.approx(expected)

    def test_reset_emergency_brake_when_stopped(self):
        self.train.speed = 20.0
        self.train.apply_emergency_brake()
        assert self.train.emergency_brake == True
        self.monitor.reset_emergency()
        # Should only reset if train is stopped? Actually SafetyMonitor.reset_emergency checks speed==0 before releasing. Let's check SafetyMonitor.reset_emergency: it calls train.release_emergency_brake() only if train.speed == 0.
        # Since train speed still 20, it won't reset.
        assert self.train.emergency_brake == True
        # Stop the train
        self.train.speed = 0.0
        self.monitor.reset_emergency()
        assert self.train.emergency_brake == False
        assert self.monitor.emergency_brake_active == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
