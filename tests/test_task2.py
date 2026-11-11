"""Task 2 tests: report strings + brute-force comparison with independent rules."""
import itertools
import re
import unittest

from task2 import machines as t2


class ReportStrings(unittest.TestCase):
    def test_table5(self):
        for kind, (acc, rej) in t2.TESTS.items():
            for s in acc:
                self.assertTrue(t2.accepts(kind, s), f"{kind}: {s!r} should be accepted")
            for s in rej:
                self.assertFalse(t2.accepts(kind, s), f"{kind}: {s!r} should be rejected")

    def test_product_state_count(self):
        self.assertEqual(t2.product_reachable_states(), 60)


class BruteForce(unittest.TestCase):
    """Compare each DFA with a rule written independently using Python regex."""

    def test_pin_all_short_strings(self):
        alphabet = "07a "
        for n in range(7):
            for chars in itertools.product(alphabet, repeat=n):
                s = "".join(chars)
                expected = re.fullmatch(r"[0-9]{4}", s) is not None
                self.assertEqual(t2.accepts("pin", s), expected, s)

    def test_password_all_class_strings(self):
        sample = {"U": "A", "L": "a", "D": "1", "S": "@"}
        for n in range(10):
            for cls in itertools.product("ULDS", repeat=n):
                s = "".join(sample[c] for c in cls)
                expected = bool(len(s) >= 8 and re.search(r"[A-Z]", s) and re.search(r"[0-9]", s)
                                and re.search(r"[!@#$%^&*]", s))
                self.assertEqual(t2.accepts("password", s), expected, s)

    def test_email_all_short_strings(self):
        rule = re.compile(r"[A-Za-z0-9]+(\.[A-Za-z0-9]+)*@([A-Za-z0-9]+\.)+[A-Za-z]{2,}")
        for n in range(9):
            for chars in itertools.product("a1.@", repeat=n):
                s = "".join(chars)
                self.assertEqual(t2.accepts("email", s), rule.fullmatch(s) is not None, s)

    def test_lock_all_short_strings(self):
        rule = re.compile(r"(|W|WW)C[CW]*")
        for n in range(9):
            for chars in itertools.product("CW", repeat=n):
                s = "".join(chars)
                self.assertEqual(t2.accepts("lock", s), rule.fullmatch(s) is not None, s)


if __name__ == "__main__":
    unittest.main()
