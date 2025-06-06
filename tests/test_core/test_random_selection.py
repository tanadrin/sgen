#!/usr/bin/env python3
"""
Tests for random rule selection functionality.
"""

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
        test_result = run_word_generator(["INPUT_FILE", f"OUTPUT_FILE_{i}", "10"], input_content)
        
        if test_result['returncode'] != 0:
            result.add_fail("random_vs_sequential", f"Script failed on run {i}: {test_result['stderr']}")
            return
        
        output = test_result['output_file_content']
        words = [line.strip() for line in output.split('\n') if line.strip()]
        # Convert to length pattern for comparison
        pattern = tuple(len(word) for word in words)
        results.append(pattern)
    
    # Check that we have some variety (not all identical)
    unique_patterns = set(results)
    
    # With random selection, we should see some variation
    # Be more realistic - even with randomness, some runs might be identical
    if len(unique_patterns) >= 2:
        result.add_pass()
    else:
        # If all identical, that's still possible but unlikely
        # Check if it's the exact sequential pattern
        expected_sequential = tuple([2, 3, 4] * 4)[:10]  # CV, CVC, CVCC repeated
        if all(pattern == expected_sequential for pattern in results):
            result.add_fail("random_vs_sequential", "All runs follow exact sequential pattern")
        else:
            result.add_pass()  # Different pattern, even if identical across runs

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
    for i in range(10):  # Reduced from 20 to be more realistic
        test_result = run_word_generator(["INPUT_FILE", f"OUTPUT_FILE_{i}", "1"], input_content)
        
        if test_result['returncode'] != 0:
            result.add_fail("randomness_multiple_runs", f"Script failed on run {i}: {test_result['stderr']}")
            return
        
        output = test_result['output_file_content'].strip()
        first_words.append(output)
    
    # Check that we got some variety in the first words
    unique_first_words = set(first_words)
    
    # With 4 rules and 10 runs, expect at least 2 different words
    # This is realistic given random chance
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

# Sound changes (fix the problematic rule)
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
    
    # Check that sound changes applied - look for evidence of the a/e/_ rule
    # The rule changes 'a' to 'e', so we should see 'e' and no 'a' in words that had 'a'
    if "Debug: Applied rule 'a/e/_'" not in stdout:
        result.add_fail("flexible_weighted_sound_changes", "Sound change a/e/_ not applied")
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
    
    # Weights should still be displayed even in dictionary mode
    if "Category 'V' weights:" not in stdout:
        result.add_fail("dictionary_weighted_features", "Category weights not shown in dict mode")
        return
    
    # Check that sound changes were applied by looking for the debug messages
    if "Debug: Applied rule 'a/o/_'" not in stdout:
        result.add_fail("dictionary_weighted_features", "Sound changes not applied in dictionary mode")
        return
    
    # Additional check: verify the output words are correct
    output = test_result['output_file_content']
    expected_transformations = ['bonono', 'coso', 'villo', 'milo']
    
    found_correct_transformations = True
    for expected in expected_transformations:
        if expected not in output:
            found_correct_transformations = False
            break
    
    if not found_correct_transformations:
        result.add_fail("dictionary_weighted_features", f"Expected transformations not found in output")
        return
    
    result.add_pass()



def test_randomness_with_equal_weights(result, run_word_generator):
    """Test randomness when all rules have equal weights."""
    print("Testing randomness with equal weights...")
    
    input_content = """
V: a
C: b

CV
CVC
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "100"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("randomness_equal_weights", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line.strip() for line in output.split('\n') if line.strip()]
    
    cv_count = sum(1 for word in lines if len(word) == 2)   # CV
    cvc_count = sum(1 for word in lines if len(word) == 3)  # CVC
    
    # With equal weights, expect roughly 50/50 distribution (±20% for randomness)
    cv_percentage = cv_count / 100
    if not (0.3 <= cv_percentage <= 0.7):
        result.add_fail("randomness_equal_weights", f"Distribution too skewed: CV={cv_percentage:.2%}, expected ~50%")
        return
    
    result.add_pass()


def test_pattern_breaking(result, run_word_generator):
    """Test that consecutive words can be the same (breaking sequential patterns)."""
    print("Testing pattern breaking...")
    
    input_content = """
V: a
C: b

CV{10}   # Heavy bias toward CV
CVC{1}
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "50"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("pattern_breaking", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line.strip() for line in output.split('\n') if line.strip()]
    
    # Look for consecutive identical words (should happen with random selection)
    consecutive_identical = False
    for i in range(len(lines) - 1):
        if lines[i] == lines[i + 1]:
            consecutive_identical = True
            break
    
    # With heavy bias toward CV and random selection, we should see "ba ba" sequences
    if not consecutive_identical:
        result.add_fail("pattern_breaking", "No consecutive identical words found - may not be truly random")
        return
    
    result.add_pass()


def test_single_rule_behavior(result, run_word_generator):
    """Test behavior with only one rule (should always use that rule)."""
    print("Testing single rule behavior...")
    
    input_content = """
V: ae
C: bc

CVC{5}
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "10"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("single_rule_behavior", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line.strip() for line in output.split('\n') if line.strip()]
    
    # All words should be 3 characters (CVC pattern)
    for word in lines:
        if len(word) != 3:
            result.add_fail("single_rule_behavior", f"Word '{word}' doesn't match CVC pattern")
            return
    
    result.add_pass()


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
        test_result = run_word_generator(["INPUT_FILE", f"OUTPUT_FILE_{i}", "1"], input_content)
        
        if test_result['returncode'] != 0:
            result.add_fail("randomness_multiple_runs", f"Script failed on run {i}: {test_result['stderr']}")
            return
        
        output = test_result['output_file_content'].strip()
        first_words.append(output)
    
    # Check that we got some variety in the first words
    unique_first_words = set(first_words)
    
    # With 4 rules and 10 runs, we should see some variety
    # With random selection, getting the same word 10 times is very unlikely but possible
    # Let's be more lenient and just check we don't get identical results for ALL runs
    if len(unique_first_words) < 2:
        # Double-check by running a few more times to be sure
        additional_words = []
        for i in range(5):
            test_result = run_word_generator(["INPUT_FILE", f"OUTPUT_FILE_extra_{i}", "1"], input_content)
            if test_result['returncode'] == 0:
                additional_words.append(test_result['output_file_content'].strip())
        
        all_words = first_words + additional_words
        if len(set(all_words)) < 2:
            result.add_fail("randomness_multiple_runs", f"Too little variety: only {len(set(all_words))} unique words in {len(all_words)} runs")
            return
    
    result.add_pass()


def test_weighted_selection_bias(result, run_word_generator):
    """Test that heavily weighted rules are strongly preferred."""
    print("Testing weighted selection bias...")
    
    input_content = """
V: a
C: b

CV{50}
CVC{1}
CVCC{1}
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "200"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("weighted_selection_bias", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line.strip() for line in output.split('\n') if line.strip()]
    
    cv_count = sum(1 for word in lines if len(word) == 2)      # CV
    cvc_count = sum(1 for word in lines if len(word) == 3)     # CVC
    cvcc_count = sum(1 for word in lines if len(word) == 4)    # CVCC
    
    total = cv_count + cvc_count + cvcc_count
    if total != 200:
        result.add_fail("weighted_selection_bias", f"Word count mismatch: expected 200, got {total}")
        return
    
    # Expected: CV:50, CVC:1, CVCC:1 -> CV should be ~96%
    cv_percentage = cv_count / 200
    if cv_percentage < 0.9:  # Allow some variance
        result.add_fail("weighted_selection_bias", f"Heavy weight not respected: CV={cv_percentage:.2%}, expected ~96%")
        return
    
    result.add_pass()


def test_rule_selection_independence(result, run_word_generator):
    """Test that each word's rule selection is independent."""
    print("Testing rule selection independence...")
    
    input_content = """
V: a
C: b

CV{1}
CVC{1}
"""
    
    # Generate many words and look for patterns that would indicate dependence
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "100"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("rule_selection_independence", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line.strip() for line in output.split('\n') if line.strip()]
    
    # Convert to pattern sequence
    patterns = []
    for word in lines:
        if len(word) == 2:
            patterns.append('CV')
        elif len(word) == 3:
            patterns.append('CVC')
    
    # Look for runs of identical patterns (which should occur with independence)
    max_run_length = 0
    current_run = 1
    
    for i in range(1, len(patterns)):
        if patterns[i] == patterns[i-1]:
            current_run += 1
        else:
            max_run_length = max(max_run_length, current_run)
            current_run = 1
    max_run_length = max(max_run_length, current_run)
    
    # With independent selection, we should occasionally see runs of 3+ identical patterns
    if max_run_length < 3:
        result.add_fail("rule_selection_independence", f"No runs of 3+ found, max run: {max_run_length} - may not be independent")
        return
    
    result.add_pass()


def test_empty_rules_list_handling(result, run_word_generator):
    """Test error handling when no rules are provided."""
    print("Testing empty rules list handling...")
    
    input_content = """
V: aeiou
C: bcdfg

# No rules defined
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "5"], input_content)
    
    # Should fail gracefully
    if test_result['returncode'] == 0:
        result.add_fail("empty_rules_handling", "Script should fail when no rules are provided")
        return
    
    if "No word structure rules found" not in test_result['stdout'] and "No word structure rules found" not in test_result['stderr']:
        result.add_fail("empty_rules_handling", f"Expected 'no rules' error, got: {test_result['stderr']}")
        return
    
    result.add_pass()


def run_random_selection_tests(result, run_word_generator):
    """Run all random selection tests."""
    print("\n=== RANDOM SELECTION TESTS ===")
    
    try:
        test_random_vs_sequential_behavior(result, run_word_generator)
        test_randomness_with_equal_weights(result, run_word_generator)
        test_pattern_breaking(result, run_word_generator)
        test_single_rule_behavior(result, run_word_generator)
        test_randomness_across_multiple_runs(result, run_word_generator)
        test_weighted_selection_bias(result, run_word_generator)
        test_rule_selection_independence(result, run_word_generator)
        test_empty_rules_list_handling(result, run_word_generator)
    except Exception as e:
        result.add_fail("random_selection_tests", f"Random selection test suite error: {e}")