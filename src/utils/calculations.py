"""Physics and utility calculations."""


def calculate_braking_distance(speed_mps, deceleration_mps2):
    """Calculate braking distance using v²/(2a) formula.

    Args:
        speed_mps: Initial speed in meters per second
        deceleration_mps2: Deceleration in m/s² (positive value)

    Returns:
        Braking distance in meters, or inf if deceleration is zero/negative
    """
    if deceleration_mps2 <= 0:
        return float("inf")
    return (speed_mps**2) / (2 * deceleration_mps2)


def mph_to_mps(mph):
    """Convert miles per hour to meters per second."""
    return mph * 0.44704


def mps_to_mph(mps):
    """Convert meters per second to miles per hour."""
    return mps / 0.44704


def kmh_to_mps(kmh):
    """Convert kilometers per hour to meters per second."""
    return kmh / 3.6


def mps_to_kmh(mps):
    """Convert meters per second to kilometers per hour."""
    return mps * 3.6


__all__ = [
    "calculate_braking_distance",
    "mph_to_mps",
    "mps_to_mph",
    "kmh_to_mps",
    "mps_to_kmh",
]
