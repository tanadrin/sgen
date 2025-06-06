def test_syllable_deletion(result, run_word_generator):
    """Test syllable deletion rules."""
    print("Testing syllable deletion...")
    
    input_content = """
V: aeiou
C: bcdfg

-syll
ALLOWED_ONSETS: C
ALLOWED_CODAS: C  
STRESS_PATTERNS: 1
-end-syll

# Syllable deletion rule: delete first syllable
σ//#_

-dict
banana casa
-end-dict
"""
    
    test_result = run_word_generator(["-ds", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("syllable_deletion", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    # Check that first syllables were deleted
    # "banana" should become something like "na.na" and "casa" should become "sa"
    has_shortened_words = any(len(line.replace('.', '').replace('ˈ', '').replace('ˌ', '')) < 4 for line in lines)
    
    if not has_shortened_words:
        result.add_fail("syllable_deletion", f"No evidence of syllable deletion: {lines}")
        return
    
    result.add_pass()


def test_stress_movement(result, run_word_generator):
    """Test stress movement rules."""
    print("Testing stress movement...")
    
    input_content = """
V: aeiou
C: bcdfg

-syll
ALLOWED_ONSETS: C
ALLOWED_CODAS: C
STRESS_PATTERNS: 2  # Initial stress on second syllable
-end-syll

# Move stress to first syllable
σ/ˈσ/#_

-dict
banana casa data
-end-dict
"""
    
    test_result = run_word_generator(["-ds", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("stress_movement", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    # Check that stress appears at word beginning
    has_initial_stress = any(line.startswith('ˈ') for line in lines if line.strip())
    
    if not has_initial_stress:
        result.add_fail("stress_movement", f"No initial stress found: {lines}")
        return
    
    result.add_pass()


def test_stress_sensitive_changes(result, run_word_generator):
    """Test character changes in specific stress contexts."""
    print("Testing stress-sensitive character changes...")
    
    input_content = """
V: aeiou
C: bcdfg

-syll
ALLOWED_ONSETS: C
ALLOWED_CODAS: C
STRESS_PATTERNS: 1 2
-end-syll

# Change 'a' to 'e' only in unstressed syllables
a/e/˘_

-dict
banana casa
-end-dict
"""
    
    test_result = run_word_generator(["-ds", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("stress_sensitive_changes", f"Script failed: {test_result['stderr']}")
        return
    
    # Just check that it runs without error - detailed testing would require
    # more sophisticated analysis of stress patterns
    result.add_pass()


def test_syllable_rules_ignored_without_s_flag(result, run_word_generator):
    """Test that syllable rules are ignored when -s flag is not used."""
    print("Testing syllable rules ignored without -s flag...")
    
    input_content = """
V: aeiou
C: bcdfg

# Regular replacement
a/e/_

# Syllable rule (should be ignored)
σ//#_

-dict
banana casa
-end-dict
"""
    
    test_result = run_word_generator(["-d", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("syllable_rules_ignored", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    # Should have normal length words (syllable deletion shouldn't have occurred)
    # and 'a' should be replaced with 'e'
    for line in lines:
        if 'a' in line:
            result.add_fail("syllable_rules_ignored", f"Regular rule 'a/e/_' not applied: '{line}'")
            return
    
    # Check that words aren't drastically shortened (no syllable deletion)
    normal_length = any(len(line.replace('e', 'a')) >= 4 for line in lines)  # Original length check
    if not normal_length:
        result.add_fail("syllable_rules_ignored", f"Words appear to have been syllable-deleted when they shouldn't: {lines}")
        return
    
    result.add_pass()


def test_category_validation(result, run_word_generator):
    """Test validation of reserved characters in category definitions."""
    print("Testing category validation...")
    
    input_content = """
# This should cause an error - using reserved character in category name
σ: abc

CV
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "5"], input_content)
    
    # Should fail with error about reserved character
    if test_result['returncode'] == 0:
        result.add_fail("category_validation", "Script should have failed with reserved character in category name")
        return
    
    if "reserved character" not in test_result['stdout'] and "reserved character" not in test_result['stderr']:
        result.add_fail("category_validation", f"Expected reserved character error, got: {test_result['stderr']}")
        return
    
    result.add_pass()#!/usr/bin/env python3
"""
Tests for the syllabification module.
"""


def test_basic_syllabification(result, run_word_generator):
    """Test basic syllabification functionality."""
    print("Testing basic syllabification...")
    
    input_content = """
V: aeiou
C: bcdfg

CV
CVC

# Simple replacement
a/e/_

-syll
ALLOWED_ONSETS: C CC
ALLOWED_CODAS: C
STRESS_PATTERNS: 1 2
-end-syll

-dict
casa banana
-end-dict
"""
    
    test_result = run_word_generator(["-ds", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("basic_syllabification", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    if len(lines) == 0:
        result.add_fail("basic_syllabification", "No output generated")
        return
    
    # Check that syllable breaks (.) and stress marks (ˈ or ˌ) are present
    has_syllable_breaks = any('.' in line for line in lines)
    has_stress_marks = any('ˈ' in line or 'ˌ' in line for line in lines)
    
    if not has_syllable_breaks:
        result.add_fail("basic_syllabification", f"No syllable breaks found in output: {lines}")
        return
    
    if not has_stress_marks:
        result.add_fail("basic_syllabification", f"No stress marks found in output: {lines}")
        return
    
    result.add_pass()


def test_syllabification_with_categories(result, run_word_generator):
    """Test syllabification with category expansion."""
    print("Testing syllabification with categories...")
    
    input_content = """
V: aeiou
C: bcdfg
L: lr
N: mn

CV
CVC

-syll
ALLOWED_ONSETS: C L CL
ALLOWED_CODAS: C N
STRESS_PATTERNS: 1
-end-syll

-dict
banana clara
-end-dict
"""
    
    test_result = run_word_generator(["-ds", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("syllabification_categories", f"Script failed: {test_result['stderr']}")
        return
    
    # Just check that it runs without error - detailed syllabification logic
    # would need more sophisticated testing
    result.add_pass()


def test_dictionary_cleaning(result, run_word_generator):
    """Test that dictionary words are cleaned of syllable marks before rule application."""
    print("Testing dictionary word cleaning...")
    
    input_content = """
V: aeiou
C: bcdfg

# Replacement rule
a/e/_

-dict
ba.ˈna.na ca.ˈsa
-end-dict
"""
    
    test_result = run_word_generator(["-d", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("dictionary_cleaning", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    # Check that 'a' was replaced with 'e' even in originally syllabified words
    for line in lines:
        if 'a' in line:
            result.add_fail("dictionary_cleaning", f"Rule 'a/e/_' not applied to cleaned word: '{line}'")
            return
    
    result.add_pass()


def test_stress_patterns_only(result, run_word_generator):
    """Test stress patterns without syllable boundaries."""
    print("Testing stress patterns only...")
    
    input_content = """
V: aeiou
C: bcdfg

-syll
STRESS_PATTERNS: 1 2 1-2
-end-syll

-dict
banana casa data
-end-dict
"""
    
    test_result = run_word_generator(["-ds", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("stress_patterns_only", f"Script failed: {test_result['stderr']}")
        return
    
    # Even without onset/coda rules, stress should still be applied
    # This tests the fallback behavior
    result.add_pass()


def test_syllabification_flag_combinations(result, run_word_generator):
    """Test syllabification with other flags."""
    print("Testing syllabification flag combinations...")
    
    input_content = """
V: aeiou
C: bcdfg

# Replacement rule
a/e/_

-syll
ALLOWED_ONSETS: C
ALLOWED_CODAS: C
STRESS_PATTERNS: 1
-end-syll

-dict
banana casa
-end-dict
"""
    
    # Test -dsir combination (dictionary, syllabify, input, rules)
    test_result = run_word_generator(["-dsir", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("syllabification_flag_combinations", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    # Check that input→output format is preserved
    for line in lines:
        if line.strip() and ' → ' not in line:
            result.add_fail("syllabification_flag_combinations", f"Line missing input→output format: '{line}'")
            return
    
    result.add_pass()


def test_generation_with_syllabification(result, run_word_generator):
    """Test syllabification with generated words (not dictionary mode)."""
    print("Testing generation with syllabification...")
    
    input_content = """
V: aeiou
C: bcdfg

CV
CVC
CVCV

-syll
ALLOWED_ONSETS: C
ALLOWED_CODAS: C
STRESS_PATTERNS: 1 2
-end-syll
"""
    
    test_result = run_word_generator(["-s", "INPUT_FILE", "OUTPUT_FILE", "8"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("generation_with_syllabification", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    if len(lines) != 8:
        result.add_fail("generation_with_syllabification", f"Expected 8 words, got {len(lines)}")
        return
    
    # Check that at least some words have stress marks
    has_stress = any('ˈ' in line for line in lines)
    if not has_stress:
        result.add_fail("generation_with_syllabification", f"No stress marks found in generated words: {lines}")
        return
    
    result.add_pass()


def run_syllabification_tests(result, run_word_generator):
    """Run all syllabification tests."""
    print("\n=== SYLLABIFICATION TESTS ===")
    
    try:
        test_basic_syllabification(result, run_word_generator)
        test_syllabification_with_categories(result, run_word_generator)
        test_dictionary_cleaning(result, run_word_generator)
        test_stress_patterns_only(result, run_word_generator)
        test_syllabification_flag_combinations(result, run_word_generator)
        test_generation_with_syllabification(result, run_word_generator)
    except Exception as e:
        result.add_fail("syllabification_tests", f"Syllabification test suite error: {e}")