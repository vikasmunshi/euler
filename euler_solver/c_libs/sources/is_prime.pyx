# distutils: language = c
# cython: boundscheck=False, wraparound=False, cdivision=True

from libc.math cimport sqrt  # Use C sqrt for better precision and speed

cdef inline bint is_divisible(const long long int number, const long long int divisor) nogil:
    return number % divisor == 0

cpdef bint is_prime(const long long int number) nogil:
    cdef long long int c_number, i, sqrt_number
    c_number = <long long int> number
    if c_number < 2:
        return False
    if c_number in (2, 3, 5):
        return True
    if is_divisible(c_number, 2) or is_divisible(c_number, 3) or is_divisible(c_number, 5):
        return False
    sqrt_number = <long long int> sqrt(c_number) + 1
    for i in range(5, sqrt_number, 6):
        if is_divisible(c_number, i):
            return False
        if is_divisible(c_number, i + 2):
            return False
    return True

__signature__ = 'def is_prime(number: int) -> bool: ...'  # for stub
