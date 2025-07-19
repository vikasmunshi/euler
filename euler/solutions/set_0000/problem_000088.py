#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 88:

Problem Statement:
A natural number, N, that can be written as the sum and product of a given set of at least two natural numbers,
a₁, a₂,..., a_k is called a product-sum number: N = a₁ + a₂ + ·s + a_k = a₁ × a₂ × ·s × a_k.

For example, 6 = 1 + 2 + 3 = 1 × 2 × 3.

For a given set of size, k, we shall call the smallest N with this property a minimal product-sum number.
The minimal product-sum numbers for sets of size, k = 2, 3, 4, 5, and 6 are as follows.

• k=2: 4 = 2 × 2 = 2 + 2
• k=3: 6 = 1 × 2 × 3 = 1 + 2 + 3
• k=4: 8 = 1 × 1 × 2 × 4 = 1 + 1 + 2 + 4
• k=5: 8 = 1 × 1 × 2 × 2 × 2 = 1 + 1 + 2 + 2 + 2
• k=6: 12 = 1 × 1 × 1 × 1 × 2 × 6 = 1 + 1 + 1 + 1 + 2 + 6

Hence for 2 <= k <= 6, the sum of all the minimal product-sum numbers is 4+6+8+12 = 30;
note that 8 is only counted once in the sum.

In fact, as the complete set of minimal product-sum numbers for 2 < k < 12 is 4, 6, 8, 12, 15, 16, the sum is 61.

What is the sum of all the minimal product-sum numbers for 2 < k < 12000?

Solution Approach:
1. For each value of k, we need to find the minimal product-sum number.
2. We use a recursive approach to generate product-sum combinations efficiently.
3. For a product-sum number, the key insight is that product - sum = k - count, where:
   - product is the product of all numbers in the set
   - sum is the sum of all numbers in the set
   - count is the number of elements in the set
   - k is the target set size
4. We can find k by rearranging: k = product - sum + count
5. We use a recursive function to explore combinations, tracking:
   - The current product
   - The current sum
   - The current count of elements
   - The starting number to prevent duplicates
6. For each valid k we find, we update the minimum product-sum if lower than current.
7. Finally, we sum the unique minimal product-sum numbers across all k values.

Test Cases:
- For 2 ≤ k ≤ 6, the sum should be 30
- For 2 ≤ k ≤ 12000, the answer is 7587457

URL: https://projecteuler.net/problem=88
Answer: 7587457
"""
from typing import List

from euler.evaluator import evaluate_solutions, register_solution, show_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=88)
problem_number: int = 88

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'min_k': 2, 'max_k': 6}, answer=30, ),
    ProblemArgs(kwargs={'min_k': 2, 'max_k': 12000}, answer=7587457, ),
]


# Register this function as a solution for problem #88 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def sum_minimal_product_sum_numbers(*, min_k: int, max_k: int) -> int:
    """
    Calculate the sum of all minimal product-sum numbers for the range min_k ≤ k ≤ max_k.

    A product-sum number is a number that can be expressed as both the sum and product
    of the same set of at least two natural numbers. The minimal product-sum number
    for a given k is the smallest such number that can be expressed using exactly k numbers.

    Args:
        min_k: The minimum set size to consider
        max_k: The maximum set size to consider

    Returns:
        The sum of all unique minimal product-sum numbers in the specified range
    """
    max_k += 1
    min_prod: List[int] = [2 * max_k] * max_k

    def find_product_sum(prod: int, total: int, count: int, start: int) -> None:
        """
        Recursive function to find minimal product-sum numbers.

        This function explores different combinations of numbers to find valid
        product-sum numbers and updates the minimal value for each k.

        Args:
            prod: Current product of the numbers in the set
            total: Current sum of the numbers in the set
            count: Current number of elements in the set
            start: Minimum value to consider for next element (prevents duplicates)
        """
        k = prod - total + count  # Calculate k for the current combination
        if k < max_k:
            min_prod[k] = min(min_prod[k], prod)  # Update minimum for this k if lower
            for i in range(start, (max_k // prod) * 2 + 1):
                find_product_sum(prod * i, total + i, count + 1, i)

    find_product_sum(1, 1, 1, min_k)
    if show_solution():
        print(min_prod[2:])
    return sum(set(min_prod[2:]))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
