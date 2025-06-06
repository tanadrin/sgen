#!/usr/bin/env python3
"""
Syllabification module for word generator.
Handles parsing syllabification rules and applying them to words.
"""

import random
import re
from typing import Dict, List, Tuple, Optional


class SyllabificationRules:
    """Container for syllabification rules."""
    def __init__(self):
        self.allowed_onsets = []
        self.allowed_codas = []
        self.stress_patterns = []
    
    def __str__(self):
        return f"SyllabificationRules(onsets={len(self.allowed_onsets)}, codas={len(self.allowed_codas)}, stress_patterns={len(self.stress_patterns)})"


class StressPattern:
    """Represents a stress pattern with primary and optional secondary stress."""
    def __init__(self, primary: int, secondary: Optional[int] = None):
        self.primary = primary
        self.secondary = secondary
    
    def __str__(self):
        if self.secondary is not None:
            return f"{self.primary}-{self.secondary}"
        return str(self.primary)
    
    def __repr__(self):
        return f"StressPattern({self.primary}, {self.secondary})"


def clean_word_for_processing(word: str) -> str:
    """Remove syllable breaks and stress marks from a word for rule processing."""
    # Remove syllable boundaries and stress marks
    cleaned = word.replace('.', '').replace('ˈ', '').replace('ˌ', '')
    return cleaned


def expand_category_in_rule(rule_part: str, categories: Dict[str, List[str]]) -> List[str]:
    """Expand a rule part that might contain categories into concrete strings."""
    if len(rule_part) == 1 and rule_part in categories:
        # Single category
        return categories[rule_part]
    else:
        # Check if it contains categories mixed with literals
        result = []
        expanded_parts = [[]]
        
        for char in rule_part:
            if char in categories:
                # Expand this category
                new_expanded_parts = []
                for existing_part in expanded_parts:
                    for category_char in categories[char]:
                        new_expanded_parts.append(existing_part + [category_char])
                expanded_parts = new_expanded_parts
            else:
                # Literal character
                for part in expanded_parts:
                    part.append(char)
        
        # Convert back to strings
        result = [''.join(part) for part in expanded_parts]
        return result


def parse_syllabification_rules(syll_content: List[str], categories: Dict[str, List[str]]) -> SyllabificationRules:
    """Parse syllabification rules from the -syll section."""
    rules = SyllabificationRules()
    
    for line in syll_content:
        line = line.strip()
        if not line:
            continue
        
        # Parse ALLOWED_ONSETS
        if line.startswith('ALLOWED_ONSETS:'):
            onset_spec = line[len('ALLOWED_ONSETS:'):].strip()
            onset_parts = onset_spec.split()
            
            for onset_part in onset_parts:
                # Expand categories if present
                expanded = expand_category_in_rule(onset_part, categories)
                rules.allowed_onsets.extend(expanded)
        
        # Parse ALLOWED_CODAS
        elif line.startswith('ALLOWED_CODAS:'):
            coda_spec = line[len('ALLOWED_CODAS:'):].strip()
            coda_parts = coda_spec.split()
            
            for coda_part in coda_parts:
                # Expand categories if present
                expanded = expand_category_in_rule(coda_part, categories)
                rules.allowed_codas.extend(expanded)
        
        # Parse STRESS_PATTERNS
        elif line.startswith('STRESS_PATTERNS:'):
            stress_spec = line[len('STRESS_PATTERNS:'):].strip()
            stress_parts = stress_spec.split()
            
            for stress_part in stress_parts:
                if '-' in stress_part:
                    # Pattern with secondary stress: "1-3"
                    primary_str, secondary_str = stress_part.split('-', 1)
                    try:
                        primary = int(primary_str)
                        secondary = int(secondary_str)
                        rules.stress_patterns.append(StressPattern(primary, secondary))
                    except ValueError:
                        print(f"Warning: Invalid stress pattern '{stress_part}', skipping")
                else:
                    # Pattern with only primary stress: "2"
                    try:
                        primary = int(stress_part)
                        rules.stress_patterns.append(StressPattern(primary))
                    except ValueError:
                        print(f"Warning: Invalid stress pattern '{stress_part}', skipping")
    
    return rules


def find_syllable_boundaries(word: str, rules: SyllabificationRules) -> List[int]:
    """
    Find syllable boundaries in a word based on onset/coda rules.
    Returns list of positions where syllable breaks should occur.
    """
    if len(word) <= 1:
        return []
    
    boundaries = []
    
    # Sort onsets and codas by length (longest first) for better matching
    sorted_onsets = sorted(rules.allowed_onsets, key=len, reverse=True)
    sorted_codas = sorted(rules.allowed_codas, key=len, reverse=True)
    
    i = 1  # Start from position 1 (can't break before first character)
    
    while i < len(word):
        # Try to find a valid syllable break at position i
        left_part = word[:i]
        right_part = word[i:]
        
        # Check if we can form valid coda (left) + onset (right)
        valid_break = False
        
        # Try different coda lengths for the left part
        for coda in sorted_codas:
            if left_part.endswith(coda):
                # Found potential coda, check if remainder can start next syllable
                remaining_left = left_part[:-len(coda)] if len(coda) > 0 else left_part
                
                # Try different onset lengths for the right part
                for onset in sorted_onsets:
                    if right_part.startswith(onset):
                        # This is a valid break point
                        valid_break = True
                        break
                
                # Also check for vowel-initial syllables (empty onset)
                if not valid_break and len(right_part) > 0:
                    # Check if right part starts with what could be a vowel
                    # For simplicity, we'll allow breaks before any character
                    # when a valid coda is found, but this could be refined
                    valid_break = True
                
                if valid_break:
                    break
        
        # Also try empty coda (syllable ends with vowel)
        if not valid_break:
            for onset in sorted_onsets:
                if right_part.startswith(onset):
                    valid_break = True
                    break
        
        if valid_break:
            boundaries.append(i)
            # Skip ahead to avoid overlapping boundaries
            i += 1
        else:
            i += 1
    
    return boundaries


def apply_syllabification(word: str, rules: SyllabificationRules) -> str:
    """Apply syllabification rules to a word, inserting syllable boundaries."""
    if not rules.allowed_onsets and not rules.allowed_codas:
        # No syllabification rules defined
        return word
    
    # Find syllable boundaries
    boundaries = find_syllable_boundaries(word, rules)
    
    # Insert syllable breaks
    result = []
    last_pos = 0
    
    for boundary in boundaries:
        result.append(word[last_pos:boundary])
        result.append('.')
        last_pos = boundary
    
    # Add the final part
    result.append(word[last_pos:])
    
    return ''.join(result)


def apply_stress_pattern(syllabified_word: str, rules: SyllabificationRules) -> str:
    """Apply stress patterns to a syllabified word."""
    if not rules.stress_patterns:
        return syllabified_word
    
    # Split into syllables
    syllables = syllabified_word.split('.')
    num_syllables = len(syllables)
    
    if num_syllables < 1:
        return syllabified_word
    
    # Choose a random stress pattern that's applicable
    applicable_patterns = []
    for pattern in rules.stress_patterns:
        # Check if primary stress position is valid
        if pattern.primary <= num_syllables:
            # Check if secondary stress position is valid (if specified)
            if pattern.secondary is None or pattern.secondary <= num_syllables:
                applicable_patterns.append(pattern)
    
    if not applicable_patterns:
        # No applicable patterns, return without stress
        return syllabified_word
    
    # Choose a random applicable pattern
    chosen_pattern = random.choice(applicable_patterns)
    
    # Apply stress marks
    stressed_syllables = syllables[:]
    
    # Apply primary stress (1-indexed to 0-indexed)
    primary_idx = chosen_pattern.primary - 1
    if 0 <= primary_idx < len(stressed_syllables):
        stressed_syllables[primary_idx] = 'ˈ' + stressed_syllables[primary_idx]
    
    # Apply secondary stress if specified
    if chosen_pattern.secondary is not None:
        secondary_idx = chosen_pattern.secondary - 1
        if 0 <= secondary_idx < len(stressed_syllables) and secondary_idx != primary_idx:
            stressed_syllables[secondary_idx] = 'ˌ' + stressed_syllables[secondary_idx]
    
    return '.'.join(stressed_syllables)


def syllabify_word(word: str, rules: SyllabificationRules) -> str:
    """Complete syllabification: apply syllable boundaries and stress."""
    # First apply syllable boundaries
    syllabified = apply_syllabification(word, rules)
    
    # Then apply stress patterns
    stressed = apply_stress_pattern(syllabified, rules)
    
    return stressed