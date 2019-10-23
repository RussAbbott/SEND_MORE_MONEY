# csp.py
# From Classic Computer Science Problems in Python Chapter 3
# Copyright 2018 David Kopec
#
# With relatively minor modifications by Russ Abbott (7/2019)
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

# Modified by Russ Abbott (2019)


# The first import allows the use of CSP as a type in all_different, a method within CSP.
# It shouldn't be necessary in Python 3.8
from __future__ import annotations

from constraints_and_propagators import all_different_assignment_propagator, column_propagator, Domains, feasible
from copy import copy
from typing import Dict, Generic, List, Optional, Tuple, TypeVar

V = TypeVar('V')  # the type of the variables
D = TypeVar('D')  # the type of the domain elements


class CSP(Generic[V, D]):
    """
    A constraint satisfaction problem consists of 
        a) variables of type V that have 
        b) domains of values of type D and 
        c) constraints that determine the validity of a given assignment of values to variables.  
    """
    
    def __init__(self, problem_vars, all_vars, cols, assignment_limit=0):
        self.cols = cols
        self.problem_vars = problem_vars
        self.all_vars = all_vars
        # Keeps track of the number of assignments created
        self.assignment_limit = assignment_limit
        self.assignment_count = 0

    def complete_the_assignment(self, domains: Domains, selected_var=None, selected_val=None) \
                                                                     -> Tuple[Optional[Domains], Domains]:
        """
        Add variable/value pairs to assignment until it either fails a consistsency check or satisfies the constraints.
        :return:
        :param domains:
        :param selected_var: the var that was just assigned a value
        :param selected_val: the assigned value for selected_var
        :return: a consistent assignment or None if no extension of assignment satisfies the constraints.
        """

        (assignment, domains) = self.run_column_propagator(domains)
        if assignment is None:
            return (None, domains)

        # Print assigned/unassigned status
        unassigned_variables: List[V] = [v for v in domains if len(domains[v]) > 1]
        if selected_var is None:
            print(f'\nState after initial propagation')
        else:
            print(f'\nPropagation after setting {selected_var} = {selected_val}')
        print(f'assigned: {assignment};\nunassigned: {unassigned_variables}')

        # If all problem variables are assigned, return result.
        assignment_for_prob_vars = domains_to_assignment(domains)
        if set(self.problem_vars) <= set(assignment_for_prob_vars):
            return (assignment_for_prob_vars, domains)

        # Move on to next unassigned variable.
        selected_var: V = unassigned_variables[0]

        # Try all possible domain values of the selected variable
        for selected_val in domains[selected_var]:

            # Extend the current assignment with: selected_var: selected_val.
            # **assignment lists the elements of assignment.
            # So the following line creates a new dictiony with all the elements of
            # assignment plus the assignment to selected_var.  selected_var: selected_val
            self.assignment_count += 1

            # For a new selected_val start back with the original domains.
            reduced_domains = all_different_assignment_propagator(selected_var, selected_val,
                                                                  copy(domains), self.problem_vars)
            if self.print_assignment_and_check_limit(reduced_domains):
                return (None, reduced_domains)

            # The assignment is consistent with the constraints. Is it complete?
            # An assignment is complete if every variable is assigned a value.
            assignment = domains_to_assignment(reduced_domains)
            if len(assignment) == len(reduced_domains):
                return (assignment, reduced_domains)

            # The assignment is consistent but not complete.
            # Use recursion to complete the assignment.
            # result will be either a valid assignment or None if no valid completion is found.
            (solution, domains_out) = self.complete_the_assignment(reduced_domains, selected_var, selected_val)

            # solution is None if we didn't find a valid assignment for the remaining variables.
            if solution is None:
                # Did we fail because we reached the assignment limit?
                # If so, fail.
                if self.assignment_limit and self.assignment_count >= self.assignment_limit:
                    return (solution, domains_out)
                # If not, continue with the next value for the selected variable.
                else:
                    continue

            # solution is not None. It is a valid assignment. Return it.
            else:  
                return (solution, domains_out)

        # If no value for selected_var yields a valid assignment, return None and
        # let the previous recursive level try the next value for its variable.
        return (None, domains)

    def print_assignment_and_check_limit(self, domains) -> bool:
        """
        Prints current assignment if not exceeded limit.
        Prints "Reached the assignment_limit" if exceeded limit. Prints this message only once.
        Returns True/False if reached assignment limit or not.
        :param domains:
        :return:
        """
        if not self.assignment_limit:
            return False

        if self.assignment_count > self.assignment_limit:
            return True

        print((f'{self.assignment_count:2}' if self.assignment_count < 100 else f'{self.assignment_count}') +
              f'. {domains_to_assignment(domains)}')
        if self.assignment_count == self.assignment_limit:
            print(f'Reached the assignment_limit of {self.assignment_limit}. ')
            return True

        return False

    def run_column_propagator(self, domains):
        """
        Run the column propagator until there are no changes in the domains.
        The normal way to do this would be recursively: either call the function with a recursive call
        if a change occurred or exit. Since the Python world prefers loops, here is a loop version.
        """
        (start_domains, end_domains) = (None, domains)
        while start_domains != end_domains:
            start_domains = copy(end_domains)
            for col in self.cols:
                end_domains = column_propagator(col, end_domains, self.problem_vars)
                # Must check feasibility after each propagation.
                if end_domains is None or not feasible(self.cols, end_domains):
                    return (None, start_domains)
        return (domains_to_assignment(end_domains), end_domains)


def domains_to_assignment(domains) -> Dict[V, D]:
    """
    Return a dictionary of key: value pairs for all keys for which domain[key] is a frozen set of one element.
    To get that element out, must convert from a frozenset to a set. Can then pop() an arbitrary element.
    But since there is only one element, that's the one we get.
    """
    assignment = {v: set(domains[v]).pop() for v in domains if len(domains[v]) == 1}
    return assignment
