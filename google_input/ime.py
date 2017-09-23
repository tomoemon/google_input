# -*- coding: utf-8 -*-
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
        current_node (TrieNode): 変換中の現在のノードを表す
    """

    __slots__ = ["root", "current_node"]

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
        if self.current_node.output_rule:
            # current_node に output_rule がある場合は下記2パターンの遷移がありうる
            # 1. ルール上の次の遷移に進むか（ルール上の次の遷移が候補）
            # 2. ルールから外れて現在の output_rule を確定させる（root からの遷移が候補）
            result = set(self.current_node.keys())
            result.update(self.root.keys())
            return result
        else:
            return self.current_node.keys()

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
            if c.output_rule:
                # 現在のノードが出力を持っている場合はそれを結果として返し、
                # 入力された値を次の入力にセットして返す
                self.current_node = self.root
                return InputResult(True, c.output_rule._replace(next_input=key), True)
            else:
                return InputResult(False, None, self.finished)

        output_rule = c[key].output_rule
        if c[key]:
            # この次にさらに現在のルール上で遷移が続く場合
            self.current_node = c[key]
            return InputResult(True, None, False)
        else:
            # finish
            self.current_node = self.root
            return InputResult(True, output_rule, True)
