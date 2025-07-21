# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 70:

Problem Statement:
Euler's totient function, φ(n) [sometimes called the phi function], is used to determine the number of positive numbers
less than or equal to n which are relatively prime to n. For example, as 1, 2, 4, 5, 7, and 8, are all less than nine
and relatively prime to nine, φ(9)=6.
The number 1 is considered to be relatively prime to every positive number, so φ(1)=1.

Interestingly, φ(87109)=79180, and it can be seen that 87109 is a permutation of 79180.

Find the value of n, 1 < n < 10⁷, for which φ(n) is a permutation of n and the ratio n/φ(n) produces a minimum.

Solution Approach:
The solution takes advantage of a mathematical property: for a product of two primes n = p₁ × p₂,
the totient function φ(n) = (p₁-1)(p₂-1). The ratio n/φ(n) is minimized when p₁ and p₂ are large.

Mathematically, for n = p₁ × p₂:
    n/φ(n) = (p₁ × p₂)/((p₁-1)(p₂-1)) = (p₁ × p₂)/(p₁p₂ - p₁ - p₂ + 1)

As p₁ and p₂ approach infinity, this ratio approaches 1. Therefore, using large primes
helps minimize the ratio.

Strategy:
1. Search for pairs of primes (p₁, p₂) where p₁ × p₂ < 10⁷
2. Focus on primes around the square root of the limit for efficient search
3. For each pair, calculate the product and totient value
4. Check if they're permutations of each other (contain the same digits)
5. Keep track of the pair with the minimum ratio

Test Cases:
- For n < 10⁷, the answer is 8319823 (= 2389 × 3461) with φ(8319823) = 8313928
- For n < 10⁸, the answer is 99836521

URL: https://projecteuler.net/problem=70
Answer: 8319823
"""

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList
from euler.utils.primes import gen_primes_sieve

# The problem number from Project Euler (https://projecteuler.net/problem=70)
problem_number: int = 70

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'n': 10 ** 7}, answer=8319823, ),
    ProblemArgs(kwargs={'n': 10 ** 8}, answer=99836521, ),
]


# Register this function as a solution for problem #70 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def find_min_totient_permutation_ratio(*, n: int) -> int:
    """
    Find the value of n < limit for which φ(n) is a permutation of n and n/φ(n) is minimized.

    The function searches for a number n that is a product of two primes p₁ and p₂,
    where the totient function φ(n) = (p₁-1)(p₂-1) forms a digit permutation of n,
    and the ratio n/φ(n) is minimized.

    Args:
        n: The upper limit for the search (exclusive)

    Returns:
        The value of n < limit for which φ(n) is a permutation of n and n/φ(n) is minimized

    Mathematical background:
    - For a product of two primes: φ(p₁×p₂) = (p₁-1)(p₂-1)
    - The ratio n/φ(n) = (p₁×p₂)/((p₁-1)(p₂-1)) approaches 1 as p₁ and p₂ increase
    - We focus on primes near √n for efficiency
    """
    min_ratio: float = float('inf')  # Initialize with infinity to find minimum
    min_n: int = 0  # The number with the minimum ratio
    sqrt_n = int(n ** 0.5)  # Square root of the limit

    # Set search boundaries for the first prime
    # We start from sqrt(n)/2 to focus on larger primes for a smaller ratio
    min_prime_1, max_prime_1 = sqrt_n // 2, sqrt_n

    for prime_1 in (p for p in gen_primes_sieve() if p > min_prime_1):
        # Exit if we've exceeded our maximum for the first prime
        if prime_1 > max_prime_1:
            break

        # Calculate bounds for the second prime
        # The second prime must be at least prime_1+2 (ensuring different primes)
        # and at most n/prime_1 (ensuring their product is less than n)
        min_prime_2, max_prime_2 = prime_1 + 2, int(n / prime_1)

        for prime_2 in (p for p in gen_primes_sieve() if p > min_prime_2):
            # Exit inner loop if second prime exceeds its maximum
            if prime_2 > max_prime_2:
                break

            # Calculate the number (product of primes) and its totient value
            # Using assignment expressions (:=) for concise code
            # Check if number and totient are permutations of each other by sorting their digits and comparing
            if sorted(str(number := prime_1 * prime_2)) == sorted(str(totient := (prime_1 - 1) * (prime_2 - 1))):
                # Calculate the ratio and update if it's smaller than the current minimum
                if (ratio := number / totient) < min_ratio:
                    min_ratio, min_n = ratio, number
    return min_n


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
