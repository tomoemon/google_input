# -*- coding: utf-8 -*-
import fileinput
from filter_rule import FilterRuleTable, FilterRule
from google_input_ime_trie import GoogleInputIME


class State(dict):
    def __init__(self, ime, finished=False):
        self.parents = []
        self.ime = ime

        # 全探索したあとに、終端ノードにたどり着かない遷移も残っているので
        # 終端ノードから正解への遷移キーを保存する set_finish_mark によって
        # セットされる
        self.to_finishes = set()

        # デバッグ表示用
        if finished:
            self["finished"] = id(self)

    def connect(self, input, next_state):
        if input in self:
            raise Exception(f"cannot overwrite connections. input:{input}, connections:{self}")
        self[input] = next_state
        next_state.parents.append((input, self))  # 何のキーとともに遷移してきたか

    def input(self, input):
        # connections に存在しなければ例外を投げるのでそれで検知する
        return self[input]  # next_state


search_called = 0


def search(inputtable_keys, current, inputted_kana, rest_kana, states_dict):
    global search_called
    search_called += 1
    #print(f"search: {backtrack(current)}, {inputted_kana}, {rest_kana}, {states_dict}")
    if not rest_kana:
        return

    # 入力対象がキー入力可能な文字そのものを表している場合（IME変換が不要な場合）
    if current.ime.finished and rest_kana[0] in inputtable_keys:
        k = rest_kana[0]
        #print(f"[without ime] inputted: {inputted_keys}, key: {k}")
        next_rest_kana = rest_kana[1:]
        inputted_kana = inputted_kana + k
        if inputted_kana in states_dict:
            next_state = states_dict[inputted_kana]
        else:
            next_state = State(current.ime.copy(), finished=next_rest_kana == "")
            states_dict[inputted_kana] = next_state
        current.connect(k, next_state)
        return

    for k in current.ime.possible_keys:
        # IME のルールに適合するキーのみを試していく
        new_ime = current.ime.copy()
        results = new_ime.input(k)
        # 入力が終わったルールが「次の入力」を持つ場合、それに対応した複数の result を持つ
        # 「次の入力」による次のルールへの遷移が存在しない場合は results[-1].moved == False になるため、
        # その場合は失敗として扱う
        if results[-1].moved:
            output = "".join(r.output_rule.output for r in results if r.output_rule)
            #print(f"[ime] inputted: {inputted_keys}, key: {k}, output: {output}")
            if output:
                if rest_kana.startswith(output):
                    next_rest_kana = rest_kana[len(output):]
                    #print("output:", k, output)
                    next_inputted_kana = inputted_kana + output
                    if results[-1].finished:
                        if next_inputted_kana in states_dict:
                            next_state = states_dict[next_inputted_kana]
                        else:
                            next_state = State(new_ime, finished=next_rest_kana == "")
                            states_dict[next_inputted_kana] = next_state
                        current.connect(k, next_state)
                    else:
                        # 次の入力により、まだ次に続く場合
                        next_state = State(new_ime)
                        current.connect(k, next_state)
                        search(inputtable_keys, next_state, next_inputted_kana, next_rest_kana, states_dict)
            else:
                #print("moved:", k)
                next_state = State(new_ime)
                current.connect(k, next_state)
                search(inputtable_keys, next_state, inputted_kana, rest_kana, states_dict)


def backtrack(leaf):
    """
    終端ノードから開始ノードまで単純に遡ってそれまでの遷移キーを返す
    """
    current = leaf
    result = []
    while current.parents:
        result.insert(0, current.parents[0][0])
        current = current.parents[0][1]
    return result


def set_finish_mark(leaf):
    for key_to_leaf, parent in leaf.parents:
        to_child_keys = []
        for key_from_parent, child in parent.items():
            if child == leaf:
                to_child_keys.append(key_from_parent)
        for key in to_child_keys:
            parent.to_finishes.add(key)
            parent[f"__{key}__"] = id(child)
        set_finish_mark(parent)


def main():
    from os import path
    from pprint import pprint
    import time
    from .. import data
    from filter_rule import FilterRuleTable, FilterRule

    table = FilterRuleTable()
    table.add(FilterRule("n", "ん", ""))
    table.add(FilterRule("nn", "ん", ""))
    table.add(FilterRule("na", "な", ""))
    table.add(FilterRule("ni", "に", ""))
    table.add(FilterRule("ka", "か", ""))
    table.add(FilterRule("kk", "っ", "k"))
    table.add(FilterRule("ltu", "っ", ""))

    start = time.time()
    #keys = "ltuakin"
    inputtable_keys = "".join([chr(i) for i in range(128) if chr(i).isprintable()])
    table = FilterRuleTable.from_file(path.join(path.dirname(path.dirname(path.abspath(__file__))),
                                                "data", "google_ime_default_roman_table.txt"))
    table.add_half_character_rules()
    ime = GoogleInputIME(table, inputtable_keys)

    print(f"ime constructed: {time.time() - start}")
    start = time.time()

    """
    {'k': {},
     'n': {'a': {},
           'b': {},
           'c': {},
           'd': {},
           'i': {},
           'k': {},
           'n': {}}}
    x [Result(moved: False, output_rule: None, finished: True)]
    n [Result(moved: True, output_rule: None, finished: False)]
    a [Result(moved: True, output_rule: Rule("na", "な", ""), finished: True)]
    n [Result(moved: True, output_rule: None, finished: False)]
    k [Result(moved: True, output_rule: Rule("nk", "ん", "k"), finished: True), Result(moved: True, output_rule: Rule("k", "か", ""), finished: True)]
    o [Result(moved: False, output_rule: None, finished: True)]
    n [Result(moved: True, output_rule: None, finished: False)]
    n [Result(moved: True, output_rule: Rule("nn", "ん", ""), finished: True)]
    n [Result(moved: True, output_rule: None, finished: False)]
    a [Result(moved: gg/True, output_rule: Rule("na", "な", ""), finished: True)]
    """

    root = State(ime.copy())

    #target_string = "ん!"
    target_string = "380えんのほっかいどうめいさん"  # 4.3 sec かかる
    #target_string = "めっさん"
    last_state_keys = set()
    #target_string = "かった"
    states_dict = {"": root}
    next_state_keys = set([""])
    while next_state_keys:
        # pprint(states_dict)
        print(f"search_called: {search_called}")
        print(f"next_state_keys: {next_state_keys}")
        last_state_keys = set(states_dict.keys())
        for inputted in next_state_keys:
            state = states_dict[inputted]
            search(inputtable_keys, state, inputted, target_string[len(inputted):], states_dict)
        next_state_keys = set(states_dict.keys()) - last_state_keys

    print(f"searched: {time.time() - start}")
    print("# Searched Tree")
    set_finish_mark(states_dict[target_string])
    #pprint(root, width=1)

    def print_finished_node(current, depth):
        for key in current.to_finishes:
            print("  " * depth, key, id(current[key]))
            print_finished_node(current[key], depth + 1)

    #print_finished_node(root, 0)

    # print("# finish state")
    # pprint(states_dict[target_string])
    # print("# parent state")
    # pprint(states_dict[target_string].parents)
    # print("# backtrack")
    # print(backtrack(states_dict[target_string]))

    # print("\n# States")
    # pprint(states_dict)


if __name__ == '__main__':
    main()
