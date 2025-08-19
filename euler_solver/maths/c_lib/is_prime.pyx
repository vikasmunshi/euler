# distutils: language = c
# cython: boundscheck=False, wraparound=False, cdivision=True

from libc.math cimport sqrt  # Use C sqrt for better precision and speed

cpdef inline bint is_divisible(long number, long divisor):
    return number % divisor == 0

cpdef bint fast_is_prime(long number):
    if number < 2:
        return False
    if number in (2, 3):
        return True
    if is_divisible(number, 2) or is_divisible(number, 3):
        return False
    cdef long limit = <long> sqrt(number) + 1
    cdef long i
    for i in range(5, limit, 6):
        if is_divisible(number, i) or is_divisible(number, i + 2):
            return False
    return True
