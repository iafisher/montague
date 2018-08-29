"""A natural-language understanding system.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: August 2018
"""
import json
import os
import readline
import sys

from .formula import unparse_formula, unparse_type
from .translator import load_lexicon, translate_sentence


FILE_DIR = os.path.dirname(os.path.realpath(__file__))


if __name__ == '__main__':
    print(
        'Enter a sentence to see its translation into logic.',
        'Press Ctrl+C to quit.\n'
    )

    try:
        with open(os.path.join(FILE_DIR, 'fragment.json')) as f:
            lexicon = load_lexicon(json.load(f))
    except (FileNotFoundError, IOError):
        sys.stderr.write('Error: failed to open fragment.json\n')
        sys.exit(1)

    while True:
        try:
            formula = input('>>> ')
        except (EOFError, KeyboardInterrupt):
            print()
            break

        try:
            entry = translate_sentence(formula, lexicon)
        except Exception as e:
            print('Error:', e)
        else:
            print('Denotation:', unparse_formula(entry.denotation))
            print('Type:', unparse_type(entry.type))
