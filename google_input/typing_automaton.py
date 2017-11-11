# -*- coding: utf-8 -*-


class State(dict):
    def __init__(self, ime):
        self.parents = []
        self.ime = ime

    def connect(self, input, next_state, overwrite=False):
        if input in self and not overwrite:
            raise Exception(f"cannot overwrite connections. input:{input}, connections:{self}")
        self[input] = next_state
        next_state.parents.append((input, self))  # 何のキーとともに遷移してきたか


class TypingAutomaton:
    def __init__(self, ime, inputtable_keys):
        self.ime = ime
        self.inputtable_keys = inputtable_keys

    def make(self, target_string):
        root = State(self.ime.copy())
        inputtable_keys = self.inputtable_keys
        search = self.search

        last_state_keys = set()
        states_dict = {"": root}  # {入力済みのかな: 入力済みの状態に対応する node object}
        next_state_keys = set([""])
        while next_state_keys:
            #print(f"next_state_keys: {next_state_keys}")
            last_state_keys = set(states_dict.keys())
            for inputted in next_state_keys:
                state = states_dict[inputted]
                search(inputtable_keys, state, inputted, target_string[len(inputted):], states_dict)
            next_state_keys = set(states_dict.keys()) - last_state_keys

        self.remove_unused_nodes(root, states_dict[target_string])

        return root, states_dict

    @classmethod
    def search(cls, inputtable_keys, current, inputted_kana, rest_kana, states_dict):
        if not rest_kana:
            return

        search = cls.search

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
                    next_state = State(current.ime.copy())
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
                    next_state = State(new_ime)
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
            e [InputResult(moved=True, matched_rule=FilterRule(input='e', output='え', next_input=''), buffer='')]
            q [InputResult(moved=True, matched_rule=FilterRule(input='q', output='ん', next_input=''), buffer='')]
            n [InputResult(moved=True, matched_rule=None, buffer='n')]
            o [InputResult(moved=True, matched_rule=FilterRule(input='no', output='の', next_input=''), buffer='')]

            "e@no"
            e [InputResult(moved=True, matched_rule=FilterRule(input='e', output='え', next_input=''), buffer='')]
            @ [InputResult(moved=True, matched_rule=FilterRule(input='@', output='', next_input='ん'), buffer=''), InputResult(moved=True, matched_rule=None, buffer='ん')]
            n [InputResult(moved=False, matched_rule=FilterRule(input='ん', output='ん', next_input='n'), buffer=''), InputResult(moved=True, matched_rule=None, buffer='n')]
            o [InputResult(moved=True, matched_rule=FilterRule(input='no', output='の', next_input=''), buffer='')

            n [InputResult(moved=True, matched_rule=None, buffer='n')]
            k [InputResult(moved=True, matched_rule=FilterRule(input='n', output='ん', next_input='k'), buffer=''),
                InputResult(moved=True, matched_rule=None, buffer='k')]
            """
            if results[-1].moved:
                output = "".join(r.output for r in results)
                if output + results[-1].buffer == rest_kana:
                    # 入力途中の状態であっても最後のかなであれば完了させる
                    next_rest_kana = rest_kana[len(output + results[-1].buffer):]
                    next_inputted_kana = inputted_kana + output + results[-1].buffer
                    if next_inputted_kana in states_dict:
                        next_state = states_dict[next_inputted_kana]
                    else:
                        next_state = State(new_ime)
                        states_dict[next_inputted_kana] = next_state
                    current.connect(k, next_state)
                else:
                    # print(f"[ime] inputted: {inputted_keys}, key: {k}, output: {output}")
                    if output:
                        if rest_kana.startswith(output):
                            next_rest_kana = rest_kana[len(output):]
                            # print("output:", k, output)
                            next_inputted_kana = inputted_kana + output
                            if results[-1].buffer == "":
                                if next_inputted_kana in states_dict:
                                    next_state = states_dict[next_inputted_kana]
                                else:
                                    next_state = State(new_ime)
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

    @classmethod
    def remove_unused_nodes(cls, root, leaf):
        to_finishes_dict = {id(leaf): set()}  # {id(node): set(key1, key2, ...)}

        def backtrack(current):
            """ 終点（すべてを入力し終わった状態）から遡っていって終端に向かう遷移を始点から辿れるようにする """
            for key_to_leaf, parent in current.parents:
                to_child_keys = []
                for key_from_parent, child in parent.items():
                    if child is current:
                        to_child_keys.append(key_from_parent)
                for key in to_child_keys:
                    to_finishes_dict.setdefault(id(parent), set()).add(key)
                backtrack(parent)

        backtrack(leaf)

        def remove(current):
            to_finish_keys = to_finishes_dict[id(current)]
            current_keys = list(current.keys())
            for key in current_keys:
                if key not in to_finish_keys:
                    del current[key]
                else:
                    remove(current[key])

        remove(root)


def make_graph(root, states_dict, filename="typing_automaton"):
    from graphviz import Digraph

    revert_states_dict = {id(v): k for k, v in states_dict.items()}

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
                  encoding="utf-8", format="pdf", body=[filename.split(".")[0]])
    dot.attr('node', shape='doublecircle')
    dot_nodes.update({k: dot.node(f'"{k}"', fontname="meiryo") for k in states_dict})
    dot.attr('node', shape='circle')
    edged = set()
    render_graphviz(dot, root, edged)
    dot.view()
