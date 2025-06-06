#!/usr/bin/env python3
"""
Tests for weighted categories functionality.
"""


def test_basic_weighted_categories(result, run_word_generator):
    """Test basic weighted category functionality."""
    print("Testing basic weighted categories...")
    
    input_content = """
# Heavily weighted 'a', normal weight others
V: a{5} e i o u
C: bcdfg

CV
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "50"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("basic_weighted_categories", f"Script failed: {test_result['stderr']}")
        return
    
    # Check that weight information is printed
    if "Category 'V' weights: a:5, e:1, i:1, o:1, u:1" not in test_result['stdout']:
        result.add_fail("basic_weighted_categories", "Weight information not printed correctly")
        return
    
    # Count 'a' occurrences in the output
    output = test_result['output_file_content']
    a_count = output.count('a')
    total_vowels = sum(output.count(v) for v in 'aeiou')
    
    # 'a' should appear much more frequently than other vowels
    # With weight 5 out of total 9, expect roughly 50%+ of vowels to be 'a'
    if total_vowels > 0:
        a_percentage = a_count / total_vowels
        if a_percentage < 0.4:  # Allow some variance due to randomness
            result.add_fail("basic_weighted_categories", f"Expected 'a' to appear frequently (~50%+), got {a_percentage:.2%}")
            return
    
    result.add_pass()


def test_weighted_categories_in_dictionary_mode(result, run_word_generator):
    """Test weighted categories with replacement rules in dictionary mode."""
    print("Testing weighted categories in dictionary mode...")
    
    input_content = """
# Weighted vowels
V: a{3} e{2} i o u
# Weighted consonants  
C: b c{2} d f g

# Replacement rule using weighted categories
V/C/_#

-dict
banana casa villa data
-end-dict
"""
    
    test_result = run_word_generator(["-dr", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("weighted_categories_dictionary", f"Script failed: {test_result['stderr']}")
        return
    
    # Check that weight information is printed for both categories
    stdout = test_result['stdout']
    if "Category 'V' weights:" not in stdout or "Category 'C' weights:" not in stdout:
        result.add_fail("weighted_categories_dictionary", "Weight information not printed for categories")
        return
    
    # Check that replacements occurred (vowels at word end should become consonants)
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    # At least some words should have been transformed
    found_transformations = False
    for line in lines:
        # Look for words ending in consonants that originally ended in vowels
        if any(word.endswith(c) for word in line.split() for c in 'bcdfg'):
            found_transformations = True
            break
    
    if not found_transformations:
        result.add_fail("weighted_categories_dictionary", "No evidence of V→C replacement at word end")
        return
    
    result.add_pass()


def test_multiple_weighted_categories(result, run_word_generator):
    """Test multiple categories with different weight patterns."""
    print("Testing multiple weighted categories...")
    
    input_content = """
# Different weight patterns
V: a{4} e{3} i{2} o{1}
C: b{1} c{3} d{2} f{1} g{1}
L: l{3} r{1}

# Use all categories
CV(L)V
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "60"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("multiple_weighted_categories", f"Script failed: {test_result['stderr']}")
        return
    
    # Check that all weight information is printed
    stdout = test_result['stdout']
    expected_patterns = [
        "Category 'V' weights: a:4, e:3, i:2, o:1",
        "Category 'C' weights: b:1, c:3, d:2, f:1, g:1", 
        "Category 'L' weights: l:3, r:1"
    ]
    
    for pattern in expected_patterns:
        if pattern not in stdout:
            result.add_fail("multiple_weighted_categories", f"Expected weight pattern not found: {pattern}")
            return
    
    # Check distribution in output
    output = test_result['output_file_content']
    
    # Count 'l' vs 'r' occurrences (should heavily favor 'l')
    l_count = output.count('l')
    r_count = output.count('r')
    
    if l_count + r_count > 0:
        l_percentage = l_count / (l_count + r_count)
        if l_percentage < 0.6:  # With 3:1 ratio, expect ~75%, allow variance
            result.add_fail("multiple_weighted_categories", f"Expected 'l' to dominate over 'r', got l:{l_percentage:.2%}")
            return
    
    result.add_pass()


def test_weighted_categories_with_flexible_rules(result, run_word_generator):
    """Test weighted categories work with flexible rule expansion."""
    print("Testing weighted categories with flexible rules...")
    
    input_content = """
V: a{2} e{1}
C: b{3} c{1}

# Flexible rule that should expand
CV(C)
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "40"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("weighted_categories_flexible_rules", f"Script failed: {test_result['stderr']}")
        return
    
    # Check rule expansion message
    if "Expanded rule 'CV(C)' into 2 variants: CV, CVC" not in test_result['stdout']:
        result.add_fail("weighted_categories_flexible_rules", "Rule expansion message not found")
        return
    
    # Check weight information
    if "Category 'V' weights:" not in test_result['stdout']:
        result.add_fail("weighted_categories_flexible_rules", "Weight information not printed")
        return
    
    # Check that weighted selection works
    output = test_result['output_file_content']
    b_count = output.count('b')
    c_count = output.count('c') 
    
    if b_count + c_count > 0:
        b_percentage = b_count / (b_count + c_count)
        if b_percentage < 0.5:  # With 3:1 ratio, expect ~75%, allow variance
            result.add_fail("weighted_categories_flexible_rules", f"Expected 'b' to dominate over 'c', got b:{b_percentage:.2%}")
            return
    
    result.add_pass()


def test_category_length_mismatch_with_weights(result, run_word_generator):
    """Test category length mismatch detection with weighted categories."""
    print("Testing category length mismatch with weighted categories...")
    
    input_content = """
# These should have different unique character counts
V: a{3} e{2} i{1}    # 3 unique chars
C: b{2} c{1}         # 2 unique chars

CV

# This should generate a warning
V/C/_
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "5"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("category_length_mismatch_weights", f"Script failed: {test_result['stderr']}")
        return
    
    # Check for warning about different unique character counts
    if "different unique character counts" not in test_result['stdout']:
        result.add_fail("category_length_mismatch_weights", f"Warning about category length mismatch not found. Stdout was: {test_result['stdout']}")
        return
    
    result.add_pass()


def test_equal_length_weighted_categories(result, run_word_generator):
    """Test that equal-length weighted categories work correctly."""
    print("Testing equal-length weighted categories...")
    
    input_content = """
# Same number of unique characters, different weights
P: p{1} t{2} k{3}
B: b{3} d{2} g{1}

CV

# This should work fine (3 unique chars each)
P/B/_
"""
    
    test_result = run_word_generator(["-r", "INPUT_FILE", "OUTPUT_FILE", "30"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("equal_length_weighted_categories", f"Script failed: {test_result['stderr']}")
        return
    
    # Should not have length mismatch warning
    if "different unique character counts" in test_result['stdout']:
        result.add_fail("equal_length_weighted_categories", "Unexpected length mismatch warning")
        return
    
    # Check that P→B replacement worked
    output = test_result['output_file_content']
    if any(char in output for char in 'ptk'):
        result.add_fail("equal_length_weighted_categories", "P→B replacement not applied correctly")
        return
    
    result.add_pass()


def test_backwards_compatibility(result, run_word_generator):
    """Test that non-weighted categories still work (backwards compatibility)."""
    print("Testing backwards compatibility...")
    
    input_content = """
# Mix of weighted and non-weighted categories
V: aeiou           # No weights - should work as before
C: b{2} c d{3} f   # Mixed weights and no weights

CV
CVC

# Simple replacement
a/e/_
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "10"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("backwards_compatibility", f"Script failed: {test_result['stderr']}")
        return
    
    # Should only show weights for C category, not V
    stdout = test_result['stdout']
    if "Category 'V' weights:" in stdout:
        result.add_fail("backwards_compatibility", "Weight info shown for non-weighted category")
        return
    
    if "Category 'C' weights:" not in stdout:
        result.add_fail("backwards_compatibility", "Weight info not shown for weighted category")
        return
    
    # Check that replacement rule still works
    output = test_result['output_file_content']
    if 'a' in output:
        result.add_fail("backwards_compatibility", "Replacement rule a/e/_ not applied")
        return
    
    result.add_pass()

def test_reserved_character_validation(result, run_word_generator):
    """Test that curly braces are properly validated in weight specifications."""
    print("Testing reserved character validation...")
    
    input_content = """
# This should cause an error - using { in category contents
V: a{e}iou

CV
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "5"], input_content)
    
    # Should fail with error about invalid weight specification
    if test_result['returncode'] == 0:
        result.add_fail("reserved_character_validation", "Script should have failed with invalid weight specification")
        return
    
    # Change this line to look for the actual error message:
    if "Invalid weight specification" not in test_result['stdout'] and "Invalid weight specification" not in test_result['stderr']:
        result.add_fail("reserved_character_validation", f"Expected invalid weight specification error, got stdout: '{test_result['stdout']}', stderr: '{test_result['stderr']}'")
        return
    
    result.add_pass()


def test_weight_distribution_statistics(result, run_word_generator):
    """Test weight distribution with statistical analysis."""
    print("Testing weight distribution statistics...")
    
    input_content = """
# Clear weight pattern for statistical testing
V: a{6} e{3} i{1}
C: bcdfg

# Generate many words for statistical analysis
CV
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "200"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("weight_distribution_statistics", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    
    # Count vowel occurrences
    a_count = output.count('a')
    e_count = output.count('e')
    i_count = output.count('i')
    total_aei = a_count + e_count + i_count
    
    if total_aei == 0:
        result.add_fail("weight_distribution_statistics", "No relevant vowels found in output")
        return
    
    # Calculate percentages
    a_pct = a_count / total_aei
    e_pct = e_count / total_aei
    i_pct = i_count / total_aei
    
    # Expected: a=60%, e=30%, i=10% (weights 6:3:1)
    # Allow reasonable variance due to randomness
    if not (0.5 <= a_pct <= 0.7):
        result.add_fail("weight_distribution_statistics", f"'a' percentage {a_pct:.2%} not in expected range 50-70%")
        return
    
    if not (0.2 <= e_pct <= 0.4):
        result.add_fail("weight_distribution_statistics", f"'e' percentage {e_pct:.2%} not in expected range 20-40%")
        return
    
    if not (0.05 <= i_pct <= 0.2):
        result.add_fail("weight_distribution_statistics", f"'i' percentage {i_pct:.2%} not in expected range 5-20%")
        return
    
    result.add_pass()


def test_complex_weighted_replacement_rules(result, run_word_generator):
    """Test complex replacement rules with weighted categories."""
    print("Testing complex weighted replacement rules...")
    
    input_content = """
# Source category heavily weighted toward certain sounds
P: p{1} t{4} k{1}
# Target category with different weighting
B: b{2} d{1} g{3}

# Category-to-category replacement - should work in any environment
P/B/_

-dict
papa tata kaka atta
-end-dict
"""
    
    test_result = run_word_generator(["-dr", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("complex_weighted_replacement", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    # Check that replacements occurred (no P sounds should remain)
    found_p_sounds = False
    for line in lines:
        words = line.split()
        for word in words:
            clean_word = word.split('[')[0].strip()  # Remove rule annotations
            if any(char in clean_word for char in 'ptk'):
                found_p_sounds = True
                break
    
    if found_p_sounds:
        result.add_fail("complex_weighted_replacement", f"Found unreplaced P sounds in output: {output}")
        return
    
    # Check that we have B sounds
    found_b_sounds = False
    for line in lines:
        words = line.split()
        for word in words:
            clean_word = word.split('[')[0].strip()  # Remove rule annotations
            if any(char in clean_word for char in 'bdg'):
                found_b_sounds = True
                break
    
    if not found_b_sounds:
        result.add_fail("complex_weighted_replacement", f"No B sounds found after replacement: {output}")
        return
    
    result.add_pass()


def run_weighted_categories_tests(result, run_word_generator):
    """Run all weighted categories tests."""
    print("\n=== WEIGHTED CATEGORIES TESTS ===")
    
    try:
        test_basic_weighted_categories(result, run_word_generator)
        test_weighted_categories_in_dictionary_mode(result, run_word_generator)
        test_multiple_weighted_categories(result, run_word_generator)
        test_weighted_categories_with_flexible_rules(result, run_word_generator)
        test_category_length_mismatch_with_weights(result, run_word_generator)
        test_equal_length_weighted_categories(result, run_word_generator)
        test_backwards_compatibility(result, run_word_generator)
        test_reserved_character_validation(result, run_word_generator)
        test_weight_distribution_statistics(result, run_word_generator)
        test_complex_weighted_replacement_rules(result, run_word_generator)
    except Exception as e:
        result.add_fail("weighted_categories_tests", f"Weighted categories test suite error: {e}")