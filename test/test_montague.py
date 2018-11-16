import pytest
from unittest.mock import patch

from montague.ast import *
from montague.montague import ShellState, execute_command, HELP_MESSAGE
from montague.translator import TranslationError


TEST_LEXICON = {
    'good': SentenceNode(
        'good',
        Lambda('x', Call(Var('Good'), Var('x'))),
        ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE),
    ),
    'bad': SentenceNode(
        'bad',
        Lambda('x', Call(Var('Bad'), Var('x'))),
        ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE),
    ),
}


@pytest.fixture
def shell_state():
    return ShellState(lexicon=TEST_LEXICON)


def test_shell_command_help(shell_state):
    response = execute_command('!help', shell_state)
    assert HELP_MESSAGE in response
    assert 'currently in ' + shell_state.mode in response


def test_shell_command_mode(shell_state):
    response = execute_command('!mode', shell_state)
    assert shell_state.mode in response


def test_shell_command_switch_mode(shell_state):
    response = execute_command('!mode translate', shell_state)
    assert 'translate' in response
    assert shell_state.mode == 'translate'


def test_shell_command_words(shell_state):
    response = execute_command('!words', shell_state)
    assert response == 'bad good'


def test_shell_switch_to_unrecognized_mode(shell_state):
    old_mode = shell_state.mode
    response = execute_command('!mode bolivia', shell_state)
    assert 'bolivia is not a recognized mode' in response
    assert shell_state.mode == old_mode


def test_shell_display_formula(shell_state):
    with patch('montague.montague.translate_sentence') as mock_translate_sentence:
        mock_translate_sentence.return_value = SentenceNode(
            'good', Call(Var('Good'), Var('j')), TYPE_TRUTH_VALUE
        )
        response = execute_command('John is good', shell_state)
        assert 'Denotation: Good(j)' in response
        assert 'Type: t' in response


def test_shell_unrecognized_command(shell_state):
    response = execute_command('!paraguay', shell_state)
    assert 'Unrecognized command paraguay.' == response
