#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 51: Prime digit replacements

Problem Statement:
By replacing the 1st digit of the 2-digit number *3, it turns out that six of the nine
possible values: 13, 23, 43, 53, 73, and 83, are all prime.

By replacing the 3rd and 4th digits of 56**3 with the same digit, this 5-digit number
is the first example having seven primes among the ten generated numbers, yielding the
family: 56003, 56113, 56333, 56443, 56663, 56773, and 56993. Consequently 56003,
being the first member of this family, is the smallest prime with this property.

Find the smallest prime which, by replacing part of the number (not necessarily adjacent
digits) with the same digit, is part of an eight prime value family.

Solution Approach:
This solution uses a systematic approach to find prime families through digit replacement:

1. Generate prime numbers in ascending order using the Sundaram sieve algorithm
2. For each prime, try replacing each digit (0-9) with other digits
3. Check how many resulting numbers are also prime
4. When a replacement pattern produces exactly the required number of primes,
   return the smallest prime in that family

Optimizations include:
- Only checking digits 0 through (9-prime_run) for replacement, as we need at least
  'prime_run' valid replacements
- Using efficient primality testing
- Only considering replacements that produce numbers greater than or equal to the
  original prime to ensure we find the smallest such prime

Test Cases:
- For prime_run=6: Returns 13 (family: 13,23,43,53,73,83)
- For prime_run=7: Returns 56003 (family includes 56003,56113,56333,...)
- For prime_run=8: Returns 121313 (the answer)

URL: https://projecteuler.net/problem=51
Answer: 121313
"""
from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList
from euler.utils.primes import gen_primes_sundaram_sieve, is_prime

# The problem number from Project Euler (https://projecteuler.net/problem=51)
problem_number: int = 51

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'prime_run': 6, 'num_digits': 6}, answer=13, ),
    ProblemArgs(kwargs={'prime_run': 7, 'num_digits': 6}, answer=56003, ),
    ProblemArgs(kwargs={'prime_run': 8, 'num_digits': 6}, answer=121313, ),
]


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def smallest_prime_prime_run_generator_on_digit_replacement(*, prime_run: int, num_digits: int) -> int:
    """
    Find the smallest prime that forms a family of prime numbers by digit replacement.

    This solution finds prime numbers where replacing specific digits with other digits
    yields a family of prime numbers of the specified size. It systematically examines
    primes in ascending order and tests various digit replacement patterns until finding
    a prime that belongs to a family of the required size.

    Args:
        prime_run: The required number of primes in the family (e.g., 6, 7, or 8)
        num_digits: The maximum number of digits to consider (default: 6)

    Returns:
        The smallest prime that generates a family of 'prime_run' primes

    Examples:
        >>> smallest_prime_prime_run_generator_on_digit_replacement(prime_run=6)
        13  # Family: 13,23,43,53,73,83
        >>> smallest_prime_prime_run_generator_on_digit_replacement(prime_run=7)
        56003  # Family includes 56003,56113,56333,etc.
        >>> smallest_prime_prime_run_generator_on_digit_replacement(prime_run=8)
        121313  # The answer to the main problem

    Raises:
        ValueError: If no solution is found within the given constraints
    """
    # Generate prime numbers up to the specified limit
    for prime in gen_primes_sundaram_sieve(max_limit=10 ** num_digits):
        # For each digit that can be replaced (we can only replace with digits that would create 'prime_run' primes)
        # We only need to check digits '0' through '9'-(prime_run) because we need 'prime_run' valid replacements
        for replaced in '0123456789'[:10 - prime_run]:
            # Create a sequence of primes by replacing the digit and checking if each result is prime.
            # To avoid duplicates, we only consider replacements with digits >= the original digit,
            # and we only include numbers that are >= the original prime to ensure we find the smallest prime
            sequence = tuple(new_prime for replacement in '0123456789' if replacement >= replaced
                             if (new_prime := int(str(prime).replace(replaced, replacement))) >= prime
                             and is_prime(new_prime))
            # If we found exactly 'prime_run' primes in the family, return the original prime
            if len(sequence) == prime_run:
                return prime
    else:
        # If we've exhausted all primes up to the limit without finding a solution
        raise ValueError('No solution found')


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
