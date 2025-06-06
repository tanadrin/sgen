#!/usr/bin/env python3
"""
Command line interface handling for word generator.
"""

import sys
from typing import Tuple, Optional


class CLIArgs:
    """Container for parsed command line arguments."""
    def __init__(self):
        self.verbose = False
        self.dict_mode = False
        self.show_input = False
        self.show_rules = False
        self.syllabify = False
        self.input_file = ""
        self.output_file = ""
        self.num_words: Optional[int] = None


def print_usage():
    """Print usage information."""
    print("Usage: python word_generator.py [-v] [-d] [-i] [-r] [-s] <input_file> <output_file> <num_words>")
    print("  -v: verbose mode, also prints generated words to terminal")
    print("  -d: dictionary mode, process words from -dict section instead of generating")
    print("  -i: input mode, show input → output format (only with -d)")
    print("  -r: rules mode, show applied replacement rules in square brackets")
    print("  -s: syllabification mode, apply syllabification and stress rules")


def parse_arguments() -> CLIArgs:
    """Parse command line arguments and return CLIArgs object."""
    args = CLIArgs()
    sys_args = sys.argv[1:]  # Remove script name
    
    # Parse flags (including combined flags like -di, -vd, etc.)
    while sys_args and sys_args[0].startswith('-'):
        flag_arg = sys_args[0]
        if flag_arg.startswith('--'):
            # Handle long flags if needed in the future
            print(f"Unknown flag: {flag_arg}")
            sys.exit(1)
        else:
            # Handle single-character flags (can be combined)
            flag_chars = flag_arg[1:]  # Remove the '-'
            for char in flag_chars:
                if char == 'v':
                    args.verbose = True
                elif char == 'd':
                    args.dict_mode = True
                elif char == 'i':
                    args.show_input = True
                elif char == 'r':
                    args.show_rules = True
                elif char == 's':
                    args.syllabify = True
                else:
                    print(f"Unknown flag: -{char}")
                    sys.exit(1)
        sys_args = sys_args[1:]
    
    # Validate flag combinations
    if args.show_input and not args.dict_mode:
        print("Error: -i flag can only be used with -d flag")
        sys.exit(1)
    
    # Check remaining arguments
    if args.dict_mode:
        if len(sys_args) != 2:
            print("Usage with -d: python word_generator.py [-v] [-d] [-i] [-r] [-s] <input_file> <output_file>")
            sys.exit(1)
        args.input_file = sys_args[0]
        args.output_file = sys_args[1]
        args.num_words = None  # Not used in dict mode
    else:
        if len(sys_args) != 3:
            print_usage()
            sys.exit(1)
        
        args.input_file = sys_args[0]
        args.output_file = sys_args[1]
        
        try:
            args.num_words = int(sys_args[2])
            if args.num_words <= 0:
                print("Error: Number of words must be a positive integer.")
                sys.exit(1)
        except ValueError:
            print("Error: Number of words must be a valid integer.")
            sys.exit(1)
    
    return args