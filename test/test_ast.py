from montague.ast import *


def test_variable_to_str():
    assert str(Var('a')) == 'a'


def test_and_to_str():
    assert str(And(Var('a'), Var('b'))) == 'a & b'


def test_or_to_str():
    assert str(Or(Var('a'), Var('b'))) == 'a | b'


def test_if_then_to_str():
    assert str(IfThen(Var('a'), Var('b'))) == 'a -> b'


def test_if_and_only_if_to_str():
    assert str(IfAndOnlyIf(Var('a'), Var('b'))) == 'a <-> b'


def test_lambda_to_str():
    tree = Lambda('x', And(Var('a'), Var('x')))
    assert str(tree) == 'λx.a & x'
    assert tree.ascii_str() == 'Lx.a & x'
    # This formula is semantically invalid but that doesn't matter.
    assert str(And(Lambda('x', Var('x')), Lambda('y', Var('y')))) == '[λx.x] & [λy.y]'


def test_call_to_str():
    assert (
        str(Call(Call(Var('P'), And(Var('a'), Var('b'))), Lambda('x', Var('x'))))
        == 'P(a & b, λx.x)'
    )
    assert str(Call(Var('P'), Var('x'))) == 'P(x)'


def test_for_all_to_str():
    tree = ForAll('x', Call(Var('P'), Var('x')))
    assert str(tree) == '∀ x.P(x)'
    assert tree.ascii_str() == 'Ax.P(x)'


def test_exists_to_str():
    tree = Exists('x', Call(Var('P'), Var('x')))
    assert str(tree) == '∃ x.P(x)'
    assert tree.ascii_str() == 'Ex.P(x)'


def test_not_to_str():
    assert str(Not(Var('x'))) == '~x'
    assert str(Not(Or(Var('x'), Var('y')))) == '~[x | y]'


def test_binary_operators_to_str():
    assert str(And(Or(Var('a'), Var('b')), Var('c'))) == '[a | b] & c'
    assert str(Or(And(Var('a'), Var('b')), Var('c'))) == 'a & b | c'
    assert str(Or(Var('a'), Or(Var('b'), Var('c')))) == 'a | b | c'
    assert str(And(Var('a'), And(Var('b'), Var('c')))) == 'a & b & c'


def test_nested_exists_and_for_all_to_str():
    assert str(And(ForAll('x', Var('x')), Exists('x', Var('x')))) == '[∀ x.x] & [∃ x.x]'


def test_iota_to_str():
    tree = Iota('x', Var('x'))
    assert str(tree) == 'ιx.x'
    assert tree.ascii_str() == 'ix.x'


def test_entity_to_str():
    assert str(TYPE_ENTITY) == 'e'


def test_event_to_str():
    assert str(TYPE_EVENT) == 'v'


def test_truth_value_to_str():
    assert str(TYPE_TRUTH_VALUE) == 't'


def test_world_to_str():
    assert str(TYPE_WORLD) == 's'


def test_recursive_type_to_str():
    assert str(ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE)) == '<e, t>'


def test_deeply_recursive_type_to_str():
    assert (
        str(
            ComplexType(
                TYPE_EVENT,
                ComplexType(
                    ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE),
                    ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE),
                ),
            )
        )
        == '<v, <<e, t>, <e, t>>>'
    )


def test_recursive_type_to_concise_str():
    typ = ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE)
    assert typ.concise_str() == 'et'


def test_deeply_recursive_type_to_concise_str():
    typ = ComplexType(
        TYPE_EVENT,
        ComplexType(
            ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE),
            ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE),
        ),
    )
    assert typ.concise_str() == '<v, <et, et>>'


def test_simple_replace_variable():
    assert Var('x').replace_variable('x', Var('y')) == Var('y')


def test_replace_variable_in_and_or():
    tree = And(Or(Var('x'), Var('y')), Var('z'))
    assert tree.replace_variable('x', Var("x'")) == And(
        Or(Var("x'"), Var('y')), Var('z')
    )


def test_replace_predicate():
    tree = Call(Var('P'), Var('x'))
    assert tree.replace_variable('P', Var('Good')) == Call(Var('Good'), Var('x'))


def test_replace_variable_in_quantifiers():
    tree = ForAll(
        'x',
        Or(And(ForAll('b', Var('b')), Exists('b', Var('b'))), Exists('y', Var('b'))),
    )
    assert tree.replace_variable('b', Var('bbb')) == ForAll(
        'x',
        Or(And(ForAll('b', Var('b')), Exists('b', Var('b'))), Exists('y', Var('bbb'))),
    )


def test_recursive_replace_variable():
    # BFP(x, Lx.x, x & y)
    tree = Call(
        Call(
            Call(Var('BFP'), Var('x')),
            Lambda('x', Var('x')),  # This should not be replaced.
        ),
        And(Var('x'), Var('y')),
    )
    assert tree.replace_variable('x', Var('j')) == Call(
        Call(Call(Var('BFP'), Var('j')), Lambda('x', Var('x'))), And(Var('j'), Var('y'))
    )


def test_replace_variable_in_iota():
    tree = Iota('x', And(Var('x'), Var('y')))
    assert tree.replace_variable('x', Var('a')) == tree
    assert tree.replace_variable('y', Var('b')) == Iota('x', And(Var('x'), Var('b')))
