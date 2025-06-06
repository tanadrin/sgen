#!/usr/bin/env python3
"""
Integration tests for full workflow functionality.
"""


def test_complete_workflow(result, run_word_generator):
    """Test complete workflow from parsing to output."""
    print("Testing complete workflow...")
    
    input_content = """
# Complete test file
V: aeiou
C: bcdfghjklmnpqrstvwxyz
L: lr
N: mn

# Flexible rules
CV(L)V
C(V)NC

# Sound changes
a/e/_
L///_C
N/m/_[pb]

-dict
banana caballus villa data
-end-dict
"""
    
    # Test generation mode
    test_result = run_word_generator(["-vr", "INPUT_FILE", "OUTPUT_FILE", "8"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("complete_workflow_generation", f"Generation workflow failed: {test_result['stderr']}")
        return
    
    # Test dictionary mode
    test_result = run_word_generator(["-vdir", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("complete_workflow_dictionary", f"Dictionary workflow failed: {test_result['stderr']}")
        return
    
    result.add_pass()


def test_complex_rules_interaction(result, run_word_generator):
    """Test interaction between flexible rules and sound changes."""
    print("Testing complex rules interaction...")
    
    input_content = """
V: aeiou
C: bcdfg
P: ptk

CV(P)

# Replace any P with corresponding voiced sound
p/b/_
t/d/_
k/g/_
"""
    
    test_result = run_word_generator(["-r", "INPUT_FILE", "OUTPUT_FILE", "12"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("complex_rules_interaction", f"Script failed: {test_result['stderr']}")
        return
    
    # Check rule expansion
    if "Expanded rule 'CV(P)' into 2 variants: CV, CVP" not in test_result['stdout']:
        result.add_fail("complex_rules_interaction", "Rule expansion message not found")
        return
    
    lines = test_result['output_file_content'].split('\n')
    
    # Extract just the words (before any rule annotations)
    words = []
    for line in lines:
        if line.strip():
            word = line.split()[0]
            words.append(word)
    
    word_text = ' '.join(words)
    
    # Check that no original P sounds remain in the actual words
    if any(char in word_text for char in 'ptk'):
        result.add_fail("complex_rules_interaction", f"Found unreplaced P sounds in words: {word_text}")
        return
    
    result.add_pass()


def test_output_formatting(result, run_word_generator):
    """Test output formatting and alignment."""
    print("Testing output formatting...")
    
    input_content = """
V: aeiou
C: bcdfg

# Replacement rules
a/e/_

-dict
casa banana verylongbanana
"""
    
    test_result = run_word_generator(["-dir", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("output_formatting", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    if len(lines) == 0:
        result.add_fail("output_formatting", "No output generated")
        return
    
    # Check that arrows are present and aligned
    arrow_positions = []
    for line in lines:
        if ' → ' in line:
            arrow_pos = line.index(' → ')
            arrow_positions.append(arrow_pos)
    
    if len(arrow_positions) > 1:
        # All arrows should be at the same position for proper alignment
        if not all(pos == arrow_positions[0] for pos in arrow_positions):
            result.add_fail("output_formatting", f"Arrows not aligned: positions {arrow_positions}")
            return
    
    result.add_pass()


def test_edge_cases(result, run_word_generator):
    """Test various edge cases."""
    print("Testing edge cases...")
    
    input_content = """
V: ae
C: bc
X: xy

# Empty parentheses and single mandatory options
CV(C)
V(!X)C
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "12"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("edge_cases", f"Script failed: {test_result['stderr']}")
        return
    
    # Should have expansion messages
    stdout = test_result['stdout']
    if "Expanded rule" not in stdout:
        result.add_fail("edge_cases", f"No rule expansion found in stdout")
        return
    
    result.add_pass()


def run_integration_tests(result, run_word_generator):
    """Run all integration tests."""
    print("\n=== INTEGRATION TESTS ===")
    
    try:
        test_complete_workflow(result, run_word_generator)
        test_complex_rules_interaction(result, run_word_generator)
        test_output_formatting(result, run_word_generator)
        test_edge_cases(result, run_word_generator)
    except Exception as e:
        result.add_fail("integration_tests", f"Integration test suite error: {e}")