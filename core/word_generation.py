#!/usr/bin/env python3
"""
Word generation for constructed languages.
Handles generating words based on category definitions and structure rules.
Now supports weighted random rule selection instead of cycling.
"""

import random
from typing import Dict, List, Tuple


def generate_word(rule: str, categories: Dict[str, List[str]]) -> str:
    """Generate a single word based on a structure rule and categories."""
    word = ""
    
    for category_char in rule:
        if category_char in categories:
            # Choose a random character from this category
            word += random.choice(categories[category_char])
        else:
            # If the character is not a category, use it literally
            word += category_char
    
    return word


def expand_weighted_rules(weighted_rules: List[Tuple[str, int]]) -> List[str]:
    """
    Expand weighted rules into a list where each rule appears according to its weight.
    
    Example: [("CV", 1), ("CVC", 2), ("CVCC", 3)] -> ["CV", "CVC", "CVC", "CVCC", "CVCC", "CVCC"]
    """
    expanded = []
    for rule, weight in weighted_rules:
        expanded.extend([rule] * weight)
    return expanded


def select_random_rule(weighted_rules: List[Tuple[str, int]]) -> str:
    """
    Select a random rule based on weights.
    
    Args:
        weighted_rules: List of (rule, weight) tuples
    
    Returns:
        A randomly selected rule string
    """
    if not weighted_rules:
        raise ValueError("No rules provided for selection")
    
    # Expand rules according to their weights
    expanded_rules = expand_weighted_rules(weighted_rules)
    
    # Select randomly from the expanded list
    return random.choice(expanded_rules)


def generate_words(categories: Dict[str, List[str]], weighted_rules: List[Tuple[str, int]], total_words: int) -> List[str]:
    """Generate a specified total number of words using weighted random rule selection."""
    words = []
    
    if not weighted_rules:
        return words
    
    # Print rule weight information if any rules have non-default weights
    rule_weights_info = []
    for rule, weight in weighted_rules:
        if weight != 1:
            rule_weights_info.append(f"{rule}:{weight}")
    
    if rule_weights_info:
        print(f"Rule weights: {', '.join(rule_weights_info)}")
    
    # Generate words by randomly selecting rules
    for _ in range(total_words):
        rule = select_random_rule(weighted_rules)
        word = generate_word(rule, categories)
        words.append(word)
    
    return words