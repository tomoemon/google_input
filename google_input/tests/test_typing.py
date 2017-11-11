# -*- coding: utf-8 -*-
import sys
from google_input.ime import GoogleInputIME
from google_input.typing import *
from google_input.convert_rule import ConvertRuleTable, ConvertRule
from google_input import data


def test_expand():
    inputtable_keys = set(chr(i) for i in range(128) if chr(i).isprintable())
    #filename = "google_ime_tomoemon_azik.txt"
    filename = "google_ime_default_roman_table.txt"

    table = ConvertRuleTable.from_file(data.filepath(filename))
    ime = GoogleInputIME(table)

    #from pprint import pprint
    #expanded_rules = expand(ime, inputtable_keys)
    #pprint(expanded_rules, width=1)


def test_match_rules():
    inputtable_keys = set(chr(i) for i in range(128) if chr(i).isprintable())
    filename = "google_ime_tomoemon_azik.txt"
    #filename = "google_ime_default_roman_table.txt"

    table = ConvertRuleTable.from_file(data.filepath(filename))
    ime = GoogleInputIME(table)

    #from pprint import pprint
    #expanded_rules = expand(ime, inputtable_keys)
    #pprint(result)
    #rules = match_rules("きょう", expanded_rules)
    #pprint(rules, width=1)

def test_automaton():
    inputtable_keys = set(chr(i) for i in range(128) if chr(i).isprintable())

    table = ConvertRuleTable([
        ConvertRule("kyo", "きょ", ""),
        ConvertRule("ki", "き", ""),
        ConvertRule("lyou", "ょう", ""),
        ConvertRule("xyou", "ょう", ""),
    ])

    ime = GoogleInputIME(table)

    #from pprint import pprint
    #expanded_rules = expand(ime, inputtable_keys)
    #pprint(result)
    #rules = match_rules("きょう", expanded_rules)
    #pprint(rules, width=1)
    #root, kana_states = to_automaton(rules)
    #pprint(root, width=1)