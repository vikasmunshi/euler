# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 69: Totient Maximum

Problem Statement:
Euler's totient function, φ(n) [sometimes called the phi function], is defined as the number of positive integers not
exceeding n which are relatively prime to n. For example, as 1, 2, 4, 5, 7, and 8, are all less than or equal to nine
and relatively prime to nine, φ(9)=6.

n  Relatively Prime  φ(n)  n/φ(n)
2  1  1  2
3  1,2  2  1.5
4  1,3  2  2
5  1,2,3,4  4  1.25
6  1,5  2  3
7  1,2,3,4,5,6  6  1.1666...
8  1,3,5,7  4  2
9  1,2,4,5,7,8  6  1.5
10  1,3,7,9  4  2.5

It can be seen that n = 6 produces a maximum n/φ(n) for n≤ 10.

Find the value of n≤ 1\,000\,000 for which n/φ(n) is a maximum.

Mathematical Insights:

1. Euler's Totient Function φ(n):
   - φ(n) counts the positive integers up to n that are coprime (relatively prime) to n
   - Two numbers are coprime when their greatest common divisor (GCD) is 1
   - φ(1) = 1 by definition

2. Properties of φ(n):
   - If p is prime, φ(p) = p-1 (all numbers less than p are coprime to p)
   - If p is prime and k > 0, φ(p^k) = p^k - p^(k-1) = p^k(1 - 1/p)
   - φ is multiplicative: if gcd(m,n) = 1, then φ(m*n) = φ(m)*φ(n)

3. Product Formula for φ(n):
   - If n = p₁^k₁ * p₂^k₂ * ... * pᵣ^kᵣ (prime factorization of n)
   - Then φ(n) = n * (1-1/p₁) * (1-1/p₂) * ... * (1-1/pᵣ)
   - This simplifies to: φ(n) = n * ∏(1-1/pᵢ) for all prime factors pᵢ of n

4. For n/φ(n) Maximum:
   - Using the product formula: n/φ(n) = 1/∏(1-1/pᵢ) = ∏(pᵢ/(pᵢ-1))
   - To maximize n/φ(n), we want to minimize φ(n) relative to n
   - This happens when n has many distinct prime factors, since each factor p contributes a factor of p/(p-1) > 1
   - Smaller primes provide larger values of p/(p-1), so using the smallest available primes is optimal

5. Optimal Solution Insight:
   - The value of n that maximizes n/φ(n) below a given limit will be the product of the smallest consecutive primes
     whose product doesn't exceed the limit
   - This is because smaller primes contribute more to increasing n/φ(n) than larger ones
   - The result must be of the form 2*3*5*7*11*... up to the largest prime that keeps the product under the limit

Solution Approach:
   The solution simply multiplies consecutive primes (2, 3, 5, 7, 11, ...) until the product exceeds the limit,
   then divides by the last prime to get the largest valid product. This product maximizes n/φ(n) because:

   1. It includes as many distinct prime factors as possible (maximizing the product ∏(pᵢ/(pᵢ-1)))
   2. It uses the smallest possible primes (which individually contribute more to n/φ(n))
   3. It maximizes the value of n itself while maintaining these properties

Test Cases:
- For n ≤ 10: 6 = 2*3
- For n ≤ 100: 30 = 2*3*5
- For n ≤ 1,000: 210 = 2*3*5*7
- For n ≤ 10,000: 2,310 = 2*3*5*7*11
- For n ≤ 100,000: 30,030 = 2*3*5*7*11*13
- For n ≤ 1,000,000: 510,510 = 2*3*5*7*11*13*17

URL: https://projecteuler.net/problem=69
Answer: 510510
"""

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList
from euler.utils.primes import gen_primes_sieve

# The problem number from Project Euler (https://projecteuler.net/problem=69)
problem_number: int = 69

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'n': 10 ** 1}, answer=6, ),
    ProblemArgs(kwargs={'n': 10 ** 2}, answer=30, ),
    ProblemArgs(kwargs={'n': 10 ** 3}, answer=210, ),
    ProblemArgs(kwargs={'n': 10 ** 4}, answer=2310, ),
    ProblemArgs(kwargs={'n': 10 ** 5}, answer=30030, ),
    ProblemArgs(kwargs={'n': 10 ** 6}, answer=510510, ),
    ProblemArgs(kwargs={'n': 10 ** 7}, answer=9699690, ),
    ProblemArgs(kwargs={'n': 10 ** 8}, answer=9699690, ),
    ProblemArgs(kwargs={'n': 10 ** 9}, answer=223092870, ),
    ProblemArgs(kwargs={'n': 10 ** 10}, answer=6469693230, ),
    ProblemArgs(kwargs={'n': 10 ** 11}, answer=6469693230, ),
    ProblemArgs(kwargs={'n': 10 ** 12}, answer=200560490130, ),
]


# Register this function as a solution for problem #69 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def solution_69(*, n: int) -> int:
    """Find the value ≤ n for which n/φ(n) is a maximum.

    This solution leverages a key mathematical insight about Euler's totient function:
    To maximize n/φ(n), we want to include as many distinct prime factors as possible,
    starting with the smallest primes.

    The algorithm works by multiplying consecutive primes (2, 3, 5, 7, 11, ...) until
    the product exceeds the limit n, then divides by the last prime to get the largest
    valid product. This approach gives us the number with the maximum value of n/φ(n)
    that doesn't exceed the given limit.

    Why this works:
    1. For any number n with prime factorization p₁^k₁ * p₂^k₂ * ... * pᵣ^kᵣ:
       n/φ(n) = ∏(pᵢ/(pᵢ-1)) for all distinct prime factors pᵢ
    2. Each distinct prime factor increases n/φ(n)
    3. Smaller primes have a larger effect (e.g., 2/(2-1) = 2 > 3/(3-1) = 1.5)
    4. Prime powers don't help (adding p^k instead of a new prime p' is less optimal)

    Args:
        n: The upper limit for the search

    Returns:
        The value ≤ n that maximizes n/φ(n)
    """
    result: int = 1
    for prime_num in gen_primes_sieve():
        # Multiply by each consecutive prime
        if (result := result * prime_num) > n:
            # If we exceed the limit, backtrack by dividing by the last prime
            result = result // prime_num
            break
    return result


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
