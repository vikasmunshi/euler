#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 59: XOR Decryption

Problem Statement:
Each character on a computer is assigned a unique code and the preferred standard is ASCII 
(American Standard Code for Information Interchange). For example, uppercase A = 65, 
asterisk (*) = 42, and lowercase k = 107.

A modern encryption method is to take a text file, convert the bytes to ASCII, then XOR each 
byte with a given value, taken from a secret key. The advantage with the XOR function is that 
using the same encryption key on the cipher text, restores the plain text; for example, 
65 XOR 42 = 107, then 107 XOR 42 = 65.

For unbreakable encryption, the key is the same length as the plain text message, and the key 
is made up of random bytes. The user would keep the encrypted message and the encryption key in 
different locations, and without both "halves", it is impossible to decrypt the message.

Unfortunately, this method is impractical for most users, so the modified method is to use a 
password as a key. If the password is shorter than the message, which is likely, the key is 
repeated cyclically throughout the message. The balance for this method is using a sufficiently
long password key for security, but short enough to be memorable.

Your task has been made easy, as the encryption key consists of three lower case characters. 
Using 0059_cipher.txt (right click and 'Save Link/Target As...'), a file containing the encrypted 
ASCII codes, and the knowledge that the plain text must contain common English words, decrypt 
the message and find the sum of the ASCII values in the original text.

Solution Approach:
This solution uses frequency analysis to break the XOR encryption:

1. Divide the encrypted text into key length parts (in this case the key length is 3)
2. For each part, try all possible lowercase letters as the key character
3. Score each candidate key based on how many common English letters appear in the decrypted text
4. Select the key character that produces the highest score for each part
5. Decrypt the message using the discovered key and calculate the sum of ASCII values

Test Cases:
- Using the provided cipher file, the sum of ASCII values in the decrypted text is 129,448

URL: https://projecteuler.net/problem=59
Answer: 129448
"""
import os
from typing import List, Tuple

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol
from euler.utils import get_text_file

# Test cases for the solution function
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'file_url': 'https://projecteuler.net/resources/documents/0059_cipher.txt',
                        'key_length': 3, 'most_common_letters': 'eEaAnNtT',
                        }, answer=129448, ),
]


def solution(*, file_url: str, key_length: int, most_common_letters: str) -> int:
    """
    Decrypt an XOR-encrypted message and return the sum of ASCII values in the original text.

    This solution uses frequency analysis to break the XOR encryption. It works by:
    1. Dividing the encrypted text into slices based on the key length
    2. For each slice, trying all lowercase letters as possible key characters
    3. Selecting the key character that produces text with the most common English letters
    4. Combining the results to get the complete decrypted message
    5. Returning the sum of ASCII values in the decrypted text

    Args:
        file_url: URL of the file containing the encrypted ASCII codes
        key_length: The length of the encryption key (3 for this problem)
        most_common_letters: String containing the most common letters in English

    Returns:
        The sum of ASCII values in the decrypted text

    Example:
        >>> solution(file_url="https://projecteuler.net/resources/documents/0059_cipher.txt", 
        ...          key_length=3, 
        ...          most_common_letters="eEaAnNtT")
        129448
    """
    encrypted: List[int] = [int(x) for x in get_text_file(file_url).split(',')]
    slices_range: Tuple[int] = tuple(range(key_length))
    encrypted_slices: List[List[int]] = [encrypted[i::key_length] for i in slices_range]
    key: List[int] = [0] * key_length
    score: List[int] = [0] * key_length
    decrypted: List[str] = [''] * key_length
    for _key in range(97, 123):
        for i in slices_range:
            _decrypted = ''.join(chr(_char ^ _key) for _char in encrypted_slices[i])
            if (_score := sum((_decrypted.count(x)) for x in most_common_letters)) > score[i]:
                score[i], key[i], decrypted[i] = _score, _key, _decrypted
    if os.getenv('VISUALIZE') is not None:
        print(''.join(''.join(chars) for chars in zip(*decrypted)))
    return sum(ord(_char) for _decrypted in decrypted for _char in _decrypted)


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
