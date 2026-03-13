"""Example: Basic train control system simulation."""

import sys

sys.path.insert(0, "src")

from train_control.train import Train
from train_control.track import Block, TrackNetwork
from train_control.speed_enforcer import SpeedProfile, SpeedEnforcer
from train_control.safety import SafetyMonitor
from train_control.signals import Signal, SignalAspect, SignalController


def main():
    """Run a basic simulation of a train on a simple track."""
    print("=" * 60)
    print("Train Control System - Basic Simulation")
    print("=" * 60)

    # Create track network
    print("\n[1] Creating track network...")
    network = TrackNetwork()

    # Add blocks: 3 blocks, each 1km
    blocks = [
        Block(id="BLOCK_1", length=1000.0, speed_limit=25.0),
        Block(id="BLOCK_2", length=1000.0, speed_limit=20.0),
        Block(id="BLOCK_3", length=1000.0, speed_limit=15.0),
    ]
    for block in blocks:
        network.add_block(block)

    # Connect blocks sequentially
    network.connect_blocks("BLOCK_1", "BLOCK_2")
    network.connect_blocks("BLOCK_2", "BLOCK_3")

    print(f"  Created {len(network.blocks)} blocks")

    # Create signals
    print("\n[2] Creating signals...")
    signal1 = Signal(
        id="SIG1", aspect=SignalAspect.GREEN, location=950.0, linked_block_id="BLOCK_1"
    )
    signal2 = Signal(
        id="SIG2", aspect=SignalAspect.GREEN, location=1950.0, linked_block_id="BLOCK_2"
    )
    network.signals["SIG1"] = signal1
    network.signals["SIG2"] = signal2

    signal_controller = SignalController(network.signals)

    # Create train
    print("\n[3] Creating train...")
    train = Train(
        id="TRAIN001",
        max_speed=30.0,
        acceleration=0.8,
        deceleration=0.6,
        emergency_deceleration=1.0,
    )
    train.position = 0.0
    print(f"  Train initial position: {train.position}m")

    # Create speed profile and enforcer
    print("\n[4] Setting up speed enforcement...")
    speed_profile = SpeedProfile()
    # Add block speed limits as restrictions
    speed_profile.add_restriction(
        type("SpeedRestriction", (), {"location": 1000.0, "speed_limit": 25.0})()
    )
    speed_profile.add_restriction(
        type("SpeedRestriction", (), {"location": 2000.0, "speed_limit": 20.0})()
    )
    speed_profile.add_restriction(
        type("SpeedRestriction", (), {"location": 3000.0, "speed_limit": 15.0})()
    )

    enforcer = SpeedEnforcer(train, speed_profile)

    # Create safety monitor
    safety_monitor = SafetyMonitor(train, network)

    # Simulation loop
    print("\n[5] Starting simulation (60 seconds)...")
    print("-" * 60)
    print(
        f"{'Time':<6} {'Pos(m)':<10} {'Speed(m/s)':<12} {'Signal':<10} {'Safety':<10}"
    )
    print("-" * 60)

    time = 0.0
    dt = 1.0  # 1 second steps

    while time < 60.0:
        # Update aspects based on track occupancy
        # (For now, keep all green except if we occupy blocking blocks)
        for block in network.blocks.values():
            # Rough approximation: if train is in BLOCK_1, BLOCK_2 should be caution
            if block.id == "BLOCK_1" and train.position > 500.0:
                network.blocks["BLOCK_2"].occupied = True
            else:
                network.blocks["BLOCK_2"].occupied = False

        signal_controller.update_signal_aspects(network)

        # Check safety
        safety_status = safety_monitor.check_safety()

        # Check speed compliance
        compliance = enforcer.check_compliance(train.position, train.speed)

        # Control logic: if signal is yellow or red, prepare to stop
        current_block = network.get_block_by_position(train.position)
        if current_block:
            # Find associated signal
            for signal in network.signals.values():
                if signal.linked_block_id == current_block.id:
                    if signal.aspect.name in ["RED", "YELLOW"]:
                        train.set_brake(0.5)  # Apply service brake
                    elif (
                        train.speed
                        < speed_profile.get_max_speed_at(train.position, train.speed)
                        - 1.0
                    ):
                        train.set_throttle(0.3)  # Moderate acceleration
                    else:
                        train.set_throttle(0.0)  # Coast
                    break

        # If emergency brake active, coast
        if train.emergency_brake:
            train.set_throttle(0.0)
            train.set_brake(0.0)

        # Update train state
        train.update(dt)
        time += dt

        # Print status every 5 seconds
        if int(time) % 5 == 0:
            current_signal = "N/A"
            for s in network.signals.values():
                if s.linked_block_id == current_block.id if current_block else None:
                    current_signal = s.aspect.name
                    break

            print(
                f"{time:<6.0f} {train.position:<10.1f} {train.speed:<12.2f} {current_signal:<10} {'UNSAFE' if not safety_status.safe else 'OK':<10}"
            )

        # Stop simulation if emergency brake applied and train stopped
        if train.emergency_brake and train.speed == 0.0:
            print(
                f"\n!!! EMERGENCY BRAKE APPLIED at t={time:.0f}s, position={train.position:.1f}m"
            )
            print(f"    Reason: {safety_status.reason}")
            break

    print("-" * 60)
    print(f"\nFinal state:")
    print(f"  Position: {train.position:.1f}m")
    print(f"  Speed: {train.speed:.2f}m/s")
    print(f"  Emergency brake: {train.emergency_brake}")
    print("\nSimulation complete!")


if __name__ == "__main__":
    main()
