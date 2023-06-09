# Model Checking Project

The project of CS3959 Model Checking, ACM Class, Shanghai Jiao Tong University.

Please leave a star if this repo helps you. Thank you!

# Usage

To prepare the environment, please install the SPECIFIC VERSION of `antlr4-python3-runtime` by

```
pip install antlr4-python3-runtime==4.7.2
```

You can run the model checking program by:

`python main.py -ts <ts_file> -bm <bm_file>`

where `ts_file` contains the description of the transition system, and `bm_file` the required LTL formula. If ommitted, the program will read TS from `TS.txt` and LTL formula from `benchmark.txt`.

The checking results are in `answer.txt`, each line corresponding to an input LTL formula.

# Description

## Parser

We use ANTLR4 to parse the input formula. The grammar file `antlr/ltl.g4` is written manually, and other files under directory `antlr` are auto-generated by ANTLR4. To generate them, please install Java first and run

```
java -jar antlr-4.7.2-complete.jar -Dlanguage=Python3 antlr/ltl.g4
java -jar antlr-4.7.2-complete.jar -Dlanguage=Python3 -no-listener -visitor antlr/ltl.g4
```

Then, we build an abstract syntax tree (AST) from the generated grammar tree. The node of AST is defined in `ltl_node.py`, and the AST is in `ltl_parser.py`.

When constructing the AST, we transform the LTL formulae to its equivalent form, only reserving $\lnot$, $\bigcirc$, $\land$, and $\mathsf{U}$. Meanwhile, we avoid double negation, i.e. `!(!a)`.

To make the node hashable, we define `_polish()` and `_middle()` for each node to calculate the string representation of its Polish notation and middle notation. A formula can be uniquely determined by them, thus we define `hash(node) = hash(node._polish() + node._middle())`.

Finally, as required by the algorithm, for an input formulae $\phi$, we construct AST for $\lnot \phi$.

## LTL -> GNBA

To construct GNBA from AST, we first calculate the closure of $\phi$ by `get_closure()` in AST. This is done when forming the AST recursively. Then we calculate elementary sets by enumerating subsets of the closure, but not in brute force. Note that to guarantee maximality, for $\psi, \lnot\psi \in closure(\phi)$, one and only one of them must be in the elementary set. Therefore, we only enumerate for each pair of subformula and its negation, $2^{|closure(\phi)|/2}$ times in total. Propositional consistensy and local until consistensy are checked by `_check_consistency()` and `_check_local_consistency()` in AST, respectively.

We follow *Theorem 5.37 (Page 278)* to construct GNBA, using `AST_to_GNBA()` in `transform.py`. For an instance `gnba` of class `GNBA`, `gnba.print()` will print its information. For example, GNBA of `G(a \/ b)` will print

```
---- GNBA ----
num states = 7
initial states: [1, 2, 5, 6]
final state sets:
[0, 1, 3, 4]
transitions:
0 --- (0,) --> [0, 3, 4]
1 --- () --> [0, 1, 2, 3, 4, 5, 6]
2 --- (0,) --> [1, 2, 5, 6]
3 --- (1,) --> [0, 3, 4]
4 --- (0, 1) --> [0, 3, 4]
5 --- (1,) --> [1, 2, 5, 6]
6 --- (0, 1) --> [1, 2, 5, 6]
---- END ----
```

Here all states are mapped into integers for clarity. The mapping integers might change between repeat runs due to randomness of `hash` function in Python.

## GNBA -> NBA

We follow *Theorem 4.56 (Page 195)* to transform GNBA to NBA, using `GNBA_to_NBA()` in `transform.py`. Similarly, `nba.print()` will print information of itself. For the example above, the corresponding NBA will print

```
---- NBA ----
num states = 7
initial states: [(1, 0), (2, 0), (5, 0), (6, 0)]
final states: [(0, 0), (1, 0), (3, 0), (4, 0)]
transitions:
[0](0, 0) --- (0,) --> [0, 3, 4]
[1](1, 0) --- () --> [0, 1, 2, 3, 4, 5, 6]
[2](2, 0) --- (0,) --> [1, 2, 5, 6]
[3](3, 0) --- (1,) --> [0, 3, 4]
[4](4, 0) --- (0, 1) --> [0, 3, 4]
[5](5, 0) --- (1,) --> [1, 2, 5, 6]
[6](6, 0) --- (0, 1) --> [1, 2, 5, 6]
---- END ----
```

Here the bracked number before each line of transitions are the mapped index in GNBA. For example, the first line

```
[0](0, 0) --- (0,) --> [0, 3, 4]
```

represents the state No.0 `(0, 0)`, taking action `(0,)`, can transit to state No.0 `(0,0)`, No.3 `(3,0)`, and No.4 `(4, 0)`.

A special case is that, if the input formulae does not contain $\mathsf{U}$, the final state sets of GNBA will be empty. To guarantee equivalence between GNBA and NBA, we build an NBA with the same structure and transitions, but setting all its states as final states.

## TS $\times$ NBA

We follow *Definition 4.62 (Page 200)* to calculate the product of TS and NBA. Before production, we mask all atomic propositions in TS which do not occur in the LTL formuale. Notice that in stages bellow, the AP set is never used, so we do not calculate it.

For the example above, the production TS contains following transitions

```
(0, 4) --- 1 --> [(1, 0), (1, 3), (1, 4)]
(0, 6) --- 1 --> [(1, 1), (1, 2), (1, 5), (1, 6)]
(0, 0) --- 0 --> [(3, 0), (3, 3), (3, 4)]
(0, 2) --- 0 --> [(3, 1), (3, 2), (3, 5), (3, 6)]
(3, 4) --- 2 --> [(1, 0), (1, 3), (1, 4)]
(3, 6) --- 2 --> [(1, 1), (1, 2), (1, 5), (1, 6)]
(1, 0) --- 2 --> [(4, 0), (4, 3), (4, 4)]
(1, 2) --- 2 --> [(4, 1), (4, 2), (4, 5), (4, 6)]
(2, 4) --- 2 --> [(1, 0), (1, 3), (1, 4)]
(2, 6) --- 2 --> [(1, 1), (1, 2), (1, 5), (1, 6)]
(5, 3) --- 0 --> [(2, 0), (2, 3), (2, 4)]
(5, 5) --- 0 --> [(2, 1), (2, 2), (2, 5), (2, 6)]
(5, 4) --- 1 --> [(1, 0), (1, 3), (1, 4)]
(5, 6) --- 1 --> [(1, 1), (1, 2), (1, 5), (1, 6)]
(4, 4) --- 0 --> [(1, 0), (1, 3), (1, 4)]
(4, 6) --- 0 --> [(1, 1), (1, 2), (1, 5), (1, 6)]
(4, 4) --- 1 --> [(5, 0), (5, 3), (5, 4)]
(4, 6) --- 1 --> [(5, 1), (5, 2), (5, 5), (5, 6)]
```

For each tuple `(s, q)`, `s` represents the state in the original TS and `q` represents the state in NBA.

## Nested DFS

We follow *Algorithm 7, 8 (Page 210, 211)* to performe the final check, using `check()` in `dfs.py`. It returns `True` if no cycle is found, and `False` other wise. To judge whether the state $(s,q) \vDash \Phi$, we check if `q` is the final state of the NBA. We implement the algorithm strictly as the pseudo-code in the textbook.
