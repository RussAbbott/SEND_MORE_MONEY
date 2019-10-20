# SEND + MORE = MONEY

```
    SEND 
  + MORE 
  ------
   MONEY
```

A solver with an arithmetic propagator for SEND+MORE=MONEY.
It is based on the propagator in Van Hentenryck's Coursera course on [Discrete Optimization](https://www.coursera.org/learn/discrete-optimization/home/welcome). The propagator is discussed in [Video CP-2](https://www.coursera.org/learn/discrete-optimization/lecture/nHott/cp-2-propagation-arithmetic-constraints-send-more-money).

The program can be run by running the file `send_more_money.py`.

The primary feature of interest is the propagator, which is based on interval arithmetic as discussed by Van Hentenryck. The propagator is specialized to arithmetic addition problems and operates one column at a time. It is implemented in the function `column_propagator` in the file `constraints_and_propagators.py`. The function is generously commented.

The propagator is called repeatedly during the search, which is implemented by the function `complete_the_assignment` in the file `CSP.py`. It is called, via the function `run_column_propagator` at the beginning of `complete_the_assignment`. Since `complete_the_assignment`is a recursive search, the propagator is called after every trial assignment of a value to a variable. 

The function `run_column_propagator` repeatedly calls `column_propagator` on all the columns until no new information is generated, at which point the search continues.  

An execution of `SEND_MORE_MONEY` generates the following output. (The variables `C_i` are carry variables. In particular, `C0` is the carry-in variable to the units position. It is defined to be 0. The anonymous variable `'_'` serves as left-fill for short numbers and has the value 0. As you can see in the Initial state,  `C0` and `_` are the only pre-defined values. They are both set to 0.) The other variables, both problem variables (other than 'M' and 'S') and carry variables are all given domains of `frozenset(range(10))`. As the initial digits of numbers `M` and `S` are given initial domains of `frozenset(range(1, 10))`. Numbers may not have leading zeros.

```
Problem: (['SEND', 'MORE'], 'MONEY')
Problem vars (in order of frequency): ['E', 'N', 'O', 'M', 'D', 'S', 'Y', 'R']

Columns:
4. (('C4', '_', '_'), ('C5', 'M'))
3. (('C3', 'S', 'M'), ('C4', 'O'))
2. (('C2', 'E', 'O'), ('C3', 'N'))
1. (('C1', 'N', 'R'), ('C2', 'E'))
0. (('C0', 'D', 'E'), ('C1', 'Y'))

Initial domains: {'C0': frozenset({0}), '_': frozenset({0}), 'M': frozenset({1, 2, 3, 4, 5, 6, 7, 8, 9}), 'S': frozenset({1, 2, 3, 4, 5, 6, 7, 8, 9}), 'E': frozenset({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}), 'N': frozenset({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}), 'O': frozenset({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}), 'D': frozenset({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}), 'Y': frozenset({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}), 'R': frozenset({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}), 'C1': frozenset({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}), 'C2': frozenset({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}), 'C3': frozenset({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}), 'C4': frozenset({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}), 'C5': frozenset({0, 1, 2, 3, 4, 5, 6, 7, 8, 9})}

Initial state:
assigned: {'C0': 0, '_': 0};
unassigned: ['E', 'N', 'O', 'M', 'D', 'S', 'Y', 'R', 'C1', 'C2', 'C3', 'C4', 'C5']

State after initial propagation
assigned: {'O': 0, 'M': 1, 'S': 9, 'C0': 0, 'C3': 0, 'C4': 1, 'C5': 0, '_': 0};
unassigned: ['E', 'N', 'D', 'Y', 'R', 'C1', 'C2']

Propagation after setting E = 5
assigned: {'E': 5, 'N': 6, 'O': 0, 'M': 1, 'D': 7, 'S': 9, 'Y': 2, 'R': 8, 'C0': 0, 'C1': 1, 'C2': 1, 'C3': 0, 'C4': 1, 'C5': 0, '_': 0};
unassigned: []

  SEND ->  9567
+ MORE ->  1085
------    -----
 MONEY -> 10652

{'E': 5, 'N': 6, 'O': 0, 'M': 1, 'D': 7, 'S': 9, 'Y': 2, 'R': 8, 'C0': 0, 'C1': 1, 'C2': 1, 'C3': 0, 'C4': 1, 'C5': 0, '_': 0}

Solution found after 4 assignments!

```

The initial propagation finds values for problem variables `O=0`, `M=1`, and `S=9`, and for the carry variables `C3=0`,  `C4=1`, and `C5=0`. (`C5` is the carry-out variables from the left-most column. The system is able to derive its value.)

The search selects `E`, the most frequently occuring variable, as the first variable for which to try trial values. Since 0 and 1 are taken, the search tries `E=2`, `E=3`, and `E=4`. These are all found to be incompatible with the problem specification. When the search tries `E=5`, it is able to solve the entire problem. 

In other words, given the power of the arithmetic propagator, only four search steps are needed to solve the problem.
