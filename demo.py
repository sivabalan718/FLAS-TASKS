"""Command-line demo for FLA CLA-2 Task 2 and Task 3.

    python demo.py                 # all accept/reject tables
    python demo.py task2           # only Task 2
    python demo.py task3           # only Task 3
    python demo.py trace pin 12a4  # step-by-step trace of one string
    python demo.py trace expr "id+id*id"
"""
import sys
from task2 import machines as t2
from task3 import machines as t3

LINE = "-" * 78


def show(s):
    return repr(s) if s and " " not in s else ("ε" if s == "" else repr(s))


def task2_tables():
    print("TASK 2 - Finite automata for input validation\n" + LINE)
    for kind, (acc, rej) in t2.TESTS.items():
        print(f"\n[{kind}]")
        print(f"  {'input':<26}{'class symbols':<26}result")
        for s in acc + rej:
            cls = t2.classify(kind, s)
            res = "Accept" if t2.accepts(kind, s) else "Reject"
            print(f"  {show(s):<26}{(cls or 'ε'):<26}{res}")
    print(f"\nPassword product DFA: {t2.product_reachable_states()} reachable states "
          f"(9 x 2 x 2 x 2 = 72 in total)")


def task3_tables():
    print("\nTASK 3 - Pushdown automata and CFGs\n" + LINE)
    for kind, (acc, rej) in t3.TESTS.items():
        m = t3.MACHINES[kind]
        det = "DPDA" if m.is_deterministic() else "NPDA"
        print(f"\n[{m.name}]  type: {det}, acceptance by {m.accept_by} "
              f"{'state' if m.accept_by == 'final' else 'stack'}")
        for s in acc + rej:
            res = "Accept" if m.accepts(t3.to_tokens(kind, s)) else "Reject"
            print(f"  {show(s):<20}{res}")
    print("\nAmbiguity check - number of parse trees")
    print(f"  {'expression':<22}{'G2 (ambiguous)':<18}G2' (revised)")
    for e in ["id+id*id", "id+id+id", "id*id+id*id", "(id+id)*id", "id+id*id+id"]:
        tk = t3.tokenize(e)
        print(f"  {e:<22}{t3.count_trees_ambiguous(tk):<18}{t3.count_trees_revised(tk)}")


def trace(kind, text):
    if kind in t2.VALIDATORS:
        if kind == "password":
            cls = t2.classify(kind, text)
            print("class symbols:", cls or "ε")
            print("tracker:", t2.M_TRACKER.format_trace(cls))
            print("length :", t2.M_LEN.format_trace(cls))
            print("password", "ACCEPTED" if t2.password_valid(text) else "REJECTED")
        else:
            machine = t2.VALIDATORS[kind][0]
            cls = t2.classify(kind, text)
            print("class symbols:", cls or "ε")
            print(machine.format_trace(cls))
    elif kind in t3.MACHINES:
        print(t3.MACHINES[kind].format_trace(t3.to_tokens(kind, text)))
    else:
        print("kinds: pin lock password email brackets expr wcwr wwr")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["trace"] and len(args) >= 2:
        trace(args[1], args[2] if len(args) > 2 else "")
    elif args[:1] == ["task2"]:
        task2_tables()
    elif args[:1] == ["task3"]:
        task3_tables()
    else:
        task2_tables()
        task3_tables()
