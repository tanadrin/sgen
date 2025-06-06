#!/usr/bin/env python3
"""
File I/O operations for word generator.
Handles output formatting and file writing.
"""

import sys
from typing import List, Optional


def write_output_file(words: List[str], filename: str, verbose: bool = False, 
                     input_words: Optional[List[str]] = None, show_input: bool = False, 
                     applied_rules: Optional[List[List[str]]] = None, show_rules: bool = False):
    """Write generated words to output file and optionally print to terminal."""
    try:
        # Calculate arrow padding for input→output alignment
        arrow_padding = 0
        if show_input and input_words:
            # Find the longest input word length
            arrow_padding = max(len(word) for word in input_words if word)
        
        # Format each line with proper arrow alignment first
        formatted_lines = []
        for i, word in enumerate(words):
            if show_input and input_words and i < len(input_words) and input_words[i]:
                # Create properly aligned input→output line
                # Use ljust instead of rjust to left-align and pad to consistent width
                padded_input_word = input_words[i].ljust(arrow_padding)
                formatted_line = f"{padded_input_word} → {word}"
            else:
                formatted_line = word
            formatted_lines.append(formatted_line)
        
        # Calculate rules padding to align rule brackets
        rules_padding = 0
        if show_rules and applied_rules:
            rules_padding = max(len(line) for line in formatted_lines)
        
        # Write the final output
        with open(filename, 'w', encoding='utf-8') as f:
            for i, formatted_line in enumerate(formatted_lines):
                output_line = formatted_line
                
                # Add rules if present
                if show_rules and applied_rules and i < len(applied_rules):
                    rules_list = applied_rules[i]
                    if rules_list:
                        rules_str = "; ".join(rules_list)
                        output_line = f"{formatted_line:<{rules_padding}} [{rules_str}]"
                    elif rules_padding > 0:
                        # Pad even when no rules to maintain alignment
                        output_line = f"{formatted_line:<{rules_padding}}"
                
                f.write(output_line + '\n')
                if verbose:
                    print(output_line)
        
        if show_input and input_words:
            print(f"Processed {len(words)} words and saved to '{filename}'")
        else:
            print(f"Generated {len(words)} words and saved to '{filename}'")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)