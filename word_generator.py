#!/usr/bin/env python3
"""
Word Generator Script - REFACTORED VERSION

Generates words based on category definitions and structure rules from an input file.
Supports replacement rules for sound changes and dictionary mode.
Now supports flexible rule syntax with optional categories and alternatives.

Usage: python word_generator.py [-v] [-d] [-i] [-r] <input_file> <output_file> <num_words>
  -v: verbose mode, also prints generated words to terminal
  -d: dictionary mode, process words from -dict section instead of generating
  -i: input mode, show input → output format (only with -d)
  -r: rules mode, show applied replacement rules in square brackets
"""

import sys
from core.parser import parse_input_file
from core.word_generation import generate_words
from core.sound_changes import apply_replacement_rules
from core.syllabification import parse_syllabification_rules, syllabify_word
from utils.cli import parse_arguments
from utils.file_io import write_output_file


def main():
    """Main function to handle command line arguments and orchestrate word generation."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Parse input file
    categories, rules, replacement_rules, dict_words, syll_rules = parse_input_file(args.input_file, args.dict_mode)
    
    # Parse syllabification rules if present
    syllabification_rules = None
    if syll_rules:
        syllabification_rules = parse_syllabification_rules(syll_rules, categories)
        if args.syllabify:
            print(f"Found syllabification rules: {syllabification_rules}")
    
    if args.dict_mode:
        if not dict_words:
            print("Error: No dictionary words found in -dict section.")
            sys.exit(1)
        
        syll_info = f", {len(syll_rules)} syllabification rules" if syll_rules else ""
        print(f"Found {len(categories)} categories, {len(replacement_rules)} replacement rules, and {len(dict_words)} dictionary words{syll_info}.")
        
        # Use dictionary words as input
        words = dict_words[:]
        input_words = dict_words[:] if args.show_input else None
        
    else:
        if not categories:
            print("Warning: No categories found in input file.")
        
        if not rules:
            print("Error: No word structure rules found in input file.")
            sys.exit(1)
        
        syll_info = f", {len(syll_rules)} syllabification rules" if syll_rules else ""
        print(f"Found {len(categories)} categories, {len(rules)} word structure rules, and {len(replacement_rules)} replacement rules{syll_info}.")
        
        # Generate words
        words = generate_words(categories, rules, args.num_words)
        input_words = None
    
    # Apply replacement rules
    applied_rules = None
    if replacement_rules:
        if args.show_rules:
            words, applied_rules = apply_replacement_rules(words, replacement_rules, categories, track_rules=True, clean_dict_words=args.dict_mode, syllabify_mode=args.syllabify)
        else:
            words, _ = apply_replacement_rules(words, replacement_rules, categories, track_rules=False, clean_dict_words=args.dict_mode, syllabify_mode=args.syllabify)
    
    # Apply syllabification if requested
    if args.syllabify and syllabification_rules:
        syllabified_words = []
        for word in words:
            syllabified_word = syllabify_word(word, syllabification_rules)
            syllabified_words.append(syllabified_word)
        words = syllabified_words
    
    # Write output
    if args.verbose:
        if args.dict_mode:
            print("\nProcessed words:")
        else:
            print("\nGenerated words:")
    
    write_output_file(words, args.output_file, args.verbose, input_words, args.show_input, applied_rules, args.show_rules)


if __name__ == "__main__":
    main()