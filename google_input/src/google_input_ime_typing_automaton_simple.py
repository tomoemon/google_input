# -*- coding: utf-8 -*-
import fileinput
from filter_rule import FilterRuleTable, FilterRule
from google_input_ime_trie import GoogleInputIME


class State(dict):
    def __init__(self, parent, ime, finished=False):
        self.parent = parent
        self.key = None
        self.ime = ime.copy()
        if finished:
            self["finished"] = True

    def connect(self, input, next_state):
        if input in self:
            raise Exception(f"cannot overwrite connections. input:{input}, connections:{self.connections}")
        self[input] = next_state
        next_state.key = input

    def input(self, input):
        # connections に存在しなければ例外を投げるのでそれで検知する
        return self[input]  # next_state


def search(inputtable_keys, candidate_keys, current, rest_kana, inputted_keys, finished_list):
    if not rest_kana:
        return

    # 入力対象がキー入力可能な文字そのものを表している場合（IME変換が不要な場合）
    if current.ime.finished and rest_kana[0] in inputtable_keys:
        k = rest_kana[0]
        #print(f"[without ime] inputted: {inputted_keys}, key: {k}")
        next_rest_kana = rest_kana[1:]
        finished = next_rest_kana == ""
        next_state = State(current, current.ime.copy(), finished=finished)
        if finished:
            finished_list.append(next_state)
        current.connect(k, next_state)
        search(inputtable_keys, candidate_keys, next_state, next_rest_kana, inputted_keys + [k], finished_list)
        return

    for k in candidate_keys:
        # TODO: 全部のキーを試すのではなく、IME が入力途中なのであればその候補だけを入力させるほうが良いかも？
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
                    # かなの入力がちょうど終わり、最後の入力結果が完全に成功＆終了した場合
                    finished = next_rest_kana == "" and results[-1].finished
                    next_state = State(current, new_ime, finished=finished)
                    if finished:
                        finished_list.append(next_state)
                    current.connect(k, next_state)
                    search(inputtable_keys, candidate_keys, next_state,
                           next_rest_kana, inputted_keys + [k], finished_list)
            else:
                next_state = State(current, new_ime)
                current.connect(k, next_state)
                search(inputtable_keys, candidate_keys, next_state, rest_kana, inputted_keys + [k], finished_list)


def backtrack(leaf):
    current = leaf
    result = []
    while current.parent:
        result.insert(0, current.key)
        current = current.parent
    return result


def main():
    from pprint import pprint
    from filter_rule import FilterRuleTable, FilterRule
    import time

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
    table = FilterRuleTable.from_file("google_ime_default_roman_table.txt")
    table.add_half_character_rules()
    candidate_keys = table.candidate_keys
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
    a [Result(moved: True, output_rule: Rule("na", "な", ""), finished: True)]
    """

    root = State(None, ime)

    #target_string = "ん!"
    target_string = "380えんのほっかいどうめいさん"  # 4.3 sec かかる
    finished_list = []
    search(inputtable_keys, candidate_keys, root, target_string, [], finished_list)

    print(f"searched: {time.time() - start}")
    print("# Searched Tree")
    pprint(root, width=1)
    print("\n# Key sequences")
    for f in finished_list:
        print("".join(backtrack(f)))


if __name__ == '__main__':
    main()
