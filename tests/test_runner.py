#!/usr/bin/env python3
"""
Main test runner for word generator tests.
Simplified version of the original test suite with weighted categories tests.
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
    cmd = [arg.replace("INPUT_FILE", input_file).replace("OUTPUT_FILE", output_file) for arg in cmd]
    
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
    print("Word Generator Test Suite - Refactored with Weighted Categories")
    print("=" * 60)
    
    # Check if word_generator.py exists
    if not os.path.exists("word_generator.py"):
        print("❌ word_generator.py not found in current directory")
        print("Please ensure the script is in the same directory as this test file.")
        sys.exit(1)
    
    result = TestResult()
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Import and run test modules
        from test_core.test_parser import run_parser_tests
        from test_core.test_word_generation import run_word_generation_tests
        from test_core.test_sound_changes import run_sound_changes_tests
        from test_core.test_syllabification import run_syllabification_tests
        from test_core.test_weighted_categories import run_weighted_categories_tests
        from test_utils.test_cli import run_cli_tests
        from test_integration.test_full_workflow import run_integration_tests
        
        # Run all test suites
        run_parser_tests(result, run_word_generator)
        run_word_generation_tests(result, run_word_generator)
        run_sound_changes_tests(result, run_word_generator)
        run_syllabification_tests(result, run_word_generator)
        run_weighted_categories_tests(result, run_word_generator)
        run_cli_tests(result, run_word_generator)
        run_integration_tests(result, run_word_generator)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        return False
    except Exception as e:
        print(f"\n\n❌ Test suite encountered an error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Print summary
    success = result.summary()
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)