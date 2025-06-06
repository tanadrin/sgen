#!/usr/bin/env python3
"""
Tests for the parser module.
"""


def test_basic_parsing(result, run_word_generator):
    """Test basic parsing functionality."""
    print("Testing basic input parsing...")
    
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
        result.add_fail("basic_parsing", f"Script failed: {test_result['stderr']}")
        return
    
    lines = test_result['output_file_content'].split('\n')
    if len(lines) != 5:
        result.add_fail("basic_parsing", f"Expected 5 words, got {len(lines)}")
        return
    
    result.add_pass()


def test_comments_handling(result, run_word_generator):
    """Test comment handling."""
    print("Testing comment handling...")
    
    input_content = """
# This is a comment
V: aeiou  # vowels
C: bcdfg  # some consonants

# Simple replacement with comment
a/e/_  # replace a with e everywhere

CV
"""
    
    test_result = run_word_generator(["INPUT_FILE", "OUTPUT_FILE", "3"], input_content)
    
    if test_result['returncode'] != 0:
        result.add_fail("comments_handling", f"Script failed: {test_result['stderr']}")
        return
    
    result.add_pass()


def test_optional_categories(result, run_word_generator):
    """Test optional categories in parentheses."""
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
    
    result.add_pass()


def test_alternative_categories(result, run_word_generator):
    """Test alternative categories."""
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
    if "Expanded rule 'S(F,L)VC' into 3 variants" not in test_result['stdout']:
        result.add_fail("alternative_categories", "Rule expansion message not found in output")
        return
    
    result.add_pass()


def test_mandatory_alternatives(result, run_word_generator):
    """Test mandatory alternatives."""
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
    if "Expanded rule 'S(!F,L)VC' into 2 variants" not in test_result['stdout']:
        result.add_fail("mandatory_alternatives", "Rule expansion message not found in output")
        return
    
    result.add_pass()


def run_parser_tests(result, run_word_generator):
    """Run all parser tests."""
    print("\n=== PARSER TESTS ===")
    
    try:
        test_basic_parsing(result, run_word_generator)
        test_comments_handling(result, run_word_generator)
        test_optional_categories(result, run_word_generator)
        test_alternative_categories(result, run_word_generator)
        test_mandatory_alternatives(result, run_word_generator)
    except Exception as e:
        result.add_fail("parser_tests", f"Parser test suite error: {e}")