"""Utility functions for calculations."""


def calculate_braking_distance(speed_mps: float, deceleration_mps2: float) -> float:
    """
    Calculate distance required to stop from current speed with given deceleration.

    Args:
        speed_mps: Current speed in meters per second
        deceleration_mps2: Deceleration rate in m/s² (positive value)

    Returns:
        Braking distance in meters
    """
    if deceleration_mps2 <= 0:
        return float("inf")
    return (speed_mps**2) / (2 * deceleration_mps2)


def mph_to_mps(speed_mph: float) -> float:
    """Convert miles per hour to meters per second."""
    return speed_mph * 0.44704


def mps_to_mph(speed_mps: float) -> float:
    """Convert meters per second to miles per hour."""
    return speed_mps * 2.23694


def kmh_to_mps(speed_kmh: float) -> float:
    """Convert kilometers per hour to meters per second."""
    return speed_kmh / 3.6


def mps_to_kmh(speed_mps: float) -> float:
    """Convert meters per second to kilometers per hour."""
    return speed_mps * 3.6
