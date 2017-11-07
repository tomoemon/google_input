# -*- coding: utf-8 -*-
from pprint import pprint
from google_input.ime import GoogleInputIME, TrieNode
from google_input.filter_rule import FilterRuleTable, FilterRule
from google_input import data


def test_empty_rule():
    # ルールなしで IME を生成
    ime = GoogleInputIME()

    # IME に対して 'x' を入力
    result_list = ime.input("x")

    assert len(result_list) == 1, "「次の入力」への継続がないので結果は1つのみ"

    result = result_list[0]
    assert result.moved == False, "ルールにマッチしないので遷移しない"
    rule = result.output_rule
    assert (rule.input, rule.output, rule.next_input) == ('x', 'x', '')
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


def test_match_longest_in_common_prefix_rules():
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
    assert result.output_rule is None, "ルールにマッチしたが出力は確定していない"
    assert result.finished == False, "まだ遷移は完了していない"

    # 続けて、IME に対して 'x' を入力
    result_list = ime.input("x")

    assert len(result_list) == 1, "「次の入力」への継続がないので結果は1つのみ"

    result = result_list[0]
    assert result.moved == True, "初期状態に戻っているのでどのルールにもマッチしない"
    assert result.output_rule is not None
    rule = result.output_rule
    assert (rule.input, rule.output, rule.next_input) == ('ax', 'AX', '')
    assert result.finished == True


def test_match_shortest_in_common_prefix_rules():
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
    assert result.output_rule is None, "ルールにマッチしたが出力は確定していない"
    assert result.buffer == "a"
    assert result.finished == False, "まだ遷移は完了していない"

    # 続けて、IME に対して 'b' を入力
    result_list = ime.input("b")

    assert len(result_list) == 2, "「次の入力」への継続があるので結果は2つ"

    result_1 = result_list[0]
    assert result_1.moved == False, "a の次にマッチするルールはない"
    assert result_1.output_rule is not None
    rule = result_1.output_rule
    assert (rule.input, rule.output, rule.next_input) == ('a', 'A', 'b')
    assert result_1.finished == True

    result_2 = result_list[1]
    assert result_2.moved == False, "初期状態に戻っているのでどのルールにもマッチしない"
    rule = result_2.output_rule
    assert (rule.input, rule.output, rule.next_input) == ('b', 'b', '')
    assert result_2.finished == True


def test_match_shortest_having_next_input_in_common_prefix_rules():
    table = FilterRuleTable()
    table.add(FilterRule("a", "A", "p"))
    table.add(FilterRule("ax", "AX", ""))

    # ルール1件で IME を生成
    ime = GoogleInputIME(table)

    # IME に対して 'a' を入力
    result_list = ime.input("a")

    assert len(result_list) == 1, "「次の入力」への継続がないので結果は1つのみ"

    result = result_list[0]
    assert result.moved == True, "ルールにマッチするので遷移する"
    assert result.output_rule is None, "ルールにマッチしたが出力は確定していない"
    assert result.finished == False, "まだ遷移は完了していない"

    # 続けて、IME に対して 'b' を入力
    result_list = ime.input("b")

    assert len(result_list) == 2, "もとのルールが持つ「次の入力」＋ルールに存在しない入力と合わせて結果は3つ"

    result_1 = result_list[0]
    assert result_1.moved == False
    assert result_1.output_rule is not None
    rule = result_1.output_rule
    assert (rule.input, rule.output, rule.next_input) == ('a', 'A', 'pb')
    assert result_1.finished == True

    result_2 = result_list[1]
    assert result_2.moved == False, "初期状態に戻っているのでどのルールにもマッチしない"
    rule = result_2.output_rule
    assert (rule.input, rule.output, rule.next_input) == ('pb', 'pb', '')
    assert result_2.finished == True


def test_possible_input():
    table = FilterRuleTable()
    table.add(FilterRule("a", "A", ""))
    table.add(FilterRule("ax", "AX", ""))
    table.add(FilterRule("b", "B", ""))

    # 初期状態
    ime = GoogleInputIME(table)
    assert sorted(list(ime.possible_input)) == ["a", "b"]

    # 共通プレフィックスを持つルールのうち、最短のルールの遷移が完了した状態
    ime = GoogleInputIME(table)
    ime.input("a")
    assert sorted(list(ime.possible_input)) == ["a", "b", "x"]
    ime.input("a")
    assert sorted(list(ime.possible_input)) == ["a", "b", "x"]

    # ルールの遷移が完了
    ime = GoogleInputIME(table)
    ime.input("a")
    ime.input("x")
    assert sorted(list(ime.possible_input)) == ["a", "b"]

    # ルールの遷移が完了した
    ime = GoogleInputIME(table)
    ime.input("b")
    assert sorted(list(ime.possible_input)) == ["a", "b"]

    # ルールとは関係ないキーを入力
    ime = GoogleInputIME(table)
    ime.input("p")
    assert sorted(list(ime.possible_input)) == ["a", "b"]


def test_romaji_input():
    table = FilterRuleTable.from_file(data.filepath("google_ime_default_roman_table.txt"))

    def _input(inputs):
        output = []
        for c in inputs:
            results = ime.input(c)
            output.append("".join(r.output_rule.output for r in results if r.output_rule))
        return "".join(output)

    # 撥音
    ime = GoogleInputIME(table)
    assert _input("nandexnnenn") == "なんでんねん"

    # 促音
    ime = GoogleInputIME(table)
    assert _input("attisoltuchi") == "あっちそっち"
    assert _input("tttta") == "っっった"

    # 清音
    ime = GoogleInputIME(table)
    assert _input("aiueokakikukekosasisusesotatitutetonaninunenohahihuhehomamimumemoyayuyorarirurerowawonn") \
        == "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"

    # 濁音、半濁音
    ime = GoogleInputIME(table)
    assert _input("gagigugegozazizuzezodadidudedobabibubebopapipupepo") \
        == "がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ"

    # 拗音
    ime = GoogleInputIME(table)
    assert _input("lalilulelokyakyukyoshashushotyatyutyonyanyunyohyahyuhyomyamyumyoryaryuryo") \
        == "ぁぃぅぇぉきゃきゅきょしゃしゅしょちゃちゅちょにゃにゅにょひゃひゅひょみゃみゅみょりゃりゅりょ"

    #
    ime = GoogleInputIME(table)
    inputs = "nk"
    output = []
    for c in inputs:
        results = ime.input(c)
        output.append("".join(r.output_rule.output for r in results if r.output_rule))


def test_azik_input():
    table = FilterRuleTable.from_file(data.filepath("google_ime_tomoemon_azik.txt"))

    def _input(inputs):
        output = []
        for c in inputs:
            results = ime.input(c)
            output.append("".join(r.output_rule.output for r in results if r.output_rule))
        return "".join(output)

    #
    ime = GoogleInputIME(table)
    assert _input("a@ko") == "あんこ"
    #
    ime = GoogleInputIME(table)
    assert _input("eqno") == "えんの"
    #
    ime = GoogleInputIME(table)
    inputs = "sa@"
    output = []
    for c in inputs:
        results = ime.input(c)
        output.append("".join(r.output_rule.output for r in results if r.output_rule))
    assert "".join(output) == "さ"
    assert results[-1].buffer == "ん"

    #
    ime = GoogleInputIME(table)
    assert _input("aksw") == "あkせい"


def test_long_not_matched():
    table = FilterRuleTable()
    table.add(FilterRule("abcde", "ABC", ""))

    # 初期状態
    ime = GoogleInputIME(table)
    results = ime.input("a")
    assert len(results) == 1
    assert results[0].output_rule is None
    results = ime.input("b")
    assert len(results) == 1
    assert results[0].output_rule is None
    results = ime.input("c")
    assert len(results) == 1
    assert results[0].output_rule is None
    results = ime.input("X")
    assert len(results) == 2
    rule = results[0].output_rule
    assert (rule.input, rule.output, rule.next_input) == ('abc', 'abc', 'X')
    rule = results[1].output_rule
    assert (rule.input, rule.output, rule.next_input) == ('X', 'X', '')


def test_long_next_input():
    table = FilterRuleTable()
    table.add(FilterRule("a", "A", ""))
    table.add(FilterRule("x", "", "ka"))

    # 初期状態
    ime = GoogleInputIME(table)
    results = ime.input("x")
    assert len(results) == 2
    rule = results[0].output_rule
    assert (rule.input, rule.output, rule.next_input) == ('x', '', 'ka')
    rule = results[1].output_rule
    assert (rule.input, rule.output, rule.next_input) == ('ka', 'ka', '')
    

def test_next_input_and_output():
    table = FilterRuleTable()
    table.add(FilterRule("x", "X", "y"))
    table.add(FilterRule("y", "Y", "z"))
    table.add(FilterRule("za", "ZA", ""))

    # 初期状態
    ime = GoogleInputIME(table)

    results = ime.input("x")
    assert len(results) == 3
    assert results[0].moved == True
    assert results[0].buffer == ""
    rule = results[0].output_rule
    assert (rule.input, rule.output, rule.next_input) == ('x', 'X', 'y')
    assert results[1].moved == True
    assert results[1].buffer == ""
    rule = results[1].output_rule
    assert (rule.input, rule.output, rule.next_input) == ('y', 'Y', 'z')
    assert results[2].moved == True
    assert results[2].buffer == "z"
    rule = results[2].output_rule
    assert rule is None

    results = ime.input("a")
    assert len(results) == 1
    assert results[0].moved == True
    assert results[0].buffer == ""
    rule = results[0].output_rule
    assert (rule.input, rule.output, rule.next_input) == ('za', 'ZA', '')
