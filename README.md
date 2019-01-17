# Montague

[![Build Status](https://travis-ci.com/iafisher/montague.png)](https://travis-ci.com/iafisher/montague)

An experimental natural-language understanding system.

Unlike conventional, machine-learning NLU systems, Montague uses formal semantics to interpret English sentences.

When Montague reads a sentence, it looks up each word in its lexicon to assign it a meaning in its logical language (an extension of first-order logic). Then, it recursively combines the words into phrases and computes the meaning of each phrase. When the sentence has been translated into a logical formula, Montague evaluates the formula against its model of the world to determine its truth value.

## Installation
```shell
$ pip3 install montague-nlu
```

Alternatively, you can install a development version with `setup.py`:

```shell
$ git clone https://github.com/iafisher/montague.git
$ python3 setup.py develop --user
```

Once you do so, you can play with Montague's command-line interface:

```shell
$ montague
```

## Limitations
The Montague system is still in early beta and suffers from many limitations.

- Montague has no knowledge of syntax. Its only criterion for grouping two phrases is whether they are linearly adjacent and whether their types are compatible. This leads Montague to interpret nonsense sentences like "Every good is child."
- Montague will fail to interpret a sentence if it contains a word that is not in its lexicon.
- Important modules of formal semantics, like plurality, tense, aspect, theta roles, intensionality, and indexicals, have yet to be implemented.
