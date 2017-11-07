# -*- coding: utf-8 -*-
from collections import namedtuple
from .filter_rule import FilterRule


class TrieNode(dict):
    def __init__(self):
        self.output_rule = None
        self.buffer = ""

    @classmethod
    def make(cls, start_node, rule, rest_input):
        key, rest_input = rest_input[:1], rest_input[1:]
        if key in start_node:
            next_node = start_node[key]
        else:
            next_node = start_node[key] = cls()
        if rest_input:
            # ここまでの入力を bufferとして保存する
            next_node.buffer = rule.input[:len(rule.input) - len(rest_input)]

            return cls.make(next_node, rule, rest_input)
        next_node.output_rule = rule
        return next_node


def make_printable(node):
    if node.output_rule:
        node["_out_"] = node.output_rule
    for k, v in node.items():
        if k != "_out_":
            make_printable(v)


class InputResult(namedtuple('InputResult', "moved output_rule buffer")):
    """
    moved: 今回の入力で1回以上次の Node へ遷移した（＝いずれかのルールの入力にマッチした）
    output_rule: 今回の入力で確定した output_rule
    buffer: 初期状態に戻った（もともと初期状態でいずれのルールにもマッチしなかったか、ルール遷移中に入力が完了したか）
    """
    @property
    def finished(self):
        return self.buffer == ""


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

    def reset(self):
        self.current_node = self.root

    @property
    def finished(self):
        return self.current_node is self.root

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
        self.reset()

    @property
    def possible_input(self):
        # 下記2パターンの遷移がありうる
        # 1. ルール上の次の遷移に進むか（ルール上の次の遷移が候補）
        # 2. ルールから外れて現在の output_rule を確定させる（root からの遷移が候補）
        result = set(self.current_node.keys())
        result.update(self.root.keys())
        return result

    def input(self, keys, last_results=[]):
        """ next_input の自動遷移を考慮して変換結果を返す

        next_input による無限ループを防ぐため、自動遷移は 10 回までとする

        Args:
            key (str): 入力文字列
        Returns:
            list(InputResult): 入力文字に対応する変換結果を返す。
                               next_input により別のルールが適用された場合は複数の InputResult を返す
        """
        if not keys:
            return last_results
        
        if len(last_results) > 10:
            # 無限ループを防ぐ
            return last_results
        
        results = []
        for key in keys:
            results.append(self._input(key))
            if results[-1].finished:
                break

        if len(results) != len(keys):
            # 複数キーを入力として受けたときはそれが1つのルールに完全一致するか前方一致する場合のみ受け入れる
            # そのため、最後の結果以外で finished している場合はどのルールにもマッチさせない
            return last_results + [InputResult(False, FilterRule(keys, keys, ""), "")]
        
        next_input = (results[-1].output_rule.next_input if results[-1].output_rule else "")
        return self.input(next_input, last_results + results)


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
            self.current_node = self.root
            if c.output_rule:
                # 現在のノードが出力を持っている場合はそれを結果として返し、
                # 入力された値を次の入力にセットして返す
                next_input = c.output_rule.next_input + key
                return InputResult(True, c.output_rule._replace(next_input=next_input), "")
            else:
                b = c.buffer
                if b:
                    # これまでに入力途中だった文字列があればそれを確定して出力する
                    return InputResult(False, FilterRule(b, b, key), "")
                else:
                    return InputResult(False, FilterRule(key, key, ""), "")

        if c[key]:
            # この次にさらに現在のルール上で遷移が続く場合
            self.current_node = c[key]
            return InputResult(True, None, c[key].buffer)
        else:
            # finish
            self.current_node = self.root
            return InputResult(True, c[key].output_rule, c[key].buffer)
