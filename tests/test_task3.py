"""Task 3 tests: report strings, determinism, ambiguity and brute-force checks."""
import itertools
import re
import unittest

from task3 import machines as t3


def balanced(s):
    depth = 0
    for ch in s:
        depth += 1 if ch == "(" else -1
        if depth < 0:
            return False
    return depth == 0


class ReportStrings(unittest.TestCase):
    def test_table8(self):
        for kind, (acc, rej) in t3.TESTS.items():
            m = t3.MACHINES[kind]
            for s in acc:
                self.assertTrue(m.accepts(t3.to_tokens(kind, s)), f"{kind}: {s!r}")
            for s in rej:
                self.assertFalse(m.accepts(t3.to_tokens(kind, s)), f"{kind}: {s!r}")

    def test_determinism(self):
        self.assertTrue(t3.P1_BRACKETS.is_deterministic())
        self.assertFalse(t3.P2_EXPR.is_deterministic())
        self.assertTrue(t3.P3_WCWR.is_deterministic())
        self.assertFalse(t3.P4_WWR.is_deterministic())

    def test_ambiguity(self):
        tk = t3.tokenize("id+id*id")
        self.assertEqual(t3.count_trees_ambiguous(tk), 2)
        self.assertEqual(t3.count_trees_revised(tk), 1)


class BruteForce(unittest.TestCase):
    def test_brackets_all_strings(self):
        for n in range(9):
            for chars in itertools.product("()", repeat=n):
                s = "".join(chars)
                self.assertEqual(t3.P1_BRACKETS.accepts(list(s)), balanced(s), s)

    def test_palindromes_all_strings(self):
        for n in range(8):
            for chars in itertools.product("abc", repeat=n):
                s = "".join(chars)
                expected = s.count("c") == 1 and s[: s.index("c")] == s[s.index("c") + 1:][::-1] \
                    if "c" in s else False
                self.assertEqual(t3.P3_WCWR.accepts(list(s)), expected, s)
            for chars in itertools.product("ab", repeat=n):
                s = "".join(chars)
                expected = len(s) % 2 == 0 and s == s[::-1]
                self.assertEqual(t3.P4_WWR.accepts(list(s)), expected, s)

    def test_expressions_against_checker(self):
        """Compare the PDA with an independent rule: repeatedly reduce the token
        string ('(id)' -> 'id', 'id+id' -> 'id', 'id*id' -> 'id') until it is 'id'."""
        def valid(toks):
            s = " ".join(toks)
            while True:
                t = re.sub(r"\( id \)|id [+*] id", "id", s, count=1)
                if t == s:
                    return s == "id"
                s = t
        for n in range(1, 8):
            for toks in itertools.product(["id", "+", "*", "(", ")"], repeat=n):
                self.assertEqual(t3.P2_EXPR.accepts(list(toks)), valid(toks), toks)

if __name__ == "__main__":
    unittest.main()
