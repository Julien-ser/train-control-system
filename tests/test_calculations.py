"""Unit tests for braking distance calculations."""

import pytest
import sys

sys.path.insert(0, "src")

from utils.calculations import (
    calculate_braking_distance,
    mph_to_mps,
    mps_to_mph,
    kmh_to_mps,
    mps_to_kmh,
)


class TestBrakingDistance:
    """Tests for braking distance calculations."""

    def test_stationary(self):
        """Braking distance at zero speed is zero."""
        assert calculate_braking_distance(0, 1) == 0

    def test_positive_values(self):
        """Test with positive speed and deceleration."""
        result = calculate_braking_distance(27, 1)  # 27 m/s, 1 m/s²
        expected = (27**2) / (2 * 1)  # 364.5
        assert result == pytest.approx(expected)

    def test_zero_deceleration(self):
        """Zero deceleration results in infinite distance."""
        assert calculate_braking_distance(10, 0) == float("inf")

    def test_negative_deceleration(self):
        """Negative deceleration is treated as zero."""
        assert calculate_braking_distance(10, -1) == float("inf")


class TestSpeedConversions:
    """Tests for speed unit conversions."""

    def test_mph_to_mps(self):
        assert mph_to_mps(60) == pytest.approx(26.8224)

    def test_mps_to_mph(self):
        assert mps_to_mph(27) == pytest.approx(60.5)

    def test_kmh_to_mps(self):
        assert kmh_to_mps(100) == pytest.approx(27.78)

    def test_mps_to_kmh(self):
        assert mps_to_kmh(27.78) == pytest.approx(100)

    def test_roundtrip(self):
        """Conversion roundtrip should be accurate."""
        original = 72.5
        assert mps_to_kmh(mph_to_mps(original)) == pytest.approx(original, rel=1e-3)
