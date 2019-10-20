# send_more_money.py
# From Classic Computer Science Problems in Python Chapter 3
# Copyright 2018 David Kopec
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from math import ceil, floor
from typing import Dict, FrozenSet, Optional  # , Set  # List, Tuple


Domains = Dict[str, FrozenSet[int]]


def all_different_assignment_propagator(var: str, val: int, domains: Domains, problem_vars: FrozenSet[str]) -> Domains:
    """
    Assign val to var. Ensure that no two variables in all_diff_vars have the same value.
    :return: The revised domains dictionary
    """
    reduced_domains = {v: frozenset({val}) if v == var else
                          domains[v] - {val} if v in problem_vars else
                          domains[v] for v in domains}
    return reduced_domains


def all_different_propagator(domains: Domains, all_diff_vars: FrozenSet[str]) -> Domains:
    """
    Ensure that no two variables in all_diff_vars have the same value.
    :return: The revised domains dictionary
    """
    assignment = {v: list(domains[v])[0] for v in domains if len(domains[v]) == 1}
    reduced_domains = domains
    for var in assignment:
        if var in all_diff_vars:
            reduced_domains = all_different_assignment_propagator(var, assignment[var], reduced_domains, all_diff_vars)
    return reduced_domains if reduced_domains == domains else all_different_propagator(reduced_domains, all_diff_vars)


# noinspection PyPep8Naming
def column_propagator(column_vars, domains: Domains, problem_vars: FrozenSet[str]) -> Optional[Domains]:
    """
    This is the core function.
    Reduce domains as the given column requires. A column is given as a tuple: (top_variables, bottom_variables),
    where top_variables is a list of the variables in the summands (along with the carry variables) and
    bottom_variables is the sum variables along with the carry variable, which may be 0.

    This is a *very long* method, but most of its line are comments, which attempt to explain and keep track of
    the manipulations being performed. It runs from line 49 to line 226. It has fewer than two dozen executable
    lines of code.

    :return: An updated domains dictionary based on information that can be deduced from the given column.

    """
    #        |-?--|
    #  C5 C4 | C3 | C2 C1 C0
    #        | S  | E  N  D
    #        | M  | O  R  E
    #  --------------------
    #     M  | O  | N  E  Y
    #        |-?--|

    # The examples in the discussion will use the indicated column from SEND + MORE = MONEY.
    #              C3 + S + M = 10*C4 + O
    # (             top_vars,                    bottom_vars          )
    # ([C3: {0, 1}, S: {0, 2 .. 9}, M: {1}], [C4: {1}, O: {0, 2 .. 9}])

    ([C_IN, TERM_1, TERM_2], [C_OUT, TOTAL]) = (top_vars, bottom_vars) = column_vars

    # domains[C3] + domains[S] + domains[M] = domains[O] + 10*domains[C4]
    # For each columns:
    # domains[C_IN] + domains[TERM_1] + domains[TERM_2] = domains[TOTAL] + 10*domains[C_OUT]

    # top_sum = domains[C_IN] + domains[TERM_1] + domains[TERM_2]
    # bottom_sum = domains[TOTAL] + 10*domains[C_OUT]

    # For each problem solution, each terms will be reduced from a range to a single number.
    # Until we find out what those numbers are we can write the following.

    top_min = min(domains[C_IN]) + min(domains[TERM_1]) + min(domains[TERM_2])  # =  3
    top_max = max(domains[C_IN]) + max(domains[TERM_1]) + max(domains[TERM_2])  # = 11
    bottom_min = min(domains[TOTAL]) + 10 * min(domains[C_OUT])  # = 10
    bottom_max = max(domains[TOTAL]) + 10 * max(domains[C_OUT])  # = 19

    col_min = max(top_min, bottom_min)  # = 10
    col_max = min(top_max, bottom_max)  # = 11

    # Shouldn't need this if we check feasibility after each propagation.
    if col_min > col_max:
        return None

    # Since top_sum == bottom_sum, the following hold.
    # col_min <= top_sum == bottom_sum <= col_max

    # Splitting these into two equations:
    # col_min <= top_sum <= col_max
    # col_min <= bottom_sum <= col_max

    # Can focus on the top and bottom variables separately.
    # Focusing on the top variables:
    for t_i in top_vars:
        # col_min <= domains[C_IN] + domains[TERM_1] + domains[TERM_2] <= col_max
        # Or more generally,
        # col_min <= domains[T_1] + domains[T_2] + ... + domains[T_N] <= col_max

        # Solving for domains[T_i]
        # col_min - (domains[T_1] + ... + domains[T_N]) <= domains[T_i] <= col_max - (domains[T_1] + ... + domains[T_N])
        # Notice that domains[T_i] is left out of the sums on the right and left.
        # Make the left as small as possible and the right as large as possible.
        # Since we are subtracting, we must use max and min on left and right respectively.
        # col_min - max(domains[T_1] + ... + domains[T_N]) <= domains[T_i]
        #                                                            <= col_max - min(domains[T_1] + ... + domains[T_N])
        # Replace max(domains[T_1] + ... + domains[T_N]) -> max(domains[T_1]) + ... + max(domains[T_N])
        # Since max(domains[T_i]) is not included in the sums:
        #                                                -> top_max - max(domains[T_i])
        # Similarly Replace min(domains[T_1] + ... + domains[T_N]) -> top_min - min(domains[T_i])
        # col_min - (top_max - max(domains[T_i])) <= domains[T_i] <= col_max - (top_min - min(domains[T_i]))

        # Split the preceding into two equations
        # col_min - (top_max - max(domains[T_i])) <= domains[T_i]
        # domains[T_i] <= col_max - (top_min - min(domains[T_i]))
        #
        # Equivalently,
        # domains[T_i] >= col_min - (top_max - max(domains[T_i]))     (1a)
        # domains[T_i] <= col_max - (top_min - min(domains[T_i]))     (1b)

        # Let's compute these before changing domains[t_i]
        max_domains_t_i = max(domains[t_i])
        min_domains_t_i = min(domains[t_i])

        # Equation (1a) says: delete from domains[T_i] everything less than col_min - (top_max - max(domains[T_i]))
        # In other words, keep col_min - (top_max - max(domains[T_i])) but delete everything smaller.
        # Or delete everything up to but not including col_min - (top_max - max(domains[T_i]))
        # Or delete range(col_min - (top_max - max(domains[T_i])))
        # domains[T_i] -= set(range(col_min - (top_max - max(domains[T_i]))))
        domains[t_i] = domains[t_i] - set(range(col_min - (top_max - max_domains_t_i)))

        # Shouldn't need this if we check feasibility after each propagation.
        if set() in domains.values( ):
            return None

        # Equation (1b) says: delete from domains[T_i] everything greater than col_max - (top_min - min(domains[T_i]))
        # In other words, keep col_max - (top_min - min(domains[T_i])) but delete everything larger
        # Or delete range(1 + col_min - (top_max - max(domains[T_i])), max(domains[T_i]) + 1)
        # domains[T_i] -= set(range(1 + col_max - (top_min - min(domains[T_i])), max(domains[T_i]) + 1))
        domains[t_i] = domains[t_i] - set(range(1 + col_max - (top_min - min_domains_t_i), max_domains_t_i + 1))

        # Shouldn't need this if we check feasibility after each propagation.
        if set( ) in domains.values( ):
            return None

        # ==> domains['C3'] = {0, 1}  <==
        # ==> domains['S'] = {8, 9}   <==
        # ==> domains['M'] = {1}      <==  (This was given.)

    # Focusing on the bottom variables. Let's use C_OUT and SUM as Python variable names for the two variables.
    [C_OUT, SUM] = bottom_vars

    # Instead of a loop as with the top_vars, we will work with each variable individually.

    # col_min <= domains[SUM] + 10*domains[C_OUT] <= col_max

    # Solving for domains[SUM]
    # col_min - 10*domains[C_OUT] <= domains[SUM] <= col_max - 10*domains[C_OUT]
    # Make the left as small as possible and the right as large as possible.
    # col_min - 10*max(domains[C_OUT]) <= domains[SUM] <= col_max - 10*min(domains[C_OUT])
    #
    # Split the preceding into two equations
    # col_min - 10*max(domains[C_OUT]) <= domains[SUM]
    # domains[SUM] <= col_max - 10*min(domains[C_OUT])
    #
    # Equivalently,
    # domains[SUM] >= col_min - 10*max(domains[C_OUT])   (2a)
    # domains[SUM] <= col_max - 10*min(domains[C_OUT])   (2b)
    #
    # Equation (2a) says: delete from domains[SUM] everything less than col_min - 10*max(domains[C_OUT])
    # In other words, keep col_min - 10*max(domains[C_OUT]) but delete everything smaller.
    # Or delete everything up to but not including col_min - 10*max(domains[C_OUT]).
    # Or delete range(col_min - 10*max(domains[C_OUT]))

    # Compute these before changing the domains
    max_domains_C_OUT = max(domains[C_OUT])
    min_domains_C_OUT = min(domains[C_OUT])
    max_domains_SUM = max(domains[SUM])
    min_domains_SUM = min(domains[SUM])

    domains[SUM] = domains[SUM] - set(range(col_min - 10 * max_domains_C_OUT))

    # Shouldn't need this if we check feasibility after each propagation.
    if set() in domains.values( ):
        return None

    # Equation (2b) says: delete from domains[SUM] everything larger than col_max - 10*min(domains[C_OUT])
    # In other words, keep col_max - 10*min(domains[C_OUT]) but delete everything larger.
    # Or delete everything larger than col_max - 10*min(domains[C_OUT])
    # Or delete range(1 + col_max - 10*min(domains[C_OUT]), max(domains[SUM])+1)

    domains[SUM] = domains[SUM] - set(range(1 + col_max - 10 * min_domains_C_OUT, max_domains_SUM + 1))

    # Shouldn't need this if we check feasibility after each propagation.
    if set() in domains.values( ):
        return None

    domains = all_different_propagator(domains, problem_vars)

    # ==> domains[SUM] = domains['O'] = {0} <==

    # Solving for domains[C_OUT]
    # col_min <= 10*domains[C_OUT] + domains[SUM] <= col_max
    # col_min - domains[SUM] <= 10*domains[C_OUT] <= col_max - domains[SUM]
    # Make the left as small as possible and the right as large as possible.
    # col_min - max(domains[SUM]) <= 10*domains[C_OUT] <= col_max - min(domains[SUM])
    #
    # Split the preceding into two equations
    # col_min - max(domains[SUM]) <= 10*domains[C_OUT]
    # 10*domains[C_OUT] <= col_max - min(domains[SUM])
    #
    # Equivalently,
    # 10*domains[C_OUT] >= col_min - max(domains[SUM])
    # domains[C_OUT] >= (col_min - max(domains[SUM]))/10
    # Since domains[C_OUT] is an integer, we can discard the fractional part of the division.
    # domains[C_OUT] >= ceil((col_min - max(domains[SUM]))/10)    (3a)

    # 10*domains[C_OUT] <= col_max - min(domains[SUM])
    # Since domains[C_OUT] is an integer, we can discard the fractional part of the division.
    # domains[C_OUT] <= floor((col_max - min(domains[SUM])/10)    (3b)

    # Equation (3a) says: delete from domains[C_OUT] everything less than ceil((col_min - max(domains[SUM]))/10)
    # In other words, keep ceil((col_min - max(domains[SUM]))/10) but delete everything smaller.
    # Or delete everything up to but not including ceil((col_min - max(domains[SUM]))/10)
    # Or delete range(ceil((col_min - max(domains[SUM]))/10))
    domains[C_OUT] = domains[C_OUT] - set(range(ceil((col_min - max_domains_SUM) / 10)))

    # Shouldn't need this if we check feasibility after each propagation.
    if set() in domains.values( ):
        return None

    # Equation (3b) says: delete from domains[C_OUT] everything greater than floor((col_max - min(domains[SUM])/10)
    # In other words, keep floor((col_max - min(domains[SUM])/10) but delete everything larger.
    # Or delete everything larger than floor((col_max - min(domains[SUM])/10)
    # Or delete range(1 + floor((col_max - min(domains[SUM])/10), max(domains[C_OUT]) + 1)
    domains[C_OUT] = domains[C_OUT] - set(range(1 + floor((col_max - min_domains_SUM) / 10), max(domains[C_OUT]) + 1))

    # Shouldn't need this if we check feasibility after each propagation.
    if set() in domains.values( ):
        return None

    # ==> domains[C_OUT] = domains['C4'] = {1}   <==  (This was given.)

    return domains


def feasible(cols, domains):
    # for ((c_top, t1, t2), (c_bottom, s)) in cols:
    for (top_terms, (c_bottom, s)) in cols:
        # print(f'\n{c_top}<{max(domains[c_top])}> + {t1}<{max(domains[t1])}> + {t2}<{max(domains[t2])}> <? '
        #       f'10*{c_bottom}<{min(domains[c_bottom])}> + {s}<{min(domains[s])}>')
        # print(f'{c_top}<{min(domains[c_top])}> + {t1}<{min(domains[t1])}> + {t2}<{min(domains[t2])}> >? '
        #       f'10*{c_bottom}<{max(domains[c_bottom])}> + {s}<{max(domains[s])}>')
        # if sum(map(max, [domains[c_top], domains[t1], domains[t2]])) < 10*min(domains[c_bottom]) + min(domains[s]):
        top_domains = [domains[t] for t in top_terms]
        if sum(map(max, top_domains)) < 10*min(domains[c_bottom]) + min(domains[s]):
            # print()
            # print((c_top, t1, t2), (c_bottom, s))
            # print(f'(max) {max(domains[c_top])} + {max(domains[t1])} + {max(domains[t2])} < '
            #       f'(min) 10*{min(domains[c_bottom])} + {min(domains[s])}')
            return False
        # if sum(map(min, [domains[c_top], domains[t1], domains[t2]])) > 10 * max(domains[c_bottom]) + max(domains[s]):
        if sum(map(min, top_domains)) > 10 * max(domains[c_bottom]) + max(domains[s]):
            # print()
            # print((c_top, t1, t2), (c_bottom, s))
            # print(f'(min) {min(domains[c_top])} + {min(domains[t1])} + {min(domains[t2])} > '
            #       f'(max) 10*{max(domains[c_bottom])} + {max(domains[s])}')
            return False
    return True
