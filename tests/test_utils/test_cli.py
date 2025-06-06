#!/usr/bin/env python3
"""
Tests for the CLI module.
"""


def test_flag_combinations(result, run_word_generator):
    """Test various flag combinations."""
    print("Testing flag combinations...")
    
    input_content = """
V: ae
C: bc
CV
-dict
ba ca
"""
    
    # Test -vdi combination
    test_result = run_word_generator(["-vdi", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("flag_combinations", f"Combined flags failed: {test_result['stderr']}")
        return
    
    # Check that verbose output is in stdout
    if "ba → ba" not in test_result['stdout'] and "ca → ca" not in test_result['stdout']:
        result.add_fail("flag_combinations", "Verbose output not found in stdout")
        return
    
    result.add_pass()


def test_error_handling(result, run_word_generator):
    """Test various error conditions."""
    print("Testing CLI error handling...")
    
    # Test missing input file
    test_result = run_word_generator(["nonexistent.txt", "OUTPUT_FILE", "5"])
    if test_result['returncode'] == 0:
        result.add_fail("error_handling_missing_file", "Script should fail with missing input file")
        return
    
    # Test invalid number of words
    input_content = "V: a\nCV"
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "abc"], input_content)
    if test_result['returncode'] == 0:
        result.add_fail("error_handling_invalid_number", "Script should fail with invalid number")
        return
    
    # Test -i without -d
    test_result = run_word_generator(["-i", "INPUT_FILE", "OUTPUT_FILE", "5"], input_content)
    if test_result['returncode'] == 0:
        result.add_fail("error_handling_i_without_d", "Script should fail with -i without -d")
        return
    
    result.add_pass()


def test_dictionary_mode_flags(result, run_word_generator):
    """Test dictionary mode specific flags."""
    print("Testing dictionary mode flags...")
    
    input_content = """
V: aeiou
C: bcdfg

# Replacement rule
a/e/_

-dict
banana kata
"""
    
    # Test basic dictionary mode
    test_result = run_word_generator(["-d", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("dictionary_mode_basic", f"Dictionary mode failed: {test_result['stderr']}")
        return
    
    # Test dictionary mode with input/output format
    test_result = run_word_generator(["-di", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("dictionary_mode_input_output", f"Dictionary input/output mode failed: {test_result['stderr']}")
        return
    
    lines = test_result['output_file_content'].split('\n')
    
    # Check format: input → output
    for line in lines:
        if line.strip() and ' → ' not in line:
            result.add_fail("dictionary_mode_input_output", f"Line '{line}' doesn't have input→output format")
            return
    
    result.add_pass()


def test_verbose_mode(result, run_word_generator):
    """Test verbose mode output."""
    print("Testing verbose mode...")
    
    input_content = """
V: ae
C: bc
CV
"""
    
    # Test verbose mode
    test_result = run_word_generator(["-v", "INPUT_FILE", "OUTPUT_FILE", "3"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("verbose_mode", f"Verbose mode failed: {test_result['stderr']}")
        return
    
    # Check that output appears in both stdout and file
    file_lines = test_result['output_file_content'].split('\n')
    stdout_lines = test_result['stdout'].split('\n')
    
    # At least some words should appear in stdout
    words_in_stdout = any(len(line.strip()) == 2 for line in stdout_lines)
    if not words_in_stdout:
        result.add_fail("verbose_mode", "Generated words not found in verbose stdout")
        return
    
    result.add_pass()


def run_cli_tests(result, run_word_generator):
    """Run all CLI tests."""
    print("\n=== CLI TESTS ===")
    
    try:
        test_flag_combinations(result, run_word_generator)
        test_error_handling(result, run_word_generator)
        test_dictionary_mode_flags(result, run_word_generator)
        test_verbose_mode(result, run_word_generator)
    except Exception as e:
        result.add_fail("cli_tests", f"CLI test suite error: {e}")