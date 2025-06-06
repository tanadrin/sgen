#!/usr/bin/env python3
"""
Input file parser for word generator.
Handles parsing of categories, rules, replacement rules, and dictionary words.
Now supports weighted categories using {weight} syntax.
"""

import sys
import re
from typing import Dict, List, Tuple, Optional
from core.sound_changes import validate_category_definition, validate_dictionary_word


def parse_weighted_category(content: str) -> List[Tuple[str, int]]:
    """
    Parse a category with optional weights into (character, weight) tuples.
    
    Examples:
    - "a{3} e{2} i o u" -> [('a', 3), ('e', 2), ('i', 1), ('o', 1), ('u', 1)]
    - "aeiou" -> [('a', 1), ('e', 1), ('i', 1), ('o', 1), ('u', 1)]
    - "bcdfg" -> [('b', 1), ('c', 1), ('d', 1), ('f', 1), ('g', 1)]
    """
    items = []
    
    # Handle both weighted and unweighted entries
    # Split by whitespace first to handle weighted entries properly
    parts = content.split()
    
    for part in parts:
        # Check if this part has a weight specification
        if '{' in part and '}' in part:
            # Extract character(s) and weight
            brace_start = part.index('{')
            brace_end = part.index('}')
            
            char = part[:brace_start]
            weight_str = part[brace_start+1:brace_end]
            
            try:
                weight = int(weight_str)
                items.append((char, weight))
            except ValueError:
                # Invalid weight, treat as weight 1
                items.append((char, 1))
        else:
            # No weight specification
            # If this is a single part with no spaces, treat each character individually
            for char in part:
                items.append((char, 1))
    
    return items


def expand_weighted_category(weighted_items: List[Tuple[str, int]]) -> List[str]:
    """
    Expand weighted category items into a list where each character appears
    according to its weight.
    
    Example: [('a', 3), ('e', 2), ('i', 1)] -> ['a', 'a', 'a', 'e', 'e', 'i']
    """
    expanded = []
    for char, weight in weighted_items:
        # Handle multi-character entries properly
        if len(char) > 1:
            # For multi-character entries, treat as single unit repeated
            expanded.extend([char] * weight)
        else:
            # For single characters, repeat according to weight
            expanded.extend([char] * weight)
    return expanded


def expand_rule(rule: str) -> List[str]:
    """
    Expand a rule with optional categories into multiple concrete rules.
    
    Examples:
    - CV(C) -> [CV, CVC]
    - S(F,L)VC -> [SVC, SFVC, SLVC]
    - S(!F,L)VC -> [SFVC, SLVC]
    """
    # Find all parenthetical groups
    paren_groups = []
    i = 0
    
    while i < len(rule):
        if rule[i] == '(':
            # Find matching closing parenthesis
            depth = 1
            start = i
            i += 1
            while i < len(rule) and depth > 0:
                if rule[i] == '(':
                    depth += 1
                elif rule[i] == ')':
                    depth -= 1
                i += 1
            
            if depth == 0:
                # Found complete group
                group_content = rule[start+1:i-1]
                paren_groups.append((start, i, group_content))
            else:
                # Unmatched parenthesis - treat as literal
                i = start + 1
        else:
            i += 1
    
    # If no parentheses found, return the rule as-is
    if not paren_groups:
        return [rule]
    
    # Process groups from right to left to maintain correct indices
    paren_groups.reverse()
    
    # Start with the original rule
    expanded_rules = [rule]
    
    for start, end, group_content in paren_groups:
        new_expanded_rules = []
        
        for current_rule in expanded_rules:
            # Parse the group content
            is_mandatory = group_content.startswith('!')
            if is_mandatory:
                group_content = group_content[1:]
            
            # Split alternatives by comma
            alternatives = [alt.strip() for alt in group_content.split(',')]
            
            # Generate all combinations for this group
            if is_mandatory:
                # Must choose one alternative, no empty option
                options = alternatives
            else:
                # Can choose any alternative or nothing
                options = [''] + alternatives
            
            # Create new rules for each option
            for option in options:
                new_rule = current_rule[:start] + option + current_rule[end:]
                new_expanded_rules.append(new_rule)
        
        expanded_rules = new_expanded_rules
    
    # Remove duplicates while preserving order
    seen = set()
    result = []
    for rule in expanded_rules:
        if rule not in seen:
            seen.add(rule)
            result.append(rule)
    
    return result


def _process_line_comments(line: str) -> str:
    """Process a line to remove comments while preserving rule syntax."""
    # Handle inline comments for replacement rules more carefully
    if '# ' in line and any(sep in line for sep in ['/', '>', '→']):
        # This is a replacement rule with a comment
        # We need to find the comment part, which is '# ' that's not part of the rule
        
        # Strategy: find all '# ' occurrences and use the one that's most likely a comment
        # A comment '# ' is typically preceded by whitespace
        comment_pos = -1
        for i in range(len(line) - 1):
            if line[i] == '#' and line[i + 1] == ' ':
                # Check if this # is preceded by whitespace (indicating it's a comment)
                if i > 0 and line[i - 1].isspace():
                    comment_pos = i
                    break
        
        if comment_pos != -1:
            line = line[:comment_pos].rstrip()
    elif '# ' in line:
        # Not a replacement rule, treat first # space as comment
        comment_pos = line.find('# ')
        line = line[:comment_pos].rstrip()
    
    return line


def _validate_colon_usage(line: str, line_num: int) -> bool:
    """Validate that colons only appear in position 2 for category definitions."""
    colon_positions = [i for i, char in enumerate(line) if char == ':']
    
    if len(colon_positions) == 0:
        return True  # No colons, that's fine
    
    if len(colon_positions) > 1:
        print(f"Error: Line {line_num}: Multiple colons found in line")
        return False
    
    # Single colon - must be at position 1 (second character) for category definition
    if colon_positions[0] != 1:
        print(f"Error: Line {line_num}: Colon must be in second position for category definitions")
        return False
    
    return True


def _categorize_line(line: str) -> Tuple[str, str]:
    """Categorize a line into its type and return (type, line)."""
    # Check if it's a category definition
    if ':' in line and not any(sep in line for sep in ['/', '>', '→']):
        return 'category', line
    
    # Check if it's a replacement rule
    elif any(sep in line for sep in ['/', '>', '→']):
        return 'replacement', line
    
    # Check if it's a word structure rule (category characters and parentheses)
    elif all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ()!,' or c.isalpha() for c in line):
        return 'structure', line
    
    else:
        return 'unknown', line


def parse_input_file(filename: str, dict_mode: bool = False) -> Tuple[Dict[str, List[str]], List[str], List[Tuple[str, int]], List[str], List[str]]:
    """
    Parse the input file to extract categories, word structure rules, replacement rules, dictionary words, and syllabification rules.
    
    Returns:
        Tuple of (categories, rules, replacement_rules, dict_words, syll_rules)
    """
    categories = {}
    rules = []
    replacement_rules = []
    dict_words = []
    syll_rules = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Process lines to handle comments
        processed_lines = []
        for line_num, line in enumerate(lines, 1):
            line = line.rstrip('\n\r')  # Remove line endings but preserve other whitespace
            
            # Skip empty lines
            if not line.strip():
                continue
            
            # Skip lines that start with #
            if line.strip().startswith('#'):
                continue
            
            # Process comments
            line = _process_line_comments(line)
            
            # Skip if line becomes empty after removing comment
            if not line.strip():
                continue
            
            processed_lines.append((line.strip(), line_num))
        
        in_dict_section = False
        dict_started = False
        in_syll_section = False
        
        for line, line_num in processed_lines:
            # Check for dictionary section markers
            if line == '-dict':
                in_dict_section = True
                dict_started = True
                continue
            elif line == '-end-dict':
                in_dict_section = False
                continue
            
            # Check for syllabification section markers
            elif line == '-syll':
                in_syll_section = True
                continue
            elif line == '-end-syll':
                in_syll_section = False
                continue
            
            # If we're in syllabification section, collect syllabification rules
            if in_syll_section:
                syll_rules.append(line)
                continue
            
            # If we're in dictionary mode, collect dictionary words
            if in_dict_section:
                if dict_mode:
                    # Split on spaces to handle multiple words per line
                    words_in_line = line.split()
                    # Validate each dictionary word
                    for word in words_in_line:
                        validated_word = validate_dictionary_word(word)
                        dict_words.append(validated_word)
                continue  # Skip processing these lines as rules
            
            # If not in dict mode but we've seen -dict, ignore everything after it
            if dict_started and not dict_mode:
                continue
            
            # Validate colon usage
            if not _validate_colon_usage(line, line_num):
                sys.exit(1)
            
            # Categorize and process the line
            line_type, line_content = _categorize_line(line)
            
            if line_type == 'category':
                category_char, characters = line_content.split(':', 1)
                category_char = category_char.strip()
                characters = characters.strip()
                
                # Parse weighted category
                weighted_items = parse_weighted_category(characters)
                
                # Validate category definition (check the base characters, not weights)
                base_chars = ''.join(char for char, weight in weighted_items)
                if not validate_category_definition(category_char, base_chars, line_num):
                    sys.exit(1)
                
                # Also validate that no reserved characters appear in the original content
                # This catches cases like a{b}cd where 'b' is inside braces
                for char in characters:
                    if char in 'ˈˌ˘σ![]()²-→/>#:{}':
                        # Allow digits and braces only in proper weight syntax
                        if char in '{}':
                            # Check if this is part of a proper weight specification
                            continue  # We'll validate this more carefully below
                        elif char.isdigit():
                            continue  # Digits are allowed in weight specifications
                        else:
                            print(f"Error: Line {line_num}: Category '{category_char}' contains reserved character '{char}'")
                            sys.exit(1)
                
                # Additional validation for brace usage
                if '{' in characters or '}' in characters:
                    # Validate proper brace usage - must be in pairs with digits between
                    import re
                    # Find all brace pairs
                    brace_pattern = r'\{([^}]*)\}'
                    brace_matches = re.findall(brace_pattern, characters)
                    
                    for match in brace_matches:
                        if not match.isdigit():
                            print(f"Error: Line {line_num}: Invalid weight specification '{{{match}}}' in category '{category_char}'")
                            sys.exit(1)
                    
                    # Check for unmatched braces
                    open_braces = characters.count('{')
                    close_braces = characters.count('}')
                    if open_braces != close_braces:
                        print(f"Error: Line {line_num}: Unmatched braces in category '{category_char}'")
                        sys.exit(1)
                
                # Expand weighted category into final list
                expanded_chars = expand_weighted_category(weighted_items)
                categories[category_char] = expanded_chars
                
                # Print weight information if weights were specified
                if any(weight != 1 for char, weight in weighted_items):
                    weight_info = ', '.join(f"{char}:{weight}" for char, weight in weighted_items)
                    print(f"Category '{category_char}' weights: {weight_info}")
            
            elif line_type == 'replacement':
                # Normalize separators to /
                normalized_line = line_content.replace('>', '/').replace('→', '/')
                replacement_rules.append((normalized_line, line_num))
            
            elif line_type == 'structure':
                # Expand the rule if it contains parentheses
                expanded = expand_rule(line_content.strip())
                rules.extend(expanded)
                if len(expanded) > 1:
                    print(f"Expanded rule '{line_content.strip()}' into {len(expanded)} variants: {', '.join(expanded)}")
            
            else:
                print(f"Warning: Line {line_num} is not a valid category, replacement rule, or word structure rule: '{line_content}'")
    
    except FileNotFoundError:
        print(f"Error: Input file '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    return categories, rules, replacement_rules, dict_words, syll_rules