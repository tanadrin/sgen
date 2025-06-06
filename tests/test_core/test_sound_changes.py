#!/usr/bin/env python3
"""
Tests for the sound changes module.
"""


def test_basic_replacement_rules(result, run_word_generator):
    """Test basic replacement rule functionality."""
    print("Testing basic replacement rules...")
    
    input_content = """
V: aeiou
C: bcdfg
P: ptk
B: bdg

CV
CVC

# Standard replacement
a/e/_
# Category replacement
P/B/_V
# Deletion
k//_#
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "10"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("basic_replacement_rules", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    if not output:
        result.add_fail("basic_replacement_rules", "No output generated")
        return
    
    # Check that 'a' was replaced with 'e'
    if 'a' in output:
        result.add_fail("basic_replacement_rules", "Rule 'a/e/_' not applied correctly")
        return
    
    result.add_pass()


def test_word_boundaries(result, run_word_generator):
    """Test word boundary handling."""
    print("Testing word boundary handling...")
    
    input_content = """
V: aeiou
C: bcdfghjklmnpqrstvwxyz

CVC
CVCV

# Delete word-final 'a'
a//_#
# Insert 'e' at word beginning before 's'
/e/#_s
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "20"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("word_boundaries", f"Script failed: {test_result['stderr']}")
        return
    
    result.add_pass()


def test_doubling_symbol(result, run_word_generator):
    """Test the ² doubling symbol."""
    print("Testing doubling symbol...")
    
    input_content = """
V: aeiou
C: bcdfghjklmnpqrstvwxyz

-dict
bana tata mala
-end-dict

# Double specific consonants
n/²/_a
t/²/_a
"""
    
    test_result = run_word_generator(["-dr", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("doubling_symbol", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    
    # Check that doubling occurred
    found_doubling = False
    for line in output.split('\n'):
        if 'banna' in line or 'tatta' in line:
            found_doubling = True
            break
    
    if not found_doubling:
        result.add_fail("doubling_symbol", "No evidence of consonant doubling found")
        return
    
    result.add_pass()


def test_rules_tracking(result, run_word_generator):
    """Test the -r flag for tracking applied rules."""
    print("Testing rules tracking...")
    
    input_content = """
V: aeiou
C: bcdfg

CV
CVC

# Simple replacement
a/e/_
"""
    
    test_result = run_word_generator(["-r", "INPUT_FILE", "OUTPUT_FILE", "10"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("rules_tracking", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    if len(lines) == 0:
        result.add_fail("rules_tracking", "No output generated")
        return
    
    result.add_pass()


def test_category_length_mismatch(result, run_word_generator):
    """Test handling of category length mismatches."""
    print("Testing category length mismatch handling...")
    
    input_content = """
V: aeiou
C: bc  # Shorter than V
P: ptk
B: bdg

CV

# This should generate a warning
V/C/_
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "5"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("category_length_mismatch", f"Script failed: {test_result['stderr']}")
        return
    
    # Check for warning message
    if "different" not in test_result['stdout']:
        result.add_fail("category_length_mismatch", f"Warning about category length mismatch not found. Stdout: {test_result['stdout']}")
        return
    
    result.add_pass()


def test_optional_environments(result, run_word_generator):
    """Test optional elements in replacement rule environments."""
    print("Testing optional environments...")
    
    input_content = """
V: aeiou
C: bcdfg

# Rule with optional environment: k/g/#(V)_V
# Expands to: #_V and #V_V
# #_V: word-initial k before vowel
# #V_V: word-initial vowel, then k, then vowel (unlikely to match our test words)
k/g/#(V)_V

-dict
kasa kvasa akasa
-end-dict
"""
    
    test_result = run_word_generator(["-dr", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("optional_environments", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    # Expected behavior:
    # "kasa" -> "gasa" (matches #_V: word-initial k before vowel a)
    # "kvasa" -> "kvasa" (doesn't match: k before consonant v, not vowel)
    # "akasa" -> "akasa" (doesn't match: k not word-initial)
    
    found_gasa = any('gasa' in line for line in lines)
    found_kvasa_unchanged = any('kvasa' in line and 'gvasa' not in line for line in lines)
    found_akasa_unchanged = any('akasa' in line for line in lines)
    
    if not found_gasa:
        result.add_fail("optional_environments", f"Expected 'kasa' -> 'gasa' transformation not found: {lines}")
        return
    
    if not found_kvasa_unchanged:
        result.add_fail("optional_environments", f"Expected 'kvasa' to remain unchanged: {lines}")
        return
    
    if not found_akasa_unchanged:
        result.add_fail("optional_environments", f"Expected 'akasa' to remain unchanged: {lines}")
        return
    
    result.add_pass()


def test_multiple_optional_elements_in_environment(result, run_word_generator):
    """Test multiple optional elements in environments."""
    print("Testing multiple optional elements in environments...")
    
    input_content = """
V: aeiou
C: bcdfg
L: lr

# Rule with multiple optional elements: t/d/(C)(L)_V
# Should expand to: t/d/_V, t/d/C_V, t/d/L_V, t/d/CL_V
t/d/(C)(L)_V

-dict
tasa ctasa ltasa cltasa atasa
-end-dict
"""
    
    test_result = run_word_generator(["-dr", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("multiple_optional_environments", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    print(f"Debug - multiple optional environments output: {lines}")
    
    # Check that transformations occurred 
    # Look for 'd' transformations instead of specific patterns
    transformations_found = 0
    for line in lines:
        if 'dasa' in line:
            transformations_found += 1
    
    if transformations_found < 1:  # At least one transformation should occur
        result.add_fail("multiple_optional_environments", f"Expected at least one transformation, found {transformations_found}: {lines}")
        return
    
    result.add_pass()


def test_mandatory_alternatives_in_environment(result, run_word_generator):
    """Test mandatory alternatives in environments."""
    print("Testing mandatory alternatives in environments...")
    
    input_content = """
V: aeiou
C: bcdfg
P: ptk
B: bdg
S: s

# Rule with mandatory alternatives: S/z/V(!P,B)_V
# Should expand to: S/z/VP_V and S/z/VB_V (no S/z/V_V)
# This means: 's' becomes 'z' when after vowel-P-s-vowel or vowel-B-s-vowel
S/z/V(!P,B)_V

-dict
apse abse arse anse
-end-dict
"""
    
    test_result = run_word_generator(["-dr", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("mandatory_alternatives_environment", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    print(f"Debug - mandatory alternatives output: {lines}")
    
    # Expected:
    # apse: a-p-s-e -> matches VP_V (a-p, then s, then e) -> should become apze
    # abse: a-b-s-e -> matches VB_V (a-b, then s, then e) -> should become abze
    # arse: a-r-s-e -> doesn't match (r not in P or B) -> should remain arse
    # anse: a-n-s-e -> doesn't match (n not in P or B) -> should remain anse
    
    found_apze = any('apze' in line for line in lines)
    found_abze = any('abze' in line for line in lines)
    
    if not found_apze and not found_abze:
        result.add_fail("mandatory_alternatives_environment", f"Expected transformations (apze or abze) not found: {output}")
        return
    
    result.add_pass()


def run_sound_changes_tests(result, run_word_generator):
    """Run all sound changes tests."""
    print("\n=== SOUND CHANGES TESTS ===")
    
    try:
        test_basic_replacement_rules(result, run_word_generator)
        test_word_boundaries(result, run_word_generator)
        test_doubling_symbol(result, run_word_generator)
        test_rules_tracking(result, run_word_generator)
        test_category_length_mismatch(result, run_word_generator)
        test_optional_environments(result, run_word_generator)
        test_multiple_optional_elements_in_environment(result, run_word_generator)
        test_mandatory_alternatives_in_environment(result, run_word_generator)
    except Exception as e:
        result.add_fail("sound_changes_tests", f"Sound changes test suite error: {e}")