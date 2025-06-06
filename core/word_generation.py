#!/usr/bin/env python3
"""
Word generation for constructed languages.
Handles generating words based on category definitions and structure rules.
"""

import random
from typing import Dict, List


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


def generate_words(categories: Dict[str, List[str]], rules: List[str], total_words: int) -> List[str]:
    """Generate a specified total number of words based on all rules."""
    words = []
    
    if not rules:
        return words
    
    # Generate words by cycling through rules until we reach the target
    rule_index = 0
    for _ in range(total_words):
        rule = rules[rule_index % len(rules)]
        word = generate_word(rule, categories)
        words.append(word)
        rule_index += 1
    
    return words