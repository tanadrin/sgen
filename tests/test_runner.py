#!/usr/bin/env python3
"""
Main test runner for word generator tests.
Updated version with weighted rules and random selection tests.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path


class TestResult:
    """Track test results and provide summary."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self):
        self.passed += 1
    
    def add_fail(self, test_name, error):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*50}")
        print(f"TEST SUMMARY")
        print(f"{'='*50}")
        print(f"Total tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        
        if self.errors:
            print(f"\nFAILED TESTS:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.failed == 0:
            print(f"\n🎉 All tests passed!")
        else:
            print(f"\n❌ {self.failed} test(s) failed")
        
        return self.failed == 0


def run_word_generator(args, input_content=None, temp_dir=None):
    """Run the word generator script with given arguments and return output."""
    if temp_dir is None:
        temp_dir = tempfile.mkdtemp()
    
    # Create input file
    input_file = os.path.join(temp_dir, "input.txt")
    if input_content:
        with open(input_file, 'w') as f:
            f.write(input_content)
    
    # Set up output file
    output_file = os.path.join(temp_dir, "output.txt")
    
    # Prepare command
    script_path = "word_generator.py"  # Assume script is in same directory
    cmd = [sys.executable, script_path] + args
    
    # Replace placeholders in args
    new_cmd = []
    for arg in cmd:
        if "INPUT_FILE" in arg:
            new_cmd.append(arg.replace("INPUT_FILE", input_file))
        elif "OUTPUT_FILE_" in arg:
            new_cmd.append(arg.replace("OUTPUT_FILE_", os.path.join(temp_dir, "output_")))
        elif "OUTPUT_FILE" in arg:
            new_cmd.append(arg.replace("OUTPUT_FILE", output_file))
        else:
            new_cmd.append(arg)
    cmd = new_cmd
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)  # Increased timeout
        
        # Read output file if it exists
        output_content = ""
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                output_content = f.read().strip()
        
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'output_file_content': output_content,
            'temp_dir': temp_dir
        }
    
    except subprocess.TimeoutExpired:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': 'Test timed out',
            'output_file_content': '',
            'temp_dir': temp_dir
        }
    except Exception as e:
        return {
            'returncode': -2,
            'stdout': '',
            'stderr': str(e),
            'output_file_content': '',
            'temp_dir': temp_dir
        }

def main():
    """Run all tests by importing and executing test modules."""
    print("Word Generator Test Suite - With Weighted Rules and Random Selection")
    print("=" * 70)
    
    # Check if word_generator.py exists
    if not os.path.exists("word_generator.py"):
        print("❌ word_generator.py not found in current directory")
        print("Please ensure the script is in the same directory as this test file.")
        sys.exit(1)
    
    # Initialize result tracker
    result = TestResult()
    
    try:
        # Set up Python path for importing test modules
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        # Import all test modules
        print("Loading test modules...")
        
        from test_core.test_parser import run_parser_tests
        from test_core.test_word_generation import run_word_generation_tests
        from test_core.test_sound_changes import run_sound_changes_tests
        from test_core.test_syllabification import run_syllabification_tests
        from test_core.test_weighted_categories import run_weighted_categories_tests
        from test_core.test_weighted_rules import run_weighted_rules_tests
        from test_core.test_random_selection import run_random_selection_tests
        from test_utils.test_cli import run_cli_tests
        from test_integration.test_full_workflow import run_integration_tests
        from test_integration.test_weighted_functionality import run_weighted_integration_tests
        
        # Define test suites to run
        test_suites = [
            ("Core Parser", run_parser_tests),
            ("Word Generation", run_word_generation_tests),
            ("Sound Changes", run_sound_changes_tests),
            ("Syllabification", run_syllabification_tests),
            ("Weighted Categories", run_weighted_categories_tests),
            ("Weighted Rules", run_weighted_rules_tests),
            ("Random Selection", run_random_selection_tests),
            ("CLI Interface", run_cli_tests),
            ("Full Workflow", run_integration_tests),
            ("Weighted Integration", run_weighted_integration_tests)
        ]
        
        # Run each test suite
        for suite_name, test_function in test_suites:
            try:
                print(f"\nRunning {suite_name} tests...")
                test_function(result, run_word_generator)
            except Exception as e:
                print(f"Error in {suite_name} test suite: {e}")
                result.add_fail(f"{suite_name}_suite", f"Test suite error: {e}")
                continue
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        return False
    except ImportError as e:
        print(f"\n\n❌ Failed to import test modules: {e}")
        print("Please ensure all test files are present in the tests/ directory")
        return False
    except Exception as e:
        print(f"\n\n❌ Test suite encountered an unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Print final summary and return success status
    success = result.summary()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)