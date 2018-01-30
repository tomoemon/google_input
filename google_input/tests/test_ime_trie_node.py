# -*- coding: utf-8 -*-
from pprint import pprint
from google_input.ime import GoogleInputIME, TrieNode
from google_input.convert_rule import ConvertRuleTable, ConvertRule
from google_input import data


def test_simple_rule():
    rules = [
        ConvertRule("abc", "ABC", ""),
    ]

    root = TrieNode()
    for rule in rules:
        TrieNode.make(root, rule, rule.input)

    c = root
    assert sorted(c.keys()) == ["a"]
    assert c.buffer == ""
    assert c.rule is None
    c = c["a"]
    assert sorted(c.keys()) == ["b"]
    assert c.buffer == "a"
    assert c.rule is None
    c = c["b"]
    assert sorted(c.keys()) == ["c"]
    assert c.buffer == "ab"
    assert c.rule is None
    c = c["c"]
    assert sorted(c.keys()) == []
    assert c.buffer == ""
    assert c.rule == rules[0]


def test_multi_rule():
    rules = [
        ConvertRule("abx", "ABX", ""),
        ConvertRule("aby", "ABY", ""),
    ]

    root = TrieNode()
    for rule in rules:
        TrieNode.make(root, rule, rule.input)

    c = root
    assert sorted(c.keys()) == ["a"]
    assert c.buffer == ""
    assert c.rule is None
    c = c["a"]
    assert sorted(c.keys()) == ["b"]
    assert c.buffer == "a"
    assert c.rule is None
    c = c["b"]
    assert sorted(c.keys()) == ["x", "y"]
    assert c.buffer == "ab"
    assert c.rule is None
    x = c["x"]
    assert sorted(x.keys()) == []
    assert x.buffer == ""
    assert x.rule == rules[0]
    y = c['y']
    assert sorted(y.keys()) == []
    assert y.buffer == ""
    assert y.rule == rules[1]


def test_common_prefix_rule():
    rules = [
        ConvertRule("abc", "ABC", ""),
        ConvertRule("ab", "AB", ""),
    ]

    root = TrieNode()
    for rule in rules:
        TrieNode.make(root, rule, rule.input)

    c = root
    assert sorted(c.keys()) == ["a"]
    assert c.buffer == ""
    assert c.rule is None
    c = c["a"]
    assert sorted(c.keys()) == ["b"]
    assert c.buffer == "a"
    assert c.rule is None
    c = c["b"]
    assert sorted(c.keys()) == ["c"]
    assert c.buffer == "ab"
    assert c.rule is rules[1]
    c = c["c"]
    assert sorted(c.keys()) == []
    assert c.buffer == ""
    assert c.rule == rules[0]