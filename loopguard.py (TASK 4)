"""Task 4 (team): LoopGuard - infinite-loop detection within the limits of computability.

"Does this loop run forever?" is the complement of the Halting Problem: undecidable, and not
even recognizable. LoopGuard therefore never claims an exact answer for every loop. It returns:

    TERMINATES - proved: a fixed iteration bound, a ranking function, or the loop exited
    LOOPS      - proved: the guard can never become false, or a full loop state repeated
    UNKNOWN    - no proof within the step budget (left to a runtime watchdog / timeout)

Checks, from cheapest to most expensive:
  1. Syntactic bound     for i in range(N)                      -> TERMINATES after N iterations
  2. Linear ranking      while x > c: x = x + d  (or x < c)     -> decided exactly by the sign of d
  3. Cycle detection     run the loop, store every state; a repeated state proves a loop
                         (exact for finite domains such as 8-bit or 16-bit integers)
  4. Step budget         no proof after `budget` iterations     -> UNKNOWN
"""
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, Tuple

TERMINATES, LOOPS, UNKNOWN = "TERMINATES", "LOOPS", "UNKNOWN"


@dataclass
class LoopProgram:
    name: str
    code: str
    init: Dict[str, object] = field(default_factory=dict)
    cond: Optional[Callable] = None              # loop guard, state -> bool
    body: Optional[Callable] = None              # state -> new state
    bound: Optional[int] = None                  # for i in range(bound)
    linear: Optional[Tuple[str, str, object, int]] = None   # (var, op, c, d): while var op c: var += d
    budget: int = 100_000


# ------------------------------------------------------------------ the four checks
def syntactic_check(p):
    if p.bound is None:
        return None
    return TERMINATES, f"fixed bound: range({p.bound}) runs exactly {p.bound} iterations"


def linear_check(p):
    """Exact for  while x > c: x = x + d  and  while x < c: x = x + d  (x, c, d integers)."""
    if p.linear is None:
        return None
    var, op, c, d = p.linear
    c = p.init[c] if isinstance(c, str) else c
    x = p.init[var]
    if not ((x > c) if op == ">" else (x < c)):
        return TERMINATES, "guard false at entry (0 iterations)"
    towards = (d < 0) if op == ">" else (d > 0)
    if towards:
        gap = (x - c) if op == ">" else (c - x)
        steps = -(-gap // abs(d))
        r = "x - c" if op == ">" else "c - x"
        return TERMINATES, f"ranking function r = {r} drops by {abs(d)} per iteration; exits after {steps} iterations"
    if d == 0:
        return LOOPS, f"'{var}' never changes inside the loop, so the guard stays true forever"
    return LOOPS, f"'{var}' moves away from the bound (d = {d:+d}), so the guard stays true forever"


def cycle_check(p):
    """Execute the loop, remembering every full state. A repeated state proves an infinite loop,
    because the loop is deterministic and will repeat the same states forever."""
    state = dict(p.init)
    seen = {}
    for i in range(p.budget):
        if not p.cond(state):
            return TERMINATES, f"loop exited after {i} iterations"
        key = tuple(sorted(state.items()))
        if key in seen:
            return LOOPS, f"state repeated: iteration {seen[key]} = iteration {i} (cycle length {i - seen[key]})"
        seen[key] = i
        state = p.body(state)
    return UNKNOWN, f"no exit and no repeated state within {p.budget:,} iterations"


def analyse(p):
    for name, check in (("syntactic bound", syntactic_check), ("linear ranking", linear_check)):
        r = check(p)
        if r is not None:
            return r[0], name, r[1]
    verdict, why = cycle_check(p)
    label = {LOOPS: "cycle detection", TERMINATES: "bounded run", UNKNOWN: "step budget"}[verdict]
    return verdict, label, why


# ------------------------------------------------------------------ benchmark loops
A = [1, 3, 5, 7]


def bsearch_step(lo_fix):
    def step(s):
        lo, hi = s["lo"], s["hi"]
        mid = (lo + hi) // 2
        if A[mid] < s["t"]:
            lo = mid + 1 if lo_fix else mid
        else:
            hi = mid
        return {"lo": lo, "hi": hi, "t": s["t"]}
    return step


def sigma(n):
    total, i = 0, 1
    while i * i <= n:
        if n % i == 0:
            total += i + (n // i if i * i != n else 0)
        i += 1
    return total


NEXT_LIGHT = {"RED": "GREEN", "GREEN": "YELLOW", "YELLOW": "RED"}

BENCHMARK = [
    LoopProgram("L1 bounded for-loop", "for i in range(1000): total += i", bound=1000),
    LoopProgram("L2 countdown by 3", "x = 10\nwhile x > 0: x = x - 3", {"x": 10}, linear=("x", ">", 0, -3)),
    LoopProgram("L3 wrong direction", "x = 1\nwhile x > 0: x = x + 1", {"x": 1}, linear=("x", ">", 0, 1)),
    LoopProgram("L4 forgotten update", "i, n, total = 0, 5, 0\nwhile i < n: total = total + i",
                {"i": 0, "n": 5, "total": 0}, linear=("i", "<", "n", 0)),
    LoopProgram("L5 binary search (bug)", "lo, hi = 0, 3   # find 6 in [1,3,5,7]\nwhile lo < hi: ... lo = mid",
                {"lo": 0, "hi": 3, "t": 6}, lambda s: s["lo"] < s["hi"], bsearch_step(False)),
    LoopProgram("L6 binary search (fixed)", "same, with lo = mid + 1",
                {"lo": 0, "hi": 3, "t": 6}, lambda s: s["lo"] < s["hi"], bsearch_step(True)),
    LoopProgram("L7 traffic-light controller", "light = RED\nwhile True: light = next(light)",
                {"light": "RED"}, lambda s: True, lambda s: {"light": NEXT_LIGHT[s["light"]]}),
    LoopProgram("L8 skip zero, 16-bit", "x = 5   # uint16\nwhile x != 0: x = (x - 2) mod 65536",
                {"x": 5}, lambda s: s["x"] != 0, lambda s: {"x": (s["x"] - 2) % 65536}),
    LoopProgram("L9 skip zero, unbounded", "x = 5   # Python int\nwhile x != 0: x = x - 2",
                {"x": 5}, lambda s: s["x"] != 0, lambda s: {"x": s["x"] - 2}),
    LoopProgram("L10 odd perfect number", "n = 1\nwhile sigma(n) != 2n: n = n + 2",
                {"n": 1}, lambda s: sigma(s["n"]) != 2 * s["n"], lambda s: {"n": s["n"] + 2}, budget=5_000),
]


if __name__ == "__main__":
    print("LoopGuard - infinite-loop detection within the limits of computability")
    print("=" * 118)
    print(f"{'loop':<30}{'verdict':<13}{'check':<18}reason")
    print("-" * 118)
    for p in BENCHMARK:
        v, check, why = analyse(p)
        print(f"{p.name:<30}{v:<13}{check:<18}{why}")
