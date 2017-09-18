# -*- coding: utf-8 -*-
from src.google_input_ime_trie import GoogleInputIME, TrieNode
from src.filter_rule import FilterRuleTable, FilterRule


def test_empty_rule():
    table = FilterRuleTable()
    ime = GoogleInputIME(table, "")
    result = ime.input("x")
    pprint(result)


def test_simple():
    table = FilterRuleTable()
    table.add(FilterRule("a", "あ", ""))


def test_main():
    table = FilterRuleTable()
    table.add(FilterRule("n", "ん", ""))
    table.add(FilterRule("nn", "ん", ""))
    table.add(FilterRule("na", "な", ""))
    table.add(FilterRule("ni", "に", ""))
    table.add(FilterRule("ka", "か", ""))
    table.add(FilterRule("kk", "っ", "y"))
    table.add(FilterRule("ltu", "っ", ""))
    # table.add(FilterRule("a", "", "☆"))
    # table.add(FilterRule("b", "", "☆"))
    # table.add(FilterRule("☆c", "", "□"))
    # table.add(FilterRule("☆d", "", "□"))
    # table.add(FilterRule("◯a", "", "□"))
    # table.add(FilterRule("□e", "か", ""))

    ime = GoogleInputIME(table, "ltuabcdkin")

    #pprint(ime.root, width=1)
    for k in "nanka":
        # pprint(list(ime.possible_keys))
        print(k, ime.input(k))

    # table = FilterRuleTable.from_file("google_ime_default_roman_table.txt")
    root = TrieNode()
    for rule in table:
        TrieNode.make(root, rule, rule.input)

    # make_printable(root)
    #pprint(root, width=1)

    #complement_node(root, "abcin")
    # make_printable(root)
    #pprint(root, width=1)


test_main()
