#!/usr/bin/env python3
"""
Comprehensive Test Runner for ZIEL-MAS Backend
Provides utilities to run different test suites
"""

import subprocess
import sys
import argparse
from pathlib import Path
from typing import List, Optional


class TestRunner:
    """Test runner for ZIEL-MAS backend tests"""

    def __init__(self, test_dir: str = "backend/tests"):
        self.test_dir = Path(test_dir)
        self.pytest_args = []

    def run_unit_tests(self, verbose: bool = False) -> int:
        """Run unit tests only"""
        print("\n" + "="*80)
        print("Running Unit Tests")
        print("="*80 + "\n")

        args = [
            "python", "-m", "pytest",
            str(self.test_dir / "test_models.py"),
            str(self.test_dir / "test_agents.py"),
            str(self.test_dir / "test_services.py"),
            str(self.test_dir / "test_core.py"),
            "-v" if verbose else "-q",
            "--tb=short",
            "--disable-warnings"
        ]

        return subprocess.run(args).returncode

    def run_integration_tests(self, verbose: bool = False) -> int:
        """Run integration tests"""
        print("\n" + "="*80)
        print("Running Integration Tests")
        print("="*80 + "\n")

        args = [
            "python", "-m", "pytest",
            str(self.test_dir / "test_api_integration.py"),
            "-v" if verbose else "-q",
            "--tb=short",
            "--disable-warnings",
            "-s"  # Show print statements
        ]

        return subprocess.run(args).returncode

    def run_security_tests(self, verbose: bool = False) -> int:
        """Run security tests"""
        print("\n" + "="*80)
        print("Running Security Tests")
        print("="*80 + "\n")

        args = [
            "python", "-m", "pytest",
            str(self.test_dir / "test_security.py"),
            "-v" if verbose else "-q",
            "--tb=short",
            "--disable-warnings"
        ]

        return subprocess.run(args).returncode

    def run_performance_tests(self, verbose: bool = False) -> int:
        """Run performance tests"""
        print("\n" + "="*80)
        print("Running Performance Tests")
        print("="*80 + "\n")

        args = [
            "python", "-m", "pytest",
            str(self.test_dir / "test_performance.py"),
            "-v" if verbose else "-q",
            "--tb=short",
            "--disable-warnings",
            "-s"  # Show performance metrics
        ]

        return subprocess.run(args).returncode

    def run_all_tests(self, verbose: bool = False) -> int:
        """Run all tests"""
        print("\n" + "="*80)
        print("Running All Tests")
        print("="*80 + "\n")

        args = [
            "python", "-m", "pytest",
            str(self.test_dir),
            "-v" if verbose else "-q",
            "--tb=short",
            "--disable-warnings",
            "-s"
        ]

        return subprocess.run(args).returncode

    def run_specific_test(self, test_file: str, verbose: bool = False) -> int:
        """Run a specific test file"""
        print(f"\n{'='*80}")
        print(f"Running {test_file}")
        print('='*80 + "\n")

        args = [
            "python", "-m", "pytest",
            str(self.test_dir / test_file),
            "-v" if verbose else "-q",
            "--tb=short",
            "--disable-warnings",
            "-s"
        ]

        return subprocess.run(args).returncode

    def run_with_coverage(self, verbose: bool = False) -> int:
        """Run tests with coverage report"""
        print("\n" + "="*80)
        print("Running Tests with Coverage")
        print("="*80 + "\n")

        args = [
            "python", "-m", "pytest",
            str(self.test_dir),
            "-v" if verbose else "-q",
            "--cov=backend",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--tb=short",
            "-s"
        ]

        return subprocess.run(args).returncode

    def run_quick_tests(self, verbose: bool = False) -> int:
        """Run quick smoke tests"""
        print("\n" + "="*80)
        print("Running Quick Smoke Tests")
        print("="*80 + "\n")

        args = [
            "python", "-m", "pytest",
            str(self.test_dir / "test_models.py"),
            "-k", "test_task_status_values or test_agent_type_values or test_task_node_creation_with_defaults",
            "-v" if verbose else "-q",
            "--tb=short"
        ]

        return subprocess.run(args).returncode


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ZIEL-MAS Backend Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python run_tests.py --all

  # Run unit tests only
  python run_tests.py --unit

  # Run integration tests
  python run_tests.py --integration

  # Run security tests
  python run_tests.py --security

  # Run performance tests
  python run_tests.py --performance

  # Run with coverage
  python run_tests.py --coverage

  # Run specific test file
  python run_tests.py --file test_models.py

  # Run with verbose output
  python run_tests.py --all --verbose

  # Run quick smoke tests
  python run_tests.py --quick
        """
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all tests"
    )

    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run unit tests only"
    )

    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run integration tests only"
    )

    parser.add_argument(
        "--security",
        action="store_true",
        help="Run security tests only"
    )

    parser.add_argument(
        "--performance",
        action="store_true",
        help="Run performance tests only"
    )

    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage report"
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick smoke tests"
    )

    parser.add_argument(
        "--file",
        type=str,
        help="Run specific test file"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()
    runner = TestRunner()

    # Default to all tests if no specific option provided
    if not any([
        args.all, args.unit, args.integration,
        args.security, args.performance,
        args.coverage, args.quick, args.file
    ]):
        args.all = True

    # Run selected tests
    exit_code = 0

    if args.all:
        exit_code = runner.run_all_tests(verbose=args.verbose)
    elif args.unit:
        exit_code = runner.run_unit_tests(verbose=args.verbose)
    elif args.integration:
        exit_code = runner.run_integration_tests(verbose=args.verbose)
    elif args.security:
        exit_code = runner.run_security_tests(verbose=args.verbose)
    elif args.performance:
        exit_code = runner.run_performance_tests(verbose=args.verbose)
    elif args.coverage:
        exit_code = runner.run_with_coverage(verbose=args.verbose)
    elif args.quick:
        exit_code = runner.run_quick_tests(verbose=args.verbose)
    elif args.file:
        exit_code = runner.run_specific_test(args.file, verbose=args.verbose)

    # Print summary
    print("\n" + "="*80)
    if exit_code == 0:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed!")
    print("="*80 + "\n")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
