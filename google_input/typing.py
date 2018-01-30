# -*- coding: utf-8 -*-


"""
n: [InputResult(moved=True, matched_rule=None, output='', next_input='', buffer='n')]
a: [InputResult(moved=True, matched_rule=ConvertRule(input='na', output='な', next_input=''), output='な', next_input='', buffer='')]

t: [InputResult(moved=True, matched_rule=None, output='', next_input='', buffer='t')]
t: [InputResult(moved=True, matched_rule=ConvertRule(input='tt', output='っ', next_input='t'), output='っ', next_input='t', buffer=''),
    InputResult(moved=True, matched_rule=None, output='', next_input='', buffer='t')]
u: [InputResult(moved=True, matched_rule=ConvertRule(input='tu', output='つ', next_input=''), output='つ', next_input='', buffer='')]

t: [InputResult(moved=True, matched_rule=None, output='', next_input='', buffer='t')]
t: [InputResult(moved=True, matched_rule=ConvertRule(input='tt', output='っ', next_input='t'), output='っ', next_input='t', buffer=''),
    InputResult(moved=True, matched_rule=None, output='', next_input='', buffer='t')]
k: [InputResult(moved=False, matched_rule=None, output='t', next_input='k', buffer=''),
    InputResult(moved=True, matched_rule=None, output='', next_input='', buffer='k')]

デフォルトローマ字入力の定義に従って nk を入力した場合の結果
n: [InputResult(moved=True, matched_rule=None, output='', next_input='', buffer='n')]
k: [InputResult(moved=False, matched_rule=ConvertRule(input='n', output='ん', next_input=''), output='ん', next_input='k', buffer=''),
    InputResult(moved=True, matched_rule=None, output='', next_input='', buffer='k')]

n: [InputResult(moved=True, matched_rule=None, output='', next_input='', buffer='n')]
!: [InputResult(moved=False, matched_rule=ConvertRule(input='n', output='ん', next_input=''), output='ん', next_input='!', buffer=''),
    InputResult(moved=False, matched_rule=None, output='!', next_input='', buffer='')]

デフォルトローマ字入力の定義に従って zzzr を入力した場合の結果
z: [InputResult(moved=True, matched_rule=None, output='', next_input='', buffer='z')]
z: [InputResult(moved=True, matched_rule=ConvertRule(input='zz', output='っ', next_input='z'), output='っ', next_input='z', buffer=''),
    InputResult(moved=True, matched_rule=None, output='', next_input='', buffer='z')]
z: [InputResult(moved=True, matched_rule=ConvertRule(input='zz', output='っ', next_input='z'), output='っ', next_input='z', buffer=''),
    InputResult(moved=True, matched_rule=None, output='', next_input='', buffer='z')]
r: [InputResult(moved=False, matched_rule=None, output='z', next_input='r', buffer=''),
    InputResult(moved=True, matched_rule=None, output='', next_input='', buffer='r')]

l: [InputResult(moved=True, matched_rule=None, output='', next_input='', buffer='l')]
t: [InputResult(moved=True, matched_rule=None, output='', next_input='', buffer='lt')]
,: [InputResult(moved=False, matched_rule=None, output='lt', next_input=',', buffer=''),
    InputResult(moved=True, matched_rule=ConvertRule(input=',', output='、', next_input=''), output='、', next_input='', buffer='')]

AZIKで @@ を入力した場合の結果
@: [InputResult(moved=True, matched_rule=ConvertRule(input='@', output='', next_input='ん'), output='', next_input='ん', buffe
r=''),
  InputResult(moved=True, matched_rule=None, output='', next_input='', buffer='ん')]
@ [InputResult(moved=True, matched_rule=ConvertRule(input='ん@', output='＠', next_input=''), output='＠', next_input='', buffer='')]
"""

"""
output_rule ありが一つでも results に含まれている場合は、その時点までの input/output を辞書登録
かつ、最後の buffer の先頭文字が inputtable_keys に含まれていなければ、さらに再帰的に処理
"""


def expand(ime, inputtable_keys, max_len=10):
    expand_result = {key: [key] for key in inputtable_keys}

    def _expand(ime, inputs, last_results):
        if len(inputs) > max_len:
            return

        for key in inputtable_keys:
            new_ime = ime.copy()
            input_results = new_ime.input(key)
            total_results = last_results + input_results
            this_output = "".join(result.output for result in input_results)

            if not input_results[0].moved and not input_results[0].matched_rule:
                # 今回の入力でリセットされ、マッチしたルールもない場合、無視する
                continue

            if this_output == key:
                # 入力と出力が同じ場合は単独で入力可能なので無視
                continue

            this_rules = [result.matched_rule for result in input_results if result.matched_rule]
            last_rules = [result.matched_rule for result in last_results if result.matched_rule]

            if [rule for rule in this_rules if rule in last_rules]:
                # 以前に同じルールが出力されていればループしてるので無視
                continue

            last_buffer = input_results[-1].buffer
            last_output = "".join(result.output for result in last_results)
            total_output = last_output + this_output + last_buffer
            total_input = "".join(inputs + [key])

            # 入力と出力を展開結果として登録
            expand_result.setdefault(total_output, []).append(total_input)

            if not last_buffer:
                # バッファがなくなれば、ルールの終端に到達したか、ルールから外れて初期状態に戻ったので終了
                continue

            _expand(new_ime, inputs + [key], total_results)

    _expand(ime, [], [])
    return expand_result


class State(dict):
    def __init__(self):
        self.parents = []

    def connect(self, input, next_state):
        self[input] = next_state
        next_state.parents.append((input, self))  # 何のキーとともに遷移してきたか


def to_automaton(match_rules_list):
    """
    文字位置の順にルールの塊が来る
    きょう: [
      [(1, [ki]), (2, [kyo])],
      [(1, [lyo, xyo])],
      [(1, [u, wu, whu])]
    ]
    """
    root = State()
    leaf = State()
    kana_states = {0: root, len(match_rules_list): leaf}

    def _connect_keys(parent, keys, next_kana_state):
        for key in keys[:-1]:
            next_state = parent.get(key, State())
            parent.connect(key, next_state)
            parent = next_state
        parent.connect(keys[-1], next_kana_state)

    def _connect_next_kana(parent, current_kana_index):
        if parent is leaf:
            return

        rules = match_rules_list[current_kana_index]
        for char_length, keys_list in rules:
            next_kana_index = current_kana_index + char_length
            next_kana_state = kana_states.setdefault(next_kana_index, State())
            for keys in keys_list:
                _connect_keys(parent, keys, next_kana_state)
            _connect_next_kana(next_kana_state, next_kana_index)

    _connect_next_kana(root, 0)
    remove_unreachable(root, leaf)
    return root, kana_states


def to_string(root):
    """
    Args:
        root (State):
    """


def remove_unreachable(root, leaf):
    """
    次のように「う」だけを入力するルールがない場合、kyo で2文字文進んだとしても、最後の1文字を入力する遷移がないため、無効にする必要がある

    きょう: [
      [(1, [ki], 2, [kyo])],
      [(2, [lyou, xyou])],
      []
    ]
    """
    to_finishes_dict = {}

    def backtrack(current):
        """ 終点（すべてを入力し終わった状態）から遡っていって終端に向かう遷移を始点から辿れるようにマークを付ける """
        if id(current) in to_finishes_dict:
            return

        to_finishes_dict[id(current)] = True

        for key_to_current, parent in current.parents:
            backtrack(parent)

    def remove(current):
        for key in list(current.keys()):
            if id(current[key]) not in to_finishes_dict:
                del current[key]
            else:
                remove(current[key])

    backtrack(leaf)
    remove(root)


def match_rules(target_string, rules):
    """
    きょう: [
      [(1, [ki]), (2, [kyo])],
      [(1, [lyo, xyo])],
      [(1, [u, wu, whu])]
    ]
    """
    max_output_len = max(len(key) for key in rules.keys())
    string_len = len(target_string)
    result = []
    for i in range(len(target_string)):
        result.append([])
        for j in range(min(max_output_len, string_len - i)):
            substring = target_string[i:i+j+1]
            if substring in rules:
                result[-1].append((len(substring), rules[substring]))
    return result
