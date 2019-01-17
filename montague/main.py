"""The command-line interface to the Montague natural language understanding system.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: November 2018
"""
import json
import os
import readline
import sys

from .translator import load_lexicon, translate_sentence


class ShellState:
    """A box holding all the information the shell needs to run."""

    def __init__(self, mode='translate', lexicon=None):
        self.mode = mode
        self.lexicon = lexicon


def main():
    print('The Montague natural language system (v0.1.6).\n')
    print(HELP_MESSAGE)

    try:
        with open(FRAGMENT_PATH) as f:
            lexicon = load_lexicon(json.load(f))
    except (FileNotFoundError, IOError):
        sys.stderr.write('Error: failed to open {}\n'.format(FRAGMENT_PATH))
        sys.exit(1)

    shell_state = ShellState(lexicon=lexicon)
    while True:
        try:
            command = input('>>> ')
        except (EOFError, KeyboardInterrupt):
            print()
            break

        response = execute_command(command, shell_state)
        if response is not None:
            print(response)


def execute_command(command, shell_state):
    command = command.strip()
    if command.startswith('!'):
        command = command[1:]
        if command == 'mode':
            return 'You are currently in {} mode.'.format(shell_state.mode)
        elif command == 'words':
            return ' '.join(sorted(shell_state.lexicon.keys(), key=str.lower))
        elif command.startswith('mode '):
            new_mode = command.split(maxsplit=1)[1]
            if new_mode in AVAILABLE_MODES:
                shell_state.mode = new_mode
                return 'Switched to {} mode.'.format(new_mode)
            else:
                return (
                    '{} is not a recognized mode. Available modes are: {}.\n'
                    + 'Remaining in {} mode.'
                ).format(new_mode, AVAILABLE_MODES_STR, shell_state.mode)
        elif command == 'help':
            return HELP_MESSAGE + '\nYou are currently in {} mode.'.format(
                shell_state.mode
            )
        else:
            return 'Unrecognized command {}.'.format(command)
    elif command:
        try:
            entry = translate_sentence(command, shell_state.lexicon)
        # TODO: Only catch montague errors
        except Exception as e:
            return 'Error: {}'.format(e)
        else:
            return 'Denotation: {0.formula}\nType: {0.type}'.format(entry)


HELP_MESSAGE = '''\
Available commands:
    !mode          Display the current operating mode.
    !mode <mode>   Switch the operating mode.
    !words         List all words in Montague's lexicon.
    !help          Display this help message.
    Ctrl+C         Exit the program.

Available modes:
    translate      Translate English text into logic.


Enter a sentence to see its translation!
'''

AVAILABLE_MODES = {'translate'}
AVAILABLE_MODES_STR = ', '.join(AVAILABLE_MODES)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
FRAGMENT_PATH = os.path.join(PROJECT_DIR, 'montague', 'resources', 'fragment.json')
