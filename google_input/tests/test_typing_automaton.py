# -*- coding: utf-8 -*-
from google_input.ime import GoogleInputIME
from google_input.typing import TypingAutomaton, make_graph
from google_input.filter_rule import FilterRuleTable, FilterRule
from google_input import data


def test_simple_rule():
    inputtable_keys = set(chr(i) for i in range(128) if chr(i).isprintable())
    #filename = "google_ime_tomoemon_azik.txt"
    filename = "google_ime_default_roman_table.txt"
    table = FilterRuleTable.from_file(data.filepath(filename))
    ime = GoogleInputIME(table)

    automaton = TypingAutomaton(ime, inputtable_keys)

    #target_string = "ん!"
    target_string = "380えんのほっかいどうめいさん"
    #target_string = "えんの"
    #target_string = "さん"
    #target_string = "えんn"
    #target_string = "こんk"  # 4.3 sec かかる
    #target_string = "めっさん"
    #target_string = "かった"
    import time
    start = time.time()
    root, states_dict = automaton.make(target_string)
    print(f"elapsed: {time.time() - start}")
    leaf = states_dict[target_string]
    print("leaf: ", id(leaf))
    #make_graph(root, states_dict)
