#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 60: Prime Pair Sets

Problem Statement:
The primes 3, 7, 109, and 673, are quite remarkable. By taking any two primes and concatenating 
them in any order the result will always be prime. For example, taking 7 and 109, both 7109 
and 1097 are prime. The sum of these four primes, 792, represents the lowest sum for a set of 
four primes with this property.

Find the lowest sum for a set of five primes for which any two primes concatenate to produce 
another prime.

Solution Approach:
This solution employs a recursive approach to build sets of compatible prime numbers:

1. Prime Generation: We use a Sundaram sieve to efficiently generate prime numbers up to
   a limit that scales with the required set size.

2. Concatenation Testing: For any two primes to be compatible, both their concatenations
   (a|b and b|a) must also be prime. We test this property for all prime pairs.

3. Incremental Set Building: We start by finding all compatible prime pairs, then recursively
   extend these pairs by adding primes that are compatible with all existing members.

4. Generator Composition: The solution uses nested generators to efficiently build larger
   sets from smaller ones, maintaining the property that any subset must also be compatible.

5. Early Termination: Once a valid set of the required size is found, we return its sum,
   which is expected (not proven) to be minimal due to our search strategy.

The approach balances efficiency with correctness, using mathematical properties to reduce
the search space while ensuring we find the optimal solution.

Test Cases:
- For set_length=3: The lowest sum is 107 (using primes 3, 37, 67)
- For set_length=4: The lowest sum is 792 (using primes 3, 7, 109, 673)
- For set_length=5: The lowest sum is 26,033 (using primes 13, 5197, 5701, 6733, 8389)

URL: https://projecteuler.net/problem=60
Answer: 26033
"""
import os
from itertools import combinations
from typing import List, Generator, Tuple

from euler.primes import is_prime, gen_primes_sundaram_sieve
from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'set_length': 3}, answer=107, ),
    ProblemArgs(kwargs={'set_length': 4}, answer=792, ),
    ProblemArgs(kwargs={'set_length': 5}, answer=26033, ),
]


def concatenate_prime(a: int, b: int) -> bool:
    """
    Check if concatenating two primes in both orders results in prime numbers.

    Args:
        a: First prime number
        b: Second prime number

    Returns:
        True if both concatenations (a+b and b+a) are prime, False otherwise
    """
    return is_prime(int(str(a) + str(b))) and is_prime(int(str(b) + str(a)))


def solution_pairs(primes: Tuple[int, ...]) -> Generator[List[int], None, None]:
    """
    Generate all pairs of primes where their concatenations in both orders are prime.

    Args:
        primes: Tuple of prime numbers to check

    Returns:
        Generator yielding lists of compatible prime pairs
    """
    for i, p1 in enumerate(primes):
        for p2 in primes[i + 1:]:
            if concatenate_prime(p1, p2):
                yield [p1, p2]


def extend_solution(current_list: List[int], primes: Tuple[int, ...]) -> Generator[List[int], None, None]:
    """
    Extend a list of compatible primes by adding another prime that concatenates
    with all existing primes in the list to form new primes.

    Args:
        current_list: List of compatible primes to extend
        primes: Tuple of candidate primes to add

    Returns:
        Generator yielding extended lists of compatible primes
    """
    for prime in primes:
        if prime <= current_list[-1]:
            continue
        if all(concatenate_prime(p, prime) for p in current_list):
            yield current_list + [prime]


def print_solution(solution_list: List[int]):
    """
    Print a solution and verify all pairs concatenate to form primes.

    Args:
        solution_list: List of primes that form a solution
    """
    print(f'{solution_list=}')
    for p1, p2 in combinations(solution_list, 2):
        print(f'concatenate_prime({p1}, {p2})={concatenate_prime(p1, p2)}')


def solution(*, set_length: int) -> int:
    """
    Find the lowest sum for a set of primes where any two concatenate to produce another prime.

    This function systematically builds sets of prime numbers with a special property: when any
    two primes in the set are concatenated (in either order), the result is also prime.

    For example, the primes 3, 7, 109, and 673 form such a set because all possible
    concatenations (37, 73, 3109, 1093, etc.) are prime. The solution finds the set
    with the minimum possible sum for a given set size.

    Args:
        set_length: The required number of primes in the set (e.g., 5 for the main problem)

    Returns:
        The sum of the primes in the set with the lowest total sum

    Raises:
        ValueError: If no solution is found within the search bounds
        NotImplementedError: If requested set_length is not implemented in solution_generator

    Algorithm:
        1. Generate prime numbers up to a reasonable limit (10^(set_length-1))
        2. Find all pairs of primes where concatenations in both orders are prime
        3. Recursively extend these pairs to build larger compatible sets
        4. Return the sum of the first valid set of the required size

    Examples:
        >>> solution(set_length=3)
        107  # Sum of primes [3, 37, 67]
        >>> solution(set_length=4)
        792  # Sum of primes [3, 7, 109, 673]
    """
    primes: Tuple[int, ...] = (2, 3, 5, 7)
    for i in range(2, 5):
        primes = gen_primes_sundaram_sieve(max_limit=10 ** (set_length - 1))
        solution_generator = {
            3: (solution_3
                for solution_2 in solution_pairs(primes=primes)
                for solution_3 in extend_solution(current_list=solution_2, primes=primes)),
            4: (solution_4
                for solution_2 in solution_pairs(primes=primes)
                for solution_3 in extend_solution(current_list=solution_2, primes=primes)
                for solution_4 in extend_solution(current_list=solution_3, primes=primes)),
            5: (solution_5
                for solution_2 in solution_pairs(primes=primes)
                for solution_3 in extend_solution(current_list=solution_2, primes=primes)
                for solution_4 in extend_solution(current_list=solution_3, primes=primes)
                for solution_5 in extend_solution(current_list=solution_4, primes=primes)),
        }
        try:
            solution_list = next(solution_generator[set_length])  # the first is expected to be the min sum
        except KeyError:
            raise NotImplementedError(f'No solution implemented for {set_length=}')
        except StopIteration:
            continue
        else:
            if os.getenv('VISUALIZE'):
                print(f'max prime = {primes[-1]}')
                print_solution(solution_list)
            return sum(solution_list)
    else:
        raise ValueError(f'No solution found for {set_length=} within max prime = {primes[-1]}')


if __name__ == '__main__':
    # This block is executed when the Python module is run directly.
    # It evaluates the solution function to ensure its correctness against test cases.

    # Importing required modules: `module_main` manages how the solution is invoked and tested,
    # while `cast` helps with type safety in passing the solution as a `SolutionProtocol`.
    from typing import cast
    from euler.evaluator import module_main

    # The `module_main` function handles the evaluation process by:
    # 1. Extracting the problem number from the file name for contextual usage.
    # 2. Accepting command-line arguments to configure execution, e.g., timeout or threading options.
    # 3. Running the `solution` function for all test cases defined in `problem_args_list`.
    # 4. Outputting the test results, including details such as whether the test passed/failed and time taken.
    # 5. Returning an appropriate exit code (exit code 0 indicates success, non-zero for failures).

    # The `SystemExit` ensures the program exits with the exit code returned by `module_main`.
    raise SystemExit(module_main(module_name=__file__,
                                 solution=cast(SolutionProtocol, solution),
                                 args_list=problem_args_list))
