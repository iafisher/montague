"""A natural-language understanding system.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: August 2018
"""
import json
import os
import readline
import sys

from .translator import load_lexicon, translate_sentence


FILE_DIR = os.path.dirname(os.path.realpath(__file__))


HELP_MESSAGE = '''\
Available commands:
    !mode          Display the current operating mode.
    !mode <mode>   Switch the operating mode.
    !help          Display this help message.
    Ctrl+C         Exit the program.

Available modes:
    translate      Translate English text into logic.
'''
AVAILABLE_MODES = {'translate'}
AVAILABLE_MODES_STR = ', '.join(AVAILABLE_MODES)


if __name__ == '__main__':
    print('The Montague natural language system.\n')
    print(HELP_MESSAGE)

    mode = 'translate'

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

        if formula.startswith('!'):
            command = formula[1:].rstrip()
            if command == 'mode':
                print(f'You are currently in {mode} mode.')
            elif command.startswith('mode '):
                new_mode = command.split(maxsplit=1)[1]
                if new_mode in AVAILABLE_MODES:
                    mode = new_mode
                else:
                    print(
                        f'{new_mode} is not a recognized mode.',
                        f'Available modes are: {AVAILABLE_MODES_STR}.'
                    )
                    print(f'Remaining in {mode} mode.')
            elif command == 'help':
                print(HELP_MESSAGE)
                print(f'You are currently in {mode} mode.')
            else:
                print(f'Unrecognized command {command}.')
        else:
            try:
                entry = translate_sentence(formula, lexicon)
            except Exception as e:
                print('Error:', e)
            else:
                print('Denotation:', entry.denotation)
                print('Type:', entry.type)
