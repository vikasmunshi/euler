#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Solution to Project Euler problem 51.

Problem statement:
By replacing the 1st digit of the 2-digit number *3, it turns out that six of the nine possible values:
13, 23, 43, 53, 73, and 83, are all prime.

By replacing the 3rd and 4th digits of 56**3 with the same digit, this 5-digit number is the first example having
seven primes among the ten generated numbers, yielding the family: 56003, 56113, 56333, 56443, 56663, 56773, and 56993.
Consequently, 56003 being the first member of this family, is the smallest prime with this property.

Find the smallest prime which, by replacing part of the number (not necessarily adjacent digits) with the same digit,
is part of an eight prime value family.

URL: https://projecteuler.net/problem=51
Answer: 121313
"""

# Import prime number generation and testing functions
from euler.primes import gen_primes_sundaram_sieve, is_prime
# Import type definitions for the solution framework
from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# List of test cases with expected answers for validation
# - prime_run=6: Find prime numbers with six-prime value families (answer: 13)
# - prime_run=7: Find prime numbers with seven-prime value families (answer: 56003)
# - prime_run=8: Find prime numbers with eight-prime value families (answer: 121313)
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'prime_run': 6}, answer=13, ),
    ProblemArgs(kwargs={'prime_run': 7}, answer=56003, ),
    ProblemArgs(kwargs={'prime_run': 8}, answer=121313, ),
]


def solution(*, prime_run: int, num_digits: int = 6) -> int:
    """Find the smallest prime that forms a family of prime numbers by digit replacement.

    This function implements the solution to Project Euler problem 51, which involves
    finding prime numbers where replacing specific digits with other digits yields a
    family of prime numbers of a given size.

    The approach works as follows:
    1. Generate prime numbers up to 10^num_digits
    2. For each prime, try replacing all occurrences of each digit (0-9) with other digits
    3. If the replacement generates exactly 'prime_run' prime numbers, return the original prime

    Args:
        prime_run: The required number of primes in the family (e.g., 6, 7, or 8)
        num_digits: The maximum number of digits to consider in the prime numbers (default: 6)

    Returns:
        int: The smallest prime number that generates a family of 'prime_run' primes

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


# Explicitly annotate that this function implements SolutionProtocol
# This ensures type checking validates that our solution conforms to the expected interface
solution: SolutionProtocol

if __name__ == '__main__':
    # When run directly, evaluate the solution with test cases
    # This allows the module to be executed directly to verify the solution

    # Import required modules for evaluating the solution
    from euler.evaluator import evaluate_solution  # Framework for testing solutions
    from euler.cli import parser  # Command-line argument parser
    from euler.logger import logger  # Logging configuration

    # Parse command-line arguments (e.g., logging level, timeout settings)
    args = parser.parse_args()

    # Set the logging level based on command-line arguments
    # This controls the verbosity of output during execution
    logger.setLevel(args.log_level)

    # Extract timeout and maximum worker threads from arguments
    # These control the execution environment for testing
    timeout, max_workers = args.timeout, args.max_workers

    # Run the solution with the specified test cases and parameters
    # This validates that our implementation gives the correct answers for all test cases
    # - solution: The solution function to evaluate
    # - args_list: List of test cases with inputs and expected outputs
    # - timeout: Maximum time allowed for each test case
    # - max_workers: Number of parallel workers for testing
    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)
