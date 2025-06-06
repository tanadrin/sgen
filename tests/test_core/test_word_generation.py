#!/usr/bin/env python3
"""
Tests for the word generation module.
"""


def test_basic_word_generation(result, run_word_generator):
    """Test basic word generation functionality."""
    print("Testing basic word generation...")
    
    input_content = """
V: aeiou
C: bcdfg

CV
CVC
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "5"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("basic_word_generation", f"Script failed: {test_result['stderr']}")
        return
    
    lines = test_result['output_file_content'].split('\n')
    if len(lines) != 5:
        result.add_fail("basic_word_generation", f"Expected 5 words, got {len(lines)}")
        return
    
    # Check that words match patterns
    for word in lines:
        if len(word) not in [2, 3]:
            result.add_fail("basic_word_generation", f"Word '{word}' doesn't match CV or CVC pattern")
            return
    
    result.add_pass()


def test_multiple_rule_cycling(result, run_word_generator):
    """Test that multiple rules are cycled through correctly."""
    print("Testing multiple rule cycling...")
    
    input_content = """
V: ae
C: bc

CV
CVC
CVCV
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "12"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("multiple_rule_cycling", f"Script failed: {test_result['stderr']}")
        return
    
    lines = test_result['output_file_content'].split('\n')
    if len(lines) != 12:
        result.add_fail("multiple_rule_cycling", f"Expected 12 words, got {len(lines)}")
        return
    
    # Check that we have words of different lengths (indicating rule cycling)
    lengths = set(len(word) for word in lines if word.strip())
    if len(lengths) < 2:
        result.add_fail("multiple_rule_cycling", f"Expected multiple word lengths, got: {lengths}")
        return
    
    result.add_pass()


def test_literal_characters(result, run_word_generator):
    """Test that literal characters (non-categories) work in rules."""
    print("Testing literal characters in rules...")
    
    input_content = """
V: ae
C: bc

# Rule with literal 'x'
CxV
VxC
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "6"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("literal_characters", f"Script failed: {test_result['stderr']}")
        return
    
    lines = test_result['output_file_content'].split('\n')
    
    # Check that all words contain 'x'
    for word in lines:
        if word.strip() and 'x' not in word:
            result.add_fail("literal_characters", f"Word '{word}' doesn't contain literal 'x'")
            return
    
    result.add_pass()


def test_flexible_rules_with_generation(result, run_word_generator):
    """Test that flexible rules work with word generation."""
    print("Testing flexible rules with generation...")
    
    input_content = """
V: aeiou
C: bcdfg

CV(C)
V(C)V
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "16"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("flexible_rules_generation", f"Script failed: {test_result['stderr']}")
        return
    
    # Check for expansion messages
    stdout = test_result['stdout']
    if "Expanded rule" not in stdout:
        result.add_fail("flexible_rules_generation", "No rule expansion found")
        return
    
    lines = test_result['output_file_content'].split('\n')
    if len(lines) != 16:
        result.add_fail("flexible_rules_generation", f"Expected 16 words, got {len(lines)}")
        return
    
    result.add_pass()


def run_word_generation_tests(result, run_word_generator):
    """Run all word generation tests."""
    print("\n=== WORD GENERATION TESTS ===")
    
    try:
        test_basic_word_generation(result, run_word_generator)
        test_multiple_rule_cycling(result, run_word_generator)
        test_literal_characters(result, run_word_generator)
        test_flexible_rules_with_generation(result, run_word_generator)
    except Exception as e:
        result.add_fail("word_generation_tests", f"Word generation test suite error: {e}")