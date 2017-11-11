# -*- coding: utf-8 -*-
from pprint import pprint
from google_input.ime import GoogleInputIME, TrieNode
from google_input.convert_rule import ConvertRuleTable, ConvertRule
from google_input import data


def test_empty_rule():
    # ルールなしで IME を生成
    ime = GoogleInputIME()

    # IME に対して 'x' を入力
    result_list = ime.input("x")

    assert len(result_list) == 1, "「次の入力」への継続がないので結果は1つのみ"

    result = result_list[0]
    assert result.moved == False, "ルールにマッチしないので遷移しない"
    assert result.matched_rule is None
    assert result.output == "x"
    assert result.next_input == ""
    assert result.buffer == ""


def test_simple_rule():
    table = ConvertRuleTable()
    table.add(ConvertRule("a", "A", ""))
    table.add(ConvertRule("b", "B", ""))

    # ルール1件で IME を生成
    ime = GoogleInputIME(table)

    # IME に対して 'x' を入力
    result_list = ime.input("a")

    assert len(result_list) == 1, "「次の入力」への継続がないので結果は1つのみ"

    result = result_list[0]
    assert result.moved == True, "ルールにマッチするので遷移する"
    assert result.matched_rule is not None, "ルールにマッチしてすべての入力を完了したので出力あり"
    rule = result.matched_rule
    assert (rule.input, rule.output, rule.next_input) == ('a', 'A', '')
    assert result.buffer == "", "すべての入力を完了したので初期状態に戻る"


def test_long_input():
    table = ConvertRuleTable()
    table.add(ConvertRule("abc", "ABCDE", ""))
    table.add(ConvertRule("abd", "XYA12", ""))

    # ルール1件で IME を生成
    ime = GoogleInputIME(table)

    # IME に対して 'a' を入力
    result_list_1 = ime.input("a")

    assert len(result_list_1) == 1, "「次の入力」への継続がないので結果は1つのみ"
    result = result_list_1[0]
    assert result.moved == True, "ルールにマッチして遷移する"
    assert result.matched_rule is None, "ルールの遷移が終わってないので出力はなし"
    assert result.output == ""
    assert result.next_input == ""
    assert result.buffer == "a", "ルールの遷移が終わってないので出力はなし"

    # 続けて、IME に対して 'b' を入力
    result_list_2 = ime.input("b")

    assert len(result_list_2) == 1, "「次の入力」への継続がないので結果は1つのみ"
    result = result_list_2[0]
    assert result.moved == True, "ルールにマッチして遷移する"
    assert result.matched_rule is None, "ルールの遷移が終わってないので出力はなし"
    assert result.output == ""
    assert result.next_input == ""
    assert result.buffer == "ab", "ルールの遷移が終わってないので出力はなし"

    # 続けて、IME に対して 'c' を入力
    result_list_3 = ime.input("c")

    assert len(result_list_3) == 1, "「次の入力」への継続がないので結果は1つのみ"
    result = result_list_3[0]
    assert result.moved == True, "ルールにマッチして遷移する"
    rule = result.matched_rule
    assert (rule.input, rule.output, rule.next_input) == ('abc', 'ABCDE', '')
    assert result.output == "ABCDE"
    assert result.next_input == ""
    assert result.buffer == "", "すべての入力を完了したので初期状態に戻る"


def test_match_longest_in_common_prefix_rules():
    table = ConvertRuleTable()
    table.add(ConvertRule("a", "A", ""))
    table.add(ConvertRule("ax", "AX", ""))

    # ルール1件で IME を生成
    ime = GoogleInputIME(table)

    # IME に対して 'a' を入力
    result_list = ime.input("a")

    assert len(result_list) == 1, "「次の入力」への継続がないので結果は1つのみ"

    result = result_list[0]
    assert result.moved == True, "ルールにマッチするので遷移する"
    assert result.matched_rule is None, "ルールにマッチしたが出力は確定していない"
    assert result.buffer == "a", "まだ遷移は完了していない"
    assert result.output == ""
    assert result.next_input == ""

    # 続けて、IME に対して 'x' を入力
    result_list = ime.input("x")

    assert len(result_list) == 1, "「次の入力」への継続がないので結果は1つのみ"

    result = result_list[0]
    assert result.moved == True, "初期状態に戻っているのでどのルールにもマッチしない"
    rule = result.matched_rule
    assert (rule.input, rule.output, rule.next_input) == ('ax', 'AX', '')
    assert result.buffer == ""
    assert result.output == "AX"
    assert result.next_input == ""


def test_match_shortest_in_common_prefix_rules():
    table = ConvertRuleTable()
    table.add(ConvertRule("a", "A", ""))
    table.add(ConvertRule("ax", "AX", ""))

    # ルール1件で IME を生成
    ime = GoogleInputIME(table)

    # IME に対して 'a' を入力
    result_list = ime.input("a")

    assert len(result_list) == 1, "「次の入力」への継続がないので結果は1つのみ"

    result = result_list[0]
    assert result.moved == True, "ルールにマッチするので遷移する"
    assert result.matched_rule is None, "ルールにマッチしたが出力は確定していない"
    assert result.buffer == "a"
    assert result.output == ""
    assert result.next_input == ""

    # 続けて、IME に対して 'b' を入力
    result_list = ime.input("b")

    assert len(result_list) == 2, "「次の入力」への継続があるので結果は2つ"

    result_1 = result_list[0]
    assert result_1.moved == False, "a の次にマッチするルールはない"
    rule = result_1.matched_rule
    assert (rule.input, rule.output, rule.next_input) == ('a', 'A', '')
    assert result_1.buffer == ""
    assert result_1.output == "A"
    assert result_1.next_input == "b"

    result_2 = result_list[1]
    assert result_2.moved == False, "初期状態に戻っているのでどのルールにもマッチしない"
    assert result_2.matched_rule is None
    assert result_2.buffer == ""
    assert result_2.output == "b"
    assert result_2.next_input == ""


def test_match_shortest_having_next_input_in_common_prefix_rules():
    table = ConvertRuleTable()
    table.add(ConvertRule("a", "A", "p"))
    table.add(ConvertRule("ax", "AX", ""))

    # ルール1件で IME を生成
    ime = GoogleInputIME(table)

    # IME に対して 'a' を入力
    result_list = ime.input("a")

    assert len(result_list) == 1, "「次の入力」への継続がないので結果は1つのみ"

    result = result_list[0]
    assert result.moved == True, "ルールにマッチするので遷移する"
    assert result.matched_rule is None, "ルールにマッチしたが出力は確定していない"
    assert result.buffer == "a", "まだ遷移は完了していない"
    assert result.output == ""
    assert result.next_input == ""

    # 続けて、IME に対して 'b' を入力
    result_list = ime.input("b")

    assert len(result_list) == 2, "もとのルールが持つ「次の入力」＋ルールに存在しない入力と合わせて結果は3つ"

    result_1 = result_list[0]
    assert result_1.moved == False
    rule = result_1.matched_rule
    assert (rule.input, rule.output, rule.next_input) == ('a', 'A', 'p')
    assert result_1.buffer == ""
    assert result_1.output == "A"
    assert result_1.next_input == "pb"

    result_2 = result_list[1]
    assert result_2.moved == False, "初期状態に戻っているのでどのルールにもマッチしない"
    assert result_2.matched_rule is None
    assert result_2.buffer == ""
    assert result_2.output == "pb"
    assert result_2.next_input == ""


def test_possible_input():
    table = ConvertRuleTable()
    table.add(ConvertRule("a", "A", ""))
    table.add(ConvertRule("ax", "AX", ""))
    table.add(ConvertRule("b", "B", ""))

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
    table = ConvertRuleTable.from_file(data.filepath("google_ime_default_roman_table.txt"))

    def _input(inputs):
        output = []
        for c in inputs:
            results = ime.input(c)
            output.append("".join(r.output for r in results))
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
    inputs = "wwwre"
    output = []
    for c in inputs:
        results = ime.input(c)
        output.append(results)
    from pprint import pprint
    pprint(output)


def test_azik_input():
    table = ConvertRuleTable.from_file(data.filepath("google_ime_tomoemon_azik.txt"))

    def _input(inputs):
        output = []
        for c in inputs:
            results = ime.input(c)
            output.append("".join(r.output for r in results))
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
        output.append("".join(r.matched_rule.output for r in results if r.matched_rule))
    assert "".join(output) == "さ"
    assert results[-1].buffer == "ん"

    #
    ime = GoogleInputIME(table)
    assert _input("aksw") == "あkせい"


def test_long_not_matched():
    table = ConvertRuleTable()
    table.add(ConvertRule("abcde", "ABC", ""))

    # 初期状態
    ime = GoogleInputIME(table)
    results = ime.input("a")
    assert len(results) == 1
    assert results[0].matched_rule is None
    assert results[0].buffer == "a"
    assert results[0].output == ""

    results = ime.input("b")
    assert len(results) == 1
    assert results[0].matched_rule is None
    assert results[0].buffer == "ab"
    assert results[0].output == ""

    results = ime.input("c")
    assert len(results) == 1
    assert results[0].matched_rule is None
    assert results[0].buffer == "abc"
    assert results[0].output == ""

    results = ime.input("X")
    assert len(results) == 2
    assert results[0].matched_rule is None
    assert results[0].buffer == ""
    assert results[0].output == "abc"
    assert results[0].next_input == "X"

    assert results[1].matched_rule is None
    assert results[1].buffer == ""
    assert results[1].output == "X"
    assert results[1].next_input == ""


def test_long_next_input():
    table = ConvertRuleTable()
    table.add(ConvertRule("a", "A", ""))
    table.add(ConvertRule("x", "", "ka"))

    # 初期状態
    ime = GoogleInputIME(table)
    results = ime.input("x")
    assert len(results) == 2
    rule = results[0].matched_rule
    assert (rule.input, rule.output, rule.next_input) == ("x", "", "ka")
    assert results[0].output == ""
    assert results[0].buffer  == ""
    assert results[0].next_input  == "ka"

    assert results[1].matched_rule is None
    assert results[1].output == "ka"
    assert results[1].buffer  == ""
    assert results[1].next_input  == ""
    

def test_next_input_and_output():
    table = ConvertRuleTable()
    table.add(ConvertRule("x", "X", "y"))
    table.add(ConvertRule("y", "Y", "z"))
    table.add(ConvertRule("za", "ZA", ""))

    # 初期状態
    ime = GoogleInputIME(table)

    results = ime.input("x")
    assert len(results) == 3
    assert results[0].moved == True
    assert results[0].buffer == ""
    rule = results[0].matched_rule
    assert (rule.input, rule.output, rule.next_input) == ('x', 'X', 'y')
    assert results[1].moved == True
    assert results[1].buffer == ""
    rule = results[1].matched_rule
    assert (rule.input, rule.output, rule.next_input) == ('y', 'Y', 'z')
    assert results[2].moved == True
    assert results[2].buffer == "z"
    rule = results[2].matched_rule
    assert rule is None

    results = ime.input("a")
    assert len(results) == 1
    assert results[0].moved == True
    assert results[0].buffer == ""
    rule = results[0].matched_rule
    assert (rule.input, rule.output, rule.next_input) == ('za', 'ZA', '')
