import pytest

from montague.ast import (
    And,
    Call,
    ComplexType,
    ForAll,
    IfThen,
    Iota,
    Lambda,
    Or,
    SentenceNode,
    TYPE_ENTITY,
    TYPE_TRUTH_VALUE,
    Var,
)
from montague.parser import parse_formula, parse_type
from montague.translator import (
    LexiconError,
    can_combine,
    combine,
    load_lexicon,
    translate_sentence,
)


TYPE_ET = ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE)


def test_translate_is_good(lexicon):
    # import pdb; pdb.set_trace()
    nodes = translate_sentence("is good", lexicon)

    assert len(nodes) == 1

    node = nodes[0]
    assert node.text == "is good"
    assert node.formula == Lambda("x", Call(Var("Good"), Var("x")))
    assert node.type == TYPE_ET


def test_translate_john_is_good(lexicon):
    nodes = translate_sentence("John is good", lexicon)

    assert len(nodes) == 1

    node = nodes[0]
    assert node.text == "John is good"
    assert node.formula == Call(Var("Good"), Var("john"))
    assert node.type == TYPE_TRUTH_VALUE


def test_translate_john_is_bad(lexicon):
    nodes = translate_sentence("John is bad", lexicon)

    assert len(nodes) == 1

    node = nodes[0]
    assert node.text == "John is bad"
    assert node.formula == Call(Var("Bad"), Var("john"))
    assert node.type == TYPE_TRUTH_VALUE


def test_translate_every_child_is_good(lexicon):
    nodes = translate_sentence("every child is good", lexicon)

    assert len(nodes) == 1

    node = nodes[0]
    assert node.text == "every child is good"
    assert node.formula == ForAll(
        "x", IfThen(Call(Var("Child"), Var("x")), Call(Var("Good"), Var("x")))
    )
    assert node.type == TYPE_TRUTH_VALUE


def test_translate_the_child(lexicon):
    nodes = translate_sentence("the child", lexicon)

    assert len(nodes) == 1

    node = nodes[0]
    assert node.text == "the child"
    assert node.formula == Iota("x", Call(Var("Child"), Var("x")))
    assert node.type == TYPE_ENTITY


def test_translate_unknown_word(lexicon):
    nodes = translate_sentence("Mikhail", lexicon)

    assert len(nodes) == 3

    assert nodes[0].text == "Mikhail"
    assert nodes[0].formula == Var("mikhail")
    assert nodes[0].type == TYPE_ENTITY

    assert nodes[1].text == "Mikhail"
    assert nodes[1].formula == Lambda("x", Call(Var("Mikhail"), Var("x")))
    assert nodes[1].type == TYPE_ET

    assert nodes[2].text == "Mikhail"
    assert nodes[2].formula == Lambda(
        "x", Lambda("y", Call(Call(Var("Mikhail"), Var("x")), Var("y")))
    )
    assert nodes[2].type == ComplexType(TYPE_ENTITY, TYPE_ET)


def test_translate_unknown_word_in_sentence(lexicon):
    nodes = translate_sentence("John is whorlious", lexicon)

    assert len(nodes) == 2

    # TODO [2019-05-20]: For now, this is just wrong (but wrong in the expected way).
    assert nodes[0].text == "John is whorlious"
    assert nodes[0].formula == Call(Var("Whorlious"), Var("john"))
    assert nodes[0].type == TYPE_TRUTH_VALUE

    assert nodes[1].text == "John is whorlious"
    assert nodes[1].formula == Call(Var("John"), Var("whorlious"))
    assert nodes[1].type == TYPE_TRUTH_VALUE


pred = SentenceNode("does", parse_formula("Lx.P(x)"), parse_type("<e, t>"))
entity = SentenceNode("me", Var("me"), TYPE_ENTITY)


def test_combine_to_saturate_predicate():
    assert can_combine(pred, entity)
    node = combine(pred, entity)
    assert node.text == "does me"
    assert node.formula == Call(pred.formula, entity.formula)
    assert node.type == TYPE_TRUTH_VALUE


def test_combine_every_child(lexicon):
    every = lexicon["every"][0]
    child = lexicon["child"][0]
    node = combine(every, child)
    assert node.text == "every child"
    assert node.formula == Call(every.formula, child.formula)
    assert node.type == ComplexType(TYPE_ET, TYPE_TRUTH_VALUE)


def test_can_combine_is_good(lexicon):
    assert can_combine(lexicon["is"][0], lexicon["good"][0])


def test_cannot_combine_mismatched_types():
    assert not can_combine(pred, pred)
    assert not can_combine(entity, pred)
    assert not can_combine(entity, entity)


def test_simplify_call():
    tree = Call(Lambda("x", Var("x")), Var("j"))
    assert tree.simplify() == Var("j")


def test_simplify_nested_call():
    # (Lx.Ly.x & y)(a)(b) -> a & b
    tree = Call(
        Call(Lambda("x", Lambda("y", And(Var("x"), Var("y")))), Var("a")), Var("b")
    )
    assert tree.simplify() == And(Var("a"), Var("b"))


def test_simplify_call_with_lambda_arg():
    # (LP.P(x))(Lx.x | a) -> x | a
    tree = Call(
        Lambda("P", Call(Var("P"), Var("x"))), Lambda("x", Or(Var("x"), Var("a")))
    )
    assert tree.simplify() == Or(Var("x"), Var("a"))


def test_simplify_super_nested_call():
    # (LP.P(a, b))(Lx.Ly.x & y) -> a & b
    tree = Call(
        Lambda("P", Call(Call(Var("P"), Var("a")), Var("b"))),
        Lambda("x", Lambda("y", And(Var("x"), Var("y")))),
    )
    assert tree.simplify() == And(Var("a"), Var("b"))


def test_simplify_every_child(lexicon):
    # (LP.LQ.Ax.P(x) -> Q(x))(Lx.Child(x)) -> LQ.Ax.Child(x) -> Q(x)
    tree = Call(lexicon["every"][0].formula, lexicon["child"][0].formula)
    assert tree.simplify() == Lambda(
        "Q", ForAll("x", IfThen(Call(Var("Child"), Var("x")), Call(Var("Q"), Var("x"))))
    )


def test_load_lexicon():
    lexicon = load_lexicon(
        {"John": [{"d": "j", "t": "e"}], "good": [{"d": "Lx.Good(x)", "t": "et"}]}
    )
    assert lexicon == {
        "John": [SentenceNode("John", parse_formula("j"), parse_type("e"))],
        "good": [SentenceNode("good", parse_formula("Lx.Good(x)"), parse_type("et"))],
    }


def test_load_lexicon_missing_denotation_field():
    with pytest.raises(LexiconError) as e:
        load_lexicon({"John": [{"t": "e"}]})
    assert "John" in str(e)


def test_load_lexicon_with_missing_type_field():
    with pytest.raises(LexiconError) as e:
        load_lexicon({"John": [{"d": "j"}]})
    assert "John" in str(e)


def test_load_lexicon_with_invalid_denotation_formula():
    with pytest.raises(LexiconError) as e:
        load_lexicon({"John": [{"d": "???", "t": "e"}]})
    assert "John" in str(e)


def test_load_lexicon_with_invalid_type():
    with pytest.raises(LexiconError) as e:
        load_lexicon({"John": [{"d": "j", "t": "???"}]})
    assert "John" in str(e)
