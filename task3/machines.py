"""Task 3: pushdown automata and context-free grammars.

Stacks are tuples with the top first; Z0 is the initial stack symbol.
"""
from automata import PDA

# ------------------------------------------------ P1 balanced parentheses (DPDA)
P1_BRACKETS = PDA("P1 Balanced parentheses", [
    ("q0", "(", "Z0", "q1", ("X", "Z0")),
    ("q1", "(", "X",  "q1", ("X", "X")),
    ("q1", ")", "X",  "q1", ()),
    ("q1", "",  "Z0", "q0", ("Z0",)),
], start="q0", finals=["q0"], accept_by="final")

# ------------------------------------------------ P2 expressions (CFG -> PDA)
# G2': E -> E+T | T,  T -> T*F | F,  F -> (E) | id
P2_EXPR = PDA("P2 Arithmetic expressions", [
    ("q", "", "E", "q", ("E", "+", "T")),
    ("q", "", "E", "q", ("T",)),
    ("q", "", "T", "q", ("T", "*", "F")),
    ("q", "", "T", "q", ("F",)),
    ("q", "", "F", "q", ("(", "E", ")")),
    ("q", "", "F", "q", ("id",)),
] + [("q", a, a, "q", ()) for a in ["id", "+", "*", "(", ")"]],
    start="q", start_stack="E", accept_by="empty")

def tokenize(expr):
    """'id+id*id' -> ['id', '+', 'id', '*', 'id'] (spaces ignored)."""
    tokens, i, s = [], 0, expr.replace(" ", "")
    while i < len(s):
        if s.startswith("id", i):
            tokens.append("id"); i += 2
        else:
            tokens.append(s[i]); i += 1
    return tokens

# ------------------------------------------------ P3 w c w^R (DPDA)
_p3 = [("q0", a, X, "q0", (a, X)) for a in "ab" for X in ["a", "b", "Z0"]]
_p3 += [("q0", "c", X, "q1", (X,)) for X in ["a", "b", "Z0"]]
_p3 += [("q1", "a", "a", "q1", ()), ("q1", "b", "b", "q1", ()), ("q1", "", "Z0", "q2", ())]
P3_WCWR = PDA("P3 Palindrome w c w^R", _p3, start="q0", finals=["q2"], accept_by="final")

# ------------------------------------------------ P4 w w^R (NPDA: guesses the middle)
_p4 = [m for m in _p3 if m[1] != "c"] + [("q0", "", X, "q1", (X,)) for X in ["a", "b", "Z0"]]
P4_WWR = PDA("P4 Palindrome w w^R (NPDA)", _p4, start="q0", finals=["q2"], accept_by="final")

# ------------------------------------------------ ambiguity check by counting parse trees
from functools import lru_cache

def count_trees_ambiguous(tokens):
    """Parse trees of `tokens` in G2: E -> E+E | E*E | (E) | id."""
    t = tuple(tokens)

    @lru_cache(None)
    def E(i, j):
        n = 0
        if j - i == 1 and t[i] == "id":
            n += 1
        if j - i >= 3 and t[i] == "(" and t[j - 1] == ")":
            n += E(i + 1, j - 1)
        for k in range(i + 1, j - 1):
            if t[k] in "+*":
                n += E(i, k) * E(k + 1, j)
        return n
    return E(0, len(t))

def count_trees_revised(tokens):
    """Parse trees of `tokens` in G2': E -> E+T | T, T -> T*F | F, F -> (E) | id."""
    t = tuple(tokens)

    @lru_cache(None)
    def F(i, j):
        n = 1 if (j - i == 1 and t[i] == "id") else 0
        if j - i >= 3 and t[i] == "(" and t[j - 1] == ")":
            n += E(i + 1, j - 1)
        return n

    @lru_cache(None)
    def T(i, j):
        return F(i, j) + sum(T(i, k) * F(k + 1, j) for k in range(i + 1, j - 1) if t[k] == "*")

    @lru_cache(None)
    def E(i, j):
        return T(i, j) + sum(E(i, k) * T(k + 1, j) for k in range(i + 1, j - 1) if t[k] == "+")
    return E(0, len(t))

MACHINES = {"brackets": P1_BRACKETS, "expr": P2_EXPR, "wcwr": P3_WCWR, "wwr": P4_WWR}

def to_tokens(kind, text):
    return tokenize(text) if kind == "expr" else list(text)

# Test strings used in the report (Table 8), plus w w^R
TESTS = {
    "brackets": (["", "()", "(())", "()()", "(()())"], ["(", ")", ")(", "(()", "())("]),
    "expr":     (["id", "id+id", "id*id+id", "(id+id)*id", "((id))"],
                 ["id+", "+id", "id id", "(id+id", "id*()"]),
    "wcwr":     (["c", "aca", "bcb", "abcba", "aabcbaa"], ["", "acb", "abcab", "abcb", "acaa"]),
    "wwr":      (["", "aa", "abba", "baab", "abbbba"], ["a", "ab", "aba", "abab", "aabb"]),
}
