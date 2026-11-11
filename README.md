# FLA CLA-2 – Finite Automata and Pushdown Automata

Course: **21CSC301T – Formal Language and Automata**, SRM IST Tiruchirappalli
Student: **Siva Balan S (RA2411026050230)**
Guide: Dr. C. Gunasundari, Department of AIML

Python implementation of the machines designed in the CLA-2 report:

| Task | Machine | Type |
|---|---|---|
| Task 2 | M1 – ATM PIN format (exactly 4 digits) | DFA, 6 states |
| Task 2 | M2 – card lock after 3 wrong attempts | DFA, 5 states |
| Task 2 | M_T + M_len – password policy (product construction, 60 reachable states) | DFAs |
| Task 2 | M3 – e-mail format `name@domain.tld` | DFA, 10 states |
| Task 3 | P1 – balanced parentheses | DPDA |
| Task 3 | P2 – arithmetic expressions from E → E+T \| T, T → T*F \| F, F → (E) \| id | NPDA (CFG → PDA) |
| Task 3 | P3 – palindromes w c wᴿ | DPDA |
| Task 3 | P4 – palindromes w wᴿ | NPDA (guesses the middle) |

No external libraries are needed – only Python 3.8 or newer.

## Project structure

```
automata/   dfa.py  – DFA class with step-by-step traces
            pda.py  – PDA simulator over instantaneous descriptions (q, w, stack),
                      works for deterministic and non-deterministic PDAs,
                      plus a DPDA check
task2/      machines.py – the Task 2 DFAs and character classifiers
task3/      machines.py – the Task 3 PDAs and a parse-tree counter for ambiguity
tests/      test_task2.py, test_task3.py
demo.py     command-line demonstration
sample_output.txt – output of `python demo.py`
```

## How to run

```bash
python demo.py                      # accept/reject tables for every machine
python demo.py task2                # only Task 2
python demo.py task3                # only Task 3
python demo.py trace pin 12a4       # step-by-step trace of one string
python demo.py trace password "Pass@123"
python demo.py trace email ravi@abc.in
python demo.py trace brackets "(())()"
python demo.py trace expr "id+id*id"
python demo.py trace wcwr abcba
```

Example trace:

```
$ python demo.py trace brackets "(())()"
(q0, (())(), Z0) ⊢ (q1, ())(), XZ0) ⊢ (q1, ))(), XXZ0) ⊢ (q1, )(), XZ0) ⊢ (q1, (), Z0)
⊢ (q0, (), Z0) ⊢ (q1, ), XZ0) ⊢ (q1, ε, Z0) ⊢ (q0, ε, Z0)   ->  Accept
```

## Tests

```bash
python -m unittest discover -s tests -t . -v
```

12 tests check:

* every accepted and rejected string from the report (Tables 5 and 8);
* that the password product DFA has exactly 60 reachable states;
* each Task 2 DFA against an independent regular-expression rule on **every** short string
  (all PIN strings up to length 6, all password class strings up to length 9,
  all e-mail strings up to length 8, all card-lock strings up to length 8);
* each PDA against an independent checker on every short string
  (brackets up to length 8, palindromes up to length 7, expressions up to 7 tokens);
* which PDAs are deterministic (P1, P3) and which are not (P2, P4);
* ambiguity: `id+id*id` has 2 parse trees in the ambiguous grammar and 1 in the revised grammar.

## Notes

* Task 2 machines read **class symbols**, not raw characters: for example `d` = any digit,
  `U` / `L` / `D` / `S` = uppercase / lowercase / digit / special. The classifier functions
  in `task2/machines.py` do this conversion.
* Any move that is not listed in a DFA goes to its dead state.
* In the PDAs the stack is printed with the top on the left and `Z0` is the initial stack symbol.
