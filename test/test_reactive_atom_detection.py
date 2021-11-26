# -*- coding: future_annotations -*-
from typing import TYPE_CHECKING
from nbsafety.analysis.reactive_modifiers import REACTIVE_ATOM_REGEX, extract_reactive_atoms, replace_reactive_atoms
from nbsafety.singletons import tracer
from .utils import make_safety_fixture

if TYPE_CHECKING:
    from typing import Set

_safety_fixture, run_cell = make_safety_fixture(enable_reactive_modifiers=True)


def _get_all_reactive_var_names() -> Set[str]:
    return {
        tracer().ast_node_by_id[node_id].id
        for node_id in tracer().reactive_node_ids
    }


def test_simple():
    assert REACTIVE_ATOM_REGEX.match("") is None
    assert REACTIVE_ATOM_REGEX.match("foo") is None
    assert REACTIVE_ATOM_REGEX.match("foo bar") is None
    assert REACTIVE_ATOM_REGEX.match("$foo").group(1) == "$foo"
    assert REACTIVE_ATOM_REGEX.match("$foo bar").group(1) == "$foo"
    assert REACTIVE_ATOM_REGEX.match("foo $bar").group(1) == "$bar"
    assert REACTIVE_ATOM_REGEX.match("\nfoo $bar").group(1) == "$bar"
    assert REACTIVE_ATOM_REGEX.match("\n$foo bar").group(1) == "$foo"
    assert REACTIVE_ATOM_REGEX.match("\n'$foo' $bar").group(1) == "$bar"
    assert extract_reactive_atoms("$foo $bar") == ["$foo", "$bar"]
    assert replace_reactive_atoms("$foo $bar") == "foo bar"
    assert extract_reactive_atoms("$foo bar $baz42") == ["$foo", "$baz42"]
    assert replace_reactive_atoms("$foo bar $baz42") == "foo bar baz42"
    assert extract_reactive_atoms("$foo $42bar $_baz42") == ["$foo", "$_baz42"]
    assert replace_reactive_atoms("$foo $42bar $_baz42") == "foo $42bar _baz42"


def test_simple_names_recovered():
    run_cell('x = 0')
    run_cell('y = $x + 1')
    assert _get_all_reactive_var_names() == {'x'}
    run_cell('z = $y + 2')
    assert _get_all_reactive_var_names() == {'x', 'y'}
    run_cell('w1 = $z + 2\nw2 = $w1 + 3')
    assert _get_all_reactive_var_names() == {'x', 'y', 'z', 'w1'}


def test_nested_names_recovered():
    run_cell(
        """
        def assert_nonzero(v):
            assert v != 0
        """
    )
    run_cell('x = 42')
    run_cell('$assert_nonzero($x)')
    varnames = _get_all_reactive_var_names()
    assert varnames == {'x', 'assert_nonzero'}, 'got %s' % varnames
