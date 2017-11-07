# -*- coding: utf-8 -*-
import fileinput
from collections import namedtuple


class FilterRule(namedtuple('FilterRule', "input output next_input")):
    """ Google 日本語入力のローマ字カスタマイズテーブルの1行に対応

    仕様は Google 日本語入力のローマ字テーブル設定と同様で、
    input/output/next_input はいずれも任意の長さの文字列を設定可（半角英数に限らない）

    以下のルールを設定した場合は、"xx" と入力することで "ほし" と出力される
    ----------------
    x//☆
    ☆x/ほし/
    ----------------

    以下のルールを設定した場合は、"x" と入力することで "ほし" と出力される
    ----------------
    x//☆
    ☆/ほし/
    ----------------

    以下のルールを設定した場合は、"x" と入力しただけでは "x" と出力され、"☆" にはならない
    "xy" で "えっくす" と出力される
    "xa" で "☆a" と出力される（y 以外の文字であればなんでも良い）
    ----------------
    x//☆
    xy/えっくす/
    ----------------

    以下のルールを設定した場合は、"xyz" or "myz" と入力することで "ほし" と出力される
    ----------------
    x//☆
    m//☆
    ☆y//□
    □z/ほし/
    ----------------

    以下のルールを設定して "xy" と入力しても "☆□" としか表示されず "ほし" にはならない
    （「次の入力」は重ねられない）
    ----------------
    x//☆
    y//□
    ☆□/ほし/
    ----------------

    Attributes:
        input (str): 入力文字列
        output (str): input に対応する出力文字列
        next_input (str): input に対応する「次の入力」
    """


class FilterRuleTable:
    """ Google 日本語入力のローマ字テーブル設定を表す

    1行1行を FilterRule として読み込み保持する """

    def __init__(self, rules=None):
        self.rules = rules if rules else []

    def __iter__(self):
        yield from self.rules

    def add(self, filter_rule):
        self.rules.append(filter_rule)

    def add_identity_rules(self, characters, overwrite=False):
        """ 入力と出力が同一のルールを追加する
        """
        inputs = {rule.input: 1 for rule in self}
        for c in characters:
            if overwrite or (c not in inputs):
                self.rules.append(FilterRule(c, c, ""))

    def add_half_character_rules(self, overwrite=False):
        """ 半角英数記号の入力をそのまま出力とするルールを追加する

        overwrite==False のときはすでに追加済みのルールの中で記号を使っているものがあれば追加しない
        例：[a/あ/] がある場合は [a/a/] を追加しない
        プレフィックスに持つ [!w/わらわらわら/] だけがある場合は [!/!/] を追加する
        """
        self.add_identity_rules([chr(i) for i in range(128) if chr(i).isprintable()], overwrite)

    @classmethod
    def from_file(cls, filename, encoding="utf-8"):
        rules = []
        with open(filename, "r", encoding=encoding) as fp:
            for i, line in enumerate(fp):
                line = line.strip()
                if not line:
                    continue
                items = line.split("\t")
                if len(items) == 2:
                    rules.append(FilterRule(items[0], items[1], ""))
                elif len(items) == 3:
                    rules.append(FilterRule(items[0], items[1], items[2]))
                else:
                    raise Exception(
                        f'''Definition file has a line which has less than 2 or more than 3 values. [Line {i+1}] "{line}"''')
        return FilterRuleTable(rules)
