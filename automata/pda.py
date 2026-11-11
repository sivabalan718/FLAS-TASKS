"""Pushdown automaton P = (Q, Sigma, Gamma, delta, q0, Z0, F).

The stack is a tuple whose first element is the top of the stack.
A move (q, a, X) -> (p, gamma) is stored with a == "" for an epsilon move.
The simulator explores all instantaneous descriptions breadth first, so it
also works for non-deterministic PDAs.
"""
from collections import deque


class PDA:
    def __init__(self, name, delta, start, start_stack="Z0", finals=(), accept_by="final"):
        self.name = name
        self.delta = delta                 # list of (q, a, X, p, gamma_tuple)
        self.start = start
        self.start_stack = start_stack
        self.finals = set(finals)
        self.accept_by = accept_by         # "final" or "empty"

    def moves(self, q, a, X):
        return [(p, g) for (s, r, t, p, g) in self.delta if s == q and r == a and t == X]

    def is_deterministic(self):
        """DPDA conditions from the class notes:
        (i)  every delta(q, a, X) has at most one element;
        (ii) if delta(q, eps, X) is non-empty, delta(q, a, X) is empty for every input a."""
        keys = {(q, a, X) for (q, a, X, _, _) in self.delta}
        for (q, a, X) in keys:
            if len(self.moves(q, a, X)) > 1:
                return False
            if a == "" and any(k[0] == q and k[2] == X and k[1] != "" for k in keys):
                return False
        return True

    def _accepting(self, q, rest, stack):
        if rest:
            return False
        return q in self.finals if self.accept_by == "final" else len(stack) == 0

    def run(self, tokens, max_extra_stack=2, limit=200000):
        """Return (accepted, list of IDs on an accepting path or the longest path tried)."""
        tokens = tuple(tokens)
        first = (self.start, 0, (self.start_stack,))
        parent = {first: None}
        queue, best = deque([first]), first
        while queue and len(parent) < limit:
            node = queue.popleft()
            q, i, stack = node
            if i > best[1]:
                best = node
            if self._accepting(q, tokens[i:], stack):
                return True, self._path(parent, node, tokens)
            if not stack:
                continue
            X, below = stack[0], stack[1:]
            options = [("", m) for m in self.moves(q, "", X)]
            if i < len(tokens):
                options += [(tokens[i], m) for m in self.moves(q, tokens[i], X)]
            for a, (p, gamma) in options:
                new_stack = tuple(gamma) + below
                # prune: every stack symbol (except Z0) must still produce input
                if len(new_stack) > len(tokens) - i + max_extra_stack:
                    continue
                nxt = (p, i + (1 if a else 0), new_stack)
                if nxt not in parent:
                    parent[nxt] = node
                    queue.append(nxt)
        return False, self._path(parent, best, tokens)

    def accepts(self, tokens):
        return self.run(tokens)[0]

    @staticmethod
    def _path(parent, node, tokens):
        path = []
        while node is not None:
            path.append(node)
            node = parent[node]
        return list(reversed(path))

    def format_trace(self, tokens, sep=""):
        ok, path = self.run(tokens)
        ids = []
        for q, i, stack in path:
            rest = sep.join(tokens[i:]) or "ε"
            st = "".join(stack) or "ε"
            ids.append(f"({q}, {rest}, {st})")
        return " ⊢ ".join(ids) + ("   ->  Accept" if ok else "   ->  Reject (no move possible)")
