#!/usr/bin/env python3
"""
Tests for weighted rules functionality.
"""


def test_basic_weighted_rules(result, run_word_generator):
    """Test basic weighted rule functionality."""
    print("Testing basic weighted rules...")
    
    input_content = """
V: aeiou
C: bcdfg

# Heavily weighted CV, normal weight CVC
CV{10}
CVC
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "100"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("basic_weighted_rules", f"Script failed: {test_result['stderr']}")
        return
    
    # Check that weight information is printed
    if "Rule weights: CV:10" not in test_result['stdout']:
        result.add_fail("basic_weighted_rules", "Weight information not printed correctly")
        return
    
    # Count rule usage in output (2-char vs 3-char words)
    output = test_result['output_file_content']
    lines = [line.strip() for line in output.split('\n') if line.strip()]
    
    if len(lines) != 100:
        result.add_fail("basic_weighted_rules", f"Expected 100 words, got {len(lines)}")
        return
    
    cv_count = sum(1 for word in lines if len(word) == 2)  # CV pattern
    cvc_count = sum(1 for word in lines if len(word) == 3)  # CVC pattern
    
    total_counted = cv_count + cvc_count
    if total_counted != 100:
        result.add_fail("basic_weighted_rules", f"Word length analysis failed: CV={cv_count}, CVC={cvc_count}, total={total_counted}")
        return
    
    # With CV:10 and CVC:1, expect roughly 90%+ CV words
    cv_percentage = cv_count / 100
    if cv_percentage < 0.8:  # Allow some variance due to randomness
        result.add_fail("basic_weighted_rules", f"Expected CV to dominate (~90%+), got {cv_percentage:.2%}")
        return
    
    result.add_pass()


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


def test_multiple_weighted_rules(result, run_word_generator):
    """Test multiple rules with different weights."""
    print("Testing multiple weighted rules...")
    
    input_content = """
V: ae
C: bc

CV{2}
CVC{3}
CVCC{4}
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "120"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("multiple_weighted_rules", f"Script failed: {test_result['stderr']}")
        return
    
    # Check that weight information is printed (any non-default weights should be shown)
    stdout = test_result['stdout']
    if not has_rule_weights_displayed(stdout):
        result.add_fail("multiple_weighted_rules", "No weight information displayed")
        return
    
    # Analyze word length distribution
    output = test_result['output_file_content']
    words = extract_words_from_output(output)
    
    cv_count = sum(1 for word in words if len(word) == 2)     # CV
    cvc_count = sum(1 for word in words if len(word) == 3)    # CVC
    cvcc_count = sum(1 for word in words if len(word) == 4)   # CVCC
    
    total = cv_count + cvc_count + cvcc_count
    if total != 120:
        result.add_fail("multiple_weighted_rules", f"Word count mismatch: expected 120, got {total}")
        return
    
    # Expected distribution: CV:2, CVC:3, CVCC:4 (total weight 9)
    # So roughly CV=22%, CVC=33%, CVCC=44%
    cvcc_percentage = cvcc_count / 120
    if cvcc_percentage < 0.35:  # CVCC should dominate
        result.add_fail("multiple_weighted_rules", f"Expected CVCC to dominate (~44%), got {cvcc_percentage:.2%}")
        return
    
    result.add_pass()


def test_weighted_rules_with_flexible_syntax(result, run_word_generator):
    """Test weighted rules combined with flexible rule syntax."""
    print("Testing weighted rules with flexible syntax...")
    
    input_content = """
V: aei
C: bc

CV(C){5}
V(C)V{2}
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "70"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("weighted_flexible_rules", f"Script failed: {test_result['stderr']}")
        return
    
    # Check for expansion messages
    stdout = test_result['stdout']
    if "Expanded rule 'CV(C)' (weight 5) into 2 variants: CV, CVC" not in stdout:
        result.add_fail("weighted_flexible_rules", "Expected expansion message with weight not found")
        return
    
    if "Expanded rule 'V(C)V' (weight 2) into 2 variants: VV, VCV" not in stdout:
        result.add_fail("weighted_flexible_rules", "Expected expansion message for V(C)V not found")
        return
    
    # Check weight information
    if "Rule weights:" not in stdout:
        result.add_fail("weighted_flexible_rules", "Weight information not displayed")
        return
    
    result.add_pass()


def test_backwards_compatibility_unweighted_rules(result, run_word_generator):
    """Test that unweighted rules still work (backwards compatibility)."""
    print("Testing backwards compatibility with unweighted rules...")
    
    input_content = """
V: aeiou
C: bcdfg

CV
CVC
CVCC
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "30"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("backwards_compatibility_rules", f"Script failed: {test_result['stderr']}")
        return
    
    # Should NOT show weight information for unweighted rules
    if "Rule weights:" in test_result['stdout']:
        result.add_fail("backwards_compatibility_rules", "Weight info shown for unweighted rules")
        return
    
    # Should still generate words of all patterns
    output = test_result['output_file_content']
    lines = [line.strip() for line in output.split('\n') if line.strip()]
    
    lengths = set(len(word) for word in lines)
    expected_lengths = {2, 3, 4}  # CV, CVC, CVCC
    
    if not expected_lengths.issubset(lengths):
        result.add_fail("backwards_compatibility_rules", f"Not all rule patterns used: got lengths {lengths}")
        return
    
    result.add_pass()


def test_mixed_weighted_and_unweighted_rules(result, run_word_generator):
    """Test mixing weighted and unweighted rules."""
    print("Testing mixed weighted and unweighted rules...")
    
    input_content = """
V: ae
C: bc

CV          # No weight (defaults to 1)
CVC{3}      # Weighted
CVCC        # No weight (defaults to 1)
CVCV{2}     # Weighted
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "70"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("mixed_weighted_rules", f"Script failed: {test_result['stderr']}")
        return
    
    # Should show only the weighted rules in weight info
    stdout = test_result['stdout']
    if "CVC:3" not in stdout or "CVCV:2" not in stdout:
        result.add_fail("mixed_weighted_rules", "Weighted rule info missing")
        return
    
    # Should not show CV:1 or CVCC:1 since they're default weights
    if "CV:1" in stdout or "CVCC:1" in stdout:
        result.add_fail("mixed_weighted_rules", "Default weights should not be displayed")
        return
    
    result.add_pass()


def test_rule_weight_syntax_validation(result, run_word_generator):
    """Test validation of rule weight syntax."""
    print("Testing rule weight syntax validation...")
    
    # Test invalid weight (non-numeric)
    input_content = """
V: ae
C: bc

CV{abc}
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "5"], input_content)
    
    if test_result['returncode'] == 0:
        result.add_fail("rule_weight_validation", "Script should have failed with invalid weight")
        return
    
    if "Invalid weight value" not in test_result['stdout'] and "Invalid weight value" not in test_result['stderr']:
        result.add_fail("rule_weight_validation", f"Expected weight validation error, got: {test_result['stderr']}")
        return
    
    result.add_pass()


def test_rule_weight_position_validation(result, run_word_generator):
    """Test that weights must be at end of rule."""
    print("Testing rule weight position validation...")
    
    input_content = """
V: ae
C: bc

CV{2}CC  # Weight not at end
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "5"], input_content)
    
    if test_result['returncode'] == 0:
        result.add_fail("rule_weight_position", "Script should have failed with weight not at end")
        return
    
    combined_output = test_result['stdout'] + test_result['stderr']
    if "Invalid weight specification position" not in combined_output:
        result.add_fail("rule_weight_position", f"Expected position validation error, got: {combined_output}")
        return
    
    result.add_pass()


def test_unmatched_braces_validation(result, run_word_generator):
    """Test validation of unmatched braces in rules."""
    print("Testing unmatched braces validation...")
    
    input_content = """
V: ae
C: bc

CV{2
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "5"], input_content)
    
    if test_result['returncode'] == 0:
        result.add_fail("unmatched_braces_rules", "Script should have failed with unmatched braces")
        return
    
    combined_output = test_result['stdout'] + test_result['stderr']
    if "Unmatched braces" not in combined_output:
        result.add_fail("unmatched_braces_rules", f"Expected unmatched braces error, got: {combined_output}")
        return
    
    result.add_pass()


def test_zero_weight_validation(result, run_word_generator):
    """Test that zero weights are rejected."""
    print("Testing zero weight validation...")
    
    input_content = """
V: ae
C: bc

CV{0}
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "5"], input_content)
    
    if test_result['returncode'] == 0:
        result.add_fail("zero_weight_validation", "Script should have failed with zero weight")
        return
    
    combined_output = test_result['stdout'] + test_result['stderr']
    if "Invalid weight value" not in combined_output:
        result.add_fail("zero_weight_validation", f"Expected zero weight error, got: {combined_output}")
        return
    
    result.add_pass()


def test_weighted_rules_with_sound_changes(result, run_word_generator):
    """Test weighted rules work with sound change rules."""
    print("Testing weighted rules with sound changes...")
    
    input_content = """
V: aeiou
C: bcdfg

CV{8}
CVC{2}

# Sound change
a/e/_
"""
    
    test_result = run_word_generator(["-r", "INPUT_FILE", "OUTPUT_FILE", "50"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("weighted_rules_sound_changes", f"Script failed: {test_result['stderr']}")
        return
    
    # Check that weight information appears
    if not has_rule_weights_displayed(test_result['stdout']):
        result.add_fail("weighted_rules_sound_changes", "Weight information missing")
        return
    
    # Check that sound changes were applied (no 'a' should remain in actual words)
    output = test_result['output_file_content']
    words = extract_words_from_output(output)
    word_text = ' '.join(words)
    
    if 'a' in word_text:
        result.add_fail("weighted_rules_sound_changes", f"Sound change rule not applied to words: {words}")
        return
    
    result.add_pass()


def test_weighted_rules_with_dictionary_mode(result, run_word_generator):
    """Test that weighted rules info is shown even in dictionary mode."""
    print("Testing weighted rules with dictionary mode...")
    
    input_content = """
V: aeiou
C: bcdfg

# These rules won't be used in dict mode, but should still be parsed
CV{5}
CVC{3}

# Sound change
a/e/_

-dict
banana casa villa
-end-dict
"""
    
    test_result = run_word_generator(["-dr", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("weighted_rules_dictionary", f"Script failed: {test_result['stderr']}")
        return
    
    # Rules should still be parsed and weights displayed (check for any weight display format)
    if not has_rule_weights_displayed(test_result['stdout']):
        result.add_fail("weighted_rules_dictionary", "Rule weight information missing in dictionary mode")
        return
    
    # Sound changes should still be applied (check actual words, not rule annotations)
    output = test_result['output_file_content']
    words = extract_words_from_output(output)
    word_text = ' '.join(words)
    
    if 'a' in word_text:
        result.add_fail("weighted_rules_dictionary", f"Sound changes not applied in dictionary mode: {words}")
        return
    
    result.add_pass()


def test_statistical_distribution(result, run_word_generator):
    """Test statistical distribution of weighted rules over many words."""
    print("Testing statistical distribution of weighted rules...")
    
    input_content = """
V: a
C: b

CV{1}
CVC{4}
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "500"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("statistical_distribution", f"Script failed: {test_result['stderr']}")
        return
    
    # Analyze distribution
    output = test_result['output_file_content']
    lines = [line.strip() for line in output.split('\n') if line.strip()]
    
    cv_count = sum(1 for word in lines if len(word) == 2)   # CV
    cvc_count = sum(1 for word in lines if len(word) == 3)  # CVC
    
    total = cv_count + cvc_count
    if total != 500:
        result.add_fail("statistical_distribution", f"Word count mismatch: expected 500, got {total}")
        return
    
    # Expected: CV:1, CVC:4 -> CV=20%, CVC=80%
    cvc_percentage = cvc_count / 500
    
    # Allow reasonable variance (should be around 80% ± 5%)
    if not (0.75 <= cvc_percentage <= 0.85):
        result.add_fail("statistical_distribution", f"CVC percentage {cvc_percentage:.2%} not in expected range 75-85%")
        return
    
    result.add_pass()


def test_large_weights(result, run_word_generator):
    """Test that large weights work correctly."""
    print("Testing large weights...")
    
    input_content = """
V: a
C: b

CV{100}
CVC{1}
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "101"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("large_weights", f"Script failed: {test_result['stderr']}")
        return
    
    # Check weight display
    if "Rule weights: CV:100" not in test_result['stdout']:
        result.add_fail("large_weights", "Large weight not displayed correctly")
        return
    
    # With CV:100 vs CVC:1, expect almost all CV words
    output = test_result['output_file_content']
    lines = [line.strip() for line in output.split('\n') if line.strip()]
    
    cv_count = sum(1 for word in lines if len(word) == 2)
    cv_percentage = cv_count / 101
    
    if cv_percentage < 0.95:  # Should be ~99%
        result.add_fail("large_weights", f"Expected CV to heavily dominate with weight 100, got {cv_percentage:.2%}")
        return
    
    result.add_pass()


def run_weighted_rules_tests(result, run_word_generator):
    """Run all weighted rules tests."""
    print("\n=== WEIGHTED RULES TESTS ===")
    
    try:
        test_basic_weighted_rules(result, run_word_generator)
        test_multiple_weighted_rules(result, run_word_generator)
        test_weighted_rules_with_flexible_syntax(result, run_word_generator)
        test_backwards_compatibility_unweighted_rules(result, run_word_generator)
        test_mixed_weighted_and_unweighted_rules(result, run_word_generator)
        test_rule_weight_syntax_validation(result, run_word_generator)
        test_rule_weight_position_validation(result, run_word_generator)
        test_unmatched_braces_validation(result, run_word_generator)
        test_zero_weight_validation(result, run_word_generator)
        test_weighted_rules_with_sound_changes(result, run_word_generator)
        test_weighted_rules_with_dictionary_mode(result, run_word_generator)
        test_statistical_distribution(result, run_word_generator)
        test_large_weights(result, run_word_generator)
    except Exception as e:
        result.add_fail("weighted_rules_tests", f"Weighted rules test suite error: {e}")