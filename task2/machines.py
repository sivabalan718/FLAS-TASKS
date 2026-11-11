"""Task 2: finite automata for real-time input validation.

Each raw character is first mapped to a class symbol, then the DFA reads
the class symbols. This matches the designs in the report.
"""
from automata import DFA

# ---------------------------------------------------------------- ATM PIN
def pin_class(ch):
    return "d" if ch in "0123456789" else "x"

M1_PIN = DFA(
    "M1 ATM PIN",
    states=["q0", "q1", "q2", "q3", "q4", "qD"],
    alphabet="dx",
    delta={("q0", "d"): "q1", ("q1", "d"): "q2", ("q2", "d"): "q3",
           ("q3", "d"): "q4"},          # every other move goes to qD
    start="q0", finals=["q4"])

M2_LOCK = DFA(
    "M2 Card lock",
    states=["A0", "A1", "A2", "OK", "LOCK"],
    alphabet="CW",
    delta={("A0", "W"): "A1", ("A1", "W"): "A2", ("A2", "W"): "LOCK",
           ("A0", "C"): "OK", ("A1", "C"): "OK", ("A2", "C"): "OK",
           ("OK", "C"): "OK", ("OK", "W"): "OK",
           ("LOCK", "C"): "LOCK", ("LOCK", "W"): "LOCK"},
    start="A0", finals=["OK"], dead="LOCK")

# ---------------------------------------------------------------- Password
SPECIAL = set("!@#$%^&*")

def pw_class(ch):
    if "A" <= ch <= "Z":
        return "U"
    if "a" <= ch <= "z":
        return "L"
    if ch in "0123456789":
        return "D"
    if ch in SPECIAL:
        return "S"
    return "O"                          # any other character -> dead state

def _tracker_delta():
    names = ["∅", "U", "D", "S", "UD", "US", "DS", "UDS"]
    delta = {}
    for st in names:
        seen = set() if st == "∅" else set(st)
        for c in "ULDS":
            new = seen | ({c} if c != "L" else set())
            key = "".join(x for x in "UDS" if x in new) or "∅"
            delta[(st, c)] = key
    return names, delta

_names, _delta = _tracker_delta()
M_TRACKER = DFA("M_T Class tracker", _names, "ULDS", _delta, "∅", ["UDS"])

M_LEN = DFA(
    "M_len Length >= 8",
    states=[f"n{i}" for i in range(9)],
    alphabet="ULDS",
    delta={(f"n{i}", c): f"n{min(i + 1, 8)}" for i in range(9) for c in "ULDS"},
    start="n0", finals=["n8"])

def password_valid(text):
    """Product of the component DFAs: accept only if every component accepts."""
    s = "".join(pw_class(ch) for ch in text)
    return M_TRACKER.accepts(s) and M_LEN.accepts(s)

def product_reachable_states():
    """Count reachable states of the single product DFA (tracker x length)."""
    start = (M_TRACKER.start, M_LEN.start)
    seen, todo = {start}, [start]
    while todo:
        t, n = todo.pop()
        for c in "ULDS":
            nxt = (M_TRACKER.step(t, c), M_LEN.step(n, c))
            if nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    return len(seen)

# ---------------------------------------------------------------- E-mail
def email_class(ch):
    if ch.isascii() and ch.isalpha():
        return "A"
    if ch in "0123456789":
        return "N"
    if ch in ".@":
        return ch
    return "O"

_e = {}
def _add(src, syms, dst):
    for s in syms:
        _e[(src, s)] = dst

_add("e0", "AN", "e1"); _add("e1", "AN", "e1"); _add("e1", ".", "e2"); _add("e1", "@", "d0")
_add("e2", "AN", "e1"); _add("d0", "AN", "d1"); _add("d1", "AN", "d1"); _add("d1", ".", "d2")
_add("d2", "A", "d3"); _add("d2", "N", "d5")
_add("d3", "A", "d4"); _add("d3", "N", "d5"); _add("d3", ".", "d2")
_add("d4", "A", "d4"); _add("d4", "N", "d5"); _add("d4", ".", "d2")
_add("d5", "AN", "d5"); _add("d5", ".", "d2")

M3_EMAIL = DFA("M3 E-mail", ["e0", "e1", "e2", "d0", "d1", "d2", "d3", "d4", "d5", "qD"],
               "AN.@", _e, "e0", ["d4"])

# ---------------------------------------------------------------- helpers
VALIDATORS = {
    "pin":      (M1_PIN, pin_class),
    "lock":     (M2_LOCK, lambda ch: ch),
    "password": (None, pw_class),
    "email":    (M3_EMAIL, email_class),
}

def classify(kind, text):
    return "".join(VALIDATORS[kind][1](ch) for ch in text)

def accepts(kind, text):
    if kind == "password":
        return password_valid(text)
    machine, _ = VALIDATORS[kind]
    return machine.accepts(classify(kind, text))

# Test strings used in the report (Table 5)
TESTS = {
    "pin":      (["1234", "0000", "0071", "9876", "4501"],
                 ["123", "12345", "12a4", "", "12 4"]),
    "lock":     (["C", "WC", "WWC", "CW", "WWCWW"],
                 ["", "W", "WW", "WWW", "WWWC"]),
    "password": (["Pass@123", "Secure#9", "Abcdef1!", "9$Kitchen", "HELLO@2026"],
                 ["Pa@1", "password1!", "PASSWORD!!", "Password123", ""]),
    "email":    (["student@srmist.edu.in", "john.doe@yahoo.com", "user123@mail2.org",
                  "a.b.c@x.io", "ravi99@abc.co.in"],
                 [".ravi@gmail.com", "ravi..k@gmail.com", "ravi@gmail",
                  "ravi@@gmail.com", "ravi@gmail.c"]),
}
