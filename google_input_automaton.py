# -*- coding: utf-8 -*-
import fileinput


class State(dict):
    def __init__(self, output=""):
        self.output = output

    def connect(self, input, next_state):
        if input in self:
            raise Exception(f"cannot overwrite connections. input:{input}, connections:{self.connections}")
        self[input] = next_state

    def input(self, input):
        # connections に存在しなければ例外を投げるのでそれで検知する
        return self[input]  # next_state


class GoogleInputAutomaton:
    def __init__(self, rule_table):
        self.rule_table = rule_table

    def match_output_rule(self, substring):
        """

        substring に "しょう" を渡したら、output に "しょう"/"しょ"/"し" を持つ
        ルールを抽出する
        """
        matched = {}
        for rule in self.rule_table:
            if substring.startswith(rule.output):
                matched.setdefault(rule.output, []).append(rule)
        return matched

    def expand_next_input_rule(self, rule_input_string):
        """
        input 文字列に「次の入力」でしか現れない文字列が含まれる可能性があるため、
        input 文字列の中から別のルールにおける「次の入力」に対する依存がないか調べ、
        依存しているものがあれば展開した文字列を返す
        ルール定義によっては展開しきれないものが残る可能性もあるがそのまま返す
        （そういうルールに遷移することはできないので事実上無視される）

        --------
        a//☆
        b//☆
        ☆c//□
        ☆d//□
        ◯a//□
        □e/か/
        --------
        arg: "か"
        return: ["ace", "bce", "ade", "bde", "◯ae"]
        """

        # 今の実装だと (tt/っ/t),(ta/た/) ルールがある場合に無限ループしてしまう
        matched = self.match_next_input_rule(rule_input_string)
        if not matched:
            return [rule_input_string]

        replaced_result = []
        for next_input, rules in matched.items():
            for r in rules:
                replaced_string = r.input + rule_input_string[len(next_input):]
                replaced_result.extend(self.expand_next_input_rule(replaced_string))

        return replaced_result

    def match_next_input_rule(self, rule_input_string):
        """
        rule_input_string に "☆✕◯" を渡したら、next_input に "☆✕◯"/"☆✕"/"☆" を持つルールを抽出する
        """
        matched = {}
        for rule in self.rule_table:
            if rule.next_input and rule_input_string.startswith(rule.next_input):
                matched.setdefault(rule.next_input, []).append(rule)
        return matched

    def connect_rule(self, rule, start, end):
        """
        最初と最後の状態は決まっており、rule からその間の遷移を作成する
        """
        current = start
        for c in rule.input[:-1]:
            if c in current:
                current = current[c]
                continue
            next_state = State()
            current.connect(c, next_state)
            current = next_state
        current.connect(rule.input[-1], end)

    def make(self, kana_string):

        root = State()
        end = State(kana_string)

        # かなの各文字の入力前に対応する状態
        kana_states = {"": root, kana_string: end}

        for input_length in range(len(kana_string)):
            inputted_string = kana_string[:input_length]
            rest_string = kana_string[input_length:]

            print(f"""{input_length}, "{inputted_string}", "{rest_string}" """)
            if inputted_string not in kana_states:
                # これまでの入力でここから start する可能性がない場合は省略
                continue

            start = kana_states[inputted_string]
            rules = self.match_output_rule(rest_string)
            for matched_output, matched_rules in rules.items():
                substring_end = kana_states.setdefault(inputted_string + matched_output, State(matched_output))
                for r in matched_rules:
                    # input 文字列に他のルールの「次の入力」に依存するものがあれば展開する
                    next_input_rules = self.expand_next_input_rule(r.input)
                    self.connect_rule(r, start, substring_end)
        return root


if __name__ == '__main__':
    from filter_rule import FilterRule, FilterRuleTable
    from pprint import pprint
    #table = FilterRuleTable.from_file("google_ime_default_roman_table.txt")
    # table.add_half_character_rules()
    #gi = GoogleInputAutomaton(table)
    #result = gi.make("った")
    #pprint(result, width=1)
    table = FilterRuleTable()
    table.add(FilterRule("a", "", "☆"))
    table.add(FilterRule("b", "", "☆"))
    table.add(FilterRule("☆c", "", "□"))
    table.add(FilterRule("☆d", "", "□"))
    table.add(FilterRule("◯a", "", "□"))
    table.add(FilterRule("□e", "か", ""))
    gi = GoogleInputAutomaton(table)
    pprint(gi.expand_next_input_rule("□e"))
