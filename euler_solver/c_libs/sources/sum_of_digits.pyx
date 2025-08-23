# distutils: language = c
# cython: boundscheck=False, wraparound=False, cdivision=True, language_level=3

cpdef int sum_of_digits(const long long int n):
    cdef int result = 0
    cdef long long int num = n
    while num > 0:
        result += num % 10
        num //= 10
    return result

__pyi__ = 'def sum_of_digits(n: int) -> int: ...'
