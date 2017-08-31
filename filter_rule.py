# -*- coding: utf-8 -*-
import fileinput


class FilterRule:
    """ Google 日本語入力のローマ字カスタマイズテーブルの1行に対応

    仕様は Google 日本語入力のローマ字テーブル設定と同様で、
    input/output/next_input はいずれも任意の文字列を設定可（半角英数に限らない）

    Attributes:
        input (str): 入力文字列
        output (str): input に対応する出力文字列
        next_input (str): input に対応する「次の入力」
    """

    def __init__(self, input, output, next_input):
        self.input = input
        self.output = output
        self.next_input = next_input


class FilterRuleTable:
    """ Google 日本語入力のローマ字テーブル設定を表す

    1行1行を FilterRule として読み込み保持する """

    def __init__(self, rules):
        self.rules = rules

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
