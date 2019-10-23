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

from itertools import zip_longest
from typing import FrozenSet, List, Tuple

from constraints_and_propagators import Domains
from csp import CSP, domains_to_assignment


def display_result(terms, sum, solution, reduced_domains, assignment_count):
    if solution is None:
        print(f"\nNo solution found after {assignment_count} assignments!")
        print(str(reduced_domains))
        return

    # (term_1, term_2) = terms
    solutions = [''.join([str(solution[x]) for x in t]) for t in terms]
    sum_solution = ''.join([str(solution[x]) for x in sum])
    terms_and_solutions = list(zip(list(['  ']*(len(terms)-1))+['+ '], terms, solutions))
    (start, term_0, solution_0) = terms_and_solutions[0]
    print(f'\n{start}{term_0} ->  {solution_0}')
    for (start, term, term_solution) in terms_and_solutions[1:]:
        print(f'{start}{term} ->  {term_solution}')
    print(f'{"-" * (len(sum) + 1)}    {"-" * (len(sum))}')
    print(f' {sum} -> {sum_solution}')
    print(f'\n{solution}')
    print(f"\nSolution found after {assignment_count} assignments!")


def domains_by_size(domains: Domains, limit=10):
    sorted_domains = {v: domains[v] for v in sorted(domains, key=lambda v: len(domains[v])) if len(domains[v]) <= limit}
    return sorted_domains


def generate_columns(terms, sum) -> Tuple[List[Tuple[List[str], Tuple[str, str]]], List[str]]:
    """
    Given the words of the problem, generates columns associated with those words.
    For example, generate_columns('SEND', 'MORE', 'MONEY') produces the following list of
    tuples, one for each column. Each tuple is a tuple of variables.

    [(['C4', '_', '_'], ('C5', 'M')),
     (['C3', 'S', 'M'], ('C4', 'O')),  # -> corresponds to the column: C3 + S + M = 10*C4 + O
     (['C2', 'E', 'O'], ('C3', 'N')),
     (['C1', 'N', 'R'], ('C2', 'E')),
     (['C0', 'D', 'E'], ('C1', 'Y'))]

    Also return the set of problem variables and the set of carry variables.
    In this case C0 - C5. C0 is the carry into the first column, which is always 0.
    C5 is the carry out of the final column, which also is always 0.  Each entry below is a column.
    For example, (('C3', 'S', 'M'), ('C4', 'O')) corresponds to the leftmost full column: C3 + S + M = 10*C4 + O.

    The number of entries in the first Tuple in each pair is one more than the number of summand words.

    '_' is used for an empty space, e.g., at the left of the summand words.

    """
    carry_vars: List[str] = [f'C{i}' for i in range(len(sum)+1)]  # = ['C1', 'C2', 'C3', 'C4']
    carry_in = carry_vars[:-1]
    carry_out = carry_vars[1:]
    cols = list(reversed(list(zip(zip_longest(carry_in, *map(list, (map(reversed, terms))), fillvalue='_'),
                                  zip_longest(carry_out, list(reversed(sum)), fillvalue=' ')))))
    return (cols, carry_vars)


def generate_columns_and_domains(terms, sum, problem_vars) -> (Domains, Domains, Domains):
    """
    Given a list of problem letters, generates domains for them. The domains are
    hard-wired for SEND + MORE = MONEY. All the domains are set(range(10)) - {1}.
    problem_var_domains['M'] = {1} and problem_var_domains['S'] = problem_var_domains['S'] - {0}.

    domains are also generated for the carry variables.
    :return:
    """
    (cols, carry_vars) = generate_columns(terms, sum)

    digits: FrozenSet[int] = frozenset(range(10))
    problem_var_domains: Domains = {var: digits for var in problem_vars}
    # Require that left-most digits be non-zero.
    for t in terms:
        problem_var_domains[t[0]] = problem_var_domains[t[0]] = digits - {0}

    # carry_vars: List[str] = [f'C{i}' for i in range(6)]    # = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5']
    carry_var_domains: Domains = {var: digits for var in carry_vars}
    # 'C0' and 'C5' are artificial carry-in and carry-out digits.
    # 'C0' carries in to the digits column. It is set to 0.
    carry_var_domains['C0'] = frozenset({0})
    # The carry out of the left-most column needn't be set.

    # Did not set 'M' or C4 to 1.

    # noinspection PyDictCreation
    combined_domains: Domains = {**problem_var_domains, **carry_var_domains}

    # '_' is an artificial anonymous variable set to 0 to fill-out 'SEND' and 'MORE' to '_SEND' and '_MORE'
    combined_domains['_'] = frozenset({0})

    # cols = list(reversed(cols))
    # combined_domains = {**{v: all_domains[v] for v in problem_vars}, **all_domains}

    return (list(reversed(cols)), problem_var_domains, combined_domains)


def run_send_more_money(problem, combined_domains, problem_vars, cols):
    (terms, sum) = problem
    # Set assignment_limit to 0 to turn off tracing. A positive number indicates
    # the number of assignment_count to allow (and to display) before quitting.
    assignment_limit = 0

    # Create the CSP object and set up the problem.
    csp: CSP[str, int] = CSP(problem_vars, set(combined_domains), cols, assignment_limit)
    (solution, reduced_domains) = csp.complete_the_assignment(combined_domains)
    assignment_count = csp.assignment_count if not csp.assignment_limit else \
                       min(csp.assignment_count, csp.assignment_limit)
    display_result(terms,    #  ['SEND', 'MORE']
                   sum,      #  'MONEY'
                   solution if not solution else domains_to_assignment(reduced_domains),
                   reduced_domains,
                   assignment_count)


# col nbr:     4  3  2  1  0  <- col_5 is never created, but C5, it's carry-in bit is created with col_4.
#          C5 C4 C3 C2 C1 C0  <- These are carry variables. C0 and C5 are set to 0.
#              _  S  E  N  D  <- '_' is an anonymous variables, set to 0.
#              _  M  O  R  E  :: These extra variables, C0, C5, and '_' make it possible for columns
#          -----------------  :: all to have the same structure.
#              M  O  N  E  Y
#


def set_up_problem(problem):
    (terms, sum) = problem
    all_letters = ''.join(terms + [sum])

    # compute problem_vars, a list of letters ordered by frequency, with ties broken alphabetically.
    problem_vars = sorted(set(all_letters), key=lambda x: all_letters.count(x), reverse=True)

    (cols, problem_var_domains, combined_domains) = generate_columns_and_domains(terms, sum, problem_vars)

    print(f'\nProblem: {problem}\nProblem vars (in order of frequency): {problem_vars}\n\nColumns:')
    for col_nbr in reversed(range(len(cols))):
        print(f'{col_nbr}. {cols[col_nbr]}')
    print(f'\nInitial domains: {domains_by_size(combined_domains)}\n')

    assignment = domains_to_assignment(combined_domains)
    unassigned_variables = [v for v in combined_domains if len(combined_domains[v]) > 1]
    print(f'Initial state:\nassigned: {assignment};\nunassigned: {unassigned_variables}')
    return (combined_domains, problem_vars, cols)


if __name__ == "__main__":
    problem = (['SEND', 'MORE'], 'MONEY')
    (combined_domains, problem_vars, cols) = set_up_problem(problem)
    run_send_more_money(problem, combined_domains, problem_vars, cols)
