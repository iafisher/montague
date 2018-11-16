import pytest

from montague.ast import *
from montague.exceptions import ParseError
from montague.parser import parse_formula, parse_type


def test_parsing_variable():
    assert parse_formula('a') == Var('a')
    assert parse_formula("s8DVY_BUvybJH-VDNS'JhjS") == Var('s8DVY_BUvybJH-VDNS\'JhjS')


def test_parsing_conjunction():
    assert parse_formula("a & a'") == And(Var('a'), Var('a\''))
    assert parse_formula('a & b & c') == And(Var('a'), And(Var('b'), Var('c')))


def test_parsing_disjunction():
    assert parse_formula('b | b0') == Or(Var('b'), Var('b0'))
    assert parse_formula('a | b | c') == Or(Var('a'), Or(Var('b'), Var('c')))


def test_parsing_if_then():
    assert parse_formula('a -> b') == IfThen(Var('a'), Var('b'))
    assert parse_formula('a -> b -> c') == IfThen(Var('a'), IfThen(Var('b'), Var('c')))


def test_parsing_if_and_only_if():
    assert parse_formula('a <-> b') == IfAndOnlyIf(Var('a'), Var('b'))
    assert parse_formula('a <-> b <-> c') == IfAndOnlyIf(
        Var('a'), IfAndOnlyIf(Var('b'), Var('c'))
    )


def test_parsing_negation():
    assert parse_formula('~a') == Not(Var('a'))
    assert parse_formula('~a | b') == Or(Not(Var('a')), Var('b'))
    assert parse_formula('~[a | b]') == Not(Or(Var('a'), Var('b')))


def test_parsing_binary_precedence():
    assert parse_formula('x & y | z -> m') == IfThen(
        Or(And(Var('x'), Var('y')), Var('z')), Var('m')
    )
    assert parse_formula('x | y -> m & z') == IfThen(
        Or(Var('x'), Var('y')), And(Var('m'), Var('z'))
    )
    assert parse_formula('[x | y] & z') == And(Or(Var('x'), Var('y')), Var('z'))


def test_parsing_lambda():
    assert parse_formula('Lx.Ly.[x & y]') == Lambda(
        'x', Lambda('y', And(Var('x'), Var('y')))
    )
    assert parse_formula('L x.L y.[x & y]') == Lambda(
        'x', Lambda('y', And(Var('x'), Var('y')))
    )
    assert parse_formula('λx.λy.[x & y]') == Lambda(
        'x', Lambda('y', And(Var('x'), Var('y')))
    )


def test_parsing_call():
    assert parse_formula('Happy(x)') == Call(Var('Happy'), Var('x'))
    assert parse_formula('Between(x, y & z, [Capital(france)])') == Call(
        Call(Call(Var('Between'), Var('x')), And(Var('y'), Var('z'))),
        Call(Var('Capital'), Var('france')),
    )
    assert parse_formula('(Lx.x)(j)') == Call(Lambda('x', Var('x')), Var('j'))
    assert parse_formula('((Lx.Ly.x & y) (a)) (b)') == Call(
        Call(Lambda('x', Lambda('y', And(Var('x'), Var('y')))), Var('a')), Var('b')
    )


def test_parsing_for_all():
    assert parse_formula('Ax.x & y') == ForAll('x', And(Var('x'), Var('y')))
    assert parse_formula('A x.x & y') == ForAll('x', And(Var('x'), Var('y')))
    assert parse_formula('∀x.x & y') == ForAll('x', And(Var('x'), Var('y')))


def test_parsing_exists():
    assert parse_formula('Ex.x | y') == Exists('x', Or(Var('x'), Var('y')))
    assert parse_formula('E x.x | y') == Exists('x', Or(Var('x'), Var('y')))
    assert parse_formula('∃x.x | y') == Exists('x', Or(Var('x'), Var('y')))


def test_parsing_iota():
    assert parse_formula('ix.Man(x)') == Iota('x', Call(Var('Man'), Var('x')))
    assert parse_formula('i x.Man(x)') == Iota('x', Call(Var('Man'), Var('x')))
    # The actual Unicode iota character may be used.
    assert parse_formula('ιx.Man(x)') == Iota('x', Call(Var('Man'), Var('x')))


def test_parsing__missing_operand():
    with pytest.raises(ParseError):
        parse_formula('a | ')
    with pytest.raises(ParseError):
        parse_formula('b & ')
    with pytest.raises(ParseError):
        parse_formula('| a')
    with pytest.raises(ParseError):
        parse_formula('& b')


def test_parsing_hanging_bracket():
    with pytest.raises(ParseError):
        parse_formula('[x | y')


def test_parsing_lambda_missing_body():
    with pytest.raises(ParseError):
        parse_formula('Lx.')


def test_parsing_for_all_missing_body():
    with pytest.raises(ParseError):
        parse_formula('Ax.')


def test_parsing_exists_missing_body():
    with pytest.raises(ParseError):
        parse_formula('Ex.')


def test_parsing_iota_missing_body():
    with pytest.raises(ParseError):
        parse_formula('ix.')


def test_parsing_call_with_no_arg():
    with pytest.raises(ParseError):
        parse_formula('Happy()')


def test_parsing_unknown_token():
    with pytest.raises(ParseError):
        parse_formula('Lx.x?')


def test_parsing_empty_string():
    with pytest.raises(ParseError):
        parse_formula('')


def test_parsing_blank_string():
    with pytest.raises(ParseError):
        parse_formula('     \t    \n \r \f')


def test_parsing_atomic_types():
    assert parse_type('e') == TYPE_ENTITY
    assert parse_type('t') == TYPE_TRUTH_VALUE
    assert parse_type('v') == TYPE_EVENT
    assert parse_type('s') == TYPE_WORLD


def test_parsing_compound_type():
    assert parse_type('<e, t>') == ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE)


def test_parsing_abbreviated_compound_types():
    assert parse_type('et') == ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE)
    assert parse_type('vt') == ComplexType(TYPE_EVENT, TYPE_TRUTH_VALUE)


def test_types_are_AtomicType_class():
    typ = parse_type('<et, et>')
    assert isinstance(typ.left.left, AtomicType)
    assert isinstance(typ.left.right, AtomicType)
    assert isinstance(typ.right.left, AtomicType)
    assert isinstance(typ.right.right, AtomicType)


def test_parsing_big_compound_type():
    assert parse_type('<<e, t>, <e, <s, t>>>') == ComplexType(
        ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE),
        ComplexType(TYPE_ENTITY, ComplexType(TYPE_WORLD, TYPE_TRUTH_VALUE)),
    )


def test_parsing_big_compound_type_with_abbreviations():
    assert parse_type('<et, <e, st>>') == ComplexType(
        ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE),
        ComplexType(TYPE_ENTITY, ComplexType(TYPE_WORLD, TYPE_TRUTH_VALUE)),
    )


def test_parsing_type_missing_opening_bracket():
    with pytest.raises(ParseError):
        parse_type('e, t>')


def test_parsing_type_missing_closing_bracket():
    with pytest.raises(ParseError):
        parse_type('<e, t')


def test_parsing_type_trailing_input():
    with pytest.raises(ParseError):
        parse_type('<e, t> e')


def test_parsing_type_missing_comma():
    with pytest.raises(ParseError):
        parse_type('<e t>')


def test_parsing_type_missing_output_type():
    with pytest.raises(ParseError):
        parse_type('<e>')


def test_parsing_type_invalid_abbreviation():
    with pytest.raises(ParseError):
        parse_type('evt')


def test_parsing_type_invalid_letter():
    with pytest.raises(ParseError):
        parse_type('b')


def test_parsing_type_unknown_token():
    with pytest.raises(ParseError):
        parse_type('e?')


def test_parsing_type_empty_string():
    with pytest.raises(ParseError):
        parse_type('')


def test_parsing_type_blank():
    with pytest.raises(ParseError):
        parse_type('     \t    \n \r \f')
