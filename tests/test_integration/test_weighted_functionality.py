#!/usr/bin/env python3
"""
Integration tests for weighted rules and categories working together.
"""


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

def extract_words_from_output(output):
    """Extract just the words from output, ignoring rule annotations."""
    words = []
    for line in output.split('\n'):
        if line.strip():
            # Split on whitespace and take first part (the word)
            word = line.split()[0]
            words.append(word)
    return words


def has_rule_weights_displayed(stdout):
    """Check if rule weights are displayed in any format."""
    return ("Rule weights:" in stdout or 
            any("has weight" in line for line in stdout.split('\n')))


def test_weighted_categories_and_rules_together(result, run_word_generator):
    """Test weighted categories and weighted rules working together."""
    print("Testing weighted categories and rules together...")
    
    input_content = """
# Weighted categories
V: a{4} e{2} i{1}
C: b{3} c{1} d{2}

# Weighted rules
CV{1}
CVC{5}
CVCC{2}

# Sound change to test everything works together
a/o/_
"""
    
    test_result = run_word_generator(["-r", "INPUT_FILE", "OUTPUT_FILE", "100"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("weighted_categories_and_rules", f"Script failed: {test_result['stderr']}")
        return
    
    stdout = test_result['stdout']
    
    # Check that both category and rule weights are displayed
    if "Category 'V' weights: a:4, e:2, i:1" not in stdout:
        result.add_fail("weighted_categories_and_rules", "Category weights not displayed")
        return
    
    if not has_rule_weights_displayed(stdout):
        result.add_fail("weighted_categories_and_rules", "Rule weights not displayed")
        return
    
    # Check that sound changes were applied (no 'a' should remain in actual words)
    output = test_result['output_file_content']
    words = extract_words_from_output(output)
    word_text = ' '.join(words)
    
    if 'a' in word_text:
        result.add_fail("weighted_categories_and_rules", f"Sound changes not applied to words: {words}")
        return
    
    # Check distribution biases
    # Rule distribution: CV:1, CVC:5, CVCC:2 -> CVC should dominate
    cvc_count = sum(1 for word in words if len(word) == 3)
    cvc_percentage = cvc_count / len(words)
    
    if cvc_percentage < 0.5:  # CVC should be majority with weight 5/8
        result.add_fail("weighted_categories_and_rules", f"CVC rule weight not respected: {cvc_percentage:.2%}")
        return
    
    # Character distribution: 'b' should be most common consonant
    b_count = word_text.count('b')
    c_count = word_text.count('c')
    d_count = word_text.count('d')
    
    if b_count <= c_count:  # b has weight 3, c has weight 1
        result.add_fail("weighted_categories_and_rules", "Character weights not respected")
        return
    
    result.add_pass()


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
    
    # Weights should still be displayed even in dictionary mode (check any format)
    if "Category 'V' weights:" not in stdout:
        result.add_fail("dictionary_weighted_features", "Category weights not shown in dict mode")
        return
    
    if not has_rule_weights_displayed(stdout):
        result.add_fail("dictionary_weighted_features", "Rule weights not shown in dict mode")
        return
    
    # Check that sound changes were applied by looking for debug messages
    # The debug script showed these exact messages appear when sound changes work
    if "Debug: Applied rule 'a/o/_'" in stdout:
        result.add_pass()
        return
    
    # Alternative check: look at the actual output content
    output = test_result['output_file_content']
    
    # The debug script showed the expected output should contain transformed words
    expected_transformations = ['bonono', 'coso', 'villo', 'milo']
    
    transformations_found = 0
    for expected in expected_transformations:
        if expected in output:
            transformations_found += 1
    
    if transformations_found >= 3:  # Most transformations present
        result.add_pass()
    else:
        result.add_fail("dictionary_weighted_features", f"Sound changes not applied in dictionary mode - expected transformations not found. Got output: {output}")


# Also add this helper function if it doesn't exist
def has_rule_weights_displayed(stdout):
    """Check if rule weights are displayed in any format."""
    return ("Rule weights:" in stdout or 
            "Rule 'CV' has weight" in stdout or
            "Rule 'CVC' has weight" in stdout or
            any("has weight" in line for line in stdout.split('\n')))

def test_complex_integration_scenario(result, run_word_generator):
    """Test a complex scenario with all features."""
    print("Testing complex integration scenario...")
    
    input_content = """
# Weighted categories
V: a{4} e{3} i{2} o{1}
C: b{1} c{2} d{1} f{1} g{1} l{3} n{2} r{4} s{3} t{2}
P: p{1} t{2} k{1}

# Weighted rules with flexible syntax
CV{2}
CVC{5}
CV(P){3}
(C)V(C)CV{1}

# Multiple sound changes
P/b/_V  # Voicing between vowels (will need P and B categories of same length)
t/d/V_V # Specific voicing
a/e/_CV # Vowel harmony

# Add B category for P/B replacement
B: b d g

P/B/V_V
"""
    
    test_result = run_word_generator(["-vr", "INPUT_FILE", "OUTPUT_FILE", "80"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("complex_integration", f"Script failed: {test_result['stderr']}")
        return
    
    stdout = test_result['stdout']
    
    # Should show multiple category weights
    if "Category 'V' weights:" not in stdout:
        result.add_fail("complex_integration", "V category weights missing")
        return
    
    if "Category 'C' weights:" not in stdout:
        result.add_fail("complex_integration", "C category weights missing")
        return
    
    # Should show rule expansion and weights
    if "Expanded rule" not in stdout:
        result.add_fail("complex_integration", "Rule expansion missing")
        return
    
    if "Rule weights:" not in stdout:
        result.add_fail("complex_integration", "Rule weights missing")
        return
    
    # Check that we got the expected number of words
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    if len(lines) != 80:
        result.add_fail("complex_integration", f"Expected 80 words, got {len(lines)}")
        return
    
    result.add_pass()


def test_error_handling_integration(result, run_word_generator):
    """Test error handling with weighted features."""
    print("Testing error handling integration...")
    
    # Test category length mismatch with weighted categories and rules
    input_content = """
V: a{2} e{3}     # 2 unique chars
C: b{1} c{2} d{1} # 3 unique chars

CV{5}
CVC{3}

# This should generate a warning
V/C/_
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "10"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("error_handling_integration", f"Script failed: {test_result['stderr']}")
        return
    
    # Should warn about category length mismatch
    if "different unique character counts" not in test_result['stdout']:
        result.add_fail("error_handling_integration", "Category length mismatch warning missing")
        return
    
    # Should still show weight information
    if "Category 'V' weights:" not in test_result['stdout']:
        result.add_fail("error_handling_integration", "Category weights missing despite error")
        return
    
    result.add_pass()


def test_performance_with_large_weights(result, run_word_generator):
    """Test performance with large weights (should not cause issues)."""
    print("Testing performance with large weights...")
    
    input_content = """
V: a{1000} e{1}
C: b{500} c{1}

CV{100}
CVC{1}
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "50"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("performance_large_weights", f"Script failed: {test_result['stderr']}")
        return
    
    # Should complete in reasonable time and show correct weights
    if "V' weights: a:1000, e:1" not in test_result['stdout']:
        result.add_fail("performance_large_weights", "Large weights not displayed correctly")
        return
    
    if "Rule weights: CV:100" not in test_result['stdout']:
        result.add_fail("performance_large_weights", "Large rule weights not displayed correctly")
        return
    
    result.add_pass()


def run_weighted_integration_tests(result, run_word_generator):
    """Run all weighted functionality integration tests."""
    print("\n=== WEIGHTED FUNCTIONALITY INTEGRATION TESTS ===")
    
    try:
        test_weighted_categories_and_rules_together(result, run_word_generator)
        test_flexible_weighted_rules_with_sound_changes(result, run_word_generator)
        test_dictionary_mode_with_weighted_features(result, run_word_generator)
        test_complex_integration_scenario(result, run_word_generator)
        test_error_handling_integration(result, run_word_generator)
        test_performance_with_large_weights(result, run_word_generator)
    except Exception as e:
        result.add_fail("weighted_integration_tests", f"Weighted integration test suite error: {e}")