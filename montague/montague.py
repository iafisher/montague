"""A natural-language understanding system.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: August 2018
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


def run_shell():
    print('The Montague natural language system.\n')
    print(HELP_MESSAGE)

    try:
        with open(os.path.join(FILE_DIR, 'fragment.json')) as f:
            lexicon = load_lexicon(json.load(f))
    except (FileNotFoundError, IOError):
        sys.stderr.write('Error: failed to open fragment.json\n')
        sys.exit(1)

    shell_state = ShellState(lexicon=lexicon)
    while True:
        try:
            command = input('>>> ')
        except (EOFError, KeyboardInterrupt):
            print()
            break

        response = execute_command(command, shell_state)
        print(response)


def execute_command(command, shell_state):
    command = command.rstrip()
    if command.startswith('!'):
        command = command[1:]
        if command == 'mode':
            return f'You are currently in {shell_state.mode} mode.'
        elif command.startswith('mode '):
            new_mode = command.split(maxsplit=1)[1]
            if new_mode in AVAILABLE_MODES:
                shell_state.mode = new_mode
                return f'Switched to {new_mode} mode.'
            else:
                return (
                    f'{new_mode} is not a recognized mode. '
                    + f'Available modes are: {AVAILABLE_MODES_STR}.\n'
                    + f'Remaining in {shell_state.mode} mode.'
                )
        elif command == 'help':
            return (
                HELP_MESSAGE
                + f'\nYou are currently in {shell_state.mode} mode.'
            )
        else:
            return f'Unrecognized command {command}.'
    else:
        try:
            entry = translate_sentence(command, shell_state.lexicon)
        except Exception as e:
            return f'Error: {e}'
        else:
            return f'Denotation: {entry.denotation}\nType: {entry.type}'


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

FILE_DIR = os.path.dirname(os.path.realpath(__file__))


if __name__ == '__main__':
    run_shell()
