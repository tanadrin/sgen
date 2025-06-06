#!/usr/bin/env python3
"""
Tests for the word generation module.
Updated for random rule selection instead of cycling.
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
    
    # Check that words match patterns (now we just check they're valid, not specific order)
    for word in lines:
        if len(word) not in [2, 3]:
            result.add_fail("basic_word_generation", f"Word '{word}' doesn't match CV or CVC pattern")
            return
    
    result.add_pass()


def test_multiple_rules_usage(result, run_word_generator):
    """Test that multiple rules are all used over many generations."""
    print("Testing multiple rules usage...")
    
    input_content = """
V: ae
C: bc

CV
CVC
CVCV
"""
    
    # Generate many words to ensure all rules get used
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "60"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("multiple_rules_usage", f"Script failed: {test_result['stderr']}")
        return
    
    lines = test_result['output_file_content'].split('\n')
    if len(lines) != 60:
        result.add_fail("multiple_rules_usage", f"Expected 60 words, got {len(lines)}")
        return
    
    # Check that we have words of different lengths (indicating all rules were used)
    lengths = set(len(word) for word in lines if word.strip())
    expected_lengths = {2, 3, 4}  # CV, CVC, CVCV
    
    if not expected_lengths.issubset(lengths):
        result.add_fail("multiple_rules_usage", f"Not all rule patterns used. Expected lengths {expected_lengths}, got: {lengths}")
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


def test_single_rule_generation(result, run_word_generator):
    """Test generation with only one rule."""
    print("Testing single rule generation...")
    
    input_content = """
V: aei
C: bc

CVC
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "10"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("single_rule_generation", f"Script failed: {test_result['stderr']}")
        return
    
    lines = test_result['output_file_content'].split('\n')
    
    # All words should follow CVC pattern (3 characters)
    for word in lines:
        if len(word) != 3:
            result.add_fail("single_rule_generation", f"Word '{word}' doesn't match CVC pattern")
            return
    
    result.add_pass()


def test_category_usage_in_generation(result, run_word_generator):
    """Test that all characters from categories are potentially used."""
    print("Testing category usage in generation...")
    
    input_content = """
V: ae
C: bc

CV
"""
    
    # Generate many words to get good coverage
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "100"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("category_usage_generation", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    
    # Check that we see characters from both categories
    vowels_used = set(char for char in 'ae' if char in output)
    consonants_used = set(char for char in 'bc' if char in output)
    
    if len(vowels_used) == 0:
        result.add_fail("category_usage_generation", "No vowels found in output")
        return
    
    if len(consonants_used) == 0:
        result.add_fail("category_usage_generation", "No consonants found in output")
        return
    
    result.add_pass()


def test_complex_rules_generation(result, run_word_generator):
    """Test generation with complex rule patterns."""
    print("Testing complex rules generation...")
    
    input_content = """
V: aei
C: bcd
L: lr
N: mn

# Complex patterns
CLVC
CVNC
VLCV
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "30"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("complex_rules_generation", f"Script failed: {test_result['stderr']}")
        return
    
    lines = test_result['output_file_content'].split('\n')
    
    # All words should be 4 characters long
    for word in lines:
        if len(word) != 4:
            result.add_fail("complex_rules_generation", f"Word '{word}' doesn't match 4-character pattern")
            return
    
    # Check that we see characters from all categories in the output
    output = test_result['output_file_content']
    
    categories_found = {
        'V': any(char in output for char in 'aei'),
        'C': any(char in output for char in 'bcd'),
        'L': any(char in output for char in 'lr'),
        'N': any(char in output for char in 'mn')
    }
    
    for cat_name, found in categories_found.items():
        if not found:
            result.add_fail("complex_rules_generation", f"Category {cat_name} not represented in output")
            return
    
    result.add_pass()


def test_generation_consistency(result, run_word_generator):
    """Test that generation produces consistent word counts."""
    print("Testing generation consistency...")
    
    input_content = """
V: a
C: b

CV
CVC
"""
    
    # Test various word counts
    for count in [1, 5, 10, 25]:
        test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", str(count)], input_content)
        
        if test_result['returncode'] != 0:
            result.add_fail("generation_consistency", f"Script failed for count {count}: {test_result['stderr']}")
            return
        
        lines = [line for line in test_result['output_file_content'].split('\n') if line.strip()]
        if len(lines) != count:
            result.add_fail("generation_consistency", f"Expected {count} words, got {len(lines)}")
            return
    
    result.add_pass()


def run_word_generation_tests(result, run_word_generator):
    """Run all word generation tests."""
    print("\n=== WORD GENERATION TESTS ===")
    
    try:
        test_basic_word_generation(result, run_word_generator)
        test_multiple_rules_usage(result, run_word_generator)
        test_literal_characters(result, run_word_generator)
        test_flexible_rules_with_generation(result, run_word_generator)
        test_single_rule_generation(result, run_word_generator)
        test_category_usage_in_generation(result, run_word_generator)
        test_complex_rules_generation(result, run_word_generator)
        test_generation_consistency(result, run_word_generator)
    except Exception as e:
        result.add_fail("word_generation_tests", f"Word generation test suite error: {e}")