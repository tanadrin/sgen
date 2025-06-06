# Word Generator

A flexible tool for generating words in constructed languages with support for phonological rules, sound changes, syllabification, and stress patterns. 

## Features

- **Word Generation**: Generate words based on syllable structure templates
- **Flexible Rule Syntax**: Support for optional and alternative categories in templates
- **Sound Changes**: Apply complex phonological rules with environmental conditioning
- **Dictionary Mode**: Process existing word lists through sound change rules
- **Syllabification**: Automatic syllable boundary detection based on onset/coda rules (experimental)
- **Stress Assignment**: Configurable primary and secondary stress patterns (experimental)
- **Syllable-Sensitive Sound Changes**: Apply phonological rules based on syllable structure and stress patterns (experimental)
- **Multiple Output Formats**: Support for verbose output, rule tracking, and input/output comparison

## Installation

No installation required. Simply download the files and ensure you have Python 3.6 or higher.

## Quick Start

### Basic Word Generation

```bash
python word_generator.py input.txt output.txt 10
```

This generates 10 words based on the rules in `input.txt` and saves them to `output.txt`.

### Dictionary Processing

```bash
python word_generator.py -d input.txt output.txt
```

This processes words from the `-dict` section of `input.txt` through any defined sound change rules.

## Input File Format

### Categories

Define character categories that can be used in word structure rules:

```
V: aeiou          # Vowels
C: bcdfghjklmnpqrstvwxyz  # Consonants
L: lr             # Liquids
N: mn             # Nasals
```

**Important**: Category names and contents cannot use reserved characters: `ˈ ˌ ˘ σ ! [ ] ( ) ² - → / > # : _`

### Word Structure Rules

Define templates for word generation using category letters:

```
CV               # Consonant + Vowel
CVC              # Consonant + Vowel + Consonant
CVCV             # Two syllables
```

#### Flexible Rule Syntax

Use parentheses for optional and alternative elements:

```
CV(C)            # CV or CVC (optional final consonant)
S(F,L)VC         # SVC, SFVC, or SLVC (optional F or L or none)
S(!F,L)VC        # SFVC or SLVC (mandatory choice: F or L)
C(V)(C)          # C, CV, CC, or CVC (multiple optional elements)
```

### Sound Change Rules

Apply phonological transformations using the format `input/output/environment`; the slash character can be replaced with `→`:

```
# Basic replacement
a/e/_            # Replace 'a' with 'e' everywhere

# Environmental conditioning
t/d/V_V          # Voice 't' to 'd' between vowels
k//_#            # Delete 'k' at word end
/e/#_s           # Insert 'e' before word-initial 's'

# Category-based rules
P/B/V_V          # Voice stops between vowels (P and B must be same length)

# Special symbols
n/²/_a           # Double 'n' before 'a' (² = doubling)

# Syllable and stress-sensitive rules (requires -s flag)
σ//#_            # Delete first syllable
σ/ˈσ/#_          # Move primary stress to first syllable
˘σ//ˈσ_σ         # Delete unstressed syllable after stressed syllable
a/e/˘_           # Change 'a' to 'e' in unstressed syllables only
```

#### Syllable and Stress Rules

**Note**: These rules only work when the `-s` flag is enabled and require syllabified input to function correctly.

**Syllable Operations**:
- `σ` - Represents any syllable
- `ˈσ` - Syllable with primary stress
- `ˌσ` - Syllable with secondary stress  
- `˘σ` - Unstressed syllable

**Stress Environment**:
- `ˈ` in environment - Within a syllable with primary stress
- `ˌ` in environment - Within a syllable with secondary stress
- `˘` in environment - Within an unstressed syllable

**Examples**:
```
σ//#_            # Delete first syllable: "ba.na.na" → "na.na"
σ//_#            # Delete last syllable: "ba.na.na" → "ba.na"
σ/ˈσ/#_          # Move primary stress to first syllable
˘σ//ˈσ_σ         # Syncope: delete unstressed syllable after stressed one
a/e/ˈ_           # Raise 'a' to 'e' in stressed syllables
o/u/˘_           # Raise 'o' to 'u' in unstressed syllables
```

#### Environment Syntax

- `_` - No environmental restriction
- `#` - Word boundary
- `V_C` - After vowel, before consonant
- `[aei]_` - After specific characters (ad-hoc categories)
- `ˈ_` or `_ˈ` - In stressed syllable (requires `-s` flag)
- `ˌ_` or `_ˌ` - In secondarily stressed syllable (requires `-s` flag)
- `˘_` or `_˘` - In unstressed syllable (requires `-s` flag)
- Category letters represent their defined character sets

#### Optional Elements in Environments

Use parentheses for optional elements in environments, just like in word structure rules:

```
k/g/#(V)_V       # k→g at word start, optionally after vowel, before vowel
                 # Equivalent to: k/g/#_V and k/g/#V_V
t/d/(C)(L)_V     # t→d optionally after consonant and/or liquid, before vowel
                 # Expands to: _V, C_V, L_V, CL_V
s/z/V(!P,B)_V    # s→z after vowel, then mandatory P or B, before vowel
                 # Expands to: VP_V, VB_V (no V_V option)
```

**Note**: The syllable boundary character `.` is not valid in replacement rules. Use stress markers (`ˈ`, `ˌ`, `˘`) to reference syllable contexts instead.

### Dictionary Section

Process existing words instead of generating new ones:

```
-dict
banana
casa
data
already.syllabified.word
-end-dict
```

**Important Notes**: 
- When using dictionary mode (`-d` flag), syllable boundaries (`.`) and stress marks (`ˈ`, `ˌ`) are automatically removed before applying sound change rules
- Avoid using reserved characters in dictionary entries: `σ ! [ ] ( ) ² - → / > # :`
- Only use `.`, `ˈ`, `ˌ` for their intended syllabification and stress purposes

### Syllabification Section

Define rules for syllable boundaries and stress patterns:

```
-syll
ALLOWED_ONSETS: C L N S CL CR SL SP TR
ALLOWED_CODAS: C N S
STRESS_PATTERNS: 1 2 1-2 2-1 1-3
-end-syll
```

#### Onset/Coda Rules

- **Individual sequences**: `st ps kt`
- **Categories**: `C L` (expands to all possible combinations)
- **Mixed**: `sP CL` (combines literals with category expansions)

#### Stress Patterns

- `1` - Primary stress on syllable 1
- `2` - Primary stress on syllable 2
- `1-2` - Primary stress on syllable 1, secondary on syllable 2
- `2-1` - Primary stress on syllable 2, secondary on syllable 1

### Comments

Use `#` for comments. Inline comments are supported:

```
V: aeiou  # This is a comment
# This is a full-line comment
a/e/_     # Replace a with e
```

## Command Line Options

### Flags

- `-v` **Verbose**: Print generated words to terminal in addition to file
- `-d` **Dictionary**: Process words from `-dict` section instead of generating
- `-i` **Input format**: Show input → output format (requires `-d`)
- `-r` **Rules**: Show applied sound change rules in square brackets
- `-s` **Syllabification**: Apply syllabification and stress rules

### Usage Patterns

```bash
# Basic generation
python word_generator.py input.txt output.txt 20

# Dictionary processing with verbose output
python word_generator.py -vd input.txt output.txt

# Show input/output transformation with rule tracking
python word_generator.py -dir input.txt output.txt

# Generate words with syllabification and stress
python word_generator.py -vs input.txt output.txt 15

# Complete dictionary processing with all features
python word_generator.py -vdirs input.txt output.txt

# Dictionary processing with syllable-sensitive sound changes
python word_generator.py -ds input.txt output.txt
```

## Output Formats

### Basic Output

```
casa
banana
data
```

### Input/Output Format (`-i` flag with `-d`)

```
banana → benene
casa   → cese
data   → dete
```

### Rule Tracking (`-r` flag)

```
banana  [a/e/_]
casa    [a/e/_]
modern
```

### Syllabification with Stress-Sensitive Changes (`-s` flag)

```
ˈba.na.na     # Primary stress on first syllable
ca.ˈse        # Primary stress on second syllable  
ˌmo.ˈdern     # Secondary stress on first, primary on second
syn.co.pe     # Result of unstressed syllable deletion
```

### Combined Format (`-dirs` flags)

```
banana  → ˈbe.ne.ne  [a/e/_]
casa    → ca.ˈse     [a/e/_]
modern  → ˌmo.ˈdern  [σ/ˈσ/#_]
```

## Output Symbols

- `.` - Syllable boundary
- `ˈ` - Primary stress (placed before stressed syllable)
- `ˌ` - Secondary stress (placed before secondarily stressed syllable)
- `˘` - Unstressed syllable marker (only in rules, not output)
- `σ` - Syllable marker (only in rules, not output)
- `→` - Input/output separator (dictionary mode with `-i`)
- `[rule]` - Applied sound change rule (with `-r`)
- `²` - Doubling symbol (only in rules, not output)

## Advanced Features

### Category Length Matching

When using category-to-category sound changes, both categories must have the same number of elements:

```
P: ptk    # 3 elements
B: bdg    # 3 elements
P/B/_     # Valid: p→b, t→d, k→g

P: ptk    # 3 elements  
V: aeiou  # 5 elements
P/V/_     # Invalid: will generate warning
```

### Rule Expansion

Complex syllable templates are automatically expanded:

```
CV(C,L)V  # Expands to: CVCV, CCVY, CLVV
```

The system will display expansion information when processing.

### Word Boundary Handling

The `#` symbol represents word boundaries in sound change environments:

```
a//_#     # Delete word-final 'a'
/e/#_s    # Insert 'e' before word-initial 's'
```

### Syllable and Stress-Sensitive Rules

When using the `-s` flag, you can apply rules that operate on syllables and stress patterns:

```
# Syllable operations
σ//#_            # Delete first syllable
σ//_#            # Delete last syllable  
σ/ˈσ/#_          # Move primary stress to first syllable
ˈσ/ˌσ/_          # Reduce primary stress to secondary everywhere

# Stress-sensitive character changes
a/e/ˈ_           # Raise 'a' to 'e' in stressed syllables
o/u/˘_           # Raise 'o' to 'u' in unstressed syllables
˘σ//ˈσ_σ         # Syncope: delete unstressed syllable after stressed syllable

# Complex prosodic rules
C//ˌ_σ           # Delete consonants at the start of secondarily stressed syllables
V//_˘σ#          # Delete vowels before final unstressed syllables
```

**Important**: 
- Syllable-sensitive rules only work with the `-s` flag enabled
- Words must be syllabified for these rules to apply
- The `.` character cannot be used in rule environments - use stress markers instead

## Example Input File

```
# Phoneme inventory
V: aeiou
C: bcdfghjklmnpqrstvwxyz
L: lr
N: mn
S: sz
P: ptk
B: bdg

# Syllable patterns  
CV
CVC
CV(L)V
C(V)CVC

# Sound changes
# Vowel harmony
a/e/_CV

# Consonant changes
P/B/V_V          # Intervocalic voicing
C//_#            # Final consonant deletion
L///_C           # Liquid deletion before consonants

# Syllable and stress-sensitive changes (require -s flag)
σ//#_            # Delete first syllable
a/e/˘_           # Change 'a' to 'e' in unstressed syllables only
ˈσ/ˌσ/_          # Reduce all primary stress to secondary

# Syllabification rules
-syll
ALLOWED_ONSETS: C L N S CL CN SL SP BR TR
ALLOWED_CODAS: C N S  
STRESS_PATTERNS: 1 2 1-2 2-1
-end-syll

# Test vocabulary
-dict
banana
casa
modern
system
-end-dict
```

## Error Handling

The tool provides helpful error messages for:

- Missing input files
- Invalid rule syntax
- Category length mismatches
- Invalid flag combinations
- Malformed syllabification rules
- Use of reserved characters in categories
- Invalid colon placement in category definitions

## Reserved Characters

The following characters have special meanings and should not be used in categories or dictionary entries except for their intended purposes:

- `ˈ ˌ ˘` - Stress markers (only for stress/syllable patterns)
- `σ` - Syllable marker (only in replacement rules)
- `! [ ] ( ) ² - → / > #` - Rule syntax characters
- `:` - Category definition separator (must be in second position)
- `.` - Syllable boundary marker (only for syllabification)

## Tips

1. **Start simple**: Begin with basic CV patterns and simple sound changes
2. **Test incrementally**: Add rules one at a time to verify behavior
3. **Use dictionary mode**: Test sound changes on known words first
4. **Check category lengths**: Ensure category-to-category mappings have equal lengths
5. **Use comments**: Document your rules for future reference
6. **Syllabification testing**: Use dictionary mode to test syllabification rules on existing words
7. **Syllable-sensitive rules**: Enable `-s` flag to use prosodic phonology rules
8. **Character restrictions**: Avoid reserved characters in categories and dictionary entries
9. **Optional environments**: Use parentheses for optional elements in rule environments
10. **Environment expansion**: Complex environments like `#(V)_V` are automatically expanded into all possible combinations

## File Structure

The tool is organized into focused modules:

- `word_generator.py` - Main entry point
- `core/parser.py` - Input file parsing
- `core/word_generation.py` - Word generation logic
- `core/sound_changes.py` - Sound change application
- `core/syllabification.py` - Syllabification and stress
- `utils/cli.py` - Command line interface
- `utils/file_io.py` - File operations
- `config.py` - Configuration constants

Additionally, the directory `tests/` contains unit and integration tests you can use to make sure new additions don't break existing functionality. Run the test suite with

```bash
python tests/test_runner.py
```