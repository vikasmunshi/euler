# distutils: language = c
# cython: boundscheck=False, wraparound=False, cdivision=True, language_level=3

cdef int factorial(const int n):
    cdef result = 1
    cdef int i
    for i in range(1, n + 1):
        result *= i
    return result

cdef tuple[int, ...] digit_factorials = tuple(factorial(d) for d in range(10))

cpdef int sum_of_digit_factorials(const long long int n):
    cdef long long int num = <long long int> n
    cdef int result = 0
    while num > 0:
        result += digit_factorials[num % 10]
        num //= 10
    return result

__pyi__ = 'def sum_of_digit_factorials(n: int) -> int: ...'
