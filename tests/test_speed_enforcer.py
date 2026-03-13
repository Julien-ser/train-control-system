"""Tests for speed enforcement system."""

import pytest
import sys

sys.path.insert(0, "src")

from train_control.speed_enforcer import SpeedProfile, SpeedRestriction, SpeedEnforcer
from train_control.train import Train


class TestSpeedRestriction:
    def test_creation(self):
        r = SpeedRestriction(location=1000.0, speed_limit=25.0, reason="track")
        assert r.location == 1000.0
        assert r.speed_limit == 25.0
        assert r.reason == "track"

    def test_is_active_at(self):
        r = SpeedRestriction(location=1000.0, speed_limit=25.0)
        assert r.is_active_at(1000.0)  # exactly at
        assert r.is_active_at(999.5)  # within 1m
        assert r.is_active_at(1000.5)
        assert not r.is_active_at(1002.0)  # beyond margin


class TestSpeedProfile:
    def test_empty_profile_returns_default(self):
        profile = SpeedProfile()
        max_speed = profile.get_max_speed_at(500.0)
        assert max_speed == 30.0

    def test_single_restriction_before_position(self):
        profile = SpeedProfile()
        profile.add_restriction(SpeedRestriction(location=1000.0, speed_limit=20.0))
        # At position 500m, distance to restriction = 500m
        # Restriction speed is 20 m/s, braking speed sqrt(2*0.6*500)=sqrt(600)=24.49, so max = min(20, 24.49)=20
        max_speed = profile.get_max_speed_at(500.0, deceleration=0.6)
        assert max_speed == pytest.approx(20.0)

    def test_braking_curve_single(self):
        profile = SpeedProfile()
        # Restriction at 1000m, limit = 30 m/s
        # At position 0, distance = 1000m, braking speed = sqrt(2*0.6*1000)=sqrt(1200)=34.64
        # So max allowed = min(30, 34.64) = 30
        profile.add_restriction(SpeedRestriction(location=1000.0, speed_limit=30.0))
        max_speed = profile.get_max_speed_at(0.0, deceleration=0.6)
        assert max_speed == pytest.approx(30.0)

        # At position 600m, distance = 400m, braking speed = sqrt(2*0.6*400)=sqrt(480)=21.89
        profile2 = SpeedProfile()
        profile2.add_restriction(SpeedRestriction(location=1000.0, speed_limit=30.0))
        max_speed2 = profile2.get_max_speed_at(600.0, deceleration=0.6)
        assert max_speed2 == pytest.approx(21.89, rel=0.01)

    def test_multiple_restrictions_takes_minimum(self):
        profile = SpeedProfile()
        # At position 0:
        # Restriction A: at 1000m, limit 30 m/s -> braking speed ≈ 34.64 -> min = 30
        # Restriction B: at 2000m, limit 20 m/s -> distance 2000, braking speed ≈ sqrt(2*0.6*2000)=sqrt(2400)=48.99 -> min(20, 48.99)=20
        # Overall max = min(30, 20) = 20
        profile.add_restriction(SpeedRestriction(location=1000.0, speed_limit=30.0))
        profile.add_restriction(SpeedRestriction(location=2000.0, speed_limit=20.0))
        max_speed = profile.get_max_speed_at(0.0, deceleration=0.6)
        assert max_speed == pytest.approx(20.0)

    def test_restriction_behind_position_ignored(self):
        profile = SpeedProfile()
        profile.add_restriction(SpeedRestriction(location=500.0, speed_limit=10.0))
        # At position 600m, restriction is behind, should not affect
        max_speed = profile.get_max_speed_at(600.0, deceleration=0.6)
        # No ahead restrictions, so default
        assert max_speed == 30.0

    def test_braking_curve_respects_deceleration(self):
        profile = SpeedProfile()
        profile.add_restriction(SpeedRestriction(location=1000.0, speed_limit=50.0))
        # With lower deceleration (0.3), braking speed at 0m: sqrt(2*0.3*1000)=sqrt(600)=24.49
        max_speed = profile.get_max_speed_at(0.0, deceleration=0.3)
        assert max_speed == pytest.approx(24.49, rel=0.01)

    def test_very_large_distance_allows_higher_speed(self):
        profile = SpeedProfile()
        profile.add_restriction(SpeedRestriction(location=10000.0, speed_limit=50.0))
        # At 0, distance huge, braking speed sqrt(2*0.6*10000)=sqrt(12000)=109.54, but limited by train's max? Actually profile returns 50 (the limit) because 50 < 109.54
        max_speed = profile.get_max_speed_at(0.0, deceleration=0.6)
        assert max_speed == 50.0


class TestSpeedEnforcer:
    def setup_method(self):
        self.train = Train(
            id="TRAIN001",
            max_speed=30.0,
            acceleration=1.0,
            deceleration=0.6,
            emergency_deceleration=1.2,
        )
        self.profile = SpeedProfile()
        self.enforcer = SpeedEnforcer(self.train, self.profile)

    def test_no_restriction_compliant(self):
        self.train.speed = 20.0
        compliance = self.enforcer.check_compliance(500.0, 20.0)
        assert compliance["compliant"] == True
        assert compliance["action"] == "CONTINUE"

    def test_speeding_triggers_emergency_brake(self):
        self.train.speed = 25.0
        self.profile.add_restriction(SpeedRestriction(location=600.0, speed_limit=20.0))
        compliance = self.enforcer.check_compliance(500.0, 25.0)
        assert compliance["compliant"] == False
        assert compliance["action"] == "EMERGENCY_BRAKE"
        assert compliance["excess"] > 0

    def test_near_limit_gives_prepare_signal(self):
        self.train.speed = 19.0
        # Use a far restriction so braking curve doesn't lower max_allowed
        self.profile.add_restriction(
            SpeedRestriction(location=5000.0, speed_limit=20.0)
        )
        compliance = self.enforcer.check_compliance(0.0, 19.0)
        assert compliance["compliant"] == True
        # Speed > 90% of limit (20*0.9=18) should give warning/prepare
        assert (
            "warning" in compliance or compliance["action"] == "PREPARE_TO_DECELERATE"
        )

    def test_brake_when_above_90_percent(self):
        self.train.speed = 18.2  # 91% of 20
        # Use far restriction to avoid braking curve limiting
        self.profile.add_restriction(
            SpeedRestriction(location=5000.0, speed_limit=20.0)
        )
        compliance = self.enforcer.check_compliance(0.0, 18.2)
        # Speed is > 90% of limit, should give warning
        assert (
            "warning" in compliance or compliance["action"] == "PREPARE_TO_DECELERATE"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
