from filter_rule import FilterRuleTable
from google_input_ime import GoogleInputIME


if __name__ == '__main__':
    table = FilterRuleTable.from_file("google_ime_default_roman_table.txt")
    gi = GoogleInputIME(table)
    input_string = "nankoattaltuke"
    output = ""
    for c in input_string:
        print(f"key: {c}")
        result = gi.input(c)
        if result.fixed:
            output += result.fixed.output
        else:
            if not result.tmp_fixed and not result.next_candidates:
                output += result.input
        print(f"output: {result}\n")
    print()
    print(output)


# output
"""
key: n
output: {
    input: n,
    tmp: {in: n, out: ん }
    fixed: {in: None, out: None }
    next_input:
    num_of_next_candidates: 12
}

key: a
output: {
    input: na,
    tmp: {in: None, out: None }
    fixed: {in: na, out: な }
    next_input:
    num_of_next_candidates: 0
}

key: n
output: {
    input: n,
    tmp: {in: n, out: ん }
    fixed: {in: None, out: None }
    next_input:
    num_of_next_candidates: 12
}

key: k
output: {
    input: nk,
    tmp: {in: None, out: None }
    fixed: {in: n, out: ん }
    next_input: k
    num_of_next_candidates: 0
}

key: o
output: {
    input: ko,
    tmp: {in: None, out: None }
    fixed: {in: ko, out: こ }
    next_input:
    num_of_next_candidates: 0
}

key: a
output: {
    input: a,
    tmp: {in: None, out: None }
    fixed: {in: a, out: あ }
    next_input:
    num_of_next_candidates: 0
}

key: t
output: {
    input: t,
    tmp: {in: None, out: None }
    fixed: {in: None, out: None }
    next_input:
    num_of_next_candidates: 29
}

key: t
output: {
    input: tt,
    tmp: {in: None, out: None }
    fixed: {in: tt, out: っ }
    next_input: t
    num_of_next_candidates: 0
}

key: a
output: {
    input: ta,
    tmp: {in: None, out: None }
    fixed: {in: ta, out: た }
    next_input:
    num_of_next_candidates: 0
}

key: l
output: {
    input: l,
    tmp: {in: None, out: None }
    fixed: {in: None, out: None }
    next_input:
    num_of_next_candidates: 16
}

key: t
output: {
    input: lt,
    tmp: {in: None, out: None }
    fixed: {in: None, out: None }
    next_input:
    num_of_next_candidates: 2
}

key: u
output: {
    input: ltu,
    tmp: {in: None, out: None }
    fixed: {in: ltu, out: っ }
    next_input:
    num_of_next_candidates: 0
}

key: k
output: {
    input: k,
    tmp: {in: None, out: None }
    fixed: {in: None, out: None }
    next_input:
    num_of_next_candidates: 16
}

key: e
output: {
    input: ke,
    tmp: {in: None, out: None }
    fixed: {in: ke, out: け }
    next_input:
    num_of_next_candidates: 0
}

なんこあったっけ
"""
