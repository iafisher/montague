"""A natural-language understanding system.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: August 2018
"""
from .parsing import parse_formula


if __name__ == '__main__':
    print('Enter a formula to see its parse tree. Press Ctrl+C to quit.\n')
    while True:
        try:
            formula = input('>>> ')
        except (EOFError, KeyboardInterrupt):
            print()
            break

        print(parse_formula(formula))
