# -*- coding: utf-8 -*-
import fileinput
from collections import namedtuple
from .filter_rule import FilterRule


class TrieNode(dict):
    def __init__(self):
        self.output_rule = None

    @classmethod
    def make(cls, start_node, rule, rest_input):
        key, rest_input = rest_input[:1], rest_input[1:]
        if key in start_node:
            next_node = start_node[key]
        else:
            next_node = start_node[key] = cls()
        if rest_input:
            return cls.make(next_node, rule, rest_input)
        next_node.output_rule = rule
        return next_node


def make_printable(node):
    if node.output_rule:
        node["_out_"] = node.output_rule
    for k, v in node.items():
        if k != "_out_":
            make_printable(v)


class InputResult(namedtuple('InputResult', "moved output_rule finished")):
    """
    moved: 今回の入力で1回以上次の Node へ遷移した（＝いずれかのルールの入力にマッチした）
    output_rule: 今回の入力で確定した output_rule
    finished: 初期状態に戻った（もともと初期状態でいずれのルールにもマッチしなかったか、ルール遷移中に入力が完了したか）
    """


class GoogleInputIME:
    """ Google 日本語入力のローマ字入力と同様のアルゴリズムでシーケンシャルにローマ字からかなに変換する

    本家に則って「ローマ字入力」と記載しているが、FilterRule 次第で様々な配列を実現できる

    Attributes:
        root (TrieNode): 開始ノード
        current (TrieNode): 変換中の現在のノードを表す
    """

    def __init__(self, rule_table=()):
        self.set_table(rule_table)

    @property
    def finished(self):
        return self.current_node == self.root

    def copy(self):
        new_ime = GoogleInputIME()
        new_ime.root = self.root
        new_ime.current_node = self.current_node
        return new_ime

    def set_table(self, rule_table):
        root = TrieNode()
        for r in rule_table:
            TrieNode.make(root, r, r.input)
        self.root = root
        self.current_node = self.root

    @property
    def possible_keys(self):
        return self.current_node.keys()

    def complement(self, inputtable_keys):
        self.complement_node(self.root, inputtable_keys)

    @classmethod
    def complement_node(cls, node, inputtable_keys):
        """ TrieNode のうち、output が定義されていてもさらにその次に遷移する可能性が残っている
        Node は遷移が不明確なので、具体的なキーで補完する

        下記のような定義があった場合、
          FilterRule("n", "ん", ""))
          FilterRule("nn", "ん", ""))
          FilterRule("na", "な", ""))

        次のような TrieNode が形成される
        'n': {'_out_': Rule("n", "ん", ""),
               'a': {'_out_': Rule("na", "な", "")},
               'n': {'_out_': Rule("nn", "ん", "")}}}

        このとき、"n" だけ打っても「ん」が確定出力されるわけではなく、
        "a" や "n" 以外のキーを打った際に初めて「ん」が確定する。
        そのため、入力される可能性のあるキー（例えば半角英字の小文字 a-z）に対する遷移を生成する

        上記の例の場合は下記 TrieNode を再構築する
        'n': { 'a': {'_out_': Rule("na", "な", "")},
               'n': {'_out_': Rule("nn", "ん", "")},
               # 'a', 'n' 以外の入力に関する遷移を生成する
               # その際、その入力は「次の入力」として扱われる
               'b': {'_out_': Rule("nb", "ん", "b")},
               'c': {'_out_': Rule("nc", "ん", "c")},
               ... # 以下 'n' を除いて同様
               }}

        ww/っ/w
        www/w/ww
        という定義があった場合は
        wwa/っ/wa
        wwb/っ/wb
        ...
        という遷移を生成する
        """
        c = cls.complement_node
        if node:
            if node.output_rule:
                output_rule = node.output_rule
                node.output_rule = None
                non_exist_transitions = set(inputtable_keys) - set(node.keys())
                for k in non_exist_transitions:
                    node[k] = TrieNode()
                    node[k].output_rule = FilterRule(output_rule.input + k,
                                                     output_rule.output,
                                                     output_rule.next_input + k)
            for k in node.keys():
                c(node[k], inputtable_keys)

    def input(self, keys, last_results=[]):
        """ next_input の自動遷移を考慮して変換結果を返す

        next_input による無限ループを防ぐため、自動遷移は 10 回までとする

        Args:
            key (str): 入力文字列
        Returns:
            list(InputResult): 入力文字に対応する変換結果を返す。
                          next_input により別のルールが適用された場合は複数の InputResult を返す
        """
        key, rest_keys = keys[:1], keys[1:]
        if not key:
            return last_results
        if len(last_results) > 10:
            return last_results
        result = self._input(key)
        rest_keys = result.output_rule.next_input if result.output_rule else rest_keys
        return self.input(rest_keys, last_results + [result])

    def _input(self, key):
        """ 1文字を入力として受け付け、その変換結果を返す。next_input による自動遷移は考慮しない

        Args:
            key (str): 入力文字
        Returns:
            InputResult: 入力文字に対応する変換結果を途中の状態も含めて返す
        """
        c = self.current_node
        if key not in c:
            # 次にマッチしうるどのルールの入力にも一致しない場合
            return InputResult(False, None, self.finished)

        output_rule = c[key].output_rule
        #print(f"output_rule: {output_rule}, next_keys: {[a for a in c[key].keys()]}")
        if output_rule:
            if c[key]:
                # 出力はあるが、次に継続する遷移が存在する
                self.current_node = c[key]
                return InputResult(True, output_rule, False)
            else:
                # finish
                self.current_node = self.root
                return InputResult(True, output_rule, True)
        else:
            self.current_node = c[key]
            return InputResult(True, None, False)


if __name__ == '__main__':
    from pprint import pprint
    from filter_rule import FilterRuleTable, FilterRule
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

    pprint(ime.root, width=1)
    for k in "nanka":
        pprint(list(ime.possible_keys))
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
