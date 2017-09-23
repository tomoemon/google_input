# -*- coding: utf-8 -*-
from pprint import pprint
from google_input.ime import GoogleInputIME, TrieNode
from google_input.filter_rule import FilterRuleTable, FilterRule


def test_empty_rule():
    # ルールなしで IME を生成
    ime = GoogleInputIME()

    # IME に対して 'x' を入力
    result_list = ime.input("x")

    assert len(result_list) == 1, "「次の入力」への継続がないので結果は1つのみ"

    result = result_list[0]
    assert result.moved == False, "ルールにマッチしないので遷移しない"
    assert result.output_rule is None, "ルールにマッチしないので出力はなし"
    assert result.finished == True, "どのルールにもマッチせず初期状態に戻る"


def test_simple_rule():
    table = FilterRuleTable()
    table.add(FilterRule("a", "A", ""))
    table.add(FilterRule("b", "B", ""))

    # ルール1件で IME を生成
    ime = GoogleInputIME(table)

    # IME に対して 'x' を入力
    result_list = ime.input("a")

    assert len(result_list) == 1, "「次の入力」への継続がないので結果は1つのみ"

    result = result_list[0]
    assert result.moved == True, "ルールにマッチするので遷移する"
    assert result.output_rule is not None, "ルールにマッチしてすべての入力を完了したので出力あり"
    rule = result.output_rule
    assert (rule.input, rule.output, rule.next_input) == ('a', 'A', '')
    assert result.finished == True, "すべての入力を完了したので初期状態に戻る"


def test_long_input():
    table = FilterRuleTable()
    pprint([e for e in table])
    table.add(FilterRule("abc", "ABCDE", ""))
    table.add(FilterRule("abd", "XYA12", ""))

    # ルール1件で IME を生成
    ime = GoogleInputIME(table)

    # IME に対して 'a' を入力
    result_list_1 = ime.input("a")

    assert len(result_list_1) == 1, "「次の入力」への継続がないので結果は1つのみ"
    result = result_list_1[0]
    assert result.moved == True, "ルールにマッチして遷移する"
    assert result.output_rule is None, "ルールの遷移が終わってないので出力はなし"
    assert result.finished == False, "ルールの遷移が終わってないので出力はなし"

    # 続けて、IME に対して 'b' を入力
    result_list_2 = ime.input("b")

    assert len(result_list_2) == 1, "「次の入力」への継続がないので結果は1つのみ"
    result = result_list_2[0]
    assert result.moved == True, "ルールにマッチして遷移する"
    assert result.output_rule is None, "ルールの遷移が終わってないので出力はなし"
    assert result.finished == False, "ルールの遷移が終わってないので出力はなし"

    # 続けて、IME に対して 'c' を入力
    result_list_3 = ime.input("c")

    assert len(result_list_3) == 1, "「次の入力」への継続がないので結果は1つのみ"
    result = result_list_3[0]
    assert result.moved == True, "ルールにマッチして遷移する"
    assert result.output_rule is not None, "ルールにマッチしてすべての入力を完了したので出力あり"
    assert result.finished == True, "すべての入力を完了したので初期状態に戻る"
    rule = result.output_rule
    assert (rule.input, rule.output, rule.next_input) == ('abc', 'ABCDE', '')


def test_common_prefix_rule():
    table = FilterRuleTable()
    table.add(FilterRule("a", "A", ""))
    table.add(FilterRule("ax", "AX", ""))

    # ルール1件で IME を生成
    ime = GoogleInputIME(table)

    # IME に対して 'a' を入力
    result_list = ime.input("a")

    assert len(result_list) == 1, "「次の入力」への継続がないので結果は1つのみ"

    result = result_list[0]
    assert result.moved == True, "ルールにマッチするので遷移する"
    assert result.output_rule is not None, "ルールにマッチしてすべての入力を完了したので出力あり"
    rule = result.output_rule
    assert (rule.input, rule.output, rule.next_input) == ('a', 'A', '')
    assert result.finished == False, "すべての入力を完了したので初期状態に戻る"

    # 続けて、IME に対して 'x' を入力
    result_list = ime.input("x")

    assert len(result_list) == 1, "「次の入力」への継続がないので結果は1つのみ"

    result = result_list[0]
    assert result.moved == True, "初期状態に戻っているのでどのルールにもマッチしない"
    assert result.output_rule is not None
    rule = result.output_rule
    assert (rule.input, rule.output, rule.next_input) == ('ax', 'AX', '')
    assert result.finished == True


def main():
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

    ime = GoogleInputIME()
    ime.set_table(table)
    ime.complement("ltuabcdkin")

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
