# Montague

[![Build Status](https://travis-ci.com/iafisher/montague.png)](https://travis-ci.com/iafisher/montague)
[![PyPI](https://img.shields.io/pypi/v/montague-nlu.svg?label=version)](https://pypi.org/project/montague-nlu/)

An experimental natural-language understanding system.

Unlike conventional, machine-learning NLU systems, Montague uses formal semantics to interpret English sentences.

When Montague reads a sentence, it looks up each word in its lexicon to assign it a meaning in its logical language (an extension of first-order logic). Then, it recursively combines the words into phrases and computes the meaning of each phrase. When the sentence has been translated into a logical formula, Montague evaluates the formula against its "world model" (the set of facts it knows about the universe) to determine its truth value.

## Installation
You can install Montague with pip:

```shell
$ pip3 install montague-nlu
```

Once installed, you can invoke Montague's interactive command-line interface:

```shell
$ montague
```

## Limitations
As it is still in early beta, the Montague system has some limitations.

- Montague has no knowledge of syntax. Its only criterion for grouping two phrases is whether they are linearly adjacent and whether their types are compatible. This leads Montague to interpret nonsense sentences like "Every good is child."
- Montague will fail to interpret a sentence if it contains a word that is not in its lexicon.
- Important modules of formal semantics, like plurality, tense, aspect, theta roles, intensionality, and indexicals, have yet to be implemented.
