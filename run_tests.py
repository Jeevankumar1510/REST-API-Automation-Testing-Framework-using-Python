"""
Interactive Test Runner CLI for the REST API Automation Framework.
Allows executing test suites by marker, launching the server, or generating reports.

Usage:
    python run_tests.py                 # Interactive Menu
    python run_tests.py --all           # Run all 59 tests
    python run_tests.py --smoke         # Run smoke tests
    python run_tests.py --auth          # Run authentication tests
    python run_tests.py --negative      # Run negative scenarios
    python run_tests.py --server        # Run FastAPI server standalone
    python run_tests.py --open-report   # Open latest HTML report
"""

import argparse
import os
import subprocess
import sys
import webbrowser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPORT_FILE = PROJECT_ROOT / "reports" / "report.html"


def run_pytest(args=None):
    """Execute pytest with specified options."""
    cmd = [sys.executable, "-m", "pytest"]
    if args:
        cmd.extend(args)
    print(f"\n🚀 Running command: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return result.returncode


def open_report():
    """Open generated HTML report in default web browser."""
    if REPORT_FILE.exists():
        print(f"\n📊 Opening HTML Report: {REPORT_FILE.resolve()}\n")
        webbrowser.open(REPORT_FILE.as_uri())
    else:
        print(f"\n⚠️  Report not found at: {REPORT_FILE}")
        print("Run the tests first to generate the report!\n")


def start_server():
    """Launch the FastAPI server using Uvicorn."""
    print("\n🌐 Starting FastAPI Target Server on http://127.0.0.1:8000...")
    print("Interactive Documentation: http://127.0.0.1:8000/docs\n")
    cmd = [sys.executable, "-m", "uvicorn", "application.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
    subprocess.run(cmd, cwd=PROJECT_ROOT)


def run_benchmark():
    """Execute load and concurrency benchmark."""
    cmd = [sys.executable, "load_test.py", "--concurrency", "10", "--requests", "100"]
    subprocess.run(cmd, cwd=PROJECT_ROOT)


def interactive_menu():
    """Display interactive CLI menu for test selection."""
    while True:
        print("\n" + "=" * 65)
        print("  🧪 REST API AUTOMATION TESTING FRAMEWORK - TEST RUNNER")
        print("=" * 65)
        print("  [1] Run All Automated Tests (Full Regression Suite)")
        print("  [2] Run Smoke Tests (Critical Path Verification)")
        print("  [3] Run Authentication & Token Tests")
        print("  [4] Run Negative Scenarios (400, 401, 404, 405, 409, 422)")
        print("  [5] Run JSON Schema & Performance SLA Tests")
        print("  [6] Open Latest HTML Test Report in Browser")
        print("  [7] Open Interactive 3D Architecture Dashboard")
        print("  [8] Run Concurrency & Load Benchmark (100 reqs / 10 workers)")
        print("  [9] Start FastAPI Target Application Server")
        print("  [0] Exit")
        print("=" * 65)

        choice = input("Enter your choice [0-9]: ").strip()

        if choice == "1":
            code = run_pytest()
            if code == 0:
                open_choice = input("\nTests completed successfully! Open HTML report? (y/n): ").strip().lower()
                if open_choice == "y":
                    open_report()
        elif choice == "2":
            run_pytest(["-m", "smoke"])
        elif choice == "3":
            run_pytest(["-m", "auth"])
        elif choice == "4":
            run_pytest(["-m", "negative"])
        elif choice == "5":
            run_pytest(["-m", "schema or performance"])
        elif choice == "6":
            open_report()
        elif choice == "7":
            dash_path = PROJECT_ROOT / "dashboard.html"
            print(f"\n📊 Opening 3D Dashboard: {dash_path.resolve()}\n")
            webbrowser.open(dash_path.as_uri())
        elif choice == "8":
            run_benchmark()
        elif choice == "9":
            start_server()
        elif choice == "0":
            print("\nExiting. Happy Testing! 🎉\n")
            break
        else:
            print("\n❌ Invalid selection. Please choose an option from 0 to 9.")


def main():
    parser = argparse.ArgumentParser(description="REST API Automation Test Runner")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests")
    parser.add_argument("--auth", action="store_true", help="Run auth tests")
    parser.add_argument("--negative", action="store_true", help="Run negative tests")
    parser.add_argument("--schema", action="store_true", help="Run schema tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--open-report", action="store_true", help="Open HTML report")
    parser.add_argument("--server", action="store_true", help="Start FastAPI server")

    args = parser.parse_args()

    if args.all:
        sys.exit(run_pytest())
    elif args.smoke:
        sys.exit(run_pytest(["-m", "smoke"]))
    elif args.auth:
        sys.exit(run_pytest(["-m", "auth"]))
    elif args.negative:
        sys.exit(run_pytest(["-m", "negative"]))
    elif args.schema:
        sys.exit(run_pytest(["-m", "schema"]))
    elif args.performance:
        sys.exit(run_pytest(["-m", "performance"]))
    elif args.open_report:
        open_report()
    elif args.server:
        start_server()
    else:
        interactive_menu()


if __name__ == "__main__":
    main()

