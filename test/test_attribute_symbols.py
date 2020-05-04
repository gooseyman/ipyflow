# -*- coding: utf-8 -*-
from __future__ import annotations
import ast

from nbsafety.analysis.attr_symbols import get_attribute_symbol_chain, CallPoint as Cp


def test_basic():
    node = ast.parse('a.b.c.d.e.f').body[0].value
    symchain = get_attribute_symbol_chain(node)
    assert symchain.symbols == ['a', 'b', 'c', 'd', 'e', 'f']
    assert symchain.call_points == []


def test_calls_none_at_endpoints():
    node = ast.parse('a.b.c().d.e().f').body[0].value
    symchain = get_attribute_symbol_chain(node)
    assert symchain.symbols == ['a', 'b', Cp('c'), 'd', Cp('e'), 'f']
    assert symchain.call_points == [Cp('c'), Cp('e')]


def test_calls_at_endpoints():
    node = ast.parse('a().b.c().d.e.f()').body[0].value
    symchain = get_attribute_symbol_chain(node)
    assert symchain.symbols == [Cp('a'), 'b', Cp('c'), 'd', 'e', Cp('f')]
    assert symchain.call_points == [Cp('a'), Cp('c'), Cp('f')]
