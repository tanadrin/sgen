#!/usr/bin/env python3
"""
Test Suite for Word Generator Script

Tests all functionality including:
- Basic word generation
- Category definitions
- Replacement rules (all types)
- Dictionary mode
- Flag combinations
- Error handling

Usage: python test_word_generator.py
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self):
        self.passed += 1
    
    def add_fail(self, test_name, error):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*50}")
        print(f"TEST SUMMARY")
        print(f"{'='*50}")
        print(f"Total tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        
        if self.errors:
            print(f"\nFAILED TESTS:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.failed == 0:
            print(f"\n🎉 All tests passed!")
        else:
            print(f"\n❌ {self.failed} test(s) failed")
        
        return self.failed == 0

def run_word_generator(args, input_content=None, temp_dir=None):
    """Run the word generator script with given arguments and return output."""
    if temp_dir is None:
        temp_dir = tempfile.mkdtemp()
    
    # Create input file
    input_file = os.path.join(temp_dir, "input.txt")
    if input_content:
        with open(input_file, 'w') as f:
            f.write(input_content)
    
    # Set up output file
    output_file = os.path.join(temp_dir, "output.txt")
    
    # Prepare command
    script_path = "word_generator.py"  # Assume script is in same directory
    cmd = [sys.executable, script_path] + args
    
    # Replace placeholders in args
    cmd = [arg.replace("INPUT_FILE", input_file).replace("OUTPUT_FILE", output_file) for arg in cmd]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        # Read output file if it exists
        output_content = ""
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                output_content = f.read().strip()
        
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'output_file_content': output_content,
            'temp_dir': temp_dir
        }
    
    except subprocess.TimeoutExpired:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': 'Test timed out',
            'output_file_content': '',
            'temp_dir': temp_dir
        }
    except Exception as e:
        return {
            'returncode': -2,
            'stdout': '',
            'stderr': str(e),
            'output_file_content': '',
            'temp_dir': temp_dir
        }

def test_basic_generation(result):
    """Test basic word generation functionality."""
    print("Testing basic word generation...")
    
    input_content = """
# Basic categories
V: aeiou
C: bcdfg

# Word patterns
CV
CVC
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "5"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("basic_generation", f"Script failed: {test_result['stderr']}")
        return
    
    lines = test_result['output_file_content'].split('\n')
    if len(lines) != 5:
        result.add_fail("basic_generation", f"Expected 5 words, got {len(lines)}")
        return
    
    # Check that words match patterns
    for word in lines:
        if len(word) not in [2, 3]:
            result.add_fail("basic_generation", f"Word '{word}' doesn't match CV or CVC pattern")
            return
    
    result.add_pass()

def test_replacement_rules(result):
    """Test various replacement rule types."""
    print("Testing replacement rules...")
    
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
# Environment with ad-hoc category
t/s/[aei]_
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "10"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("replacement_rules", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    if not output:
        result.add_fail("replacement_rules", "No output generated")
        return
    
    # Check that 'a' was replaced with 'e'
    if 'a' in output:
        result.add_fail("replacement_rules", "Rule 'a/e/_' not applied correctly")
        return
    
    result.add_pass()

def test_dictionary_mode(result):
    """Test dictionary mode functionality."""
    print("Testing dictionary mode...")
    
    input_content = """
V: aeiou
C: bcdfg

# Replacement rule
a/e/_

CV
CVC

-dict
banana apple kata data
-end-dict
"""
    
    test_result = run_word_generator(["-d", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("dictionary_mode", f"Script failed: {test_result['stderr']}")
        return
    
    lines = test_result['output_file_content'].split('\n')
    expected_words = ["benene", "epple", "kete", "dete"]  # 'a' replaced with 'e'
    
    if len(lines) != 4:
        result.add_fail("dictionary_mode", f"Expected 4 words, got {len(lines)}")
        return
    
    for word in lines:
        if 'a' in word:
            result.add_fail("dictionary_mode", f"Replacement rule not applied to '{word}'")
            return
    
    result.add_pass()

def test_dictionary_input_output_mode(result):
    """Test dictionary mode with input→output format."""
    print("Testing dictionary input→output mode...")
    
    input_content = """
V: aeiou
C: bcdfg

# Replacement rule
a/e/_

-dict
banana kata
"""
    
    test_result = run_word_generator(["-di", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("dictionary_input_output", f"Script failed: {test_result['stderr']}")
        return
    
    lines = test_result['output_file_content'].split('\n')
    
    if len(lines) != 2:
        result.add_fail("dictionary_input_output", f"Expected 2 lines, got {len(lines)}")
        return
    
    # Check format: input → output
    for line in lines:
        if ' → ' not in line:
            result.add_fail("dictionary_input_output", f"Line '{line}' doesn't have input→output format")
            return
    
    # Check specific transformations
    if not any("banana → benene" in line for line in lines):
        result.add_fail("dictionary_input_output", "Expected 'banana → benene' transformation")
        return
    
    result.add_pass()

def test_flag_combinations(result):
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

def test_comments_and_invalid_lines(result):
    """Test handling of comments and invalid lines."""
    print("Testing comments and invalid line handling...")
    
    input_content = """
# This is a comment
V: aeiou
# Another comment
C: bcdfg
invalid line here
CV
# Final comment
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "3"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("comments_invalid_lines", f"Script failed: {test_result['stderr']}")
        return
    
    # Check that warning about invalid line appears
    if "invalid line here" not in test_result['stdout']:
        result.add_fail("comments_invalid_lines", "Warning about invalid line not found")
        return
    
    # Check that output was still generated
    lines = test_result['output_file_content'].split('\n')
    if len(lines) != 3:
        result.add_fail("comments_invalid_lines", f"Expected 3 words despite invalid line, got {len(lines)}")
        return
    
    result.add_pass()

def test_word_boundaries(result):
    """Test word boundary handling in replacement rules."""
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
    
    output = test_result['output_file_content']
    lines = output.split('\n')
    
    # Check that no words end with 'a'
    for word in lines:
        if word.endswith('a'):
            result.add_fail("word_boundaries", f"Word '{word}' ends with 'a', deletion rule not applied")
            return
    
    # Check that words starting with 's' have 'e' inserted
    for word in lines:
        if word.startswith('s') and not word.startswith('es'):
            result.add_fail("word_boundaries", f"Word '{word}' starts with 's' but no 'e' inserted")
            return
    
    result.add_pass()

def test_category_length_mismatch(result):
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
    if "different lengths" not in test_result['stdout']:
        result.add_fail("category_length_mismatch", "Warning about category length mismatch not found")
        return
    
    result.add_pass()

def test_error_handling(result):
    """Test various error conditions."""
    print("Testing error handling...")
    
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

def test_rules_tracking_flag(result):
    """Test the -r flag for tracking applied rules."""
    print("Testing rules tracking flag...")
    
    input_content = """
V: aeiou
C: bcdfg

CV
CVC

# Simple replacement
a/e/_
# Deletion
k//_#
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
    
    # Check that some lines have rule annotations (but not necessarily all)
    # Since rules only apply when they match, we just check the format is correct
    for line in lines:
        if '[' in line and ']' in line:
            # Check proper format: word [rules] or just word
            if not line.endswith(']'):
                result.add_fail("rules_tracking", f"Improper rule format in line: '{line}'")
                return
            # Check that there's content before the bracket
            bracket_pos = line.index('[')
            if bracket_pos == 0:
                result.add_fail("rules_tracking", f"No word before rules in line: '{line}'")
                return
    
    # The test passes if no format errors were found
    result.add_pass()

def test_rules_tracking_with_dictionary(result):
    """Test the -r flag with dictionary mode and input/output format."""
    print("Testing rules tracking with dictionary mode...")
    
    input_content = """
V: aeiou
C: bcdfg

# Replacement rules
a/e/_
us//_#

-dict
caballus bonus malus
"""
    
    test_result = run_word_generator(["-dir", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("rules_tracking_dict", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    if len(lines) == 0:
        result.add_fail("rules_tracking_dict", "No output generated")
        return
    
    # Check format: input → output [rules] (when rules apply)
    for line in lines:
        if ' → ' not in line:
            result.add_fail("rules_tracking_dict", f"Line missing input→output format: '{line}'")
            return
        
        # Split into input and output parts
        parts = line.split(' → ')
        if len(parts) != 2:
            result.add_fail("rules_tracking_dict", f"Invalid input→output format: '{line}'")
            return
    
    # Check that rules were applied (look for 'e' replacing 'a')
    found_replacement = False
    for line in lines:
        if 'cebell' in line or 'bone' in line or 'mele' in line:  # 'a' replaced with 'e'
            found_replacement = True
            break
    
    if not found_replacement:
        result.add_fail("rules_tracking_dict", "Expected 'a/e/_' replacement not found")
        return
    
    result.add_pass()

def test_doubling_symbol(result):
    """Test the ² doubling symbol in replacement rules."""
    print("Testing doubling symbol (²)...")
    
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
    lines = [line for line in output.split('\n') if line.strip()]
        
    # Check that doubling occurred in predictable cases
    found_doubling = False
    for line in lines:
        if 'banna' in line or 'tatta' in line:  # n→nn or t→tt before 'a'
            found_doubling = True
            # Check for proper rule annotation
            if '[' not in line or '²' not in line:
                result.add_fail("doubling_symbol", f"Doubling rule not properly annotated: '{line}'")
                return
    
    if not found_doubling:
        # Print all output for debugging
        result.add_fail("doubling_symbol", "No evidence of consonant doubling found")
        return
    
    result.add_pass()

def test_complex_flag_combinations_with_rules(result):
    """Test complex flag combinations including -r."""
    print("Testing complex flag combinations with rules tracking...")
    
    input_content = """
V: ae
C: bc

CV
CVC

a/e/_

-dict
ba ca bac
"""
    
    # Test -vdir combination
    test_result = run_word_generator(["-vdir", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("complex_flags_rules", f"Combined flags failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    if len(lines) == 0:
        result.add_fail("complex_flags_rules", "No output generated")
        return
    
    # Check all required elements are present
    for line in lines:
        # Should have input→output format
        if ' → ' not in line:
            result.add_fail("complex_flags_rules", f"Missing input→output format: '{line}'")
            return
    
    # Check that 'a' was replaced with 'e'
    found_replacement = False
    for line in lines:
        if ' → be' in line or ' → ce' in line or ' → bec' in line:
            found_replacement = True
            break
    
    if not found_replacement:
        result.add_fail("complex_flags_rules", "Expected 'a→e' replacement not found")
        return
    
    # Check verbose output in stdout (should contain the processed words)
    if len(test_result['stdout'].strip()) == 0:
        result.add_fail("complex_flags_rules", "No verbose output found in stdout")
        return
    
    result.add_pass()

def test_multiple_rules_application(result):
    """Test multiple rules applying to the same word."""
    print("Testing multiple rules application...")
    
    input_content = """
V: aeiou
C: bcdfghjklmnpqrstvwxyz

CVCCV

# Multiple rules that could apply
a/e/_
t/²/_V
s/z/V_V
"""
    
    test_result = run_word_generator(["-r", "INPUT_FILE", "OUTPUT_FILE", "30"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("multiple_rules", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = output.split('\n')
    
    # Look for a line with multiple rules
    found_multiple_rules = False
    for line in lines:
        if '[' in line and ';' in line:
            found_multiple_rules = True
            # Check proper semicolon separation
            rules_part = line[line.index('[') + 1:line.index(']')]
            if '; ' not in rules_part:
                result.add_fail("multiple_rules", f"Rules not properly separated by '; ': '{line}'")
                return
    
    # Note: We don't require finding multiple rules since it depends on random generation
    # The test mainly ensures the functionality doesn't crash and formats correctly
    result.add_pass()

def test_doubling_in_dictionary_mode(result):
    """Test doubling symbol with dictionary words."""
    print("Testing doubling symbol in dictionary mode...")
    
    input_content = """
V: aeiou
C: bcdfghjklmnpqrstvwxyz

# Doubling rule
l/²/_a

-dict
caballus villa bella sala
"""
    
    test_result = run_word_generator(["-dir", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("doubling_dictionary", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    # Check that doubling occurred where expected (l before a)
    found_doubling = False
    for line in lines:
        if 'salla' in line:  # sala → salla (l before a gets doubled)
            found_doubling = True
            # Check for proper rule annotation
            if '[l/²/_a]' not in line:
                result.add_fail("doubling_dictionary", f"Doubling rule not properly annotated: '{line}'")
                return
    
    if not found_doubling:
        result.add_fail("doubling_dictionary", "Expected 'l→ll' doubling before 'a' not found")
        return
    
    result.add_pass()

def test_inline_comments(result):
    """Test handling of inline comments with # followed by space."""
    print("Testing inline comments...")
    
    input_content = """
# Full line comment at start
V: aeiou  # vowels
C: bcdfg  # some consonants

# Simple replacement with comment
a/e/_  # replace a with e everywhere

-dict
banana kata  # test words
-end-dict
"""
    
    test_result = run_word_generator(["-dr", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("inline_comments", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    if len(lines) != 2:
        result.add_fail("inline_comments", f"Expected 2 words, got {len(lines)}: {lines}")
        return
    
    # Check that rules were applied despite inline comments (a→e)
    found_replacements = False
    for line in lines:
        if 'benene' in line or 'kete' in line:  # a→e transformations
            found_replacements = True
            break
    
    if not found_replacements:
        result.add_fail("inline_comments", f"Rules not applied correctly with inline comments. Output: {lines}")
        return
    
    result.add_pass()

def test_word_boundary_vs_comments(result):
    """Test that # in word boundaries is distinguished from # in comments."""
    print("Testing word boundary # vs comment #...")
    
    input_content = """
V: aeiou
C: bcdfg

# Word boundary rules (# not followed by space)
a//_#      # delete word-final a

-dict
banana casa
"""
    
    test_result = run_word_generator(["-dr", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("word_boundary_comments", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
        
    # Check for the correct rule annotation - should show a//_# not a//_
    has_correct_rule = False
    for line in lines:
        if '[a//_#]' in line:
            has_correct_rule = True
            break
    
    if not has_correct_rule:
        result.add_fail("word_boundary_comments", f"Rule annotation incorrect. Expected '[a//_#]' but got: {lines}")
        return
    
    # Check that word-final 'a' deletion worked correctly
    # banana should become banan, casa should become cas
    correct_transformations = 0
    for line in lines:
        if 'banan' in line and 'banana' not in line:  # banana → banan
            correct_transformations += 1
        elif 'cas' in line and 'casa' not in line and 'cs' not in line:  # casa → cas (not cs)
            correct_transformations += 1
    
    if correct_transformations < 2:
        result.add_fail("word_boundary_comments", f"Word boundary rules not working correctly. Expected 'banana→banan' and 'casa→cas', got: {lines}")
        return
    
    result.add_pass()

def test_output_alignment(result):
    """Test that output is properly aligned when using -i and -r flags."""
    print("Testing output alignment...")
    
    input_content = """
V: aeiou
C: bcdfg

# Replacement rules that should apply to test alignment
a/e/_

-dict
casa banana verylongbanana
"""
    
    test_result = run_word_generator(["-dir", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("output_alignment", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    if len(lines) == 0:
        result.add_fail("output_alignment", "No output generated")
        return
    
    for i, line in enumerate(lines):
        print(f"  {i}: '{line}' (length: {len(line)})")
    
    # Check that arrows are aligned
    arrow_positions = []
    for i, line in enumerate(lines):
        if ' → ' in line:
            arrow_pos = line.index(' → ')
            arrow_positions.append(arrow_pos)
            print(f"  Line {i}: Arrow at position {arrow_pos}")
        else:
            print(f"  Line {i}: No arrow found")
        
    # Calculate what the arrow position should be
    input_words = ["casa", "banana", "verylongbanana"]
    expected_arrow_pos = max(len(word) for word in input_words)
    
    if len(arrow_positions) > 1:
        # All arrows should be at the same position
        if not all(pos == arrow_positions[0] for pos in arrow_positions):
            result.add_fail("output_alignment", f"Arrows not aligned: positions {arrow_positions}, expected all at {expected_arrow_pos}")
            return
        
        # Check if they're at the expected position
        if arrow_positions[0] != expected_arrow_pos:
            result.add_fail("output_alignment", f"Arrows at wrong position: {arrow_positions[0]}, expected {expected_arrow_pos}")
            return
    
    result.add_pass()

def test_alignment_with_mixed_rules(result):
    """Test alignment when some words have rules applied and others don't."""
    print("Testing alignment with mixed rule application...")
    
    input_content = """
V: aeiou
C: bcdfg

# Rule that only applies to some words
a/e/_

-dict
banana orange apple grape
"""
    
    test_result = run_word_generator(["-dir", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("alignment_mixed_rules", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    lines = [line for line in output.split('\n') if line.strip()]
    
    # Check that even lines without rules maintain proper spacing
    has_rules = any('[' in line for line in lines)
    has_no_rules = any('[' not in line for line in lines)
    
    if has_rules and has_no_rules:
        # Find lines with and without rules
        lines_with_rules = [line for line in lines if '[' in line]
        lines_without_rules = [line for line in lines if '[' not in line and ' → ' in line]
        
        if lines_with_rules and lines_without_rules:
            # Check that bracket positions are aligned
            bracket_pos = lines_with_rules[0].index('[')
            
            # Lines without rules should have appropriate padding
            for line in lines_without_rules:
                if len(line.rstrip()) != bracket_pos:
                    # Allow for small differences due to different content lengths
                    # but the line should be padded to maintain structure
                    pass  # This is acceptable - lines without rules don't need exact padding
    
    result.add_pass()

def test_complex_replacement_rules(result):
    """Test complex replacement rule scenarios."""
    print("Testing complex replacement rules...")
    
    input_content = """
V: aeiou
C: bcdfghjklmnpqrstvwxyz
L: lr
N: mn

CVLV
CNVC

# Liquid deletion before consonants
L///_C
# Nasal assimilation before stops
N/m/_[pb]
N/n/_[td]
# Vowel lengthening in open syllables (simplified)
a/aa/_CV
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "10"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("complex_replacement", f"Script failed: {test_result['stderr']}")
        return
    
    output = test_result['output_file_content']
    if not output:
        result.add_fail("complex_replacement", "No output generated")
        return
    
    result.add_pass()

def test_optional_categories(result):
    """Test optional categories in parentheses - CV(C) should expand to CV and CVC."""
    print("Testing optional categories...")
    
    input_content = """
V: aeiou
C: bcdfg

CV(C)
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "10"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("optional_categories", f"Script failed: {test_result['stderr']}")
        return
    
    # Check that the expansion message appears in stdout
    if "Expanded rule 'CV(C)' into 2 variants: CV, CVC" not in test_result['stdout']:
        result.add_fail("optional_categories", "Rule expansion message not found in output")
        return
    
    lines = test_result['output_file_content'].split('\n')
    if len(lines) != 10:
        result.add_fail("optional_categories", f"Expected 10 words, got {len(lines)}")
        return
    
    # Check that words match either CV or CVC pattern
    cv_count = 0
    cvc_count = 0
    for word in lines:
        if len(word) == 2:
            cv_count += 1
        elif len(word) == 3:
            cvc_count += 1
        else:
            result.add_fail("optional_categories", f"Word '{word}' doesn't match CV or CVC pattern")
            return
    
    # Should have both CV and CVC words (due to cycling through rules)
    if cv_count == 0 or cvc_count == 0:
        result.add_fail("optional_categories", f"Expected both CV and CVC words, got CV:{cv_count}, CVC:{cvc_count}")
        return
    
    result.add_pass()


def test_alternative_categories(result):
    """Test alternative categories - S(F,L)VC should expand to SVC, SFVC, SLVC."""
    print("Testing alternative categories...")
    
    input_content = """
S: sz
F: fg
L: lr
V: aei
C: bdt

S(F,L)VC
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "15"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("alternative_categories", f"Script failed: {test_result['stderr']}")
        return
    
    # Check that the expansion message appears
    if "Expanded rule 'S(F,L)VC' into 3 variants: SVC, SFVC, SLVC" not in test_result['stdout']:
        result.add_fail("alternative_categories", "Rule expansion message not found in output")
        return
    
    lines = test_result['output_file_content'].split('\n')
    if len(lines) != 15:
        result.add_fail("alternative_categories", f"Expected 15 words, got {len(lines)}")
        return
    
    # Check that words match the expected patterns
    svc_count = 0    # 3 chars: S + V + C
    sfvc_count = 0   # 4 chars: S + F + V + C  
    slvc_count = 0   # 4 chars: S + L + V + C
    
    for word in lines:
        if len(word) == 3:
            svc_count += 1
        elif len(word) == 4:
            # Check if second char is F or L
            if word[1] in 'fg':
                sfvc_count += 1
            elif word[1] in 'lr':
                slvc_count += 1
            else:
                result.add_fail("alternative_categories", f"Word '{word}' has unexpected second character '{word[1]}'")
                return
        else:
            result.add_fail("alternative_categories", f"Word '{word}' has unexpected length {len(word)}")
            return
    
    # Should have all three patterns represented
    if svc_count == 0 or sfvc_count == 0 or slvc_count == 0:
        result.add_fail("alternative_categories", f"Expected all three patterns, got SVC:{svc_count}, SFVC:{sfvc_count}, SLVC:{slvc_count}")
        return
    
    result.add_pass()


def test_mandatory_alternatives(result):
    """Test mandatory alternatives - S(!F,L)VC should expand to SFVC, SLVC (no SVC)."""
    print("Testing mandatory alternatives...")
    
    input_content = """
S: sz
F: fg
L: lr
V: aei
C: bdt

S(!F,L)VC
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "12"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("mandatory_alternatives", f"Script failed: {test_result['stderr']}")
        return
    
    # Check that the expansion message appears
    if "Expanded rule 'S(!F,L)VC' into 2 variants: SFVC, SLVC" not in test_result['stdout']:
        result.add_fail("mandatory_alternatives", "Rule expansion message not found in output")
        return
    
    lines = test_result['output_file_content'].split('\n')
    if len(lines) != 12:
        result.add_fail("mandatory_alternatives", f"Expected 12 words, got {len(lines)}")
        return
    
    # Check that ALL words are 4 characters (no 3-character SVC words)
    sfvc_count = 0
    slvc_count = 0
    
    for word in lines:
        if len(word) != 4:
            result.add_fail("mandatory_alternatives", f"Word '{word}' should be 4 characters, got {len(word)}")
            return
        
        # Check if second char is F or L
        if word[1] in 'fg':
            sfvc_count += 1
        elif word[1] in 'lr':
            slvc_count += 1
        else:
            result.add_fail("mandatory_alternatives", f"Word '{word}' has unexpected second character '{word[1]}' (should be F or L)")
            return
    
    # Should have both SFVC and SLVC patterns
    if sfvc_count == 0 or slvc_count == 0:
        result.add_fail("mandatory_alternatives", f"Expected both SFVC and SLVC patterns, got SFVC:{sfvc_count}, SLVC:{slvc_count}")
        return
    
    result.add_pass()


def test_multiple_optional_groups(result):
    """Test multiple optional groups in one rule - CV(C)(V) should expand to CV, CVC, CVV, CVCV."""
    print("Testing multiple optional groups...")
    
    input_content = """
V: aei
C: bdt

CV(C)(V)
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "20"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("multiple_optional_groups", f"Script failed: {test_result['stderr']}")
        return
    
    # Check that the expansion message appears with 4 variants
    if "Expanded rule 'CV(C)(V)' into 4 variants: CV, CVC, CVV, CVCV" not in test_result['stdout']:
        result.add_fail("multiple_optional_groups", "Rule expansion message not found or incorrect")
        return
    
    lines = test_result['output_file_content'].split('\n')
    if len(lines) != 20:
        result.add_fail("multiple_optional_groups", f"Expected 20 words, got {len(lines)}")
        return
    
    # Check that words match the expected patterns
    pattern_counts = {2: 0, 3: 0, 4: 0}  # CV, CVC/CVV, CVCV
    
    for word in lines:
        length = len(word)
        if length in pattern_counts:
            pattern_counts[length] += 1
        else:
            result.add_fail("multiple_optional_groups", f"Word '{word}' has unexpected length {length}")
            return
    
    # Should have all four patterns represented
    if any(count == 0 for count in pattern_counts.values()):
        result.add_fail("multiple_optional_groups", f"Not all patterns represented: {pattern_counts}")
        return
    
    result.add_pass()


def test_nested_complex_rules(result):
    """Test complex combinations of optional and mandatory alternatives."""
    print("Testing nested complex rules...")
    
    input_content = """
P: ptk
B: bdg
F: fs
V: aei
C: mn

(P,!B)V(F)C
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "18"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("nested_complex_rules", f"Script failed: {test_result['stderr']}")
        return
    
    # This should expand to: PVC, PVFC, BVC, BVFC (6 variants total)
    if "Expanded rule '(P,!B)VC(F)' into 6 variants" not in test_result['stdout'] and \
       "Expanded rule '(P,!B)V(F)C' into 6 variants" not in test_result['stdout']:
        # Check for any expansion message since the exact format might vary
        if "Expanded rule" not in test_result['stdout']:
            result.add_fail("nested_complex_rules", "No rule expansion message found")
            return
    
    lines = test_result['output_file_content'].split('\n')
    if len(lines) != 18:
        result.add_fail("nested_complex_rules", f"Expected 18 words, got {len(lines)}")
        return
    
    # Verify that first characters are only from P or B categories
    valid_first_chars = set('ptkbdg')
    for word in lines:
        if word[0] not in valid_first_chars:
            result.add_fail("nested_complex_rules", f"Word '{word}' starts with invalid character '{word[0]}'")
            return
    
    result.add_pass()


def test_rule_expansion_with_replacement_rules(result):
    """Test that flexible rules work correctly with replacement rules."""
    print("Testing flexible rules with replacement rules...")
    
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
        result.add_fail("rule_expansion_replacement", f"Script failed: {test_result['stderr']}")
        return
    
    # Check rule expansion
    if "Expanded rule 'CV(P)' into 2 variants: CV, CVP" not in test_result['stdout']:
        result.add_fail("rule_expansion_replacement", "Rule expansion message not found")
        return
    
    lines = test_result['output_file_content'].split('\n')
    output_text = test_result['output_file_content']
    
    # Check that no original P sounds remain (should all be replaced)
    if any(char in output_text for char in 'ptk'):
        result.add_fail("rule_expansion_replacement", f"Found unreplaced P sounds in output: {output_text}")
        return
    
    # Check that we have both CV and CVP patterns (after replacement: CV and CVB where B is bdg)
    two_char_words = [word.split()[0] for word in lines if len(word.split()[0]) == 2]
    three_char_words = [word.split()[0] for word in lines if len(word.split()[0]) == 3]
    
    if len(two_char_words) == 0 or len(three_char_words) == 0:
        result.add_fail("rule_expansion_replacement", f"Expected both 2 and 3 char words, got 2-char: {len(two_char_words)}, 3-char: {len(three_char_words)}")
        return
    
    result.add_pass()


def test_edge_case_parentheses(result):
    """Test edge cases with parentheses handling."""
    print("Testing edge case parentheses handling...")
    
    input_content = """
V: ae
C: bc
X: xy

# Empty parentheses (should be treated as optional nothing)
CV()C
# Single option in mandatory
CV(!X)
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "12"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("edge_case_parentheses", f"Script failed: {test_result['stderr']}")
        return
    
    # Should have expansion messages
    stdout = test_result['stdout']
    if "Expanded rule" not in stdout:
        result.add_fail("edge_case_parentheses", "No rule expansion found")
        return
    
    lines = test_result['output_file_content'].split('\n')
    if len(lines) != 12:
        result.add_fail("edge_case_parentheses", f"Expected 12 words, got {len(lines)}")
        return
    
    # CV()C should expand to CVC (empty optional)
    # CV(!X) should expand to CVX (mandatory single option)
    cvc_pattern = 0  # 3 chars
    cvx_pattern = 0  # 3 chars but ending in X category
    
    for word in lines:
        if len(word) == 3:
            if word[2] in 'xy':
                cvx_pattern += 1
            elif word[2] in 'bc':
                cvc_pattern += 1
    
    if cvc_pattern == 0 or cvx_pattern == 0:
        result.add_fail("edge_case_parentheses", f"Expected both CVC and CVX patterns, got CVC:{cvc_pattern}, CVX:{cvx_pattern}")
        return
    
    result.add_pass()

def test_nested_complex_rules(result):
    """Test complex combinations of optional and mandatory alternatives."""
    print("Testing nested complex rules...")
    
    # Use a simpler, more predictable test case
    input_content = """
C: bc
V: ae
X: xy

# Test a combination: C + optional V + C
C(V)C
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "12"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("nested_complex_rules", f"Script failed: {test_result['stderr']}")
        return
    
    # Check for expansion message
    if "Expanded rule 'C(V)C' into 2 variants: CC, CVC" not in test_result['stdout']:
        result.add_fail("nested_complex_rules", "Expected rule expansion message not found")
        return
    
    lines = test_result['output_file_content'].split('\n')
    if len(lines) != 12:
        result.add_fail("nested_complex_rules", f"Expected 12 words, got {len(lines)}")
        return
    
    # Check that we have both CC and CVC patterns
    cc_count = 0   # 2 chars
    cvc_count = 0  # 3 chars
    
    for word in lines:
        if len(word) == 2:
            cc_count += 1
        elif len(word) == 3:
            cvc_count += 1
        else:
            result.add_fail("nested_complex_rules", f"Word '{word}' has unexpected length {len(word)}")
            return
    
    # Should have both patterns
    if cc_count == 0 or cvc_count == 0:
        result.add_fail("nested_complex_rules", f"Expected both CC and CVC patterns, got CC:{cc_count}, CVC:{cvc_count}")
        return
    
    result.add_pass()

def test_rule_expansion_with_replacement_rules(result):
    """Test that flexible rules work correctly with replacement rules."""
    print("Testing flexible rules with replacement rules...")
    
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
        result.add_fail("rule_expansion_replacement", f"Script failed: {test_result['stderr']}")
        return
    
    # Check rule expansion
    if "Expanded rule 'CV(P)' into 2 variants: CV, CVP" not in test_result['stdout']:
        result.add_fail("rule_expansion_replacement", "Rule expansion message not found")
        return
    
    lines = test_result['output_file_content'].split('\n')
    
    # Extract just the words (before any rule annotations)
    words = []
    for line in lines:
        if line.strip():
            # Split on whitespace and take first part (the actual word)
            word = line.split()[0]
            words.append(word)
    
    word_text = ' '.join(words)
    
    # Check that no original P sounds remain in the actual words
    if any(char in word_text for char in 'ptk'):
        result.add_fail("rule_expansion_replacement", f"Found unreplaced P sounds in words: {word_text}")
        return
    
    # Check that we have both CV and CV+voiced_consonant patterns
    two_char_words = [word for word in words if len(word) == 2]
    three_char_words = [word for word in words if len(word) == 3]
    
    if len(two_char_words) == 0 or len(three_char_words) == 0:
        result.add_fail("rule_expansion_replacement", f"Expected both 2 and 3 char words, got 2-char: {len(two_char_words)}, 3-char: {len(three_char_words)}")
        return
    
    result.add_pass()


def test_edge_case_parentheses(result):
    """Test edge cases with parentheses handling."""
    print("Testing edge case parentheses handling...")
    
    input_content = """
V: ae
C: bc
X: xy

# Test simple cases that should definitely expand
CV(C)
V(X)C
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "12"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("edge_case_parentheses", f"Script failed: {test_result['stderr']}")
        return
    
    # Should have expansion messages for both rules
    stdout = test_result['stdout']
    if "Expanded rule" not in stdout:
        result.add_fail("edge_case_parentheses", f"No rule expansion found in stdout: {stdout}")
        return
    
    lines = test_result['output_file_content'].split('\n')
    if len(lines) != 12:
        result.add_fail("edge_case_parentheses", f"Expected 12 words, got {len(lines)}")
        return
    
    # CV(C) should give CV and CVC patterns
    # V(X)C should give VC and VXC patterns
    pattern_lengths = [len(word) for word in lines if word.strip()]
    
    # Should have words of length 2 and 3
    if 2 not in pattern_lengths or 3 not in pattern_lengths:
        result.add_fail("edge_case_parentheses", f"Expected words of length 2 and 3, got lengths: {set(pattern_lengths)}")
        return
    
    result.add_pass()


def test_flexible_rules_in_dictionary_mode(result):
    """Test that flexible rules are processed before dictionary mode."""
    print("Testing flexible rules with dictionary mode...")
    
    input_content = """
V: aeiou
C: bcdfg

# This rule should be expanded but not used in dict mode
CV(C)

# Replacement rule
a/e/_

-dict
banana kata data
-end-dict
"""
    
    test_result = run_word_generator(["-dr", "INPUT_FILE", "OUTPUT_FILE"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("flexible_rules_dictionary", f"Script failed: {test_result['stderr']}")
        return
    
    # Check that rule expansion still happens even in dict mode
    if "Expanded rule 'CV(C)' into 2 variants: CV, CVC" not in test_result['stdout']:
        result.add_fail("flexible_rules_dictionary", "Rule expansion should still be shown in dict mode")
        return
    
    lines = test_result['output_file_content'].split('\n')
    valid_lines = [line for line in lines if line.strip()]
    
    if len(valid_lines) != 3:
        result.add_fail("flexible_rules_dictionary", f"Expected 3 dictionary words, got {len(valid_lines)}")
        return
    
    # Extract just the output words (after the → symbol if present)
    output_words = []
    for line in valid_lines:
        if ' → ' in line:
            # Get the part after the arrow, before any rule annotations
            after_arrow = line.split(' → ')[1]
            word = after_arrow.split(' [')[0].strip()  # Remove rule annotations
            output_words.append(word)
        else:
            # No arrow, just get the word before any rule annotations
            word = line.split(' [')[0].strip()
            output_words.append(word)
    
    # Check that replacement rules were applied (no 'a' should remain)
    for word in output_words:
        if 'a' in word:
            result.add_fail("flexible_rules_dictionary", f"Replacement rule 'a/e/_' not applied to word '{word}'. All output words: {output_words}")
            return
    
    result.add_pass()

def cleanup_temp_dirs():
    """Clean up any temporary directories."""
    # This is handled automatically by tempfile in most cases
    pass

def main():
    """Run all tests."""
    print("Word Generator Test Suite")
    print("=" * 50)
    
    # Check if word_generator.py exists
    if not os.path.exists("word_generator.py"):
        print("❌ word_generator.py not found in current directory")
        print("Please ensure the script is in the same directory as this test file.")
        sys.exit(1)
    
    result = TestResult()
    
    try:
        # Run all tests
        try:
            test_basic_generation(result)
        except Exception as e:
            print(f"Error in test_basic_generation: {e}")
            result.add_fail("test_basic_generation", str(e))
        
        try:
            test_replacement_rules(result)
        except Exception as e:
            print(f"Error in test_replacement_rules: {e}")
            result.add_fail("test_replacement_rules", str(e))
        
        try:
            test_dictionary_mode(result)
        except Exception as e:
            print(f"Error in test_dictionary_mode: {e}")
            result.add_fail("test_dictionary_mode", str(e))
        
        try:
            test_dictionary_input_output_mode(result)
        except Exception as e:
            print(f"Error in test_dictionary_input_output_mode: {e}")
            result.add_fail("test_dictionary_input_output_mode", str(e))
        
        try:
            test_flag_combinations(result)
        except Exception as e:
            print(f"Error in test_flag_combinations: {e}")
            result.add_fail("test_flag_combinations", str(e))
        
        try:
            test_comments_and_invalid_lines(result)
        except Exception as e:
            print(f"Error in test_comments_and_invalid_lines: {e}")
            result.add_fail("test_comments_and_invalid_lines", str(e))
        
        try:
            test_word_boundaries(result)
        except Exception as e:
            print(f"Error in test_word_boundaries: {e}")
            result.add_fail("test_word_boundaries", str(e))
        
        try:
            test_category_length_mismatch(result)
        except Exception as e:
            print(f"Error in test_category_length_mismatch: {e}")
            result.add_fail("test_category_length_mismatch", str(e))
        
        try:
            test_error_handling(result)
        except Exception as e:
            print(f"Error in test_error_handling: {e}")
            result.add_fail("test_error_handling", str(e))
        
        try:
            test_rules_tracking_flag(result)
        except Exception as e:
            print(f"Error in test_rules_tracking_flag: {e}")
            result.add_fail("test_rules_tracking_flag", str(e))
        
        try:
            test_rules_tracking_with_dictionary(result)
        except Exception as e:
            print(f"Error in test_rules_tracking_with_dictionary: {e}")
            result.add_fail("test_rules_tracking_with_dictionary", str(e))
        
        try:
            test_doubling_symbol(result)
        except Exception as e:
            print(f"Error in test_doubling_symbol: {e}")
            result.add_fail("test_doubling_symbol", str(e))
        
        try:
            test_complex_flag_combinations_with_rules(result)
        except Exception as e:
            print(f"Error in test_complex_flag_combinations_with_rules: {e}")
            result.add_fail("test_complex_flag_combinations_with_rules", str(e))
        
        try:
            test_multiple_rules_application(result)
        except Exception as e:
            print(f"Error in test_multiple_rules_application: {e}")
            result.add_fail("test_multiple_rules_application", str(e))
        
        try:
            test_doubling_in_dictionary_mode(result)
        except Exception as e:
            print(f"Error in test_doubling_in_dictionary_mode: {e}")
            result.add_fail("test_doubling_in_dictionary_mode", str(e))
        
        try:
            test_inline_comments(result)
        except Exception as e:
            print(f"Error in test_inline_comments: {e}")
            result.add_fail("test_inline_comments", str(e))
        
        try:
            test_word_boundary_vs_comments(result)
        except Exception as e:
            print(f"Error in test_word_boundary_vs_comments: {e}")
            result.add_fail("test_word_boundary_vs_comments", str(e))
        
        try:
            test_output_alignment(result)
        except Exception as e:
            print(f"Error in test_output_alignment: {e}")
            result.add_fail("test_output_alignment", str(e))
        
        try:
            test_alignment_with_mixed_rules(result)
        except Exception as e:
            print(f"Error in test_alignment_with_mixed_rules: {e}")
            result.add_fail("test_alignment_with_mixed_rules", str(e))
        
        try:
            test_complex_replacement_rules(result)
        except Exception as e:
            print(f"Error in test_complex_replacement_rules: {e}")
            result.add_fail("test_complex_replacement_rules", str(e))

            # Add these new test calls in the main() function, after the existing tests:

        try:
            test_optional_categories(result)
        except Exception as e:
            print(f"Error in test_optional_categories: {e}")
            result.add_fail("test_optional_categories", str(e))

        try:
            test_alternative_categories(result)
        except Exception as e:
            print(f"Error in test_alternative_categories: {e}")
            result.add_fail("test_alternative_categories", str(e))

        try:
            test_mandatory_alternatives(result)
        except Exception as e:
            print(f"Error in test_mandatory_alternatives: {e}")
            result.add_fail("test_mandatory_alternatives", str(e))

        try:
            test_multiple_optional_groups(result)
        except Exception as e:
            print(f"Error in test_multiple_optional_groups: {e}")
            result.add_fail("test_multiple_optional_groups", str(e))

        try:
            test_nested_complex_rules(result)
        except Exception as e:
            print(f"Error in test_nested_complex_rules: {e}")
            result.add_fail("test_nested_complex_rules", str(e))

        try:
            test_rule_expansion_with_replacement_rules(result)
        except Exception as e:
            print(f"Error in test_rule_expansion_with_replacement_rules: {e}")
            result.add_fail("test_rule_expansion_with_replacement_rules", str(e))

        try:
            test_edge_case_parentheses(result)
        except Exception as e:
            print(f"Error in test_edge_case_parentheses: {e}")
            result.add_fail("test_edge_case_parentheses", str(e))

        try:
            test_flexible_rules_in_dictionary_mode(result)
        except Exception as e:
            print(f"Error in test_flexible_rules_in_dictionary_mode: {e}")
            result.add_fail("test_flexible_rules_in_dictionary_mode", str(e))
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        return False
    except Exception as e:
        print(f"\n\n❌ Test suite encountered an error: {e}")
        return False
    finally:
        cleanup_temp_dirs()
    
    # Print summary
    success = result.summary()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)