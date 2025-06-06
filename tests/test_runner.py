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
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write(input_content)
    
    # Set up output file
    output_file = os.path.join(temp_dir, "output.txt")
    
    # Prepare command
    script_path = "word_generator.py"
    cmd = [sys.executable, script_path] + args
    
    # Replace placeholders in args - handle multiple output files
    new_cmd = []
    for arg in cmd:
        if "INPUT_FILE" in arg:
            new_cmd.append(arg.replace("INPUT_FILE", input_file))
        elif "OUTPUT_FILE_" in arg:
            # Handle numbered output files for multiple runs
            base_name = arg.replace("OUTPUT_FILE_", "output_")
            full_path = os.path.join(temp_dir, base_name + ".txt")
            new_cmd.append(full_path)
        elif "OUTPUT_FILE" in arg:
            new_cmd.append(arg.replace("OUTPUT_FILE", output_file))
        else:
            new_cmd.append(arg)
    cmd = new_cmd
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # Determine which output file to read
        actual_output_file = output_file
        for arg in cmd:
            if arg.endswith('.txt') and 'output' in arg and arg != input_file:
                actual_output_file = arg
                break
        
        # Read output file if it exists
        output_content = ""
        if os.path.exists(actual_output_file):
            with open(actual_output_file, 'r', encoding='utf-8') as f:
                output_content = f.read()
        
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'output_file_content': output_content.strip() if output_content else "",
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


# Fixed test functions
def test_random_vs_sequential_behavior(result, run_word_generator):
    """Test that random selection produces different results from sequential cycling."""
    print("Testing random vs sequential behavior...")
    
    input_content = """
V: a
C: b

CV
CVC
CVCC
"""
    
    # Generate the same words multiple times
    results = []
    for i in range(3):
        test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "10"], input_content)
        
        if test_result['returncode'] != 0:
            result.add_fail("random_vs_sequential", f"Script failed on run {i}: {test_result['stderr']}")
            return
        
        output = test_result['output_file_content']
        if not output:
            result.add_fail("random_vs_sequential", f"No output content on run {i}")
            return
            
        words = [line.strip() for line in output.split('\n') if line.strip()]
        if not words:
            result.add_fail("random_vs_sequential", f"No words extracted on run {i}")
            return
            
        # Convert to length pattern for comparison
        pattern = tuple(len(word) for word in words)
        results.append(pattern)
    
    # Check that we have some variety (not all identical)
    unique_patterns = set(results)
    
    # With random selection, expect some variation
    if len(unique_patterns) >= 2:
        result.add_pass()
    else:
        result.add_fail("random_vs_sequential", f"All runs produced identical patterns - may not be random. Patterns: {unique_patterns}")


def test_randomness_across_multiple_runs(result, run_word_generator):
    """Test that multiple runs with same input produce different outputs."""
    print("Testing randomness across multiple runs...")
    
    input_content = """
V: aei
C: bc

CV
CVC
CVCC
CVCV
"""
    
    # Run multiple times and collect first words
    first_words = []
    for i in range(10):
        test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "1"], input_content)
        
        if test_result['returncode'] != 0:
            result.add_fail("randomness_multiple_runs", f"Script failed on run {i}: {test_result['stderr']}")
            return
        
        output = test_result['output_file_content']
        if not output:
            result.add_fail("randomness_multiple_runs", f"No output on run {i}")
            return
            
        first_words.append(output.strip())
    
    # Check that we got some variety in the first words
    unique_first_words = set(first_words)
    
    # With 4 rules and 10 runs, expect at least 2 different words
    if len(unique_first_words) >= 2:
        result.add_pass()
    else:
        result.add_fail("randomness_multiple_runs", f"Too little variety: only {len(unique_first_words)} unique words in {len(first_words)} runs. Words: {unique_first_words}")


def test_flexible_weighted_rules_with_sound_changes(result, run_word_generator):
    """Test flexible weighted rules with sound changes."""
    print("Testing flexible weighted rules with sound changes...")
    
    input_content = """
V: aeiou
C: bcdfg
L: lr

# Flexible rule with weight
CV(L){3}
CVC{1}

# Sound changes
L//_C
a/e/_
"""
    
    test_result = run_word_generator(["-vr", "INPUT_FILE", "OUTPUT_FILE", "50"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("flexible_weighted_sound_changes", f"Script failed: {test_result['stderr']}")
        return
    
    stdout = test_result['stdout']
    
    # Check rule expansion with weight
    if "Expanded rule 'CV(L)' (weight 3) into 2 variants: CV, CVL" not in stdout:
        result.add_fail("flexible_weighted_sound_changes", "Flexible rule expansion with weight not shown")
        return
    
    # Check that sound changes applied by looking for debug messages or evidence
    if "Debug: Applied rule 'a/e/_'" in stdout or "[a/e/_]" in test_result['output_file_content']:
        result.add_pass()
    else:
        result.add_fail("flexible_weighted_sound_changes", "Sound change a/e/_ not applied")


def test_dictionary_mode_with_weighted_features(result, run_word_generator):
    """Test dictionary mode with weighted categories and rules."""
    print("Testing dictionary mode with weighted features...")
    
    input_content = """
# These features should be parsed but not affect dictionary processing
V: a{3} e{2} i{1}
C: b{2} c{1} d{3}

CV{10}
CVC{5}

# Sound change that should apply
a/o/_
e/i/_

-dict
banana casa villa mela
-end-dict
"""
    
    test_result = run_word_generator(["-vdir", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("dictionary_weighted_features", f"Script failed: {test_result['stderr']}")
        return
    
    stdout = test_result['stdout']
    
    # Weights should still be displayed even in dictionary mode
    if "Category 'V' weights:" not in stdout:
        result.add_fail("dictionary_weighted_features", "Category weights not shown in dict mode")
        return
    
    # Check that sound changes were applied
    if "Debug: Applied rule 'a/o/_'" in stdout and "Debug: Applied rule 'e/i/_'" in stdout:
        result.add_pass()
    else:
        result.add_fail("dictionary_weighted_features", "Sound changes not applied in dictionary mode")


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