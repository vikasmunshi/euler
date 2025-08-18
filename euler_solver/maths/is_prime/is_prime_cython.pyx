# distutils: language = c
# cython: boundscheck=False, wraparound=False, cdivision=True

from libc.math cimport sqrt  # Use C sqrt for better precision and speed

cdef inline bint is_divisible(long number, long divisor):
    """
    Check if number is divisible by the divisor.
    """
    return number % divisor == 0

def fast_is_prime(long number) -> bool:
    """
    Check if a number is prime using trial division optimized for performance.

    Args:
        number: The number to check for primality.

    Returns:
        True if the number is prime, False otherwise.
    """
    # Handle small primes and edge cases
    if number < 2:
        return False
    if number in (2, 3):  # 2 and 3 are prime
        return True
    if is_divisible(number, 2) or is_divisible(number, 3):  # Eliminate even numbers and multiples of 3
        return False

    # Trial division: test only odd numbers and skip multiples of 2 and 3
    cdef long limit = <long>sqrt(number) + 1  # Use C sqrt for precision
    cdef long i

    for i in range(5, limit, 6):  # Check numbers of the form 6k ± 1
        if is_divisible(number, i) or is_divisible(number, i + 2):
            return False

    return True