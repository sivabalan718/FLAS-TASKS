"""Deterministic finite automaton M = (Q, Sigma, delta, q0, F)."""


class DFA:
    def __init__(self, name, states, alphabet, delta, start, finals, dead="qD"):
        self.name = name
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.delta = dict(delta)          # (state, symbol) -> next state
        self.start = start
        self.finals = set(finals)
        self.dead = dead                  # any move that is not listed goes here

    def step(self, state, symbol):
        return self.delta.get((state, symbol), self.dead)

    def trace(self, symbols):
        """Return the list of instantaneous descriptions (state, remaining input)."""
        state, ids = self.start, []
        for i, s in enumerate(symbols):
            ids.append((state, symbols[i:]))
            state = self.step(state, s)
        ids.append((state, ""))
        return ids

    def accepts(self, symbols):
        return self.trace(symbols)[-1][0] in self.finals

    def format_trace(self, symbols):
        parts = [f"({q}, {rest if rest else 'ε'})" for q, rest in self.trace(symbols)]
        final = self.trace(symbols)[-1][0]
        verdict = "Accept" if final in self.finals else "Reject"
        return " ⊢ ".join(parts) + f"   ->  {verdict}"
