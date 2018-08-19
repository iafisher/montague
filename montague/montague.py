"""A natural-language understanding system.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: August 2018
"""
import readline

from .parsing import parse_formula


if __name__ == '__main__':
    print('Enter a formula to see its parse tree. Press Ctrl+C to quit.\n')
    while True:
        try:
            formula = input('>>> ')
        except (EOFError, KeyboardInterrupt):
            print()
            break

        try:
            tree = parse_formula(formula)
        except RuntimeError as e:
            print('Error:', e)
        else:
            print(tree)
