Montague: a natural-language understanding system.

Montague is different from most NLU systems in that it uses formal semantics
rather than machine learning to interpret English sentences.

When Montague reads a sentence, it looks up each word in its lexicon to assign
it a meaning in a logical language that extends first-order logic. Then, it
recursively combines the words into phrases and calculates the meaning of each
phrase that it creates. Finally, when the sentence has been translated into a
logical formula, Montague evaluates the formula against its model of the world
to determine its truth value.

## Limitations
The Montague system is still in early beta and suffers from many limitations.

- Montague has no knowledge of syntax. Its only criterion for grouping two
  phrases is whether they are linearly adjacent and whether their types are
  compatible. This leads Montague to interpret nonsense sentences like "Every
  good is child."
- Montague will fail to interpret a sentence if it contains a word not in its
  lexicon.
- Important modules of formal semantics, like plurality, tense, aspect, theta
  roles, intensionality, and indexicals, have yet to be implemented.
