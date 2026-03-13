#!/usr/bin/env python3
"""Health check and validation script for Train Control System deployment."""

import sys
import subprocess
import importlib.util


def check_imports():
    """Verify all core modules can be imported."""
    print("Checking module imports...")
    required_modules = [
        "train_control.train",
        "train_control.track",
        "train_control.signals",
        "train_control.movement_authority",
        "train_control.speed_enforcer",
        "train_control.safety",
        "train_control.utils.calculations",
    ]

    sys.path.insert(0, "src")

    all_ok = True
    for module in required_modules:
        try:
            spec = importlib.util.find_spec(module)
            if spec is None:
                print(f"  ✗ {module} - NOT FOUND")
                all_ok = False
            else:
                importlib.import_module(module)
                print(f"  ✓ {module}")
        except Exception as e:
            print(f"  ✗ {module} - ERROR: {e}")
            all_ok = False

    return all_ok


def run_tests():
    """Run a subset of tests to verify functionality."""
    print("\nRunning quick test suite...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "-x"],
            capture_output=False,
            timeout=60,
        )
        if result.returncode == 0:
            print("  ✓ All tests passed")
            return True
        else:
            print("  ✗ Some tests failed")
            return False
    except subprocess.TimeoutExpired:
        print("  ✗ Tests timed out")
        return False
    except Exception as e:
        print(f"  ✗ Error running tests: {e}")
        return False


def check_examples():
    """Verify example files exist and are runnable."""
    print("\nChecking examples...")
    import os

    examples_dir = "examples"
    if not os.path.exists(examples_dir):
        print("  ✗ Examples directory not found")
        return False

    example_files = ["basic_simulation.py"]
    all_ok = True
    for example in example_files:
        path = os.path.join(examples_dir, example)
        if os.path.exists(path):
            print(f"  ✓ {example}")
        else:
            print(f"  ✗ {example} - NOT FOUND")
            all_ok = False

    return all_ok


def main():
    """Run all health checks."""
    print("=" * 60)
    print("Train Control System - Health Check")
    print("=" * 60)
    print()

    results = []
    results.append(("Module Imports", check_imports()))
    results.append(("Examples", check_examples()))
    results.append(("Test Suite", run_tests()))

    print()
    print("=" * 60)
    print("Health Check Summary")
    print("=" * 60)

    all_healthy = True
    for check, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {check}: {status}")
        if not passed:
            all_healthy = False

    print()
    if all_healthy:
        print("✓ System is healthy and ready for deployment")
        sys.exit(0)
    else:
        print("✗ System health check failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
