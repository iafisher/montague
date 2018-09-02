"""Exception classes for the Montague package.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: September 2018
"""

class CombinationError(Exception):
    """When two expressions cannot be combined."""
    pass


class LexiconError(Exception):
    """When the lexicon is ill-formatted."""
    pass


class ParseError(Exception):
    """When a formula or type could not be parsed."""
    pass


class TranslationError(Exception):
    """When an English sentence cannot be translated into logic."""
    pass
