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


class FilterResult:
    """ GoogleInput.input の返り値

    Attributes:
        input (str): 入力した文字列
        next_input (str): ルールにマッチした場合、そのルールの「次の入力」
        tmp_fixed (FilterRule): 仮確定したルール。他にマッチするルールがなくなった際に確定する
        fixed (FilterRule): 確定したルール
        next_candidates (list(FilterRule)): input が入力されている状態で次にマッチする可能性があるルールのリスト
    """

    def __init__(self, input, next_input, tmp_fixed, fixed, next_candidates):
        self.input = input
        self.next_input = next_input
        self.tmp_fixed = tmp_fixed
        self.fixed = fixed
        self.next_candidates = next_candidates

    def __str__(self):
        t = self.tmp_fixed
        f = self.fixed
        return f"""{{
    input: {self.input},
    tmp: {{in: {t.input if t else "None"}, out: {t.output if t else "None"} }}
    fixed: {{in: {f.input if f else "None"}, out: {f.output if f else "None"} }}
    next_input: {self.next_input}
    num_of_next_candidates: {len(self.next_candidates)}
}}"""


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


class GoogleInput:
    """ Google 日本語入力のローマ字入力と同様のアルゴリズムでシーケンシャルにローマ字からかなに変換する

    本家に則って「ローマ字入力」と記載しているが、FilterRule 次第で様々な配列を実現できる

    Attributes:
        rule_table (list(FilterRuleTable)): 変換ルールのリスト
        input_buffer (str): 直前までに入力された文字列を保持する
        tmp_fixed (FileterRule): 直前までの入力で仮確定しているルール
        next_candidates (list(FilterRule)): 直前までの入力に対して、次にマッチする可能性があるルールの候補
    """

    def __init__(self, rule_table):
        self.rule_table = rule_table
        self.reset()

    def reset(self):
        # 入力に応じて変わる状態
        self.input_buffer = ""
        self.tmp_fixed = None
        self.next_candidates = []

    def input(self, char):
        """ 1文字を入力として受け付け、その変換結果を返す

        Args:
            char (str): 入力文字
        Returns:
            FilterResult: 入力文字に対応する変換結果を途中の状態も含めて返す
        """
        if not self.next_candidates:
            candidates = self.rule_table.rules
        else:
            candidates = self.next_candidates

        next_candidates = []
        input = self.input_buffer + char
        tmp_fixed = self.tmp_fixed
        for rule in candidates:
            if rule.input.startswith(input):
                if rule.input == input:
                    tmp_fixed = rule
                else:
                    next_candidates.append(rule)

        self.next_candidates = next_candidates

        if not next_candidates:
            """ 次以降の入力にマッチするルールの候補がない """
            if tmp_fixed:
                """ これまでの入力で確定したルールがある """
                if len(tmp_fixed.input) == len(input):
                    """ 今回の入力でちょうどルールにマッチした場合
                    マッチしたルールの「次の入力」が引き回される
                    """
                    self.input_buffer = tmp_fixed.next_input
                else:
                    """ 前回のルールにマッチしており、今回そのルールから外れる入力があった場合
                    マッチしたルールの「次の入力」と今回の入力が引き回される
                    """
                    self.input_buffer = tmp_fixed.next_input + char
                self.tmp_fixed = None
                return FilterResult(input, self.input_buffer, None, tmp_fixed, next_candidates)
            else:
                """ これまでの入力で確定したルールがない（ミス入力） """
                self.input_buffer = ""
                self.tmp_fixed = None
                return FilterResult(input, "", None, None, next_candidates)
        else:
            """ 次以降の入力にマッチするルールの候補がある """
            self.input_buffer = input
            self.tmp_fixed = tmp_fixed
            return FilterResult(input, "", tmp_fixed, None, next_candidates)
