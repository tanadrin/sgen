#!/usr/bin/env python3
"""
Configuration constants for word generator.
"""

# Default values
DEFAULT_ENVIRONMENT = '_'
DOUBLING_SYMBOL = '²'
WORD_BOUNDARY = '#'

# Separators for replacement rules
RULE_SEPARATORS = ['/', '>', '→']
COMMENT_MARKER = '# '

# Dictionary section markers
DICT_START = '-dict'
DICT_END = '-end-dict'

# Error messages
ERROR_MESSAGES = {
    'file_not_found': "Error: Input file '{}' not found.",
    'invalid_number': "Error: Number of words must be a valid integer.",
    'negative_number': "Error: Number of words must be a positive integer.",
    'no_dict_words': "Error: No dictionary words found in -dict section.",
    'no_rules': "Error: No word structure rules found in input file.",
    'flag_combination': "Error: -i flag can only be used with -d flag",
    'file_write_error': "Error writing output file: {}",
    'file_read_error': "Error reading input file: {}"
}

# Warning messages
WARNING_MESSAGES = {
    'invalid_rule_format': "Warning: Invalid replacement rule format on line {}: '{}'",
    'category_length_mismatch': "Warning: Categories {} and {} have different lengths on line {}. Rule ignored.",
    'invalid_line': "Warning: Line {} is not a valid category, replacement rule, or word structure rule: '{}'"
}

# Success messages
SUCCESS_MESSAGES = {
    'words_generated': "Generated {} words and saved to '{}'",
    'words_processed': "Processed {} words and saved to '{}'"
}

# Usage information
USAGE_INFO = {
    'basic': "Usage: python word_generator.py [-v] [-d] [-i] [-r] <input_file> <output_file> <num_words>",
    'dict_mode': "Usage with -d: python word_generator.py [-v] [-d] [-i] [-r] <input_file> <output_file>",
    'flags': [
        "  -v: verbose mode, also prints generated words to terminal",
        "  -d: dictionary mode, process words from -dict section instead of generating",
        "  -i: input mode, show input → output format (only with -d)",
        "  -r: rules mode, show applied replacement rules in square brackets"
    ]
}