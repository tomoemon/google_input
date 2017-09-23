# -*- coding: utf-8 -*-
from .ime import GoogleInputIME


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

    def connect(self, input, next_state, overwrite=False):
        if input in self and not overwrite:
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
    # print(f"search: {backtrack(current)}, {inputted_kana}, {rest_kana}, {states_dict}")
    if not rest_kana:
        return

    # 入力対象がキー入力可能な文字そのものを表している場合（IME変換が不要な場合）
    if rest_kana[0] in inputtable_keys:
        k = rest_kana[0]
        if current.ime.finished:
            # print(f"[without ime] inputted: {inputted_keys}, key: {k}")
            next_rest_kana = rest_kana[1:]
            inputted_kana = inputted_kana + k
            if inputted_kana in states_dict:
                next_state = states_dict[inputted_kana]
            else:
                next_state = State(current.ime.copy(), finished=next_rest_kana == "")
                states_dict[inputted_kana] = next_state
            current.connect(k, next_state)
            return
        elif current.ime.last_buffer == k:
            # buffer が残っている場合それをそのまま消費する
            # print(f"[without ime] inputted: {inputted_keys}, key: {k}")
            new_ime = current.ime.copy()
            new_ime.reset()
            next_rest_kana = rest_kana[1:]
            inputted_kana = inputted_kana + k
            if inputted_kana in states_dict:
                next_state = states_dict[inputted_kana]
            else:
                next_state = State(new_ime, finished=next_rest_kana == "")
                states_dict[inputted_kana] = next_state
            key, parent = current.parents[0]
            parent.connect(key, next_state, overwrite=True)
            return

    #print(f"inputterd_kana: {inputted_kana}, possible_input: {list(current.ime.possible_input & inputtable_keys)}")

    for k in current.ime.possible_input & inputtable_keys:
        # IME のルールに適合するキーのみを試していく
        new_ime = current.ime.copy()
        results = new_ime.input(k)
        # 入力が終わったルールが「次の入力」を持つ場合、それに対応した複数の result を持つ
        # 「次の入力」による次のルールへの遷移が存在しない場合は results[-1].moved == False になるため、
        # その場合は失敗として扱う
        """
        "eqno"
        e [InputResult(moved=True, output_rule=FilterRule(input='e', output='え', next_input=''), buffer='')]
        q [InputResult(moved=True, output_rule=FilterRule(input='q', output='ん', next_input=''), buffer='')]
        n [InputResult(moved=True, output_rule=None, buffer='n')]
        o [InputResult(moved=True, output_rule=FilterRule(input='no', output='の', next_input=''), buffer='')]

        "e@no"
        e [InputResult(moved=True, output_rule=FilterRule(input='e', output='え', next_input=''), buffer='')]
        @ [InputResult(moved=True, output_rule=FilterRule(input='@', output='', next_input='ん'), buffer=''), InputResult(moved=True, output_rule=None, buffer='ん')]
        n [InputResult(moved=False, output_rule=FilterRule(input='ん', output='ん', next_input='n'), buffer=''), InputResult(moved=True, output_rule=None, buffer='n')]
        o [InputResult(moved=True, output_rule=FilterRule(input='no', output='の', next_input=''), buffer='')

        n [InputResult(moved=True, output_rule=None, buffer='n')]
        k [InputResult(moved=True, output_rule=FilterRule(input='n', output='ん', next_input='k'), buffer=''),
            InputResult(moved=True, output_rule=None, buffer='k')]
        """
        if results[-1].moved:
            output = "".join(r.output_rule.output for r in results if r.output_rule)
            if output + results[-1].buffer == rest_kana:
                # 入力途中の状態であっても最後のかなであれば完了させる
                next_rest_kana = rest_kana[len(output + results[-1].buffer):]
                next_inputted_kana = inputted_kana + output + results[-1].buffer
                if next_inputted_kana in states_dict:
                    next_state = states_dict[next_inputted_kana]
                else:
                    next_state = State(new_ime, finished=next_rest_kana == "")
                    states_dict[next_inputted_kana] = next_state
                current.connect(k, next_state)
            else:
                # print(f"[ime] inputted: {inputted_keys}, key: {k}, output: {output}")
                if output:
                    if rest_kana.startswith(output):
                        next_rest_kana = rest_kana[len(output):]
                        # print("output:", k, output)
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
                    # print("moved:", k)
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
    from .filter_rule import FilterRuleTable, FilterRule
    from google_input import data

    table = FilterRuleTable()
    table.add(FilterRule("n", "ん", ""))
    table.add(FilterRule("nn", "ん", ""))
    table.add(FilterRule("na", "な", ""))
    table.add(FilterRule("ni", "に", ""))
    table.add(FilterRule("ka", "か", ""))
    table.add(FilterRule("kk", "っ", "k"))
    table.add(FilterRule("ltu", "っ", ""))

    start = time.time()
    # keys = "ltuakin"
    inputtable_keys = set(chr(i) for i in range(128) if chr(i).isprintable())
    filename = "google_ime_tomoemon_azik.txt"
    #filename = "google_ime_default_roman_table.txt"
    table = FilterRuleTable.from_file(data.filepath(filename))
    # table.add_half_character_rules()
    ime = GoogleInputIME(table)
    # ime.complement(inputtable_keys)

    print(f"ime constructed: {time.time() - start}")
    start = time.time()

    root = State(ime.copy())

    #target_string = "ん!"
    target_string = "380えんのほっかいどうめいさん"
    #target_string = "えんの"
    #target_string = "さん"
    #target_string = "えんn"
    # target_string = "こんk"  # 4.3 sec かかる
    # target_string = "めっさん"
    last_state_keys = set()
    # target_string = "かった"
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
    # pprint(root, width=1)

    def print_finished_node(current, depth):
        for key in current.to_finishes:
            print("  " * depth, key, id(current[key]))
            print_finished_node(current[key], depth + 1)

    from graphviz import Digraph

    revert_states_dict = {id(v): k for k, v in states_dict.items()}
    print(revert_states_dict)

    def search_parent_kana(node, keys=""):
        key, parent = node.parents[0]
        if id(parent) in revert_states_dict:
            kana = revert_states_dict[id(parent)]
            return (kana, key + keys)
        else:
            return search_parent_kana(parent, key + keys)

    def render_graphviz(dot, node, edged):
        for key in node.to_finishes:
            pair = (id(node), key, id(node[key]))
            if id(node) in revert_states_dict:
                node1 = f'"{revert_states_dict[id(node)]}"'
            else:
                kana, keys = search_parent_kana(node)
                node1 = f'"{kana}" {keys}'
            if id(node[key]) in revert_states_dict:
                node2 = f'"{revert_states_dict[id(node[key])]}"'
            else:
                kana, keys = search_parent_kana(node[key])
                node2 = f'"{kana}" {keys}'
            if node1 == "":
                node1 = "START"
            if node1 not in dot_nodes:
                dot.node(node1, fontname="meiryo")
            if node2 not in dot_nodes:
                dot.node(node2, fontname="meiryo")
            if pair not in edged:
                edged.add(pair)
                dot.edge(node1, node2, label=key, fontname="meiryo")
                render_graphviz(dot, node[key], edged)

    dot_nodes = {}
    dot = Digraph(comment="typing automaton", filename=filename + ".gv",
                  encoding="utf-8", format="png", body=[filename.split(".")[0]])
    dot.attr('node', shape='doublecircle')
    dot_nodes.update({k: dot.node(f'"{k}"', fontname="meiryo") for k in states_dict})
    dot.attr('node', shape='circle')
    edged = set()
    render_graphviz(dot, root, edged)
    dot.view()

    print_finished_node(root, 0)

    # print("# finish state")
    # pprint(states_dict[target_string])
    # print("# parent state")
    # pprint(states_dict[target_string].parents)
    # print("# backtrack")
    # print(backtrack(states_dict[target_string]))

    # print("\n# States")
    # pprint(states_dict)


main()
