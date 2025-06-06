#!/usr/bin/env python3
"""
Debug script to understand the failing tests.
"""

import tempfile
import os
import subprocess
import sys

def debug_category_parsing():
    """Debug how categories are being parsed."""
    print("=== DEBUGGING CATEGORY PARSING ===")
    
    input_content = """
V: aeiou
C: bcdfg

CV
CVC
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as input_file:
        input_file.write(input_content)
        input_filename = input_file.name
    
    output_filename = input_filename.replace('.txt', '_output.txt')
    
    try:
        cmd = [sys.executable, 'word_generator.py', input_filename, output_filename, '5']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout:\n{result.stdout}")
        print(f"Stderr:\n{result.stderr}")
        
        if os.path.exists(output_filename):
            with open(output_filename, 'r') as f:
                output = f.read()
            print(f"Output file content:\n{output}")
            
            # Analyze words
            words = output.strip().split('\n')
            print(f"Generated words: {words}")
            for word in words:
                print(f"  '{word}' - length: {len(word)}")
        
    finally:
        try:
            os.unlink(input_filename)
            if os.path.exists(output_filename):
                os.unlink(output_filename)
        except:
            pass

def debug_weighted_categories():
    """Debug weighted category parsing."""
    print("\n=== DEBUGGING WEIGHTED CATEGORIES ===")
    
    input_content = """
V: a{3} e{2} i o u
C: bcdfg

CV
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as input_file:
        input_file.write(input_content)
        input_filename = input_file.name
    
    output_filename = input_filename.replace('.txt', '_output.txt')
    
    try:
        cmd = [sys.executable, 'word_generator.py', input_filename, output_filename, '10']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout:\n{result.stdout}")
        print(f"Stderr:\n{result.stderr}")
        
        if os.path.exists(output_filename):
            with open(output_filename, 'r') as f:
                output = f.read()
            print(f"Output file content:\n{output}")
            
            # Count vowel frequencies
            vowel_counts = {}
            for vowel in 'aeiou':
                vowel_counts[vowel] = output.count(vowel)
            print(f"Vowel frequencies: {vowel_counts}")
        
    finally:
        try:
            os.unlink(input_filename)
            if os.path.exists(output_filename):
                os.unlink(output_filename)
        except:
            pass

def debug_replacement_rules():
    """Debug replacement rules."""
    print("\n=== DEBUGGING REPLACEMENT RULES ===")
    
    input_content = """
P: ptk
B: bdg

CV

P/B/_

-dict
papa tata kaka
-end-dict
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as input_file:
        input_file.write(input_content)
        input_filename = input_file.name
    
    output_filename = input_filename.replace('.txt', '_output.txt')
    
    try:
        cmd = [sys.executable, 'word_generator.py', '-dr', input_filename, output_filename]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout:\n{result.stdout}")
        print(f"Stderr:\n{result.stderr}")
        
        if os.path.exists(output_filename):
            with open(output_filename, 'r') as f:
                output = f.read()
            print(f"Output file content:\n{output}")
        
    finally:
        try:
            os.unlink(input_filename)
            if os.path.exists(output_filename):
                os.unlink(output_filename)
        except:
            pass

def debug_syllabification():
    """Debug syllabification."""
    print("\n=== DEBUGGING SYLLABIFICATION ===")
    
    input_content = """
V: aeiou
C: bcdfg

CV
CVC

a/e/_

-syll
ALLOWED_ONSETS: C
ALLOWED_CODAS: C
STRESS_PATTERNS: 1 2
-end-syll

-dict
banana casa
-end-dict
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as input_file:
        input_file.write(input_content)
        input_filename = input_file.name
    
    output_filename = input_filename.replace('.txt', '_output.txt')
    
    try:
        cmd = [sys.executable, 'word_generator.py', '-ds', input_filename, output_filename]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout:\n{result.stdout}")
        print(f"Stderr:\n{result.stderr}")
        
        if os.path.exists(output_filename):
            with open(output_filename, 'r') as f:
                output = f.read()
            print(f"Output file content:\n{output}")
        
    finally:
        try:
            os.unlink(input_filename)
            if os.path.exists(output_filename):
                os.unlink(output_filename)
        except:
            pass

def main():
    """Run debug tests."""
    if not os.path.exists("word_generator.py"):
        print("❌ word_generator.py not found in current directory")
        sys.exit(1)
    
    debug_category_parsing()
    debug_weighted_categories()
    debug_replacement_rules()
    debug_syllabification()

if __name__ == "__main__":
    main()