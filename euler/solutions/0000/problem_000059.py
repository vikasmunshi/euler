# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 59: XOR Decryption

This module implements a solution to Project Euler problem 59, which involves
decrypting a text file encoded with XOR encryption using a three-character
lower case key. The solution uses frequency analysis to detect common
English characters and determine the most likely encryption key.

The module provides the following components:
- problem_args_list: A list of predefined test cases with expected answers
- solution(): The main function implementing the XOR decryption algorithm

The final answer is the sum of ASCII values in the decrypted text.
Answer: 129448

URL: https://projecteuler.net/problem=59
"""
from itertools import product
from typing import cast, List

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol
from euler.utils import get_text_file

# Test cases for the solution function
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'file_url': 'https://projecteuler.net/resources/documents/0059_cipher.txt', }, answer=129448, ),
]


def solution(*, file_url: str) -> int:
    """
    This function implements a solution to Project Euler problem 59, which involves decrypting a text file encoded
    with XOR encryption using a three-character lower case key.
    URL: https://projecteuler.net/problem=59

    The solution uses frequency analysis to detect common English characters and determine the most likely plain-text.

    This function solves Project Euler problem 59 by:
    1. Loading encrypted ASCII codes from the provided file URL
    2. Trying all possible 3-character lowercase keys (a-z)
    3. Scoring each decryption attempt based on the frequency of common English letters
    4. Selecting the plain-text that has the highest score
    5. Returning the sum of ASCII values in the decrypted text

    The approach assumes that the most likely correct decryption will contain
    a high frequency of common English letters (E, A, N, T in both cases).    

    Args:
        file_url: URL to a text file containing comma-separated encrypted ASCII codes

    Returns:
        int: Sum of ASCII values in the decrypted text

    Example:
        >>> solution(file_url='https://projecteuler.net/resources/documents/0059_cipher.txt')
        129448
    """
    # Load the encrypted ASCII codes from the provided file URL
    encrypted: List[int] = [int(x) for x in get_text_file(file_url).split(',')]
    len_encrypted = len(encrypted)
    len_key = 3  # The encryption key consists of three lowercase characters

    # Initialize variables for tracking the best decryption result
    score, key, plain_text = 0, (0, 0, 0), ''

    # Try all possible 3-character keys (lowercase a-z, ASCII 97-122)
    for _key in product(range(97, 123), repeat=len_key):
        # Decrypt the message by XORing each encrypted byte with the appropriate key character
        # The key is repeated cyclically (i % len_key) throughout the message
        _plain_text = ''.join(chr(encrypted[i] ^ _key[i % len_key]) for i in range(len_encrypted))

        # Score the decryption based on the frequency of common English letters (E, A, N, T)
        # Higher scores indicate more likely correct decryption
        if (_score := sum(_plain_text.count(char) for char in 'eEaAnNtT')) > score:
            score, key, plain_text = _score, _key, _plain_text

    # Print the decryption key and resulting plain text for inspection
    print(f'{key=}\nplain text:\n{plain_text}\n')

    # Calculate and return the sum of ASCII values in the decrypted text
    return sum(ord(c) for c in plain_text)


if __name__ == '__main__':
    # When run directly, evaluate the solution with test cases
    # Import required modules for evaluating the solution
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    # Parse command-line arguments
    args = parser.parse_args()

    # Set the logging level based on command-line arguments
    logger.setLevel(args.log_level)

    # Extract timeout and maximum worker threads from arguments
    timeout, max_workers = args.timeout, args.max_workers

    # Run the solution with the specified test cases and parameters
    # This validates that our implementation gives the correct answers
    evaluate_solution(solution=cast(SolutionProtocol, solution), args_list=problem_args_list, timeout=timeout,
                      max_workers=max_workers)
