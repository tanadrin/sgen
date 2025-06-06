#!/usr/bin/env python3
"""
Verification script to test the weighted categories implementation step by step.
"""

import tempfile
import os
import subprocess
import sys

def test_basic_parsing():
    """Test that basic category parsing still works."""
    print("1. Testing basic category parsing...")
    
    input_content = """V: aeiou
C: bcdfg

CV
CVC
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(input_content)
        input_file = f.name
    
    output_file = input_file.replace('.txt', '_out.txt')
    
    try:
        cmd = [sys.executable, 'word_generator.py', input_file, output_file, '5']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        print(f"   Return code: {result.returncode}")
        if result.returncode != 0:
            print(f"   STDERR: {result.stderr}")
            return False
        
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                output = f.read().strip()
            words = output.split('\n')
            print(f"   Generated {len(words)} words: {words}")
            
            # Check word lengths
            for word in words:
                if len(word) not in [2, 3]:
                    print(f"   ❌ Word '{word}' has length {len(word)}, expected 2 or 3")
                    return False
            
            print("   ✓ Basic parsing works")
            return True
        else:
            print("   ❌ No output file generated")
            return False
    
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False
    
    finally:
        try:
            os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)
        except:
            pass

def test_weighted_parsing():
    """Test weighted category parsing."""
    print("\n2. Testing weighted category parsing...")
    
    input_content = """V: a{3} e{2} i o u
C: bcdfg

CV
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(input_content)
        input_file = f.name
    
    output_file = input_file.replace('.txt', '_out.txt')
    
    try:
        cmd = [sys.executable, 'word_generator.py', input_file, output_file, '20']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        print(f"   Return code: {result.returncode}")
        if result.returncode != 0:
            print(f"   STDERR: {result.stderr}")
            return False
        
        print(f"   STDOUT:\n{result.stdout}")
        
        # Check for weight information
        if "Category 'V' weights:" not in result.stdout:
            print("   ❌ Weight information not printed")
            return False
        
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                output = f.read().strip()
            
            # Count vowel frequencies
            a_count = output.count('a')
            e_count = output.count('e')
            i_count = output.count('i')
            
            print(f"   Vowel counts: a={a_count}, e={e_count}, i={i_count}")
            
            if a_count > 0:  # Should have some 'a's since it's weighted heavily
                print("   ✓ Weighted parsing works")
                return True
            else:
                print("   ❌ No 'a' characters found despite heavy weighting")
                return False
        else:
            print("   ❌ No output file generated")
            return False
    
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False
    
    finally:
        try:
            os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)
        except:
            pass

def test_replacement_rules():
    """Test replacement rules with weighted categories."""
    print("\n3. Testing replacement rules...")
    
    input_content = """P: p t k
B: b d g

P/B/_

-dict
papa tata kaka
-end-dict
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(input_content)
        input_file = f.name
    
    output_file = input_file.replace('.txt', '_out.txt')
    
    try:
        cmd = [sys.executable, 'word_generator.py', '-d', input_file, output_file]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        print(f"   Return code: {result.returncode}")
        if result.returncode != 0:
            print(f"   STDERR: {result.stderr}")
            return False
        
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                output = f.read().strip()
            
            print(f"   Output: {output}")
            
            # Check that P→B replacement occurred
            if any(char in output for char in 'ptk'):
                print("   ❌ Found unreplaced P sounds")
                return False
            
            if any(char in output for char in 'bdg'):
                print("   ✓ Replacement rules work")
                return True
            else:
                print("   ❌ No B sounds found")
                return False
        else:
            print("   ❌ No output file generated")
            return False
    
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False
    
    finally:
        try:
            os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)
        except:
            pass

def test_reserved_characters():
    """Test reserved character validation."""
    print("\n4. Testing reserved character validation...")
    
    input_content = """V: a{b}cd

CV
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(input_content)
        input_file = f.name
    
    output_file = input_file.replace('.txt', '_out.txt')
    
    try:
        cmd = [sys.executable, 'word_generator.py', input_file, output_file, '5']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        print(f"   Return code: {result.returncode}")
        
        # Should fail
        if result.returncode == 0:
            print("   ❌ Should have failed with reserved character error")
            return False
        
        combined_output = result.stdout + result.stderr
        if "reserved character" in combined_output:
            print("   ✓ Reserved character validation works")
            return True
        else:
            print(f"   ❌ Expected reserved character error, got: {combined_output}")
            return False
    
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False
    
    finally:
        try:
            os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)
        except:
            pass

def main():
    """Run verification tests."""
    print("Weighted Categories Implementation Verification")
    print("=" * 50)
    
    if not os.path.exists("word_generator.py"):
        print("❌ word_generator.py not found")
        sys.exit(1)
    
    tests = [
        test_basic_parsing,
        test_weighted_parsing,
        test_replacement_rules,
        test_reserved_characters
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ Test exception: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Verification Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 Implementation is working correctly!")
    else:
        print("❌ Some issues found - check the failures above")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)