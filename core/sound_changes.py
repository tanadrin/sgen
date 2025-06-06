#!/usr/bin/env python3
"""
Sound change application for word generator.
Handles all replacement rule parsing and application, including syllable and stress-sensitive rules.
Updated to handle weighted categories and reserved character validation.
"""

import re
from typing import Dict, List, Tuple, Optional


def clean_word_for_processing(word: str) -> str:
    """Remove syllable breaks and stress marks from a word for rule processing."""
    # Remove syllable boundaries and stress marks
    cleaned = word.replace('.', '').replace('ˈ', '').replace('ˌ', '')
    return cleaned


def validate_category_definition(category_char: str, characters: str, line_num: int) -> bool:
    """Validate that a category definition doesn't use reserved characters."""
    reserved_chars = set('ˈˌ˘σ![]()²-→/>#:{}')  # Added {} to reserved chars
    
    # Check category character
    if category_char in reserved_chars:
        print(f"Error: Line {line_num}: Category name '{category_char}' uses reserved character")
        return False
    
    # Check category contents
    for char in characters:
        if char in reserved_chars:
            print(f"Error: Line {line_num}: Category '{category_char}' contains reserved character '{char}'")
            return False
    
    return True


def validate_dictionary_word(word: str) -> str:
    """Validate and clean dictionary word, warning about problematic characters."""
    problematic_chars = set('σ![]()²-→/>#:{}')  # Added {} to problematic chars
    found_problematic = []
    
    for char in word:
        if char in problematic_chars:
            found_problematic.append(char)
    
    if found_problematic:
        print(f"Warning: Dictionary word '{word}' contains potentially problematic characters: {found_problematic}")
    
    return word


def is_syllable_sensitive_rule(rule_str: str) -> bool:
    """Check if a replacement rule involves syllables or stress."""
    syllable_stress_chars = set('σˈˌ˘')
    return any(char in rule_str for char in syllable_stress_chars)


def parse_syllable_in_rule(rule_part: str) -> Tuple[Optional[str], bool]:
    """
    Parse a syllable specification in a rule.
    Returns (stress_type, is_syllable) where stress_type is 'primary', 'secondary', 'unstressed', or None
    """
    if 'σ' not in rule_part:
        return None, False
    
    if 'ˈσ' in rule_part:
        return 'primary', True
    elif 'ˌσ' in rule_part:
        return 'secondary', True
    elif '˘σ' in rule_part:
        return 'unstressed', True
    elif 'σ' in rule_part:
        return None, True  # Any syllable
    
    return None, False


def get_syllable_stress_type(syllable: str) -> str:
    """Determine the stress type of a syllable."""
    if syllable.startswith('ˈ'):
        return 'primary'
    elif syllable.startswith('ˌ'):
        return 'secondary'
    else:
        return 'unstressed'


def split_syllabified_word(word: str) -> List[str]:
    """Split a syllabified word into syllables, preserving stress marks."""
    if '.' not in word:
        # Single syllable
        return [word]
    
    return word.split('.')


def join_syllables(syllables: List[str]) -> str:
    """Join syllables back into a word."""
    return '.'.join(syllables)


def remove_stress_from_syllables(syllables: List[str], stress_type: str) -> List[str]:
    """Remove specific stress type from all syllables."""
    result = []
    stress_char = 'ˈ' if stress_type == 'primary' else 'ˌ'
    
    for syllable in syllables:
        if syllable.startswith(stress_char):
            result.append(syllable[1:])  # Remove stress mark
        else:
            result.append(syllable)
    
    return result


def apply_syllable_replacement(word: str, rule: Dict[str, str]) -> str:
    """Apply a syllable-sensitive replacement rule."""
    input_part = rule['input']
    output_part = rule['output']
    environment = rule['environment']
    
    # Split word into syllables
    syllables = split_syllabified_word(word)
    
    # Handle different types of syllable rules
    input_stress, input_is_syllable = parse_syllable_in_rule(input_part)
    output_stress, output_is_syllable = parse_syllable_in_rule(output_part)
    
    if not input_is_syllable:
        return word  # Not a syllable rule
    
    result_syllables = syllables[:]
    
    # Syllable deletion (σ//)
    if input_is_syllable and not output_part:
        new_syllables = []
        
        for i, syllable in enumerate(syllables):
            should_delete = False
            
            # Check if this syllable matches the input specification
            if input_stress is None:
                # Any syllable - check environment
                if environment == '#_':  # Word-initial
                    should_delete = (i == 0)
                elif environment == '_#':  # Word-final
                    should_delete = (i == len(syllables) - 1)
                elif environment == '_':  # Any position
                    should_delete = True
                # Add more environment patterns as needed
            else:
                # Specific stress type
                syllable_stress = get_syllable_stress_type(syllable)
                if syllable_stress == input_stress:
                    # Check environment if needed
                    should_delete = True
            
            if not should_delete:
                new_syllables.append(syllable)
        
        return join_syllables(new_syllables)
    
    # Stress movement (σ/ˈσ/ or similar)
    elif input_is_syllable and output_is_syllable:
        if input_stress is None and output_stress is not None:
            # Moving stress to specific position
            new_syllables = syllables[:]
            
            # First remove existing stress of this type
            if output_stress == 'primary':
                new_syllables = remove_stress_from_syllables(new_syllables, 'primary')
            elif output_stress == 'secondary':
                new_syllables = remove_stress_from_syllables(new_syllables, 'secondary')
            
            # Then add stress to target position
            if environment == '#_':  # First syllable
                if len(new_syllables) > 0:
                    stress_char = 'ˈ' if output_stress == 'primary' else 'ˌ'
                    # Remove any existing stress from first syllable
                    first_syll = new_syllables[0]
                    if first_syll.startswith('ˈ') or first_syll.startswith('ˌ'):
                        first_syll = first_syll[1:]
                    new_syllables[0] = stress_char + first_syll
            elif environment == '_#':  # Last syllable
                if len(new_syllables) > 0:
                    stress_char = 'ˈ' if output_stress == 'primary' else 'ˌ'
                    # Remove any existing stress from last syllable
                    last_syll = new_syllables[-1]
                    if last_syll.startswith('ˈ') or last_syll.startswith('ˌ'):
                        last_syll = last_syll[1:]
                    new_syllables[-1] = stress_char + last_syll
            
            return join_syllables(new_syllables)
    
    return word


def apply_stress_sensitive_character_replacement(word: str, rule: Dict[str, str]) -> str:
    """Apply character replacement that's sensitive to syllable stress."""
    input_part = rule['input']
    output_part = rule['output']
    environment = rule['environment']
    
    # Check if environment specifies stress context
    stress_context = None
    if 'ˈ' in environment:
        stress_context = 'primary'
    elif 'ˌ' in environment:
        stress_context = 'secondary'
    elif '˘' in environment:
        stress_context = 'unstressed'
    
    if stress_context is None:
        return word  # Not a stress-sensitive rule
    
    # Split into syllables
    syllables = split_syllabified_word(word)
    result_syllables = []
    
    for syllable in syllables:
        syllable_stress = get_syllable_stress_type(syllable)
        
        if syllable_stress == stress_context:
            # Apply replacement within this syllable
            # Remove stress mark temporarily for replacement
            clean_syllable = syllable
            stress_prefix = ''
            if clean_syllable.startswith('ˈ'):
                stress_prefix = 'ˈ'
                clean_syllable = clean_syllable[1:]
            elif clean_syllable.startswith('ˌ'):
                stress_prefix = 'ˌ'
                clean_syllable = clean_syllable[1:]
            
            # Apply simple character replacement
            modified_syllable = clean_syllable.replace(input_part, output_part)
            result_syllables.append(stress_prefix + modified_syllable)
        else:
            result_syllables.append(syllable)
    
    return join_syllables(result_syllables)

def parse_replacement_rule(rule_str: str, line_num: int) -> Optional[Dict[str, str]]:
    """Parse a replacement rule string into components."""
    # Handle empty replacement (deletion) rules like L///_C
    if '//' in rule_str:
        # Split on // first
        parts = rule_str.split('//')
        if len(parts) == 2:
            input_part = parts[0]
            rest = parts[1]
            if rest.startswith('/'):
                # Format: input//_environment
                environment = rest[1:] if len(rest) > 1 else '_'
                return {
                    'input': input_part,
                    'output': '',
                    'environment': environment,
                    'line_num': line_num
                }
    
    # Original logic for other rule types
    parts = rule_str.split('/')
    
    if len(parts) == 1:
        print(f"Warning: Invalid replacement rule format on line {line_num}: '{rule_str}'")
        return None
    elif len(parts) == 2:
        # Format: input/output (treat as input/output/_)
        input_part, output_part = parts
        environment = '_'
    elif len(parts) == 3:
        input_part, output_part, environment = parts
        if not environment:
            environment = '_'
    else:
        print(f"Warning: Invalid replacement rule format on line {line_num}: '{rule_str}'")
        return None
    
    return {
        'input': input_part,
        'output': output_part,
        'environment': environment,
        'line_num': line_num
    }

def expand_environment_rule(environment: str) -> List[str]:
    """
    Expand an environment with optional elements into multiple concrete environments.
    
    Examples:
    - k/g/#(V)_V -> [k/g/#_V, k/g/#V_V]
    - t/d/_(C)# -> [t/d/_#, t/d/_C#]
    - s/z/V(L)_V -> [s/z/V_V, s/z/VL_V]
    """
    # Find all parenthetical groups
    paren_groups = []
    i = 0
    
    while i < len(environment):
        if environment[i] == '(':
            # Find matching closing parenthesis
            depth = 1
            start = i
            i += 1
            while i < len(environment) and depth > 0:
                if environment[i] == '(':
                    depth += 1
                elif environment[i] == ')':
                    depth -= 1
                i += 1
            
            if depth == 0:
                # Found complete group
                group_content = environment[start+1:i-1]
                paren_groups.append((start, i, group_content))
            else:
                # Unmatched parenthesis - treat as literal
                i = start + 1
        else:
            i += 1
    
    # If no parentheses found, return the environment as-is
    if not paren_groups:
        return [environment]
    
    # Process groups from right to left to maintain correct indices
    paren_groups.reverse()
    
    # Start with the original environment
    expanded_environments = [environment]
    
    for start, end, group_content in paren_groups:
        new_expanded_environments = []
        
        for current_env in expanded_environments:
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
            
            # Create new environments for each option
            for option in options:
                new_env = current_env[:start] + option + current_env[end:]
                new_expanded_environments.append(new_env)
        
        expanded_environments = new_expanded_environments
    
    # Remove duplicates while preserving order
    seen = set()
    result = []
    for env in expanded_environments:
        if env not in seen:
            seen.add(env)
            result.append(env)
    
    return result


def match_environment(word: str, position: int, environment: str, categories: Dict[str, List[str]]) -> bool:
    """Check if the environment matches at the given position in the word."""
    if environment == '_':
        return True
    
    # Expand environment if it has optional elements
    expanded_environments = expand_environment_rule(environment)
    
    # Check if any of the expanded environments match
    for expanded_env in expanded_environments:
        if _match_single_environment(word, position, expanded_env, categories):
            return True
    
    return False


def _match_single_environment(word: str, position: int, environment: str, categories: Dict[str, List[str]]) -> bool:
    """Check if a single (non-expandable) environment matches at the given position."""
    if environment == '_':
        return True
    
    # Find the underscore position in the environment
    if '_' not in environment:
        return False
    
    underscore_pos = environment.index('_')
    left_context = environment[:underscore_pos]
    right_context = environment[underscore_pos + 1:]
    
    # Check left context
    if left_context:
        if left_context == '#':
            # Word boundary at beginning
            if position != 0:
                return False
        else:
            left_start = position - len(left_context)
            if left_start < 0:
                return False
            
            word_left = word[left_start:position]
            if not match_context(word_left, left_context, categories):
                return False
    
    # Check right context
    if right_context:
        if right_context == '#':
            # Word boundary at end - position is where the character starts
            # For single character, check if position + 1 equals word length
            if position + 1 != len(word):
                return False
        else:
            right_start = position + 1  # Start after the matched character
            right_end = right_start + len(right_context)
            
            if right_end > len(word):
                return False
            
            word_right = word[right_start:right_end]
            if not match_context(word_right, right_context, categories):
                return False
    
    return True


def match_environment_for_segment(word: str, position: int, segment_length: int, environment: str, categories: Dict[str, List[str]]) -> bool:
    """Check if environment matches for a multi-character segment."""
    if environment == '_':
        return True
    
    # Expand environment if it has optional elements
    expanded_environments = expand_environment_rule(environment)
    
    # Check if any of the expanded environments match
    for expanded_env in expanded_environments:
        if _match_single_environment_for_segment(word, position, segment_length, expanded_env, categories):
            return True
    
    return False


def _match_single_environment_for_segment(word: str, position: int, segment_length: int, environment: str, categories: Dict[str, List[str]]) -> bool:
    """Check if environment matches for a multi-character segment (single environment)."""
    if environment == '_':
        return True
    
    if '_' not in environment:
        return False
    
    underscore_pos = environment.index('_')
    left_context = environment[:underscore_pos]
    right_context = environment[underscore_pos + 1:]
    
    # Check left context
    if left_context:
        if left_context == '#':
            if position != 0:
                return False
        else:
            left_start = position - len(left_context)
            if left_start < 0:
                return False
            
            word_left = word[left_start:position]
            if not match_context(word_left, left_context, categories):
                return False
    
    # Check right context
    if right_context:
        if right_context == '#':
            # For word-final position, check if we're at the end after this segment
            if position + segment_length != len(word):
                return False
        else:
            right_start = position + segment_length
            right_end = right_start + len(right_context)
            
            if right_end > len(word):
                return False
            
            word_right = word[right_start:right_end]
            if not match_context(word_right, right_context, categories):
                return False
    
    return True


def match_context(word_part: str, context_part: str, categories: Dict[str, List[str]]) -> bool:
    """Match a word part against a context part, handling categories."""
    if len(word_part) != len(context_part):
        return False
    
    for i, (word_char, context_char) in enumerate(zip(word_part, context_part)):
        if context_char == '#':
            continue  # Word boundary, handled elsewhere
        elif context_char == '_':
            continue  # Should not happen in this context
        elif context_char == '[':
            # Find the end of the ad-hoc category
            bracket_end = context_part.index(']', i)
            bracket_content = context_part[i+1:bracket_end]
            if word_char not in bracket_content:
                return False
            # Skip ahead in context_part
            context_part = context_part[:i] + context_part[bracket_end+1:]
            word_part = word_part[:i] + word_part[i+1:]
            return match_context(word_part, context_part, categories)
        elif context_char in categories:
            if word_char not in categories[context_char]:
                return False
        else:
            if word_char != context_char:
                return False
    
    return True


def match_input_at_position(word_segment: str, input_pattern: str, categories: Dict[str, List[str]]) -> bool:
    """Check if a word segment matches an input pattern."""
    if len(word_segment) != len(input_pattern):
        return False
    
    for word_char, pattern_char in zip(word_segment, input_pattern):
        if pattern_char in categories:
            if word_char not in categories[pattern_char]:
                return False
        else:
            if word_char != pattern_char:
                return False
    
    return True


def get_replacement_output(matched_segment: str, input_pattern: str, output_pattern: str, categories: Dict[str, List[str]]) -> Optional[str]:
    """Generate the replacement output for a matched segment."""
    # Handle doubling symbol
    if output_pattern == '²':
        return matched_segment + matched_segment
    
    if len(input_pattern) != len(output_pattern):
        # Check if both are single categories
        if (len(input_pattern) == 1 and input_pattern in categories and
            len(output_pattern) == 1 and output_pattern in categories):
            
            # Get unique characters from categories (remove duplicates for comparison)
            input_chars = list(dict.fromkeys(categories[input_pattern]))  # Preserve order, remove dupes
            output_chars = list(dict.fromkeys(categories[output_pattern]))
            
            if len(input_chars) != len(output_chars):
                return None  # Categories don't match in length
            
            # Find position of matched character in input category
            matched_char = matched_segment[0]
            if matched_char in input_chars:
                pos = input_chars.index(matched_char)
                return output_chars[pos]
            return None
        else:
            # For non-category replacements, just use the output pattern
            return output_pattern
    
    # Build output character by character
    result = []
    for i, (matched_char, output_char) in enumerate(zip(matched_segment, output_pattern)):
        if output_char == '²':
            result.append(matched_char + matched_char)
        elif output_char in categories and i < len(input_pattern) and input_pattern[i] in categories:
            # Both input and output are categories
            input_chars = list(dict.fromkeys(categories[input_pattern[i]]))
            output_chars = list(dict.fromkeys(categories[output_char]))
            
            if len(input_chars) != len(output_chars):
                return None  # Categories don't match in length
            
            if matched_char in input_chars:
                pos = input_chars.index(matched_char)
                result.append(output_chars[pos])
            else:
                result.append(matched_char)  # Fallback
        else:
            result.append(output_char)
    
    return ''.join(result)


def apply_insertion_rule(word: str, output_part: str, environment: str, categories: Dict[str, List[str]]) -> str:
    """Apply an insertion rule."""
    # Handle doubling in insertion
    if output_part == '²':
        # For insertion, doubling doesn't make much sense, so treat as literal
        output_part = '²'
    
    # Add word boundaries
    bounded_word = '#' + word + '#'
    result = []
    
    for i in range(len(bounded_word)):
        if match_environment(bounded_word, i, environment, categories):
            result.append(output_part)
        if i < len(bounded_word):
            if bounded_word[i] != '#':
                result.append(bounded_word[i])
    
    return ''.join(result)


def apply_deletion_rule(word: str, input_part: str, environment: str, categories: Dict[str, List[str]]) -> str:
    """Apply a deletion rule."""
    result = []
    i = 0
    
    while i < len(word):
        # Check if we can match the input at this position
        if i + len(input_part) <= len(word):
            potential_match = word[i:i + len(input_part)]
            
            if match_input_at_position(potential_match, input_part, categories):
                # For environment matching, we need to check based on the input length
                env_match = False
                if environment == '_':
                    env_match = True
                else:
                    # For multi-character inputs, check environment at the start position
                    env_match = match_environment_for_segment(word, i, len(input_part), environment, categories)
                
                if env_match:
                    # Delete by skipping
                    i += len(input_part)
                    continue
        
        result.append(word[i])
        i += 1
    
    return ''.join(result)


def apply_standard_replacement(word: str, input_part: str, output_part: str, environment: str, categories: Dict[str, List[str]]) -> str:
    """Apply a standard replacement rule."""
    result = []
    i = 0
    
    while i < len(word):
        # Check if we can match the input at this position
        if i + len(input_part) <= len(word):
            potential_match = word[i:i + len(input_part)]
            
            if match_input_at_position(potential_match, input_part, categories):
                # Use appropriate environment matching based on input length
                env_match = False
                if environment == '_':
                    env_match = True
                else:
                    if len(input_part) == 1:
                        env_match = match_environment(word, i, environment, categories)
                    else:
                        env_match = match_environment_for_segment(word, i, len(input_part), environment, categories)
                
                if env_match:
                    # Apply replacement
                    replacement = get_replacement_output(potential_match, input_part, output_part, categories)
                    if replacement is not None:
                        result.append(replacement)
                        i += len(input_part)
                        continue
        
        result.append(word[i])
        i += 1
    
    return ''.join(result)


def apply_replacement_rule(word: str, rule: Dict[str, str], categories: Dict[str, List[str]], syllabify_mode: bool = False) -> str:
    """Apply a single replacement rule to a word."""
    # Skip syllable/stress rules if not in syllabification mode
    if not syllabify_mode and is_syllable_sensitive_rule(rule['input'] + rule['output'] + rule['environment']):
        return word
    
    input_part = rule['input']
    output_part = rule['output']
    environment = rule['environment']
    
    # Handle syllable-sensitive rules
    if syllabify_mode and is_syllable_sensitive_rule(input_part + output_part + environment):
        # Check if it's a syllable-level rule (contains σ)
        if 'σ' in input_part or 'σ' in output_part:
            return apply_syllable_replacement(word, rule)
        # Check if it's a character rule with stress-sensitive environment
        elif any(char in environment for char in 'ˈˌ˘'):
            return apply_stress_sensitive_character_replacement(word, rule)
    
    # Handle regular replacement rules (existing logic)
    if not input_part:
        return apply_insertion_rule(word, output_part, environment, categories)
    
    if not output_part:
        return apply_deletion_rule(word, input_part, environment, categories)
    
    return apply_standard_replacement(word, input_part, output_part, environment, categories)

def apply_replacement_rules(words: List[str], replacement_rules: List[Tuple[str, int]], categories: Dict[str, List[str]], track_rules: bool = False, clean_dict_words: bool = False, syllabify_mode: bool = False) -> Tuple[List[str], Optional[List[List[str]]]]:
    """Apply all replacement rules to all words in order."""
    processed_words = []
    applied_rules_list = [] if track_rules else None
    
    for word in words:
        # Clean dictionary words if requested (remove syllable marks and stress)
        current_word = clean_word_for_processing(word) if clean_dict_words else word
        applied_rules = [] if track_rules else None
        
        for rule_str, line_num in replacement_rules:
            parsed_rule = parse_replacement_rule(rule_str, line_num)
            if parsed_rule:
                # Check for category length mismatches
                input_part = parsed_rule['input']
                output_part = parsed_rule['output']
                
                if (len(input_part) == 1 and input_part in categories and
                    len(output_part) == 1 and output_part in categories):
                    
                    # Get unique characters for length comparison
                    input_unique = list(dict.fromkeys(categories[input_part]))
                    output_unique = list(dict.fromkeys(categories[output_part]))
                    
                    if len(input_unique) != len(output_unique):
                        print(f"Warning: Categories {input_part} and {output_part} have different unique character counts on line {line_num}. Rule ignored.")
                        continue
                
                # Check if rule applies before applying it
                old_word = current_word
                current_word = apply_replacement_rule(current_word, parsed_rule, categories, syllabify_mode)
                
                # Track if rule was applied
                if track_rules and old_word != current_word:
                    applied_rules.append(rule_str)
                
                # Debug output for failed tests
                if old_word != current_word:
                    print(f"Debug: Applied rule '{rule_str}' to '{old_word}' -> '{current_word}'")
        
        processed_words.append(current_word)
        if track_rules:
            applied_rules_list.append(applied_rules)
    
    if track_rules:
        return processed_words, applied_rules_list
    else:
        return processed_words, None