"""Exception classes for the Montague package.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: May 2019
"""


class CombinationError(Exception):
    """When two expressions cannot be combined."""


class LexiconError(Exception):
    """When the lexicon is ill-formatted."""


class ParseError(Exception):
    """When a formula or type could not be parsed."""
